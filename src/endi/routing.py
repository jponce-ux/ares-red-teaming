"""Deterministic input classification and routing for ENDI CLI."""

import hashlib
import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from difflib import get_close_matches
from enum import StrEnum
from uuid import uuid4

from endi.authorization import (
    AuthorizationSurface,
    authorization_metadata,
    evaluate_capabilities,
)
from endi.backends import (
    BackendKind,
    ExecutionBackend,
    LocalBackend,
    backend_selection_metadata,
    resolve_backend_selection,
)
from endi.context import (
    build_safe_session_snapshot,
    build_safe_telemetry_payload,
    resolve_context_layers,
)
from endi.conversation import (
    ConversationAction,
    ConversationActionType,
    ConversationResult,
    RuntimeErrorComponent,
    RuntimeErrorEnvelope,
    run_bounded_conversation,
)
from endi.persistence import ExecutionHistoryStore, PersistenceContractError
from endi.providers import (
    ProviderCapability,
    evaluate_local_fallback_policy,
    provider_routing_metadata,
)
from endi.tools import ToolResult, ToolStatus, ToolStatusCode
from endi.workflow import (
    EventType,
    StageEvent,
    WorkflowFailure,
    WorkflowInput,
    WorkflowLifecycleRunner,
    WorkflowOutput,
    WorkflowStage,
    WorkflowStatus,
)

_COMMAND_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_PROVIDER_CONTRACT_FAILURE_CODES = frozenset(
    {
        "invalid_provider_contract",
        "incompatible_provider_contract_version",
        "provider_fallback_blocked",
        "provider_not_found",
    }
)
_PROVIDER_FALLBACK_FAILURE_REASONS = frozenset(
    {
        "missing_credentials",
        "provider_failure",
        "timeout",
    }
)


class RouteKind(StrEnum):
    """Routing outcomes for submitted terminal input."""

    COMMAND = "command"
    CONVERSATION = "conversation"
    VALIDATION_ERROR = "validation_error"
    EXECUTION_ERROR = "execution_error"


@dataclass(frozen=True)
class CommandValidationError:
    """Structured command validation error suitable for terminal output."""

    code: str
    message: str
    hint: str
    execution_id: str | None = None


@dataclass(frozen=True)
class WorkflowExecutionError:
    """Structured workflow runtime failure for command execution."""

    component: WorkflowStage
    failure_type: str
    message: str
    execution_id: str


@dataclass(frozen=True)
class ClassifiedInput:
    """Classification output before execution takes place."""

    route: RouteKind
    raw_input: str
    command_name: str | None
    command_args: list[str]
    validation_error: CommandValidationError | None


@dataclass(frozen=True)
class DispatchResult:
    """Routing result after dispatch, including output when executed."""

    route: RouteKind
    output: object | None
    validation_error: CommandValidationError | None
    execution_error: WorkflowExecutionError | None
    workflow_output: WorkflowOutput[object] | None
    conversation_output: ConversationResult | None
    runtime_error: RuntimeErrorEnvelope | None = None
    resolved_context: dict[str, object] | None = None
    session_snapshot: dict[str, object] | None = None
    telemetry_payload: dict[str, object] | None = None


@dataclass(frozen=True)
class ConversationRuntimeConfig:
    """Runtime configuration for bounded conversational loop execution."""

    max_iterations: int = 3


ConversationRuntime = Callable[[str], ConversationResult]


@dataclass(frozen=True)
class CommandDiscoverability:
    """Canonical metadata for command discoverability surfaces."""

    name: str
    description: str
    arg_schema: str
    examples: tuple[str, ...]
    execution_target: str


_COMMAND_DISCOVERABILITY: tuple[CommandDiscoverability, ...] = (
    CommandDiscoverability(
        name="delete-branch",
        description="Delete a repository branch.",
        arg_schema="<branch-name>",
        examples=("/delete-branch feature/foo",),
        execution_target="worker",
    ),
    CommandDiscoverability(
        name="delete-project",
        description="Delete a project and related resources.",
        arg_schema="<project-name>",
        examples=("/delete-project my-project",),
        execution_target="worker",
    ),
    CommandDiscoverability(
        name="help",
        description="Show command descriptions, argument schemas, and usage examples.",
        arg_schema="[command-name]",
        examples=("/help", "/help show-status"),
        execution_target="local",
    ),
    CommandDiscoverability(
        name="introspect",
        description="Inspect command execution targets and usage contracts.",
        arg_schema="[command-name]",
        examples=("/introspect", "/introspect delete-project"),
        execution_target="local",
    ),
    CommandDiscoverability(
        name="show-status",
        description="Show current environment and workflow status.",
        arg_schema="[scope]",
        examples=("/show-status", "/show-status now"),
        execution_target="local",
    ),
)


def command_discoverability_catalog() -> tuple[CommandDiscoverability, ...]:
    """Return canonical discoverability metadata in deterministic command order."""
    return _COMMAND_DISCOVERABILITY


def nearest_command_suggestion(command_name: str) -> str | None:
    """Return nearest known command suggestion for invalid invocations."""
    normalized = command_name.strip().lower()
    if not normalized:
        return None
    command_names = [metadata.name for metadata in _COMMAND_DISCOVERABILITY]
    matches = get_close_matches(normalized, command_names, n=1, cutoff=0.6)
    return matches[0] if matches else None


class AuthorizationDeniedError(ValueError):
    """Validation-stage authorization denial with deterministic structured details."""

    def __init__(self, message: str, details: dict[str, object]) -> None:
        super().__init__(message)
        self.failure_type = "authorization_denied"
        self.details = details


class ConfirmationMode(StrEnum):
    """Confirmation policy mode resolved from runtime context."""

    PER_ACTION = "per_action"
    APPROVE_PLAN = "approve_plan"


class ConfirmationOutcome(StrEnum):
    """Deterministic outcomes for sensitive action confirmation."""

    APPROVED = "approved"
    DECLINED = "declined"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class ConfirmationDecision:
    """Normalized confirmation decision provided by runtime policy."""

    outcome: ConfirmationOutcome
    actor_id: str | None = None


class ConfirmationDeniedError(ValueError):
    """Validation-stage confirmation denial with deterministic structured details."""

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, object],
        failure_type: str,
    ) -> None:
        super().__init__(message)
        self.failure_type = failure_type
        self.details = details


class BackendUnavailableError(ValueError):
    """Validation-stage backend availability error for selected execution backend."""

    def __init__(self, message: str, details: dict[str, object]) -> None:
        super().__init__(message)
        self.failure_type = "backend_unavailable"
        self.details = details


_SENSITIVE_CAPABILITIES = frozenset(
    {
        "repo.write",
        "filesystem.write",
        "shell.exec",
        "cloud.write",
        "system.modify",
        "network.admin",
    }
)


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _event_status(event_type: EventType) -> str:
    if event_type is EventType.STAGE_FAILED:
        return "failure"
    if event_type is EventType.STAGE_COMPLETED:
        return "success"
    return "in_progress"


def _workflow_duration_ms(events: list[StageEvent]) -> int:
    duration_ms = sum(
        event.duration_ms
        for event in events
        if event.event_type in {EventType.STAGE_COMPLETED, EventType.STAGE_FAILED}
    )
    return max(duration_ms, 0)


def _workflow_failure_status_code(failure_type: str) -> str | None:
    if failure_type == "authorization_denied" or failure_type.startswith("confirmation"):
        return ToolStatusCode.PERMISSION_DENIED.value
    if failure_type == "provider_not_found":
        return ToolStatusCode.NOT_FOUND.value
    if failure_type in _PROVIDER_CONTRACT_FAILURE_CODES:
        return ToolStatusCode.INVALID_CONTRACT.value
    return None


