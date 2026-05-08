"""Bounded conversational runtime with deterministic termination behavior."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum

from endi.tools import ToolResult, ToolStatus, ToolStatusCode


class ConversationActionType(StrEnum):
    """Actions selected by the conversational policy each turn."""

    COMPLETE = "complete"
    TOOL_CALL = "tool_call"


class ConversationTerminationReason(StrEnum):
    """Explicit terminal outcomes for bounded conversational loops."""

    COMPLETED = "completed"
    MAX_ITERATIONS = "max-iterations"
    TOOL_FAILURE = "tool-failure"
    POLICY_DENIED = "policy-denied"
    TIMEOUT = "timeout"


class ConversationResultStatus(StrEnum):
    """Structured status for conversational runtime output envelope."""

    SUCCESS = "success"
    FAILURE = "failure"


class RuntimeErrorComponent(StrEnum):
    """Runtime component source for structured errors across execution paths."""

    COMMAND = "command"
    WORKFLOW = "workflow"
    AGENT = "agent"
    TOOL = "tool"


@dataclass(frozen=True)
class RuntimeErrorEnvelope:
    """Shared structured runtime error envelope for command and conversation paths."""

    code: str
    component: RuntimeErrorComponent
    message: str
    status_code: str | None = None
    details: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ConversationAction:
    """Selected action for one conversational turn."""

    action_type: ConversationActionType
    response_text: str | None = None
    tool_name: str | None = None
    tool_args: dict[str, object] | None = None


@dataclass(frozen=True)
class ToolOutputReference:
    """Stable reference to a tool output consumed in final synthesis."""

    reference_id: str
    tool_name: str
    summary: str


@dataclass(frozen=True)
class ToolObservation:
    """Observation data recorded for successful tool execution."""

    reference_id: str
    tool_name: str
    summary: str


@dataclass(frozen=True)
class ConversationTurnRecord:
    """Structured execution record for a conversational turn."""

    iteration: int
    action: ConversationAction
    observation: ToolObservation | None


@dataclass(frozen=True)
class ConversationPayload:
    """Structured payload produced by conversational runtime."""

    response_text: str
    tool_references: list[ToolOutputReference]


@dataclass(frozen=True)
class ConversationMetadata:
    """Conversation loop metadata for deterministic observability."""

    termination_reason: ConversationTerminationReason
    iterations: int
    max_iterations: int
    turns: list[ConversationTurnRecord]
    runtime_error: RuntimeErrorEnvelope | None = None


@dataclass(frozen=True)
class ConversationResult:
    """Structured conversational runtime envelope."""

    status: ConversationResultStatus
    payload: ConversationPayload
    metadata: ConversationMetadata


@dataclass(frozen=True)
class SynthesisResult:
    """Synthesized response plus optional consumed tool reference identifiers."""

    response_text: str
    consumed_reference_ids: list[str] | None = None


ActionSelector = Callable[[str, list[ConversationTurnRecord]], ConversationAction]
ToolExecutor = Callable[[str, dict[str, object]], object]
ResponseSynthesizer = Callable[
    [str, list[ConversationTurnRecord], list[ToolOutputReference]],
    str | SynthesisResult,
]
PolicyCheck = Callable[[str, dict[str, object]], bool]
TimeoutCheck = Callable[[int], bool]


def _default_policy_check(_: str, __: dict[str, object]) -> bool:
    return True


def _default_timeout_check(_: int) -> bool:
    return False


def _resolve_synthesis_result(
    synthesized: str | SynthesisResult,
) -> tuple[str, list[str] | None]:
    if isinstance(synthesized, SynthesisResult):
        return synthesized.response_text, synthesized.consumed_reference_ids
    return synthesized, None


def _filter_references(
    references: list[ToolOutputReference],
    consumed_reference_ids: list[str] | None,
) -> list[ToolOutputReference]:
    if consumed_reference_ids is None:
        return references

    consumed = set(consumed_reference_ids)
    return [reference for reference in references if reference.reference_id in consumed]


def run_bounded_conversation(
    user_input: str,
    max_iterations: int,
    select_action: ActionSelector,
    execute_tool: ToolExecutor,
    synthesize_response: ResponseSynthesizer,
    policy_check: PolicyCheck = _default_policy_check,
    timeout_check: TimeoutCheck = _default_timeout_check,
) -> ConversationResult:
    """Run deterministic bounded conversational iterations with explicit termination reasons."""
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1")

    turns: list[ConversationTurnRecord] = []
    references: list[ToolOutputReference] = []
    response_text: str | None = None
    consumed_reference_ids: list[str] | None = None
    termination_reason: ConversationTerminationReason | None = None
    runtime_error: RuntimeErrorEnvelope | None = None

    for iteration in range(1, max_iterations + 1):
        if timeout_check(iteration):
            termination_reason = ConversationTerminationReason.TIMEOUT
            break

        action = select_action(user_input, turns)

        if action.action_type is ConversationActionType.COMPLETE:
            turns.append(
                ConversationTurnRecord(
                    iteration=iteration,
                    action=action,
                    observation=None,
                )
            )
            if action.response_text is None:
                response_text, consumed_reference_ids = _resolve_synthesis_result(
                    synthesize_response(
                        user_input,
                        turns,
                        references,
                    )
                )
            else:
                response_text = action.response_text
            termination_reason = ConversationTerminationReason.COMPLETED
            break

        tool_name = action.tool_name
        tool_args = action.tool_args or {}
        if tool_name is None:
            turns.append(
                ConversationTurnRecord(
                    iteration=iteration,
                    action=action,
                    observation=None,
                )
            )
            termination_reason = ConversationTerminationReason.TOOL_FAILURE
            runtime_error = RuntimeErrorEnvelope(
                code="missing_tool_name",
                component=RuntimeErrorComponent.AGENT,
                message="Conversation action requested a tool call without a tool name.",
                status_code=ToolStatusCode.INVALID_CONTRACT.value,
            )
            break

        if not policy_check(tool_name, tool_args):
            turns.append(
                ConversationTurnRecord(
                    iteration=iteration,
                    action=action,
                    observation=None,
                )
            )
            termination_reason = ConversationTerminationReason.POLICY_DENIED
            break

        try:
            tool_output = execute_tool(tool_name, tool_args)
        except Exception:
            turns.append(
                ConversationTurnRecord(
                    iteration=iteration,
                    action=action,
                    observation=None,
                )
            )
            termination_reason = ConversationTerminationReason.TOOL_FAILURE
            runtime_error = RuntimeErrorEnvelope(
                code="tool_execution_error",
                component=RuntimeErrorComponent.TOOL,
                message="Tool execution failed.",
                status_code=ToolStatusCode.EXECUTION_ERROR.value,
                details={"tool_name": tool_name},
            )
            break

        if isinstance(tool_output, ToolResult):
            if tool_output.status is ToolStatus.ERROR:
                turns.append(
                    ConversationTurnRecord(
                        iteration=iteration,
                        action=action,
                        observation=None,
                    )
                )
                termination_reason = ConversationTerminationReason.TOOL_FAILURE
                error_details = (
                    dict(tool_output.error.details)
                    if tool_output.error is not None
                    else {}
                )
                if tool_output.tool_name is not None:
                    error_details.setdefault("tool_name", tool_output.tool_name)
                runtime_error = RuntimeErrorEnvelope(
                    code=(
                        tool_output.error.code
                        if tool_output.error is not None
                        else "tool_execution_error"
                    ),
                    component=RuntimeErrorComponent.TOOL,
                    message=(
                        tool_output.error.message
                        if tool_output.error is not None
                        else "Tool execution failed."
                    ),
                    status_code=tool_output.status_code.value,
                    details=error_details,
                )
                break
            tool_output = tool_output.payload

        reference_id = f"tool-{len(references) + 1:03d}"
        summary = str(tool_output)
        observation = ToolObservation(
            reference_id=reference_id,
            tool_name=tool_name,
            summary=summary,
        )
        turns.append(
            ConversationTurnRecord(
                iteration=iteration,
                action=action,
                observation=observation,
            )
        )
        references.append(
            ToolOutputReference(reference_id=reference_id, tool_name=tool_name, summary=summary)
        )

    if termination_reason is None:
        termination_reason = ConversationTerminationReason.MAX_ITERATIONS

    if response_text is None:
        response_text, consumed_reference_ids = _resolve_synthesis_result(
            synthesize_response(user_input, turns, references)
        )

    payload_references = _filter_references(references, consumed_reference_ids)

    status = (
        ConversationResultStatus.SUCCESS
        if termination_reason is ConversationTerminationReason.COMPLETED
        else ConversationResultStatus.FAILURE
    )

    return ConversationResult(
        status=status,
        payload=ConversationPayload(
            response_text=response_text,
            tool_references=payload_references,
        ),
        metadata=ConversationMetadata(
            termination_reason=termination_reason,
            iterations=len(turns),
            max_iterations=max_iterations,
            turns=turns,
            runtime_error=runtime_error,
        ),
    )