def _parse_provider_capability(value: object) -> ProviderCapability | None:
    if value == ProviderCapability.CHAT.value:
        return ProviderCapability.CHAT
    if value == ProviderCapability.TOOL_CALLING.value:
        return ProviderCapability.TOOL_CALLING
    if value == ProviderCapability.EMBEDDINGS.value:
        return ProviderCapability.EMBEDDINGS
    return None


def _infer_provider_fallback_reason(
    *,
    failure_type: str,
    details: dict[str, object],
) -> str | None:
    reason = details.get("reason")
    if isinstance(reason, str) and reason in _PROVIDER_FALLBACK_FAILURE_REASONS:
        return reason

    normalized_failure_type = failure_type.strip().lower()
    if normalized_failure_type in {"provider_timeout", "timeout"}:
        return "timeout"
    if normalized_failure_type in {
        "provider_missing_credentials",
        "missing_credentials",
    }:
        return "missing_credentials"
    if normalized_failure_type == "provider_failure":
        return "provider_failure"

    return None


def _normalize_provider_fallback_failure(
    *,
    workflow_output: WorkflowOutput[object],
    resolved_context: dict[str, object],
) -> WorkflowOutput[object]:
    failure = workflow_output.failure
    if failure is None or failure.failure_type == "provider_fallback_blocked":
        return workflow_output

    failure_details = dict(failure.details)
    failure_reason = _infer_provider_fallback_reason(
        failure_type=failure.failure_type,
        details=failure_details,
    )
    if failure_reason is None:
        return workflow_output

    capability = _parse_provider_capability(failure_details.get("capability"))
    if capability is None:
        return workflow_output

    selected_provider: str | None = None
    for key in ("selected_provider", "provider_name", "identifier"):
        value = failure_details.get(key)
        if isinstance(value, str) and value:
            selected_provider = value
            break

    if selected_provider is None:
        routing_defaults = provider_routing_metadata(resolved_context).get("defaults")
        if isinstance(routing_defaults, dict):
            default_value = routing_defaults.get(capability.value)
            if isinstance(default_value, str) and default_value:
                selected_provider = default_value

    if selected_provider is None:
        return workflow_output

    fallback_result = evaluate_local_fallback_policy(
        capability=capability,
        selected_provider=selected_provider,
        failure_reason=failure_reason,
        context=resolved_context,
    )
    if fallback_result.error is None:
        return workflow_output

    normalized_failure = WorkflowFailure(
        component=failure.component,
        failure_type=fallback_result.error.code,
        message=fallback_result.error.message,
        details={
            **dict(fallback_result.error.details),
            "upstream_failure_type": failure.failure_type,
        },
    )
    return WorkflowOutput(
        status=workflow_output.status,
        payload=workflow_output.payload,
        metadata=workflow_output.metadata,
        failure=normalized_failure,
    )


def _build_workflow_execution_events(
    *,
    events: list[StageEvent],
    session_id: str,
    command_id: str,
    workflow_id: str,
) -> list[dict[str, object]]:
    execution_events: list[dict[str, object]] = []
    for event in events:
        step_id = f"{workflow_id}:step:{event.sequence:03d}"
        execution_events.append(
            {
                "timestamp": event.timestamp,
                "component": event.stage.value,
                "action": event.event_type.value,
                "status": _event_status(event.event_type),
                "duration_ms": event.duration_ms,
                "correlation": {
                    "session_id": session_id,
                    "command_id": command_id,
                    "workflow_id": workflow_id,
                    "execution_id": event.execution_id,
                    "step_id": step_id,
                },
            }
        )
    return execution_events


def _resolve_execution_history_store(
    resolved_context: dict[str, object],
) -> ExecutionHistoryStore | None:
    def _resolve_positive_int_override(key: str, default: int) -> int:
        value = resolved_context.get(key)
        if type(value) is int and value > 0:
            return value
        return default

    database_path = resolved_context.get("execution_history_db")
    if not isinstance(database_path, str) or not database_path:
        return None

    retention_days = _resolve_positive_int_override(
        "execution_history_retention_days",
        30,
    )
    max_storage_gb = _resolve_positive_int_override(
        "execution_history_max_storage_gb",
        2,
    )

    auto_prune = resolved_context.get("execution_history_auto_prune")
    if not isinstance(auto_prune, bool):
        auto_prune = True

    return ExecutionHistoryStore(
        database_path=database_path,
        retention_days=retention_days,
        max_storage_gb=max_storage_gb,
        auto_prune=auto_prune,
    )


def _session_id_from_context(resolved_context: dict[str, object]) -> str:
    session_id = resolved_context.get("session_id")
    if isinstance(session_id, str) and session_id:
        return session_id
    return "session-default"


def _normalize_capabilities(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        capabilities = [value]
    elif isinstance(value, (list, tuple, set)):
        capabilities = list(value)
    else:
        capabilities = []

    normalized = {
        capability.strip()
        for capability in capabilities
        if isinstance(capability, str) and capability.strip()
    }
    return tuple(sorted(normalized))


def _resolve_granted_capabilities(resolved_context: dict[str, object]) -> tuple[str, ...]:
    return _normalize_capabilities(resolved_context.get("granted_capabilities"))


def _resolve_command_required_capabilities(
    command_name: str,
    resolved_context: dict[str, object],
) -> tuple[str, ...]:
    command_capabilities = resolved_context.get("command_capabilities")
    if isinstance(command_capabilities, dict):
        return _normalize_capabilities(command_capabilities.get(command_name))
    return ()


def _resolve_confirmation_mode(resolved_context: dict[str, object]) -> ConfirmationMode:
    mode_value = resolved_context.get("confirmation_mode")
    if isinstance(mode_value, str):
        normalized = mode_value.strip().lower()
        if normalized == ConfirmationMode.PER_ACTION.value:
            return ConfirmationMode.PER_ACTION
        if normalized == ConfirmationMode.APPROVE_PLAN.value:
            return ConfirmationMode.APPROVE_PLAN
    return ConfirmationMode.PER_ACTION


def _resolve_confirmation_outcome(value: object) -> ConfirmationOutcome:
    if isinstance(value, str):
        normalized = value.strip().lower().replace("-", "_")
        if normalized == ConfirmationOutcome.APPROVED.value:
            return ConfirmationOutcome.APPROVED
        if normalized == ConfirmationOutcome.DECLINED.value:
            return ConfirmationOutcome.DECLINED
        if normalized == ConfirmationOutcome.CANCELLED.value:
            return ConfirmationOutcome.CANCELLED
        if normalized == ConfirmationOutcome.TIMEOUT.value:
            return ConfirmationOutcome.TIMEOUT
    return ConfirmationOutcome.TIMEOUT


def _resolve_confirmation_decision(
    operation: str,
    resolved_context: dict[str, object],
) -> ConfirmationDecision:
    raw_decision: object | None = resolved_context.get("confirmation_decision")
    per_action_decisions = resolved_context.get("confirmation_decisions")
    if isinstance(per_action_decisions, dict):
        if operation in per_action_decisions:
            raw_decision = per_action_decisions.get(operation)

    if isinstance(raw_decision, dict):
        actor_id = raw_decision.get("actor_id")
        return ConfirmationDecision(
            outcome=_resolve_confirmation_outcome(raw_decision.get("outcome")),
            actor_id=actor_id if isinstance(actor_id, str) and actor_id else None,
        )

    return ConfirmationDecision(outcome=_resolve_confirmation_outcome(raw_decision))


def _resolve_summary_targets(
    operation: str,
    resolved_context: dict[str, object],
) -> list[str]:
    command_targets = resolved_context.get("command_targets")
    if not isinstance(command_targets, dict):
        return []

    targets = command_targets.get(operation)
    if not isinstance(targets, list):
        return []
    if not all(isinstance(target, str) for target in targets):
        return []
    return sorted(targets)


def _normalize_targets(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        targets = [value]
    elif isinstance(value, list):
        targets = value
    else:
        return ()
    normalized = {
        target.strip()
        for target in targets
        if isinstance(target, str) and target.strip()
    }
    return tuple(sorted(normalized))


def _build_sensitive_action_record(
    *,
    operation: str,
    required_capabilities: tuple[str, ...],
    resolved_context: dict[str, object],
) -> dict[str, object]:
    backend = resolved_context.get("execution_backend")
    backend_value = backend if isinstance(backend, str) and backend else "local"
    return {
        "operation": operation,
        "capabilities": list(required_capabilities),
        "targets": _resolve_summary_targets(operation, resolved_context),
        "backend": backend_value,
    }


def _normalized_action_record(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    operation = value.get("operation")
    if not isinstance(operation, str) or not operation:
        return None

    backend = value.get("backend")
    backend_value = backend if isinstance(backend, str) and backend else "local"
    capabilities = list(_normalize_capabilities(value.get("capabilities")))
    targets = list(_normalize_targets(value.get("targets")))
    return {
        "operation": operation,
        "capabilities": capabilities,
        "targets": targets,
        "backend": backend_value,
    }


def _resolve_approved_plan(
    resolved_context: dict[str, object],
) -> dict[str, object] | None:
    raw_plan = resolved_context.get("approved_plan")
    if not isinstance(raw_plan, dict):
        return None

    raw_actions = raw_plan.get("actions")
    if not isinstance(raw_actions, list):
        return None
    actions: list[dict[str, object]] = []
    for action in raw_actions:
        normalized_action = _normalized_action_record(action)
        if normalized_action is None:
            return None
        actions.append(normalized_action)
    if not actions:
        return None

    context_id = raw_plan.get("context_id")
    approved = raw_plan.get("approved")
    fingerprint = raw_plan.get("fingerprint")

    return {
        "actions": sorted(
            actions,
            key=lambda action: (
                str(action["operation"]),
                str(action["backend"]),
                str(action["capabilities"]),
                str(action["targets"]),
            ),
        ),
        "approved": approved is True,
        "context_id": context_id if isinstance(context_id, str) and context_id else None,
        "fingerprint": fingerprint if isinstance(fingerprint, str) and fingerprint else None,
    }


def _build_plan_fingerprint(actions: list[dict[str, object]]) -> str:
    serialized_actions = json.dumps(
        actions,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(serialized_actions.encode("utf-8")).hexdigest()[:16]


def _resolve_non_interactive(resolved_context: dict[str, object]) -> bool:
    value = resolved_context.get("non_interactive")
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        return normalized in {"1", "true", "yes", "on"}
    return False


def _action_in_plan(
    *,
    action: dict[str, object],
    approved_plan_actions: list[dict[str, object]],
) -> bool:
    for approved_action in approved_plan_actions:
        if approved_action == action:
            return True
    return False


def _build_approve_plan_summary(
    *,
    action: dict[str, object],
    approved_plan: dict[str, object] | None,
    execution_id: str,
) -> dict[str, object]:
    plan_actions = (
        approved_plan["actions"]
        if approved_plan is not None
        else [action]
    )
    assert isinstance(plan_actions, list)
    plan_fingerprint = _build_plan_fingerprint(plan_actions)
    operation = action.get("operation")
    operation_value = operation if isinstance(operation, str) and operation else "unknown"
    capabilities = action.get("capabilities")
    targets = action.get("targets")
    backend = action.get("backend")
    summary = _build_confirmation_summary_contract(
        intent=operation_value,
        targets=list(_normalize_targets(targets)),
        capabilities=list(_normalize_capabilities(capabilities)),
        backend=backend if isinstance(backend, str) and backend else "local",
        risk_level="high",
        execution_id=execution_id,
        additional_fields={
            "action_count": len(plan_actions),
            "execution_context": {
                "route": RouteKind.COMMAND.value,
                "workflow_stage": WorkflowStage.VALIDATE.value,
            },
            "plan_fingerprint": plan_fingerprint,
            "planned_sensitive_actions": list(plan_actions),
        },
    )
    if approved_plan is not None:
        context_id = approved_plan.get("context_id")
        if isinstance(context_id, str) and context_id:
            summary["context_id"] = context_id
    summary_without_id = dict(summary)
    summary_without_id.pop("summary_id", None)
    summary["summary_id"] = _summary_identifier(summary_without_id)
    return summary


def _validate_non_interactive_approved_plan(
    *,
    approved_plan: dict[str, object] | None,
    expected_action: dict[str, object],
    resolved_context: dict[str, object],
    confirmation_payload: dict[str, object],
) -> None:
    details = dict(confirmation_payload)
    if approved_plan is None:
        raise ConfirmationDeniedError(
            "Approved plan required for non-interactive approve-plan mode.",
            details=details,
            failure_type="confirmation_plan_missing",
        )

    if not approved_plan.get("approved"):
        raise ConfirmationDeniedError(
            "Non-interactive approve-plan mode requires an approved plan artifact.",
            details=details,
            failure_type="confirmation_plan_unapproved",
        )

    plan_actions = approved_plan.get("actions")
    if not isinstance(plan_actions, list):
        raise ConfirmationDeniedError(
            "Approved plan actions are invalid.",
            details=details,
            failure_type="confirmation_plan_invalid",
        )

    expected_fingerprint = _build_plan_fingerprint(plan_actions)
    provided_fingerprint = approved_plan.get("fingerprint")
    if not isinstance(provided_fingerprint, str) or provided_fingerprint != expected_fingerprint:
        details["expected_plan_fingerprint"] = expected_fingerprint
        raise ConfirmationDeniedError(
            "Approved plan fingerprint is invalid for non-interactive execution.",
            details=details,
            failure_type="confirmation_plan_invalid",
        )

    context_id = approved_plan.get("context_id")
    execution_context_id = resolved_context.get("execution_context_id")
    if (
        not isinstance(context_id, str)
        or not context_id
        or not isinstance(execution_context_id, str)
        or context_id != execution_context_id
    ):
        details["approval_context_id"] = context_id
        details["execution_context_id"] = execution_context_id
        raise ConfirmationDeniedError(
            "Approved plan context binding mismatch.",
            details=details,
            failure_type="confirmation_plan_context_mismatch",
        )

    if not _action_in_plan(action=expected_action, approved_plan_actions=plan_actions):
        details["violation"] = "sensitive_action_not_in_approved_plan"
        raise ConfirmationDeniedError(
            "Sensitive action not present in approved plan.",
            details=details,
            failure_type="confirmation_out_of_plan",
        )


def _requires_confirmation(
    required_capabilities: tuple[str, ...],
    mode: ConfirmationMode,
) -> bool:
    if not any(capability in _SENSITIVE_CAPABILITIES for capability in required_capabilities):
        return False
    return mode in {ConfirmationMode.PER_ACTION, ConfirmationMode.APPROVE_PLAN}


def _summary_identifier(summary: dict[str, object]) -> str:
    serialized_summary = json.dumps(
        summary,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(serialized_summary.encode("utf-8")).hexdigest()[:16]


def _build_confirmation_summary_contract(
    *,
    intent: str,
    targets: list[str],
    capabilities: list[str],
    backend: str,
    risk_level: str,
    execution_id: str,
    additional_fields: dict[str, object] | None = None,
) -> dict[str, object]:
    summary: dict[str, object] = {
        "intent": intent,
        "targets": list(targets),
        "capabilities": list(capabilities),
        "backend": backend,
        "risk_level": risk_level,
        "execution_id": execution_id,
    }
    if additional_fields is not None:
        for key in sorted(additional_fields):
            summary[key] = additional_fields[key]

    sanitized_summary = _remove_raw_text_fields(summary)
    if not isinstance(sanitized_summary, dict):
        return summary
    sanitized_summary["summary_id"] = _summary_identifier(sanitized_summary)
    return sanitized_summary


def _build_high_impact_summary(
    *,
    operation: str,
    required_capabilities: tuple[str, ...],
    resolved_context: dict[str, object],
    execution_id: str,
) -> dict[str, object]:
    backend = resolved_context.get("execution_backend")
    backend_value = backend if isinstance(backend, str) and backend else "local"
    capabilities = list(required_capabilities)
    targets = _resolve_summary_targets(operation, resolved_context)
    return _build_confirmation_summary_contract(
        intent=operation,
        targets=targets,
        capabilities=capabilities,
        backend=backend_value,
        risk_level="high",
        execution_id=execution_id,
        additional_fields={
            "execution_context": {
                "route": RouteKind.COMMAND.value,
                "workflow_stage": WorkflowStage.VALIDATE.value,
            },
        },
    )


def _build_confirmation_payload(
    *,
    mode: ConfirmationMode,
    required: bool,
    decision: ConfirmationDecision,
    summary: dict[str, object] | None,
    backend_selection: dict[str, object],
) -> dict[str, object]:
    payload: dict[str, object] = {
        "mode": mode.value,
        "required": required,
        "outcome": decision.outcome.value,
        "backend_selection": dict(backend_selection),
    }
    if decision.actor_id is not None:
        payload["actor_id"] = decision.actor_id
    if summary is not None:
        payload["summary"] = summary
    return payload


def _run_default_conversation_runtime(
    user_input: str,
    conversation_handler: Callable[[str], str],
    max_iterations: int,
) -> ConversationResult:
    return run_bounded_conversation(
        user_input=user_input,
        max_iterations=max_iterations,
        select_action=lambda text, _turns: ConversationAction(
            action_type=ConversationActionType.COMPLETE,
            response_text=conversation_handler(text),
        ),
        execute_tool=lambda _tool_name, _tool_args: "",
        synthesize_response=lambda text, _turns, _references: conversation_handler(text),
    )


def _validation_error(
    message: str,
    invalid_command_name: str | None = None,
) -> CommandValidationError:
    hint = "Use lowercase kebab-case command names (e.g. /show-status) or /help."
    if invalid_command_name is not None:
        suggestion = nearest_command_suggestion(invalid_command_name)
        if suggestion is not None:
            hint = f"{hint} Did you mean /{suggestion}?"

    return CommandValidationError(
        code="invalid_command_syntax",
        message=message,
        hint=hint,
        execution_id=None,
    )


def _execution_validation_error(message: str, execution_id: str) -> CommandValidationError:
    return CommandValidationError(
        code="invalid_command_execution",
        message=message,
        hint="Review command arguments and try again.",
        execution_id=execution_id,
    )


_RAW_TEXT_CONTEXT_FIELDS = {
    "command_args",
    "conversation_text",
    "input_text",
    "raw_input",
    "request_text",
    "response_text",
    "user_input",
}


def _build_command_context_for_telemetry(
    resolved_context: dict[str, object],
) -> dict[str, object]:
    return _build_context_without_raw_text_fields(resolved_context)


def _build_context_without_raw_text_fields(
    resolved_context: dict[str, object],
) -> dict[str, object]:
    telemetry_context: dict[str, object] = {}
    for key in sorted(resolved_context):
        if key in _RAW_TEXT_CONTEXT_FIELDS:
            continue
        telemetry_context[key] = resolved_context[key]
    return telemetry_context


def _remove_raw_text_fields(value: object) -> object:
    if isinstance(value, dict):
        sanitized: dict[str, object] = {}
        for key in sorted(value):
            if key in _RAW_TEXT_CONTEXT_FIELDS:
                continue
            sanitized[key] = _remove_raw_text_fields(value[key])
        return sanitized
    if isinstance(value, list):
        return [_remove_raw_text_fields(item) for item in value]
    return value


def _to_string_list(value: object) -> list[str] | None:
    if not isinstance(value, list):
        return None
    if not all(isinstance(item, str) for item in value):
        return None
    return value


def _extract_authorization_decision(
    runtime_error: RuntimeErrorEnvelope,
) -> dict[str, object] | None:
    if runtime_error.code != "capability_denied":
        return None

    details = runtime_error.details
    if not isinstance(details, dict):
        return None

    surface = details.get("surface")
    operation = details.get("operation")
    allowed = details.get("allowed")
    required_capabilities = _to_string_list(details.get("required_capabilities"))
    missing_capabilities = _to_string_list(details.get("missing_capabilities"))
    if (
        not isinstance(surface, str)
        or not isinstance(operation, str)
        or not isinstance(allowed, bool)
        or required_capabilities is None
        or missing_capabilities is None
    ):
        return None

    return {
        "surface": surface,
        "operation": operation,
        "allowed": allowed,
        "required_capabilities": required_capabilities,
        "missing_capabilities": missing_capabilities,
    }


def _extract_confirmation_decision(
    runtime_error: RuntimeErrorEnvelope,
) -> dict[str, object] | None:
    if not runtime_error.code.startswith("confirmation_"):
        return None

    details = runtime_error.details
    if not isinstance(details, dict):
        return None

    mode = details.get("mode")
    required = details.get("required")
    outcome = details.get("outcome")
    if not isinstance(mode, str) or not isinstance(required, bool) or not isinstance(outcome, str):
        return None

    payload: dict[str, object] = {
        "mode": mode,
        "required": required,
        "outcome": outcome,
    }
    actor_id = details.get("actor_id")
    if isinstance(actor_id, str) and actor_id:
        payload["actor_id"] = actor_id
    summary = details.get("summary")
    if isinstance(summary, dict):
        sanitized_summary = _remove_raw_text_fields(summary)
        if isinstance(sanitized_summary, dict):
            payload["summary"] = sanitized_summary
    execution_id = details.get("execution_id")
    if isinstance(execution_id, str) and execution_id:
        payload["correlation"] = {"execution_id": execution_id}
    return payload


def _extract_backend_selection(runtime_error: RuntimeErrorEnvelope) -> dict[str, object] | None:
    details = runtime_error.details
    if not isinstance(details, dict):
        return None

    selection = details.get("backend_selection")
    if not isinstance(selection, dict):
        return None

    sanitized_selection = _remove_raw_text_fields(selection)
    if not isinstance(sanitized_selection, dict):
        return None
    return sanitized_selection


def _extract_provider_fallback(runtime_error: RuntimeErrorEnvelope) -> dict[str, object] | None:
    if runtime_error.code != "provider_fallback_blocked":
        return None

    details = runtime_error.details
    if not isinstance(details, dict):
        return {
            "decision": "fallback_blocked",
            "fallback_enabled": False,
            "fallback_mode": "explicit_only",
        }

    capability = details.get("capability")
    selected_provider = details.get("selected_provider")
    fallback_provider = details.get("fallback_provider")
    fallback_mode = details.get("fallback_mode")
    fallback_enabled = details.get("fallback_enabled")
    reason = details.get("reason")
    decision = details.get("decision")

    payload: dict[str, object] = {
        "decision": (
            decision if isinstance(decision, str) and decision else "fallback_blocked"
        ),
        "fallback_enabled": (
            fallback_enabled if isinstance(fallback_enabled, bool) else False
        ),
        "fallback_mode": (
            fallback_mode if isinstance(fallback_mode, str) and fallback_mode else "explicit_only"
        ),
    }
    if isinstance(capability, str) and capability:
        payload["capability"] = capability
    if isinstance(selected_provider, str) and selected_provider:
        payload["selected_provider"] = selected_provider
    if isinstance(fallback_provider, str) and fallback_provider:
        payload["fallback_provider"] = fallback_provider
    if isinstance(reason, str) and reason:
        payload["reason"] = reason

    sanitized = _remove_raw_text_fields(payload)
    return sanitized if isinstance(sanitized, dict) else payload


def _extract_provider_contract(runtime_error: RuntimeErrorEnvelope) -> dict[str, object] | None:
    if runtime_error.code not in _PROVIDER_CONTRACT_FAILURE_CODES:
        return None

    details = runtime_error.details
    if not isinstance(details, dict):
        return {
            "code": runtime_error.code,
            "capability": None,
            "provider_name": None,
            "missing_fields": [],
            "invalid_fields": [],
        }

    capability = details.get("capability")
    provider_name = details.get("provider_name")
    if not isinstance(provider_name, str) or not provider_name:
        provider_name = details.get("identifier")
    missing_fields = details.get("missing_fields")
    invalid_fields = details.get("invalid_fields")

    payload: dict[str, object] = {
        "code": runtime_error.code,
        "capability": capability if isinstance(capability, str) else None,
        "provider_name": provider_name if isinstance(provider_name, str) else None,
        "missing_fields": (
            sorted(field for field in missing_fields if isinstance(field, str))
            if isinstance(missing_fields, list)
            else []
        ),
        "invalid_fields": (
            sorted(field for field in invalid_fields if isinstance(field, str))
            if isinstance(invalid_fields, list)
            else []
        ),
    }

    expected_version = details.get("expected_version")
    actual_version = details.get("actual_version")
    if type(expected_version) is int and expected_version > 0:
        payload["expected_version"] = expected_version
    if type(actual_version) is int and actual_version > 0:
        payload["actual_version"] = actual_version

    registered = details.get("registered")
    if isinstance(registered, list):
        payload["registered"] = sorted(
            identifier for identifier in registered if isinstance(identifier, str)
        )

    sanitized = _remove_raw_text_fields(payload)
    return sanitized if isinstance(sanitized, dict) else payload


def _build_conversation_execution_id(
    *,
    session_id: str,
    conversation_output: ConversationResult,
    runtime_error: RuntimeErrorEnvelope | None,
) -> str:
    if runtime_error is not None:
        details = runtime_error.details
        if isinstance(details, dict):
            execution_id = details.get("execution_id")
            if isinstance(execution_id, str) and execution_id:
                return execution_id

    turn_fingerprint = [
        {
            "iteration": turn.iteration,
            "action_type": turn.action.action_type.value,
            "tool_name": turn.action.tool_name,
            "has_observation": turn.observation is not None,
            "reference_id": turn.observation.reference_id if turn.observation is not None else None,
        }
        for turn in conversation_output.metadata.turns
    ]
    payload = {
        "session_id": session_id,
        "termination_reason": conversation_output.metadata.termination_reason.value,
        "iterations": conversation_output.metadata.iterations,
        "max_iterations": conversation_output.metadata.max_iterations,
        "turns": turn_fingerprint,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"conv-{digest}"


def _observability_parent_linkage_error(
    *,
    execution_id: str,
    event_component: str,
    reason: str,
    iteration: int | None = None,
) -> RuntimeErrorEnvelope:
    details: dict[str, object] = {
        "error": {
            "type": "runtime_error",
            "code": "observability_parent_linkage_invalid",
            "component": RuntimeErrorComponent.WORKFLOW.value,
        },
        "surface": RouteKind.CONVERSATION.value,
        "event_component": event_component,
        "reason": reason,
        "execution_id": execution_id,
    }
    if iteration is not None:
        details["iteration"] = iteration

    return RuntimeErrorEnvelope(
        code="observability_parent_linkage_invalid",
        component=RuntimeErrorComponent.WORKFLOW,
        message="Conversation observability parent linkage is invalid.",
        status_code=ToolStatusCode.INVALID_CONTRACT.value,
        details=details,
    )


def _build_conversation_correlation_extension(
    *,
    session_id: str,
    conversation_output: ConversationResult,
    runtime_error: RuntimeErrorEnvelope | None,
) -> tuple[dict[str, object], RuntimeErrorEnvelope | None]:
    execution_id = _build_conversation_execution_id(
        session_id=session_id,
        conversation_output=conversation_output,
        runtime_error=runtime_error,
    )
    command_id = f"cmd-{execution_id}"
    workflow_id = f"wf-{execution_id}"
    correlation_extension: dict[str, object] = {
        "execution_id": execution_id,
        "command_id": command_id,
        "workflow_id": workflow_id,
        "events": [],
    }
    turn_events: list[dict[str, object]] = []
    step_ids: set[str] = set()

    for turn in conversation_output.metadata.turns:
        if turn.iteration < 1:
            return correlation_extension, _observability_parent_linkage_error(
                execution_id=execution_id,
                event_component="step",
                reason="invalid_step_iteration",
                iteration=turn.iteration,
            )

        step_id = f"{workflow_id}:step:{turn.iteration:03d}"
        if step_id in step_ids:
            return correlation_extension, _observability_parent_linkage_error(
                execution_id=execution_id,
                event_component="step",
                reason="duplicate_step_identifier",
                iteration=turn.iteration,
            )
        step_ids.add(step_id)

        turn_events.append(
            {
                "component": "step",
                "correlation": {
                    "session_id": session_id,
                    "command_id": command_id,
                    "workflow_id": workflow_id,
                    "execution_id": execution_id,
                    "step_id": step_id,
                },
                "parent": {"workflow_id": workflow_id},
                "iteration": turn.iteration,
            }
        )

        agent_id = f"{step_id}:agent"
        turn_events.append(
            {
                "component": RuntimeErrorComponent.AGENT.value,
                "correlation": {
                    "session_id": session_id,
                    "command_id": command_id,
                    "workflow_id": workflow_id,
                    "execution_id": execution_id,
                    "step_id": step_id,
                    "agent_id": agent_id,
                },
                "parent": {
                    "workflow_id": workflow_id,
                    "step_id": step_id,
                },
                "agent": {
                    "action_type": turn.action.action_type.value,
                },
            }
        )

        if turn.action.action_type is not ConversationActionType.TOOL_CALL:
            if turn.observation is not None:
                return correlation_extension, _observability_parent_linkage_error(
                    execution_id=execution_id,
                    event_component="tool_call",
                    reason="orphan_tool_observation",
                    iteration=turn.iteration,
                )
            continue

        tool_name = turn.action.tool_name
        if not isinstance(tool_name, str) or not tool_name:
            return correlation_extension, _observability_parent_linkage_error(
                execution_id=execution_id,
                event_component="tool_call",
                reason="missing_tool_name",
                iteration=turn.iteration,
            )

        raw_tool_call_id = (
            turn.observation.reference_id
            if turn.observation is not None
            else f"{agent_id}:tool_call"
        )
        tool_call_id = (
            raw_tool_call_id.strip() if isinstance(raw_tool_call_id, str) else ""
        )
        if not tool_call_id:
            return correlation_extension, _observability_parent_linkage_error(
                execution_id=execution_id,
                event_component="tool_call",
                reason="missing_tool_call_identifier",
                iteration=turn.iteration,
            )

        tool_arg_keys = []
        if isinstance(turn.action.tool_args, dict):
            tool_arg_keys = sorted(
                key
                for key in turn.action.tool_args
                if isinstance(key, str) and key and key not in _RAW_TEXT_CONTEXT_FIELDS
            )

        turn_events.append(
            {
                "component": "tool_call",
                "correlation": {
                    "session_id": session_id,
                    "command_id": command_id,
                    "workflow_id": workflow_id,
                    "execution_id": execution_id,
                    "step_id": step_id,
                    "agent_id": agent_id,
                    "tool_call_id": tool_call_id,
                },
                "parent": {
                    "workflow_id": workflow_id,
                    "step_id": step_id,
                    "agent_id": agent_id,
                },
                "tool_call": {
                    "tool_name": tool_name,
                    "reference_id": (
                        tool_call_id
                        if turn.observation is not None
                        else None
                    ),
                    "arg_keys": tool_arg_keys,
                },
            }
        )

    correlation_extension["events"] = turn_events
    return correlation_extension, None


def _build_command_telemetry_payload(
    *,
    resolved_context: dict[str, object],
    workflow_output: WorkflowOutput[object],
    command_name: str,
    command_args: list[str],
    session_id: str,
    command_id: str,
    workflow_id: str,
    backend_selection: dict[str, object],
    authorization: dict[str, object],
    confirmation: dict[str, object] | None,
) -> dict[str, object]:
    telemetry_payload: dict[str, object] = {
        "event": "command_dispatch",
        "envelope": {
            "timestamp": _utc_now_iso(),
            "component": RouteKind.COMMAND.value,
            "action": "command_dispatch",
            "status": workflow_output.status.value,
            "duration_ms": _workflow_duration_ms(workflow_output.metadata.events),
        },
        "correlation": {
            "route": RouteKind.COMMAND.value,
            "session_id": session_id,
            "command_id": command_id,
            "workflow_id": workflow_id,
            "execution_id": workflow_output.metadata.execution_id,
        },
        "command": {
            "name": command_name,
            "arg_count": len(command_args),
        },
        "workflow": {
            "status": workflow_output.status.value,
            "skipped_stages": [
                stage.value for stage in workflow_output.metadata.skipped_stages
            ],
        },
        "execution_events": _build_workflow_execution_events(
            events=workflow_output.metadata.events,
            session_id=session_id,
            command_id=command_id,
            workflow_id=workflow_id,
        ),
        "backend_selection": dict(backend_selection),
        "provider_routing": provider_routing_metadata(resolved_context),
        "authorization_decision": authorization,
        "context": _build_command_context_for_telemetry(resolved_context),
    }
    if workflow_output.failure is not None:
        telemetry_payload["runtime_error"] = {
            "type": "runtime_error",
            "code": workflow_output.failure.failure_type,
            "component": workflow_output.failure.component.value,
            "status_code": _workflow_failure_status_code(workflow_output.failure.failure_type),
        }
        telemetry_payload["failure"] = {
            "component": workflow_output.failure.component.value,
            "failure_type": workflow_output.failure.failure_type,
            "message": workflow_output.failure.message,
            "details": dict(workflow_output.failure.details),
        }
    if confirmation is not None:
        confirmation_payload = dict(confirmation)
        confirmation_payload["correlation"] = {
            "execution_id": workflow_output.metadata.execution_id,
        }
        telemetry_payload["confirmation_decision"] = confirmation_payload
    if workflow_output.failure is not None:
        failure_runtime_error = RuntimeErrorEnvelope(
            code=workflow_output.failure.failure_type,
            component=RuntimeErrorComponent.WORKFLOW,
            message=workflow_output.failure.message,
            status_code=_workflow_failure_status_code(workflow_output.failure.failure_type),
            details=dict(workflow_output.failure.details),
        )
        provider_fallback_payload = _extract_provider_fallback(failure_runtime_error)
        if provider_fallback_payload is not None:
            telemetry_payload["provider_fallback"] = provider_fallback_payload
    return build_safe_telemetry_payload(telemetry_payload)


def classify_input(user_input: str) -> ClassifiedInput:
    """Classify terminal input as command, conversation, or validation error."""
    normalized_input = user_input.strip()
    if not normalized_input.startswith("/"):
        return ClassifiedInput(
            route=RouteKind.CONVERSATION,
            raw_input=user_input,
            command_name=None,
            command_args=[],
            validation_error=None,
        )

    command_payload = normalized_input[1:].strip()
    if not command_payload:
        return ClassifiedInput(
            route=RouteKind.VALIDATION_ERROR,
            raw_input=user_input,
            command_name=None,
            command_args=[],
            validation_error=_validation_error("Unsupported command syntax: missing command name."),
        )

    command_parts = command_payload.split()
    command_name = command_parts[0]
    if not _COMMAND_NAME_PATTERN.fullmatch(command_name):
        return ClassifiedInput(
            route=RouteKind.VALIDATION_ERROR,
            raw_input=user_input,
            command_name=None,
            command_args=[],
            validation_error=_validation_error(
                f"Unsupported command syntax: '{command_name}' is not a valid command name.",
                invalid_command_name=command_name,
            ),
        )

    return ClassifiedInput(
        route=RouteKind.COMMAND,
        raw_input=user_input,
        command_name=command_name,
        command_args=command_parts[1:],
        validation_error=None,
    )


def dispatch_input(
    user_input: str,
    command_executor: Callable[[str, list[str]], object],
    conversation_handler: Callable[[str], str],
    conversation_config: ConversationRuntimeConfig | None = None,
    conversation_runtime: ConversationRuntime | None = None,
    explicit_context: dict[str, object] | None = None,
    command_context: dict[str, object] | None = None,
    session_context: dict[str, object] | None = None,
    project_context: dict[str, object] | None = None,
    environment_context: dict[str, object] | None = None,
    default_context: dict[str, object] | None = None,
    execution_backends: dict[BackendKind, ExecutionBackend] | None = None,
) -> DispatchResult:
    """Dispatch input to command or conversation path based on deterministic classification."""
    classified = classify_input(user_input)

    resolved_context = resolve_context_layers(
        explicit_input=explicit_context,
        command_inputs=command_context,
        session=session_context,
        project=project_context,
        environment=environment_context,
        defaults=default_context,
    )

    if classified.route is RouteKind.VALIDATION_ERROR:
        return DispatchResult(
            route=RouteKind.VALIDATION_ERROR,
            output=None,
            validation_error=classified.validation_error,
            execution_error=None,
            workflow_output=None,
            conversation_output=None,
            runtime_error=(
                RuntimeErrorEnvelope(
                    code=classified.validation_error.code,
                    component=RuntimeErrorComponent.COMMAND,
                    message=classified.validation_error.message,
                )
                if classified.validation_error is not None
                else None
            ),
            resolved_context=resolved_context,
        )

    if classified.route is RouteKind.COMMAND:
        assert classified.command_name is not None
        command_name = classified.command_name
        command_args = classified.command_args
        command_payload_context = {
            "command_name": command_name,
            "command_args": command_args,
        }
        merged_command_inputs = dict(command_context or {})
        merged_command_inputs.update(command_payload_context)
        resolved_context = resolve_context_layers(
            explicit_input=explicit_context,
            command_inputs=merged_command_inputs,
            session=session_context,
            project=project_context,
            environment=environment_context,
            defaults=default_context,
        )
        granted_capabilities = _resolve_granted_capabilities(resolved_context)
        required_capabilities = _resolve_command_required_capabilities(
            command_name,
            resolved_context,
        )
        backend_selection = resolve_backend_selection(
            required_capabilities=required_capabilities,
            context=resolved_context,
        )
        backend_selection_payload = backend_selection_metadata(backend_selection)
        resolved_context = dict(resolved_context)
        resolved_context["execution_backend"] = backend_selection.selected_backend.value
        resolved_context["backend_selection"] = backend_selection_payload
        confirmation_mode = _resolve_confirmation_mode(resolved_context)
        confirmation_required = _requires_confirmation(
            required_capabilities,
            confirmation_mode,
        )
        sensitive_action = (
            _build_sensitive_action_record(
                operation=command_name,
                required_capabilities=required_capabilities,
                resolved_context=resolved_context,
            )
            if confirmation_required
            else None
        )
        approved_plan = (
            _resolve_approved_plan(resolved_context)
            if confirmation_mode is ConfirmationMode.APPROVE_PLAN and confirmation_required
            else None
        )
        workflow_execution_id = uuid4().hex
        workflow_input = WorkflowInput(
            payload=command_payload_context,
            execution_id=workflow_execution_id,
        )
        confirmation_summary = (
            _build_approve_plan_summary(
                action=sensitive_action,
                approved_plan=approved_plan,
                execution_id=workflow_execution_id,
            )
            if confirmation_mode is ConfirmationMode.APPROVE_PLAN and sensitive_action is not None
            else (
                _build_high_impact_summary(
                    operation=command_name,
                    required_capabilities=required_capabilities,
                    resolved_context=resolved_context,
                    execution_id=workflow_execution_id,
                )
                if confirmation_required
                else None
            )
        )
        confirmation_decision = _resolve_confirmation_decision(
            command_name,
            resolved_context,
        )
        confirmation_payload = _build_confirmation_payload(
            mode=confirmation_mode,
            required=confirmation_required,
            decision=confirmation_decision,
            summary=confirmation_summary,
            backend_selection=backend_selection_payload,
        )
        authorization_decision = evaluate_capabilities(
            required_capabilities=required_capabilities,
            granted_capabilities=granted_capabilities,
        )
        authorization_payload = authorization_metadata(
            decision=authorization_decision,
            surface=AuthorizationSurface.COMMAND,
            operation=command_name,
        )
        authorization_payload["backend_selection"] = dict(backend_selection_payload)
        backend_registry: dict[BackendKind, ExecutionBackend] = {
            BackendKind.LOCAL: LocalBackend(command_executor=command_executor)
        }
        if execution_backends is not None:
            backend_registry.update(execution_backends)

        def validate_input(_: WorkflowInput) -> None:
            if not command_name:
                raise ValueError("Missing command name for execution.")
            if not authorization_decision.allowed:
                raise AuthorizationDeniedError(
                    (
                        "Missing required capabilities for command "
                        f"'{command_name}'."
                    ),
                    details=authorization_payload,
                )
            if (
                confirmation_required
                and confirmation_mode is ConfirmationMode.APPROVE_PLAN
            ):
                assert sensitive_action is not None
                if _resolve_non_interactive(resolved_context):
                    _validate_non_interactive_approved_plan(
                        approved_plan=approved_plan,
                        expected_action=sensitive_action,
                        resolved_context=resolved_context,
                        confirmation_payload=confirmation_payload,
                    )
                if (
                    approved_plan is not None
                ):
                    approved_plan_actions = approved_plan.get("actions")
                    if isinstance(approved_plan_actions, list) and not _action_in_plan(
                        action=sensitive_action,
                        approved_plan_actions=approved_plan_actions,
                    ):
                        confirmation_payload["violation"] = "sensitive_action_not_in_approved_plan"
                        raise ConfirmationDeniedError(
                            "Sensitive action not present in approved plan.",
                            details=confirmation_payload,
                            failure_type="confirmation_out_of_plan",
                        )

            if (
                confirmation_required
                and confirmation_decision.outcome is not ConfirmationOutcome.APPROVED
            ):
                failure_label = (
                    "plan"
                    if confirmation_mode is ConfirmationMode.APPROVE_PLAN
                    else "Per-action"
                )
                raise ConfirmationDeniedError(
                    (
                        f"{failure_label} confirmation "
                        f"{confirmation_decision.outcome.value} for sensitive command "
                        f"'{command_name}'."
                    ),
                    details=confirmation_payload,
                    failure_type=f"confirmation_{confirmation_decision.outcome.value}",
                )

            selected_backend = backend_selection.selected_backend
            if selected_backend not in backend_registry:
                raise BackendUnavailableError(
                    (
                        "Selected execution backend is not available for command "
                        f"'{command_name}'."
                    ),
                    details={
                        "selected_backend": selected_backend.value,
                        "available_backends": sorted(
                            backend.value for backend in backend_registry
                        ),
                        "backend_selection": dict(backend_selection_payload),
                    },
                )

        def execute_command(_: WorkflowInput) -> object:
            execution_backend = backend_registry[backend_selection.selected_backend]
            return execution_backend.execute(
                command_name,
                command_args,
                context=resolved_context,
            )

        runner: WorkflowLifecycleRunner[object] = WorkflowLifecycleRunner(
            validate=validate_input,
            execute=execute_command,
        )
        workflow_output = runner.run(workflow_input)
        workflow_output = _normalize_provider_fallback_failure(
            workflow_output=workflow_output,
            resolved_context=resolved_context,
        )
        session_id = _session_id_from_context(resolved_context)
        command_id = f"cmd-{workflow_output.metadata.execution_id}"
        workflow_id = f"wf-{workflow_output.metadata.execution_id}"
        confirmation_for_telemetry = (
            dict(confirmation_payload)
            if confirmation_required
            else None
        )
        if (
            confirmation_for_telemetry is not None
            and confirmation_mode is ConfirmationMode.APPROVE_PLAN
            and sensitive_action is not None
            and workflow_output.status is WorkflowStatus.SUCCESS
        ):
            confirmation_for_telemetry["executed_sensitive_actions"] = [
                dict(sensitive_action)
            ]
        telemetry_payload = _build_command_telemetry_payload(
            resolved_context=resolved_context,
            workflow_output=workflow_output,
            command_name=command_name,
            command_args=command_args,
            session_id=session_id,
            command_id=command_id,
            workflow_id=workflow_id,
            backend_selection=backend_selection_payload,
            authorization=authorization_payload,
            confirmation=confirmation_for_telemetry,
        )
        persistence_store = _resolve_execution_history_store(resolved_context)

        if persistence_store is not None:
            persistence_runtime_error: RuntimeErrorEnvelope | None = None
            if workflow_output.failure is not None:
                failure_status_code = (
                    _workflow_failure_status_code(workflow_output.failure.failure_type)
                )
                failure_details: dict[str, object] = {
                    "execution_id": workflow_output.metadata.execution_id,
                    "workflow_stage": workflow_output.failure.component.value,
                    "failure_type": workflow_output.failure.failure_type,
                }
                failure_details.update(workflow_output.failure.details)
                persistence_runtime_error = RuntimeErrorEnvelope(
                    code=workflow_output.failure.failure_type,
                    component=RuntimeErrorComponent.WORKFLOW,
                    message=workflow_output.failure.message,
                    status_code=failure_status_code,
                    details=failure_details,
                )

            try:
                retention_summary = persistence_store.record_command_dispatch(
                    session_id=session_id,
                    command_id=command_id,
                    workflow_id=workflow_id,
                    execution_id=workflow_output.metadata.execution_id,
                    command_name=command_name,
                    command_arg_count=len(command_args),
                    route=RouteKind.COMMAND.value,
                    workflow_status=workflow_output.status,
                    events=workflow_output.metadata.events,
                    context=resolved_context,
                    telemetry_payload=telemetry_payload,
                    runtime_error=persistence_runtime_error,
                )
                telemetry_payload["retention"] = retention_summary
            except PersistenceContractError as exc:
                persistence_runtime_error_details: dict[str, object] = {
                    "error": {
                        "type": "runtime_error",
                        "code": exc.code,
                        "component": RuntimeErrorComponent.WORKFLOW.value,
                    },
                    "execution_id": workflow_output.metadata.execution_id,
                }
                persistence_runtime_error_details.update(exc.details)

                return DispatchResult(
                    route=RouteKind.EXECUTION_ERROR,
                    output=None,
                    validation_error=None,
                    execution_error=WorkflowExecutionError(
                        component=WorkflowStage.FINALIZE,
                        failure_type="persistence_write_failed",
                        message=exc.message,
                        execution_id=workflow_output.metadata.execution_id,
                    ),
                    workflow_output=workflow_output,
                    conversation_output=None,
                    runtime_error=RuntimeErrorEnvelope(
                        code=exc.code,
                        component=RuntimeErrorComponent.WORKFLOW,
                        message=exc.message,
                        status_code=ToolStatusCode.EXECUTION_ERROR.value,
                        details=persistence_runtime_error_details,
                    ),
                    resolved_context=resolved_context,
                    telemetry_payload=telemetry_payload,
                )

        if workflow_output.status is WorkflowStatus.FAILURE:
            assert workflow_output.failure is not None
            failure = workflow_output.failure

            if (
                failure.component is WorkflowStage.VALIDATE
                and failure.failure_type == "validation_error"
            ):
                return DispatchResult(
                    route=RouteKind.VALIDATION_ERROR,
                    output=None,
                    validation_error=_execution_validation_error(
                        failure.message,
                        workflow_output.metadata.execution_id,
                    ),
                    execution_error=None,
                    workflow_output=workflow_output,
                    conversation_output=None,
                    runtime_error=RuntimeErrorEnvelope(
                        code="invalid_command_execution",
                        component=RuntimeErrorComponent.WORKFLOW,
                        message=failure.message,
                        details={
                            "execution_id": workflow_output.metadata.execution_id,
                            "workflow_stage": failure.component.value,
                            "failure_type": failure.failure_type,
                        },
                    ),
                    resolved_context=resolved_context,
                    telemetry_payload=telemetry_payload,
                )

            execution_error = WorkflowExecutionError(
                component=failure.component,
                failure_type=failure.failure_type,
                message=failure.message,
                execution_id=workflow_output.metadata.execution_id,
            )
            runtime_error_details: dict[str, object] = {
                "execution_id": workflow_output.metadata.execution_id,
                "workflow_stage": failure.component.value,
                "failure_type": failure.failure_type,
            }
            runtime_error_details.update(failure.details)
            return DispatchResult(
                route=RouteKind.EXECUTION_ERROR,
                output=None,
                validation_error=None,
                execution_error=execution_error,
                workflow_output=workflow_output,
                conversation_output=None,
                runtime_error=RuntimeErrorEnvelope(
                    code=failure.failure_type,
                    component=RuntimeErrorComponent.WORKFLOW,
                    message=failure.message,
                    status_code=(
                        _workflow_failure_status_code(failure.failure_type)
                    ),
                    details=runtime_error_details,
                ),
                resolved_context=resolved_context,
                telemetry_payload=telemetry_payload,
            )

        command_output = workflow_output.payload
        if isinstance(command_output, ToolResult):
            if command_output.status is ToolStatus.ERROR:
                error_message = (
                    command_output.error.message
                    if command_output.error is not None
                    else "Tool execution failed."
                )
                execution_error = WorkflowExecutionError(
                    component=WorkflowStage.EXECUTE,
                    failure_type="tool_error",
                    message=error_message,
                    execution_id=workflow_output.metadata.execution_id,
                )
                runtime_details = (
                    dict(command_output.error.details)
                    if command_output.error is not None
                    else {}
                )
                if command_output.tool_name is not None:
                    runtime_details.setdefault("tool_name", command_output.tool_name)

                return DispatchResult(
                    route=RouteKind.EXECUTION_ERROR,
                    output=None,
                    validation_error=None,
                    execution_error=execution_error,
                    workflow_output=workflow_output,
                    conversation_output=None,
                    runtime_error=RuntimeErrorEnvelope(
                        code=(
                            command_output.error.code
                            if command_output.error is not None
                            else "tool_execution_error"
                        ),
                        component=RuntimeErrorComponent.TOOL,
                        message=error_message,
                        status_code=command_output.status_code.value,
                        details=runtime_details,
                    ),
                    resolved_context=resolved_context,
                    telemetry_payload=telemetry_payload,
                )
            command_output = command_output.payload

        return DispatchResult(
            route=RouteKind.COMMAND,
            output=command_output,
            validation_error=None,
            execution_error=None,
            workflow_output=workflow_output,
            conversation_output=None,
            runtime_error=None,
            resolved_context=resolved_context,
            telemetry_payload=telemetry_payload,
        )

    runtime_config = conversation_config or ConversationRuntimeConfig()
    bounded_runtime = conversation_runtime or (
        lambda text: _run_default_conversation_runtime(
            user_input=text,
            conversation_handler=conversation_handler,
            max_iterations=runtime_config.max_iterations,
        )
    )
    conversation_output = bounded_runtime(user_input)
    runtime_error = conversation_output.metadata.runtime_error
    session_id = _session_id_from_context(resolved_context)
    conversation_correlation_extension, observability_validation_error = (
        _build_conversation_correlation_extension(
            session_id=session_id,
            conversation_output=conversation_output,
            runtime_error=runtime_error,
        )
    )
    effective_runtime_error = observability_validation_error or runtime_error
    context_without_raw_text = _build_context_without_raw_text_fields(resolved_context)

    interaction_state = {
        "route": RouteKind.CONVERSATION.value,
        "termination_reason": conversation_output.metadata.termination_reason.value,
        "resolved_context": context_without_raw_text,
        "input_length": len(user_input),
        "response_length": len(conversation_output.payload.response_text),
    }
    session_snapshot = build_safe_session_snapshot(interaction_state)
    telemetry_data: dict[str, object] = {
        "event": "conversation_dispatch",
        "envelope": {
            "timestamp": _utc_now_iso(),
            "component": RouteKind.CONVERSATION.value,
            "action": "conversation_dispatch",
            "status": conversation_output.status.value,
            "duration_ms": 0,
        },
        "correlation": {
            "route": RouteKind.CONVERSATION.value,
            "session_id": session_id,
            "termination_reason": conversation_output.metadata.termination_reason.value,
            "command_id": conversation_correlation_extension["command_id"],
            "workflow_id": conversation_correlation_extension["workflow_id"],
            "execution_id": conversation_correlation_extension["execution_id"],
        },
        "context": context_without_raw_text,
        "provider_routing": provider_routing_metadata(resolved_context),
        "interaction": {
            "input_length": len(user_input),
            "response_length": len(conversation_output.payload.response_text),
        },
        "conversation_correlation": conversation_correlation_extension,
    }
    if effective_runtime_error is not None:
        telemetry_data["runtime_error"] = {
            "type": "runtime_error",
            "code": effective_runtime_error.code,
            "component": effective_runtime_error.component.value,
            "status_code": effective_runtime_error.status_code,
        }
        conversation_authorization_payload = _extract_authorization_decision(
            effective_runtime_error
        )
        if conversation_authorization_payload is not None:
            telemetry_data["authorization_decision"] = conversation_authorization_payload
        conversation_confirmation_payload = _extract_confirmation_decision(
            effective_runtime_error
        )
        if conversation_confirmation_payload is not None:
            telemetry_data["confirmation_decision"] = conversation_confirmation_payload
        conversation_backend_selection_payload = _extract_backend_selection(
            effective_runtime_error
        )
        if conversation_backend_selection_payload is not None:
            telemetry_data["backend_selection"] = conversation_backend_selection_payload
        provider_contract_payload = _extract_provider_contract(
            effective_runtime_error
        )
        if provider_contract_payload is not None:
            telemetry_data["provider_contract"] = provider_contract_payload
        provider_fallback_payload = _extract_provider_fallback(
            effective_runtime_error
        )
        if provider_fallback_payload is not None:
            telemetry_data["provider_fallback"] = provider_fallback_payload
    telemetry_payload = build_safe_telemetry_payload(telemetry_data)

    return DispatchResult(
        route=RouteKind.CONVERSATION,
        output=conversation_output.payload.response_text,
        validation_error=None,
        execution_error=None,
        workflow_output=None,
        conversation_output=conversation_output,
        runtime_error=effective_runtime_error,
        resolved_context=resolved_context,
        session_snapshot=session_snapshot,
        telemetry_payload=telemetry_payload,
    )
