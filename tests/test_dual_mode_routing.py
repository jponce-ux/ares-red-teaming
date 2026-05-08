"""Tests for dual-mode input classification and dispatch routing."""

from collections.abc import Callable, Mapping
from typing import assert_type

from typer.testing import CliRunner

import endi.cli as cli_module
import endi.routing as routing_module
from endi.backends import (
    BackendKind,
    ContainerBackend,
    ExecutionBackend,
    LocalBackend,
    RemoteBackend,
    WorkerBackend,
    backend_selection_metadata,
    resolve_backend_selection,
)
from endi.cli import app
from endi.context import (
    CONTEXT_PRECEDENCE_ORDER,
    REDACTED_VALUE,
    ContextLayer,
    resolve_context_layers,
)
from endi.conversation import (
    ConversationAction,
    ConversationActionType,
    ConversationMetadata,
    ConversationPayload,
    ConversationResult,
    ConversationResultStatus,
    ConversationTerminationReason,
    ConversationTurnRecord,
    RuntimeErrorComponent,
    RuntimeErrorEnvelope,
    ToolObservation,
    run_bounded_conversation,
)
from endi.routing import (
    CommandValidationError,
    DispatchResult,
    RouteKind,
    classify_input,
    command_discoverability_catalog,
    dispatch_input,
    nearest_command_suggestion,
)
from endi.workflow import (
    WorkflowFailure,
    WorkflowMetadata,
    WorkflowOutput,
    WorkflowStage,
    WorkflowStatus,
)


class PassThroughWorkerBackend:
    def __init__(self, command_executor: Callable[[str, list[str]], object]) -> None:
        self._command_executor = command_executor

    @property
    def kind(self) -> BackendKind:
        return BackendKind.WORKER

    def execute(
        self,
        operation: str,
        args: list[str],
        *,
        context: Mapping[str, object] | None = None,
    ) -> object:
        del context
        return self._command_executor(operation, args)


def _assert_summary_id_matches_sanitized_payload(summary: Mapping[str, object]) -> None:
    summary_copy = dict(summary)
    summary_id = summary_copy.pop("summary_id", None)
    assert isinstance(summary_id, str)

    sanitized_summary = routing_module._remove_raw_text_fields(summary_copy)
    assert isinstance(sanitized_summary, dict)
    expected_summary_id = routing_module._summary_identifier(sanitized_summary)
    assert summary_id == expected_summary_id


def _assert_summary_id_changes_with_execution_id(summary: Mapping[str, object]) -> None:
    summary_copy = dict(summary)
    summary_id = summary_copy.pop("summary_id", None)
    assert isinstance(summary_id, str)

    execution_id = summary_copy.get("execution_id")
    assert isinstance(execution_id, str)
    summary_copy["execution_id"] = f"{execution_id}-mutated"

    sanitized_summary = routing_module._remove_raw_text_fields(summary_copy)
    assert isinstance(sanitized_summary, dict)
    mutated_summary_id = routing_module._summary_identifier(sanitized_summary)
    assert mutated_summary_id != summary_id


def test_classifier_detects_command_mode() -> None:
    classified = classify_input("/show-status now")

    assert classified.route is RouteKind.COMMAND
    assert classified.command_name == "show-status"
    assert classified.command_args == ["now"]
    assert classified.validation_error is None


def test_classifier_detects_command_mode_with_leading_whitespace() -> None:
    classified = classify_input("   /show-status now")

    assert classified.route is RouteKind.COMMAND
    assert classified.command_name == "show-status"
    assert classified.command_args == ["now"]
    assert classified.validation_error is None


def test_classifier_detects_conversation_mode() -> None:
    classified = classify_input("what is the status?")

    assert classified.route is RouteKind.CONVERSATION
    assert classified.command_name is None
    assert classified.command_args == []
    assert classified.validation_error is None


def test_classifier_treats_whitespace_only_input_as_conversation() -> None:
    classified = classify_input("   ")

    assert classified.route is RouteKind.CONVERSATION
    assert classified.command_name is None
    assert classified.command_args == []
    assert classified.validation_error is None


def test_classifier_rejects_unsupported_command_syntax() -> None:
    classified = classify_input("/InvalidName arg")

    assert classified.route is RouteKind.VALIDATION_ERROR
    assert classified.validation_error is not None
    assert "lowercase kebab-case" in classified.validation_error.hint


def test_dispatch_routes_command_to_executor() -> None:
    command_calls: list[tuple[str, list[str]]] = []
    conversation_calls: list[str] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "command-ok"

    def conversation_handler(text: str) -> str:
        conversation_calls.append(text)
        return "conversation-ok"

    result = dispatch_input("/show-status now", command_executor, conversation_handler)

    assert result.route is RouteKind.COMMAND
    assert result.output == "command-ok"
    assert result.validation_error is None
    assert result.execution_error is None
    assert result.conversation_output is None
    assert result.workflow_output is not None
    assert result.workflow_output.status is WorkflowStatus.SUCCESS
    assert result.workflow_output.payload == "command-ok"
    assert result.workflow_output.metadata.execution_id
    assert result.workflow_output.metadata.events
    assert result.workflow_output.metadata.skipped_stages == [WorkflowStage.PLAN]
    assert command_calls == [("show-status", ["now"])]
    assert conversation_calls == []


def test_dispatch_routes_text_to_conversation() -> None:
    command_calls: list[tuple[str, list[str]]] = []
    conversation_calls: list[str] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "command-ok"

    def conversation_handler(text: str) -> str:
        conversation_calls.append(text)
        return "conversation-ok"

    result = dispatch_input("Hello there", command_executor, conversation_handler)

    assert result.route is RouteKind.CONVERSATION
    assert result.output == "conversation-ok"
    assert result.validation_error is None
    assert result.execution_error is None
    assert result.conversation_output is not None
    assert (
        result.conversation_output.metadata.termination_reason
        is ConversationTerminationReason.COMPLETED
    )
    assert result.workflow_output is None
    assert command_calls == []
    assert conversation_calls == ["Hello there"]


def test_malformed_command_does_not_execute_any_path() -> None:
    command_calls: list[tuple[str, list[str]]] = []
    conversation_calls: list[str] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "command-ok"

    def conversation_handler(text: str) -> str:
        conversation_calls.append(text)
        return "conversation-ok"

    result = dispatch_input("/", command_executor, conversation_handler)

    assert result.route is RouteKind.VALIDATION_ERROR
    assert result.output is None
    assert result.validation_error is not None
    assert result.execution_error is None
    assert result.conversation_output is None
    assert result.workflow_output is None
    assert "Use lowercase kebab-case" in result.validation_error.hint
    assert command_calls == []
    assert conversation_calls == []


def test_malformed_command_returns_structured_validation_fields() -> None:
    command_calls: list[tuple[str, list[str]]] = []
    conversation_calls: list[str] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "command-ok"

    def conversation_handler(text: str) -> str:
        conversation_calls.append(text)
        return "conversation-ok"

    result = dispatch_input("/BadCmd", command_executor, conversation_handler)

    assert result.route is RouteKind.VALIDATION_ERROR
    assert result.output is None
    assert result.validation_error is not None
    assert result.execution_error is None
    assert result.workflow_output is None
    assert result.validation_error.code == "invalid_command_syntax"
    assert "'BadCmd'" in result.validation_error.message
    assert "lowercase kebab-case" in result.validation_error.hint
    assert "/help" in result.validation_error.hint
    assert result.validation_error.execution_id is None
    assert command_calls == []
    assert conversation_calls == []


def test_cli_submit_displays_actionable_validation_error() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["submit", "/BadCmd"])  # invalid command casing

    assert result.exit_code == 1
    assert "Validation Error" in result.stdout
    assert "'BadCmd'" in result.stdout
    assert "Hint:" in result.stdout
    assert "lowercase kebab-case" in result.stdout
    assert "/help" in result.stdout
    assert "Execution ID:" not in result.stdout


def test_cli_submit_validation_error_displays_nearest_command_suggestion() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["submit", "/show_statu"])

    assert result.exit_code == 1
    assert "Hint:" in result.stdout
    assert "Did you mean /show-status?" in result.stdout


def test_cli_submit_renders_help_panel_for_discoverability_contract() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["submit", "/help"])

    assert result.exit_code == 0
    assert "Help" in result.stdout
    assert "Command" in result.stdout
    assert "Description" in result.stdout
    assert "Arguments" in result.stdout
    assert "Examples" in result.stdout
    assert "show-status" in result.stdout


def test_cli_submit_renders_introspection_panel_with_execution_targets() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["submit", "/introspect"])

    assert result.exit_code == 0
    assert "Command Introspection" in result.stdout
    assert "Execution Target" in result.stdout
    assert "show-status" in result.stdout
    assert "local" in result.stdout
    assert "delete-project" in result.stdout
    assert "worker" in result.stdout


def test_cli_submit_does_not_render_help_panel_from_output_string_collision(monkeypatch) -> None:
    def fake_dispatch_input(
        _user_input: str,
        _command_executor: object,
        _conversation_handler: object,
    ) -> DispatchResult:
        return DispatchResult(
            route=RouteKind.COMMAND,
            output="help",
            validation_error=None,
            execution_error=None,
            workflow_output=None,
            conversation_output=None,
            resolved_context={"command_name": "show-status"},
        )

    monkeypatch.setattr(cli_module, "dispatch_input", fake_dispatch_input)

    runner = CliRunner()
    result = runner.invoke(app, ["submit", "/show-status"])

    assert result.exit_code == 0
    assert "Route: command" in result.stdout
    assert "Command Introspection" not in result.stdout
    assert "Available commands" not in result.stdout


def test_cli_submit_does_not_render_introspection_panel_from_output_string_collision(
    monkeypatch,
) -> None:
    def fake_dispatch_input(
        _user_input: str,
        _command_executor: object,
        _conversation_handler: object,
    ) -> DispatchResult:
        return DispatchResult(
            route=RouteKind.COMMAND,
            output="introspect",
            validation_error=None,
            execution_error=None,
            workflow_output=None,
            conversation_output=None,
            resolved_context={"command_name": "show-status"},
        )

    monkeypatch.setattr(cli_module, "dispatch_input", fake_dispatch_input)

    runner = CliRunner()
    result = runner.invoke(app, ["submit", "/show-status"])

    assert result.exit_code == 0
    assert "Route: command" in result.stdout
    assert "Command Introspection" not in result.stdout
    assert "Execution Target" not in result.stdout


def test_dispatch_returns_structured_execution_error_for_runtime_failures() -> None:
    def command_executor(_: str, __: list[str]) -> str:
        raise RuntimeError("executor failed")

    result = dispatch_input("/show-status", command_executor, lambda text: text)

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.output is None
    assert result.validation_error is None
    assert result.execution_error is not None
    assert result.conversation_output is None
    assert result.execution_error.component == WorkflowStage.EXECUTE
    assert result.execution_error.failure_type == "runtime_error"
    assert result.execution_error.message == "executor failed"
    assert result.execution_error.execution_id
    assert result.workflow_output is not None
    assert result.workflow_output.status is WorkflowStatus.FAILURE
    assert result.workflow_output.failure is not None


def test_command_discoverability_catalog_is_deterministic_and_complete() -> None:
    first = command_discoverability_catalog()
    second = command_discoverability_catalog()

    assert first == second
    assert tuple(command.name for command in first) == (
        "delete-branch",
        "delete-project",
        "help",
        "introspect",
        "show-status",
    )
    for command in first:
        assert command.description
        assert command.arg_schema
        assert command.examples
        assert command.execution_target


def test_nearest_command_suggestion_returns_expected_match() -> None:
    assert nearest_command_suggestion("show_statu") == "show-status"
    assert nearest_command_suggestion("introspec") == "introspect"
    assert nearest_command_suggestion("zzzz") is None


def test_dispatch_propagates_execution_id_for_workflow_validation_failures(monkeypatch) -> None:
    class FakeRunner:
        def __init__(self, **_: object) -> None:
            pass

        def run(self, __: object) -> WorkflowOutput[str]:
            return WorkflowOutput(
                status=WorkflowStatus.FAILURE,
                payload=None,
                metadata=WorkflowMetadata(
                    execution_id="exec-validate-1",
                    events=[],
                    skipped_stages=[WorkflowStage.PLAN],
                    finalize_failure=None,
                ),
                failure=WorkflowFailure(
                    component=WorkflowStage.VALIDATE,
                    failure_type="validation_error",
                    message="missing required arg",
                ),
            )

    monkeypatch.setattr(routing_module, "WorkflowLifecycleRunner", FakeRunner)

    result = dispatch_input("/show-status", lambda _name, _args: "ok", lambda text: text)

    assert result.route is RouteKind.VALIDATION_ERROR
    assert result.output is None
    assert result.execution_error is None
    assert result.validation_error is not None
    assert result.conversation_output is None
    assert result.validation_error.code == "invalid_command_execution"
    assert result.validation_error.execution_id == "exec-validate-1"


def test_cli_submit_displays_execution_id_for_validation_error(monkeypatch) -> None:
    def fake_dispatch_input(
        _user_input: str,
        _command_executor: object,
        _conversation_handler: object,
    ) -> DispatchResult:
        return DispatchResult(
            route=RouteKind.VALIDATION_ERROR,
            output=None,
            validation_error=CommandValidationError(
                code="invalid_command_execution",
                message="invalid payload",
                hint="fix input",
                execution_id="exec-123",
            ),
            execution_error=None,
            workflow_output=None,
            conversation_output=None,
        )

    monkeypatch.setattr(cli_module, "dispatch_input", fake_dispatch_input)

    runner = CliRunner()
    result = runner.invoke(app, ["submit", "/show-status"]) 

    assert result.exit_code == 1
    assert "Validation Error" in result.stdout
    assert "Execution ID: exec-123" in result.stdout


def test_cli_submit_displays_runtime_error_details_for_validation_errors(monkeypatch) -> None:
    def fake_dispatch_input(
        _user_input: str,
        _command_executor: object,
        _conversation_handler: object,
    ) -> DispatchResult:
        return DispatchResult(
            route=RouteKind.VALIDATION_ERROR,
            output=None,
            validation_error=CommandValidationError(
                code="invalid_command_syntax",
                message="invalid command",
                hint="use /help",
                execution_id=None,
            ),
            execution_error=None,
            workflow_output=None,
            conversation_output=None,
            runtime_error=RuntimeErrorEnvelope(
                code="invalid_command_syntax",
                component=RuntimeErrorComponent.COMMAND,
                message="Unsupported command syntax",
                status_code=None,
                details={},
            ),
        )

    monkeypatch.setattr(cli_module, "dispatch_input", fake_dispatch_input)

    runner = CliRunner()
    result = runner.invoke(app, ["submit", "/BadCmd"])

    assert result.exit_code == 1
    assert "Validation Error" in result.stdout
    assert "Runtime Context" in result.stdout
    assert "code=invalid_command_syntax" in result.stdout
    assert "component=command" in result.stdout
    assert "status_code=n/a" in result.stdout


def test_cli_submit_displays_runtime_error_details_for_execution_errors(monkeypatch) -> None:
    def fake_dispatch_input(
        _user_input: str,
        _command_executor: object,
        _conversation_handler: object,
    ) -> DispatchResult:
        return DispatchResult(
            route=RouteKind.EXECUTION_ERROR,
            output=None,
            validation_error=None,
            execution_error=routing_module.WorkflowExecutionError(
                component=WorkflowStage.EXECUTE,
                failure_type="tool_error",
                message="invalid payload",
                execution_id="exec-456",
            ),
            workflow_output=None,
            conversation_output=None,
            runtime_error=RuntimeErrorEnvelope(
                code="invalid_tool_input",
                component=RuntimeErrorComponent.TOOL,
                message="Tool input schema validation failed.",
                status_code="invalid_input",
                details={"tool_name": "echo"},
            ),
        )

    monkeypatch.setattr(cli_module, "dispatch_input", fake_dispatch_input)

    runner = CliRunner()
    result = runner.invoke(app, ["submit", "/echo"]) 

    assert result.exit_code == 1
    assert "Execution Error" in result.stdout
    assert "Runtime Context" in result.stdout
    assert "code=invalid_tool_input" in result.stdout
    assert "component=tool" in result.stdout
    assert "status_code=invalid_input" in result.stdout
    assert "tool_name=echo" in result.stdout


def test_cli_submit_renders_pre_confirmation_summary_and_filters_sensitive_fields(
    monkeypatch,
) -> None:
    def fake_dispatch_input(
        _user_input: str,
        _command_executor: object,
        _conversation_handler: object,
    ) -> DispatchResult:
        return DispatchResult(
            route=RouteKind.EXECUTION_ERROR,
            output=None,
            validation_error=None,
            execution_error=routing_module.WorkflowExecutionError(
                component=WorkflowStage.VALIDATE,
                failure_type="confirmation_declined",
                message="confirmation declined",
                execution_id="exec-confirm-1",
            ),
            workflow_output=None,
            conversation_output=None,
            runtime_error=RuntimeErrorEnvelope(
                code="confirmation_declined",
                component=RuntimeErrorComponent.COMMAND,
                message="Per-action confirmation declined.",
                status_code="permission_denied",
                details={
                    "summary": {
                        "intent": "delete-branch",
                        "targets": ["feature/foo"],
                        "capabilities": ["repo.write"],
                        "backend": "local",
                        "risk_level": "high",
                        "execution_id": "exec-confirm-1",
                        "raw_input": "rm -rf .",
                    }
                },
            ),
        )

    monkeypatch.setattr(cli_module, "dispatch_input", fake_dispatch_input)

    runner = CliRunner()
    result = runner.invoke(app, ["submit", "/delete-branch feature/foo"])

    assert result.exit_code == 1
    assert "Pre-Confirmation Summary" in result.stdout
    assert "Intent" in result.stdout
    assert "delete-branch" in result.stdout
    assert "Targets" in result.stdout
    assert "feature/foo" in result.stdout
    assert "Risk Level" in result.stdout
    assert "high" in result.stdout
    assert "Execution ID" in result.stdout
    assert "exec-confirm-1" in result.stdout
    assert "raw_input" not in result.stdout
    assert "rm -rf ." not in result.stdout


def test_cli_submit_uses_shared_result_panel_for_command_and_conversation(monkeypatch) -> None:
    dispatch_results = [
        DispatchResult(
            route=RouteKind.COMMAND,
            output="command-ok",
            validation_error=None,
            execution_error=None,
            workflow_output=None,
            conversation_output=None,
        ),
        DispatchResult(
            route=RouteKind.CONVERSATION,
            output="conversation-ok",
            validation_error=None,
            execution_error=None,
            workflow_output=None,
            conversation_output=None,
        ),
    ]

    def fake_dispatch_input(
        _user_input: str,
        _command_executor: object,
        _conversation_handler: object,
    ) -> DispatchResult:
        assert dispatch_results
        return dispatch_results.pop(0)

    monkeypatch.setattr(cli_module, "dispatch_input", fake_dispatch_input)

    runner = CliRunner()
    command_result = runner.invoke(app, ["submit", "/show-status"])
    conversation_result = runner.invoke(app, ["submit", "status?"])

    assert command_result.exit_code == 0
    assert conversation_result.exit_code == 0
    assert "Result" in command_result.stdout
    assert "Result" in conversation_result.stdout
    assert "Route: command" in command_result.stdout
    assert "Route: conversation" in conversation_result.stdout


def test_dispatch_conversation_runtime_success_with_tool_references() -> None:
    def runtime(user_input: str):
        return run_bounded_conversation(
            user_input=user_input,
            max_iterations=3,
            select_action=lambda _text, turns: ConversationAction(
                action_type=(
                    ConversationActionType.TOOL_CALL
                    if len(turns) == 0
                    else ConversationActionType.COMPLETE
                ),
                tool_name="echo",
                tool_args={"v": "ok"},
                response_text="done",
            ),
            execute_tool=lambda _tool_name, _tool_args: "tool-ok",
            synthesize_response=lambda _text, _turns, refs: f"refs={len(refs)}",
        )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=runtime,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.conversation_output is not None
    assert (
        result.conversation_output.metadata.termination_reason
        is ConversationTerminationReason.COMPLETED
    )
    assert [
        ref.reference_id for ref in result.conversation_output.payload.tool_references
    ] == ["tool-001"]


def test_dispatch_conversation_runtime_reports_max_iterations() -> None:
    def runtime(user_input: str):
        return run_bounded_conversation(
            user_input=user_input,
            max_iterations=2,
            select_action=lambda _text, _turns: ConversationAction(
                action_type=ConversationActionType.TOOL_CALL,
                tool_name="echo",
                tool_args={},
            ),
            execute_tool=lambda _tool_name, _tool_args: "ok",
            synthesize_response=lambda _text, _turns, _refs: "partial",
        )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=runtime,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.conversation_output is not None
    assert (
        result.conversation_output.metadata.termination_reason
        is ConversationTerminationReason.MAX_ITERATIONS
    )


def test_dispatch_conversation_runtime_reports_tool_failure() -> None:
    def runtime(user_input: str):
        return run_bounded_conversation(
            user_input=user_input,
            max_iterations=2,
            select_action=lambda _text, _turns: ConversationAction(
                action_type=ConversationActionType.TOOL_CALL,
                tool_name="boom",
                tool_args={},
            ),
            execute_tool=lambda _tool_name, _tool_args: (_ for _ in ()).throw(RuntimeError("boom")),
            synthesize_response=lambda _text, _turns, _refs: "failed",
        )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=runtime,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.conversation_output is not None
    assert (
        result.conversation_output.metadata.termination_reason
        is ConversationTerminationReason.TOOL_FAILURE
    )
    assert result.runtime_error is not None
    assert result.telemetry_payload is not None
    telemetry_runtime_error = result.telemetry_payload["runtime_error"]
    assert isinstance(telemetry_runtime_error, dict)
    assert telemetry_runtime_error["type"] == "runtime_error"
    assert telemetry_runtime_error["component"] == "tool"
    assert telemetry_runtime_error["code"] == "tool_execution_error"
    assert telemetry_runtime_error["status_code"] == "execution_error"
    assert "message" not in telemetry_runtime_error
    assert "details" not in telemetry_runtime_error


def test_dispatch_conversation_runtime_reports_policy_denied() -> None:
    def runtime(user_input: str):
        return run_bounded_conversation(
            user_input=user_input,
            max_iterations=2,
            select_action=lambda _text, _turns: ConversationAction(
                action_type=ConversationActionType.TOOL_CALL,
                tool_name="dangerous",
                tool_args={},
            ),
            execute_tool=lambda _tool_name, _tool_args: "ok",
            synthesize_response=lambda _text, _turns, _refs: "denied",
            policy_check=lambda _tool_name, _tool_args: False,
        )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=runtime,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.conversation_output is not None
    assert (
        result.conversation_output.metadata.termination_reason
        is ConversationTerminationReason.POLICY_DENIED
    )


def test_dispatch_conversation_runtime_reports_timeout() -> None:
    def runtime(user_input: str):
        return run_bounded_conversation(
            user_input=user_input,
            max_iterations=2,
            select_action=lambda _text, _turns: ConversationAction(
                action_type=ConversationActionType.TOOL_CALL,
                tool_name="echo",
                tool_args={},
            ),
            execute_tool=lambda _tool_name, _tool_args: "ok",
            synthesize_response=lambda _text, _turns, _refs: "timed out",
            timeout_check=lambda _iteration: True,
        )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=runtime,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.conversation_output is not None
    assert (
        result.conversation_output.metadata.termination_reason
        is ConversationTerminationReason.TIMEOUT
    )


def test_context_precedence_order_contract_matches_prd_sequence() -> None:
    assert CONTEXT_PRECEDENCE_ORDER == (
        ContextLayer.EXPLICIT_INPUT,
        ContextLayer.COMMAND_INPUTS,
        ContextLayer.SESSION,
        ContextLayer.PROJECT,
        ContextLayer.ENVIRONMENT,
        ContextLayer.DEFAULTS,
    )


def test_resolver_applies_explicit_to_default_precedence_deterministically() -> None:
    explicit = {"shared": "explicit", "explicit_only": "top", "nested": {"x": "explicit"}}
    command = {"shared": "command", "command_only": "cmd", "nested": {"x": "command"}}
    session = {"shared": "session", "session_only": "sess", "nested": {"x": "session"}}
    project = {"shared": "project", "project_only": "proj", "nested": {"x": "project"}}
    environment = {"shared": "env", "env_only": "env", "nested": {"x": "env"}}
    defaults = {"shared": "default", "default_only": "def", "nested": {"x": "default"}}

    first = resolve_context_layers(
        explicit_input=explicit,
        command_inputs=command,
        session=session,
        project=project,
        environment=environment,
        defaults=defaults,
    )
    second = resolve_context_layers(
        explicit_input=explicit,
        command_inputs=command,
        session=session,
        project=project,
        environment=environment,
        defaults=defaults,
    )

    assert first == second
    assert first["shared"] == "explicit"
    assert first["explicit_only"] == "top"
    assert first["command_only"] == "cmd"
    assert first["session_only"] == "sess"
    assert first["project_only"] == "proj"
    assert first["env_only"] == "env"
    assert first["default_only"] == "def"
    assert first["nested"] == {"x": "explicit"}


def test_resolver_returns_deep_copies_without_mutating_input_layers() -> None:
    defaults = {"nested": {"v": "default"}}
    resolved = resolve_context_layers(defaults=defaults)
    nested = resolved["nested"]
    assert isinstance(nested, dict)
    nested["v"] = "changed"

    assert defaults == {"nested": {"v": "default"}}


def test_dispatch_conversation_sanitizes_session_snapshot_and_telemetry_payload() -> None:
    secret_token = "TOPSECRET-INPUT-123"
    raw_request_text = "remove all repos now"
    raw_response_text = "deleted repo-a"
    result = dispatch_input(
        f"hello {secret_token}",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: f"echo:{text}",
        explicit_context={
            "api_key": "secret-explicit",
            "temperature": 0.2,
            "request_text": raw_request_text,
            "response_text": raw_response_text,
            "conversation_text": f"conversation::{secret_token}",
        },
        session_context={
            "auth_token": "session-token",
            "history": [{"password": "pw", "query": "keep"}],
            "raw_input": raw_request_text,
        },
        project_context={"project_name": "endi"},
        environment_context={"authorization": "Bearer abc"},
        default_context={"model": "mini", "private_key": "pk"},
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.session_snapshot is not None
    assert result.telemetry_payload is not None
    assert result.resolved_context is not None
    assert "input_text" not in result.session_snapshot
    assert "response_text" not in result.session_snapshot

    assert "api_key" not in result.session_snapshot["resolved_context"]
    assert "auth_token" not in result.session_snapshot["resolved_context"]
    assert "authorization" not in result.session_snapshot["resolved_context"]
    assert "private_key" not in result.session_snapshot["resolved_context"]
    history = result.session_snapshot["resolved_context"]["history"]
    assert isinstance(history, list)
    first_history_item = history[0]
    assert isinstance(first_history_item, dict)
    assert "password" not in first_history_item

    telemetry_context = result.telemetry_payload["context"]
    assert isinstance(telemetry_context, dict)
    assert telemetry_context["api_key"] == REDACTED_VALUE
    assert telemetry_context["auth_token"] == REDACTED_VALUE
    assert telemetry_context["authorization"] == REDACTED_VALUE
    assert telemetry_context["private_key"] == REDACTED_VALUE

    correlation = result.telemetry_payload["correlation"]
    assert isinstance(correlation, dict)
    assert correlation["route"] == RouteKind.CONVERSATION.value
    assert correlation["session_id"] == "session-default"
    assert (
        correlation["termination_reason"]
        == ConversationTerminationReason.COMPLETED.value
    )
    assert isinstance(correlation["command_id"], str)
    assert correlation["command_id"]
    assert isinstance(correlation["workflow_id"], str)
    assert correlation["workflow_id"]
    assert isinstance(correlation["execution_id"], str)
    assert correlation["execution_id"]
    assert "request_text" not in telemetry_context
    assert "response_text" not in telemetry_context
    assert "conversation_text" not in telemetry_context
    assert "raw_input" not in telemetry_context
    interaction = result.telemetry_payload["interaction"]
    assert isinstance(interaction, dict)
    assert "input_length" in interaction
    assert "response_length" in interaction
    assert "input" not in result.telemetry_payload
    assert "request_text" not in result.session_snapshot["resolved_context"]
    assert "response_text" not in result.session_snapshot["resolved_context"]
    assert "conversation_text" not in result.session_snapshot["resolved_context"]
    assert "raw_input" not in result.session_snapshot["resolved_context"]
    assert secret_token not in str(result.session_snapshot)
    assert secret_token not in str(result.telemetry_payload)
    assert raw_request_text not in str(result.session_snapshot)
    assert raw_request_text not in str(result.telemetry_payload)
    assert raw_response_text not in str(result.session_snapshot)
    assert raw_response_text not in str(result.telemetry_payload)


def test_dispatch_uses_command_inputs_over_lower_precedence_layers() -> None:
    result = dispatch_input(
        "/show-status",
        command_executor=lambda _name, _args: "ok",
        conversation_handler=lambda _text: "unused",
        command_context={"request_id": "req-1", "command_name": "from-command-context"},
        session_context={"command_name": "session-command", "command_args": ["sess"]},
        project_context={"command_name": "project-command", "command_args": ["proj"]},
        environment_context={"command_name": "env-command", "command_args": ["env"]},
        default_context={"command_name": "default-command", "command_args": ["def"]},
    )

    assert result.route is RouteKind.COMMAND
    assert result.resolved_context is not None
    assert result.resolved_context["command_name"] == "show-status"
    assert result.resolved_context["command_args"] == []
    assert result.resolved_context["request_id"] == "req-1"


def test_dispatch_command_emits_sanitized_telemetry_payload() -> None:
    secret_arg = "TOPSECRET-ARG-123"
    result = dispatch_input(
        f"/show-status {secret_arg}",
        command_executor=lambda _name, _args: "ok",
        conversation_handler=lambda _text: "unused",
        explicit_context={"api_key": "secret-explicit"},
        command_context={"request_id": "req-77"},
        session_context={"auth_token": "session-secret"},
    )

    assert result.route is RouteKind.COMMAND
    assert result.telemetry_payload is not None
    assert result.workflow_output is not None
    execution_id = result.workflow_output.metadata.execution_id
    assert result.telemetry_payload["event"] == "command_dispatch"
    envelope = result.telemetry_payload["envelope"]
    assert isinstance(envelope, dict)
    assert envelope["component"] == RouteKind.COMMAND.value
    assert envelope["action"] == "command_dispatch"
    assert envelope["status"] == WorkflowStatus.SUCCESS.value
    assert isinstance(envelope["timestamp"], str)
    assert isinstance(envelope["duration_ms"], int)

    correlation = result.telemetry_payload["correlation"]
    assert isinstance(correlation, dict)
    assert correlation["route"] == RouteKind.COMMAND.value
    assert correlation["execution_id"] == execution_id
    assert correlation["session_id"] == "session-default"
    assert correlation["command_id"] == f"cmd-{execution_id}"
    assert correlation["workflow_id"] == f"wf-{execution_id}"

    execution_events = result.telemetry_payload["execution_events"]
    assert isinstance(execution_events, list)
    assert execution_events
    first_event = execution_events[0]
    assert isinstance(first_event, dict)
    assert first_event.keys() == {
        "timestamp",
        "component",
        "action",
        "status",
        "duration_ms",
        "correlation",
    }
    first_event_correlation = first_event["correlation"]
    assert isinstance(first_event_correlation, dict)
    assert first_event_correlation["session_id"] == "session-default"
    assert first_event_correlation["command_id"] == f"cmd-{execution_id}"
    assert first_event_correlation["workflow_id"] == f"wf-{execution_id}"
    assert first_event_correlation["execution_id"] == execution_id
    assert first_event_correlation["step_id"] == f"wf-{execution_id}:step:001"

    assert result.telemetry_payload["command"] == {"name": "show-status", "arg_count": 1}
    assert result.telemetry_payload["workflow"]["status"] == WorkflowStatus.SUCCESS.value

    telemetry_context = result.telemetry_payload["context"]
    assert isinstance(telemetry_context, dict)
    assert telemetry_context["api_key"] == REDACTED_VALUE
    assert telemetry_context["auth_token"] == REDACTED_VALUE
    assert telemetry_context["request_id"] == "req-77"
    assert "command_args" not in telemetry_context
    assert secret_arg not in str(result.telemetry_payload)


def test_dispatch_command_denied_capability_short_circuits_executor() -> None:
    command_calls: list[tuple[str, list[str]]] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "executed"

    result = dispatch_input(
        "/delete-project now",
        command_executor=command_executor,
        conversation_handler=lambda text: text,
        command_context={
            "command_capabilities": {
                "delete-project": ["system.delete"],
            }
        },
        session_context={"granted_capabilities": ["system.read"]},
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.execution_error is not None
    assert result.execution_error.failure_type == "authorization_denied"
    assert result.runtime_error is not None
    assert result.runtime_error.code == "authorization_denied"
    assert result.runtime_error.component is RuntimeErrorComponent.WORKFLOW
    assert result.runtime_error.status_code == "permission_denied"
    assert result.telemetry_payload is not None
    authorization = result.telemetry_payload["authorization_decision"]
    assert isinstance(authorization, dict)
    assert authorization["surface"] == "command"
    assert authorization["operation"] == "delete-project"
    assert authorization["allowed"] is False
    assert authorization["missing_capabilities"] == ["system.delete"]
    assert command_calls == []


def test_dispatch_command_provider_contract_failure_maps_invalid_contract_status(
    monkeypatch,
) -> None:
    class FakeRunner:
        def __init__(self, **_: object) -> None:
            pass

        def run(self, __: object) -> WorkflowOutput[str]:
            return WorkflowOutput(
                status=WorkflowStatus.FAILURE,
                payload=None,
                metadata=WorkflowMetadata(
                    execution_id="exec-provider-contract-1",
                    events=[],
                    skipped_stages=[WorkflowStage.PLAN],
                    finalize_failure=None,
                ),
                failure=WorkflowFailure(
                    component=WorkflowStage.VALIDATE,
                    failure_type="invalid_provider_contract",
                    message="Provider contract validation failed.",
                    details={
                        "capability": "chat",
                        "provider_name": "chat-primary",
                        "missing_fields": ["provider"],
                        "invalid_fields": ["metadata.vendor"],
                    },
                ),
            )

    monkeypatch.setattr(routing_module, "WorkflowLifecycleRunner", FakeRunner)

    result = dispatch_input(
        "/show-status",
        command_executor=lambda _name, _args: "ok",
        conversation_handler=lambda text: text,
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.execution_error is not None
    assert result.execution_error.failure_type == "invalid_provider_contract"
    assert result.runtime_error is not None
    assert result.runtime_error.code == "invalid_provider_contract"
    assert result.runtime_error.status_code == "invalid_contract"
    assert result.telemetry_payload is not None
    telemetry_runtime_error = result.telemetry_payload["runtime_error"]
    assert isinstance(telemetry_runtime_error, dict)
    assert telemetry_runtime_error["status_code"] == "invalid_contract"


def test_dispatch_conversation_emits_provider_contract_payload_with_sanitization() -> None:
    runtime_error = RuntimeErrorEnvelope(
        code="invalid_provider_contract",
        component=RuntimeErrorComponent.WORKFLOW,
        message="Provider contract validation failed.",
        status_code="invalid_contract",
        details={
            "capability": "chat",
            "provider_name": "chat-primary",
            "missing_fields": ["provider"],
            "invalid_fields": ["metadata.vendor"],
            "request_text": "secret-provider-payload",
        },
    )

    conversation_output = ConversationResult(
        status=ConversationResultStatus.FAILURE,
        payload=ConversationPayload(response_text="failed", tool_references=[]),
        metadata=ConversationMetadata(
            termination_reason=ConversationTerminationReason.TOOL_FAILURE,
            iterations=0,
            max_iterations=3,
            turns=[],
            runtime_error=runtime_error,
        ),
    )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=lambda _text: conversation_output,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.telemetry_payload is not None
    telemetry_runtime_error = result.telemetry_payload["runtime_error"]
    assert isinstance(telemetry_runtime_error, dict)
    assert telemetry_runtime_error == {
        "type": "runtime_error",
        "code": "invalid_provider_contract",
        "component": "workflow",
        "status_code": "invalid_contract",
    }
    provider_contract = result.telemetry_payload["provider_contract"]
    assert isinstance(provider_contract, dict)
    assert provider_contract == {
        "code": "invalid_provider_contract",
        "capability": "chat",
        "provider_name": "chat-primary",
        "missing_fields": ["provider"],
        "invalid_fields": ["metadata.vendor"],
    }
    assert "secret-provider-payload" not in str(result.telemetry_payload)


def test_dispatch_conversation_provider_contract_payload_falls_back_to_identifier() -> None:
    runtime_error = RuntimeErrorEnvelope(
        code="provider_not_found",
        component=RuntimeErrorComponent.WORKFLOW,
        message="Provider is not registered for requested capability.",
        status_code="not_found",
        details={
            "capability": "chat",
            "identifier": "chat-missing",
            "registered": ["chat-a", "chat-z"],
        },
    )

    conversation_output = ConversationResult(
        status=ConversationResultStatus.FAILURE,
        payload=ConversationPayload(response_text="failed", tool_references=[]),
        metadata=ConversationMetadata(
            termination_reason=ConversationTerminationReason.TOOL_FAILURE,
            iterations=0,
            max_iterations=3,
            turns=[],
            runtime_error=runtime_error,
        ),
    )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=lambda _text: conversation_output,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.telemetry_payload is not None
    provider_contract = result.telemetry_payload["provider_contract"]
    assert isinstance(provider_contract, dict)
    assert provider_contract == {
        "code": "provider_not_found",
        "capability": "chat",
        "provider_name": "chat-missing",
        "missing_fields": [],
        "invalid_fields": [],
        "registered": ["chat-a", "chat-z"],
    }


def test_dispatch_command_provider_fallback_blocked_maps_invalid_contract_status(
    monkeypatch,
) -> None:
    class FakeRunner:
        def __init__(self, **_: object) -> None:
            pass

        def run(self, __: object) -> WorkflowOutput[str]:
            return WorkflowOutput(
                status=WorkflowStatus.FAILURE,
                payload=None,
                metadata=WorkflowMetadata(
                    execution_id="exec-provider-fallback-1",
                    events=[],
                    skipped_stages=[WorkflowStage.PLAN],
                    finalize_failure=None,
                ),
                failure=WorkflowFailure(
                    component=WorkflowStage.VALIDATE,
                    failure_type="provider_fallback_blocked",
                    message="Local fallback is disabled unless explicitly enabled.",
                    details={
                        "capability": "chat",
                        "selected_provider": "openai:gpt-4o-mini",
                        "fallback_provider": "ollama",
                        "fallback_mode": "explicit_only",
                        "fallback_enabled": False,
                        "decision": "fallback_blocked",
                        "reason": "timeout",
                        "request_text": "secret provider payload",
                    },
                ),
            )

    monkeypatch.setattr(routing_module, "WorkflowLifecycleRunner", FakeRunner)

    result = dispatch_input(
        "/show-status",
        command_executor=lambda _name, _args: "ok",
        conversation_handler=lambda text: text,
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.execution_error is not None
    assert result.execution_error.failure_type == "provider_fallback_blocked"
    assert result.runtime_error is not None
    assert result.runtime_error.code == "provider_fallback_blocked"
    assert result.runtime_error.status_code == "invalid_contract"
    assert result.telemetry_payload is not None
    telemetry_runtime_error = result.telemetry_payload["runtime_error"]
    assert isinstance(telemetry_runtime_error, dict)
    assert telemetry_runtime_error["status_code"] == "invalid_contract"
    provider_fallback = result.telemetry_payload["provider_fallback"]
    assert isinstance(provider_fallback, dict)
    assert provider_fallback == {
        "decision": "fallback_blocked",
        "fallback_enabled": False,
        "fallback_mode": "explicit_only",
        "capability": "chat",
        "selected_provider": "openai:gpt-4o-mini",
        "fallback_provider": "ollama",
        "reason": "timeout",
    }
    provider_routing = result.telemetry_payload["provider_routing"]
    assert isinstance(provider_routing, dict)
    assert provider_routing == {
        "defaults": {
            "chat": "openai:gpt-4o-mini",
            "tool-calling": "anthropic:claude-3.7-sonnet",
            "embeddings": "openai:text-embedding-3-large",
        },
        "local_fallback": {
            "provider": "ollama",
            "mode": "explicit_only",
            "enabled": False,
        },
    }
    assert "secret provider payload" not in str(result.telemetry_payload)


def test_dispatch_command_provider_failure_is_normalized_to_fallback_blocked(
    monkeypatch,
) -> None:
    class FakeRunner:
        def __init__(self, **_: object) -> None:
            pass

        def run(self, __: object) -> WorkflowOutput[str]:
            return WorkflowOutput(
                status=WorkflowStatus.FAILURE,
                payload=None,
                metadata=WorkflowMetadata(
                    execution_id="exec-provider-fallback-normalized",
                    events=[],
                    skipped_stages=[WorkflowStage.PLAN],
                    finalize_failure=None,
                ),
                failure=WorkflowFailure(
                    component=WorkflowStage.EXECUTE,
                    failure_type="provider_failure",
                    message="Provider request failed.",
                    details={
                        "capability": "chat",
                        "selected_provider": "openai:gpt-4o-mini",
                        "reason": "timeout",
                        "request_text": "raw secret",
                    },
                ),
            )

    monkeypatch.setattr(routing_module, "WorkflowLifecycleRunner", FakeRunner)

    result = dispatch_input(
        "/show-status",
        command_executor=lambda _name, _args: "ok",
        conversation_handler=lambda text: text,
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.execution_error is not None
    assert result.execution_error.failure_type == "provider_fallback_blocked"
    assert result.runtime_error is not None
    assert result.runtime_error.code == "provider_fallback_blocked"
    assert result.runtime_error.status_code == "invalid_contract"
    assert result.telemetry_payload is not None
    provider_fallback = result.telemetry_payload["provider_fallback"]
    assert isinstance(provider_fallback, dict)
    assert provider_fallback == {
        "decision": "fallback_blocked",
        "fallback_enabled": False,
        "fallback_mode": "explicit_only",
        "capability": "chat",
        "selected_provider": "openai:gpt-4o-mini",
        "fallback_provider": "ollama",
        "reason": "timeout",
    }
    assert "raw secret" not in str(result.telemetry_payload)


def test_dispatch_command_provider_failure_not_blocked_when_local_fallback_enabled(
    monkeypatch,
) -> None:
    class FakeRunner:
        def __init__(self, **_: object) -> None:
            pass

        def run(self, __: object) -> WorkflowOutput[str]:
            return WorkflowOutput(
                status=WorkflowStatus.FAILURE,
                payload=None,
                metadata=WorkflowMetadata(
                    execution_id="exec-provider-fallback-enabled",
                    events=[],
                    skipped_stages=[WorkflowStage.PLAN],
                    finalize_failure=None,
                ),
                failure=WorkflowFailure(
                    component=WorkflowStage.EXECUTE,
                    failure_type="provider_failure",
                    message="Provider request failed.",
                    details={
                        "capability": "chat",
                        "selected_provider": "openai:gpt-4o-mini",
                        "reason": "provider_failure",
                    },
                ),
            )

    monkeypatch.setattr(routing_module, "WorkflowLifecycleRunner", FakeRunner)

    result = dispatch_input(
        "/show-status",
        command_executor=lambda _name, _args: "ok",
        conversation_handler=lambda text: text,
        command_context={"provider_local_fallback_enabled": True},
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.execution_error is not None
    assert result.execution_error.failure_type == "provider_failure"
    assert result.runtime_error is not None
    assert result.runtime_error.code == "provider_failure"
    assert result.runtime_error.status_code is None
    assert result.telemetry_payload is not None
    assert "provider_fallback" not in result.telemetry_payload


def test_dispatch_provider_fallback_parity_between_command_and_conversation(
    monkeypatch,
) -> None:
    class FakeRunner:
        def __init__(self, **_: object) -> None:
            pass

        def run(self, __: object) -> WorkflowOutput[str]:
            return WorkflowOutput(
                status=WorkflowStatus.FAILURE,
                payload=None,
                metadata=WorkflowMetadata(
                    execution_id="exec-provider-fallback-parity",
                    events=[],
                    skipped_stages=[WorkflowStage.PLAN],
                    finalize_failure=None,
                ),
                failure=WorkflowFailure(
                    component=WorkflowStage.VALIDATE,
                    failure_type="provider_fallback_blocked",
                    message="Local fallback is disabled unless explicitly enabled.",
                    details={
                        "capability": "chat",
                        "selected_provider": "openai:gpt-4o-mini",
                        "fallback_provider": "ollama",
                        "fallback_mode": "explicit_only",
                        "fallback_enabled": False,
                        "decision": "fallback_blocked",
                        "reason": "provider_failure",
                    },
                ),
            )

    monkeypatch.setattr(routing_module, "WorkflowLifecycleRunner", FakeRunner)

    command_result = dispatch_input(
        "/show-status",
        command_executor=lambda _name, _args: "ok",
        conversation_handler=lambda text: text,
    )

    conversation_runtime_error = RuntimeErrorEnvelope(
        code="provider_fallback_blocked",
        component=RuntimeErrorComponent.WORKFLOW,
        message="Local fallback is disabled unless explicitly enabled.",
        status_code="invalid_contract",
        details={
            "capability": "chat",
            "selected_provider": "openai:gpt-4o-mini",
            "fallback_provider": "ollama",
            "fallback_mode": "explicit_only",
            "fallback_enabled": False,
            "decision": "fallback_blocked",
            "reason": "provider_failure",
        },
    )
    conversation_output = ConversationResult(
        status=ConversationResultStatus.FAILURE,
        payload=ConversationPayload(response_text="failed", tool_references=[]),
        metadata=ConversationMetadata(
            termination_reason=ConversationTerminationReason.TOOL_FAILURE,
            iterations=0,
            max_iterations=3,
            turns=[],
            runtime_error=conversation_runtime_error,
        ),
    )
    conversation_result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=lambda _text: conversation_output,
    )

    assert command_result.runtime_error is not None
    assert conversation_result.runtime_error is not None
    assert command_result.runtime_error.code == "provider_fallback_blocked"
    assert command_result.runtime_error.status_code == "invalid_contract"
    assert conversation_result.runtime_error.code == "provider_fallback_blocked"
    assert conversation_result.runtime_error.status_code == "invalid_contract"
    assert command_result.telemetry_payload is not None
    assert conversation_result.telemetry_payload is not None
    assert (
        command_result.telemetry_payload["provider_fallback"]
        == conversation_result.telemetry_payload["provider_fallback"]
    )
    assert (
        command_result.telemetry_payload["provider_routing"]
        == conversation_result.telemetry_payload["provider_routing"]
    )


def test_dispatch_sensitive_command_requires_confirmation_by_default() -> None:
    command_calls: list[tuple[str, list[str]]] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "executed"

    result = dispatch_input(
        "/delete-project now",
        command_executor=command_executor,
        conversation_handler=lambda text: text,
        command_context={
            "command_capabilities": {
                "delete-project": ["system.modify"],
            }
        },
        session_context={"granted_capabilities": ["system.modify"]},
        execution_backends={
            BackendKind.WORKER: PassThroughWorkerBackend(command_executor)
        },
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.execution_error is not None
    assert result.execution_error.failure_type == "confirmation_timeout"
    assert result.runtime_error is not None
    assert result.runtime_error.code == "confirmation_timeout"
    assert result.runtime_error.component is RuntimeErrorComponent.WORKFLOW
    assert result.runtime_error.status_code == "permission_denied"
    assert result.telemetry_payload is not None
    confirmation = result.telemetry_payload["confirmation_decision"]
    assert isinstance(confirmation, dict)
    assert confirmation["mode"] == "per_action"
    assert confirmation["required"] is True
    assert confirmation["outcome"] == "timeout"
    summary = confirmation["summary"]
    assert isinstance(summary, dict)
    assert summary["targets"] == []
    assert summary["intent"] == "delete-project"
    assert summary["capabilities"] == ["system.modify"]
    assert summary["backend"] == "worker"
    assert summary["risk_level"] == "high"
    assert summary["execution_id"] == result.execution_error.execution_id
    _assert_summary_id_matches_sanitized_payload(summary)
    assert "now" not in str(result.telemetry_payload)
    assert command_calls == []


def test_dispatch_sensitive_command_with_approved_confirmation_executes() -> None:
    command_calls: list[tuple[str, list[str]]] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "executed"

    result = dispatch_input(
        "/delete-project now",
        command_executor=command_executor,
        conversation_handler=lambda text: text,
        command_context={
            "command_capabilities": {
                "delete-project": ["system.modify"],
            },
            "command_targets": {
                "delete-project": ["repo-01", "repo-02"],
            },
            "confirmation_decisions": {
                "delete-project": {
                    "outcome": "approved",
                    "actor_id": "operator-1",
                }
            },
        },
        session_context={"granted_capabilities": ["system.modify"]},
        execution_backends={
            BackendKind.WORKER: PassThroughWorkerBackend(command_executor)
        },
    )

    assert result.route is RouteKind.COMMAND
    assert result.output == "executed"
    assert result.workflow_output is not None
    assert result.telemetry_payload is not None
    confirmation = result.telemetry_payload["confirmation_decision"]
    assert isinstance(confirmation, dict)
    assert confirmation["outcome"] == "approved"
    assert confirmation["actor_id"] == "operator-1"
    assert confirmation["correlation"] == {
        "execution_id": result.workflow_output.metadata.execution_id,
    }
    summary = confirmation["summary"]
    assert isinstance(summary, dict)
    assert summary["targets"] == ["repo-01", "repo-02"]
    assert summary["backend"] == "worker"
    assert summary["risk_level"] == "high"
    assert summary["execution_id"] == result.workflow_output.metadata.execution_id
    _assert_summary_id_matches_sanitized_payload(summary)
    _assert_summary_id_changes_with_execution_id(summary)
    assert summary["execution_context"] == {
        "route": "command",
        "workflow_stage": "validate",
    }
    assert command_calls == [("delete-project", ["now"])]


def test_dispatch_sensitive_command_with_approved_confirmation_blocks_when_backend_unavailable(
) -> None:
    result = dispatch_input(
        "/delete-project now",
        command_executor=lambda _name, _args: "executed",
        conversation_handler=lambda text: text,
        command_context={
            "command_capabilities": {
                "delete-project": ["system.modify"],
            },
            "confirmation_decision": {
                "outcome": "approved",
            },
        },
        session_context={"granted_capabilities": ["system.modify"]},
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.execution_error is not None
    assert result.execution_error.failure_type == "backend_unavailable"
    assert result.runtime_error is not None
    assert result.runtime_error.code == "backend_unavailable"


def test_dispatch_sensitive_command_uses_global_confirmation_fallback() -> None:
    command_calls: list[tuple[str, list[str]]] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "executed"

    result = dispatch_input(
        "/delete-project now",
        command_executor=command_executor,
        conversation_handler=lambda text: text,
        command_context={
            "command_capabilities": {
                "delete-project": ["system.modify"],
            },
            "confirmation_decisions": {
                "another-command": "declined",
            },
            "confirmation_decision": {
                "outcome": "approved",
                "actor_id": "operator-global",
            },
        },
        session_context={"granted_capabilities": ["system.modify"]},
        execution_backends={
            BackendKind.WORKER: PassThroughWorkerBackend(command_executor)
        },
    )

    assert result.route is RouteKind.COMMAND
    assert result.output == "executed"
    assert result.workflow_output is not None
    assert result.telemetry_payload is not None
    confirmation = result.telemetry_payload["confirmation_decision"]
    assert isinstance(confirmation, dict)
    assert confirmation["outcome"] == "approved"
    assert confirmation["actor_id"] == "operator-global"
    assert command_calls == [("delete-project", ["now"])]


def test_dispatch_conversation_emits_confirmation_decision_from_runtime_error() -> None:
    runtime_error = RuntimeErrorEnvelope(
        code="confirmation_declined",
        component=RuntimeErrorComponent.WORKFLOW,
        message="Per-action confirmation declined.",
        status_code="permission_denied",
        details={
            "mode": "per_action",
            "required": True,
            "outcome": "declined",
            "actor_id": "operator-2",
            "summary": {
                "summary_id": "abc123",
                "intent": "danger.delete",
                "targets": ["repo-1"],
                "capabilities": ["system.modify"],
                "backend": "local",
                "risk_level": "high",
                "execution_context": {"route": "conversation", "workflow_stage": "validate"},
            },
            "execution_id": "exec-confirm-1",
        },
    )

    def runtime(_: str) -> ConversationResult:
        return ConversationResult(
            status=ConversationResultStatus.FAILURE,
            payload=ConversationPayload(response_text="denied", tool_references=[]),
            metadata=ConversationMetadata(
                termination_reason=ConversationTerminationReason.POLICY_DENIED,
                iterations=1,
                max_iterations=3,
                turns=[],
                runtime_error=runtime_error,
            ),
        )

    result = dispatch_input(
        "please delete repository",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=runtime,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.telemetry_payload is not None
    confirmation = result.telemetry_payload["confirmation_decision"]
    assert isinstance(confirmation, dict)
    assert confirmation["mode"] == "per_action"
    assert confirmation["required"] is True
    assert confirmation["outcome"] == "declined"
    assert confirmation["actor_id"] == "operator-2"
    assert confirmation["correlation"] == {"execution_id": "exec-confirm-1"}


def test_dispatch_sensitive_command_approve_plan_non_interactive_executes() -> None:
    command_calls: list[tuple[str, list[str]]] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "executed"

    action = {
        "operation": "delete-project",
        "capabilities": ["system.modify"],
        "targets": ["repo-01", "repo-02"],
        "backend": "worker",
    }
    fingerprint = routing_module._build_plan_fingerprint([action])

    result = dispatch_input(
        "/delete-project now",
        command_executor=command_executor,
        conversation_handler=lambda text: text,
        command_context={
            "command_capabilities": {
                "delete-project": ["system.modify"],
            },
            "command_targets": {
                "delete-project": ["repo-02", "repo-01"],
            },
            "confirmation_mode": "approve_plan",
            "non_interactive": True,
            "execution_context_id": "exec-ctx-1",
            "confirmation_decision": {
                "outcome": "approved",
                "actor_id": "ci-bot",
            },
            "approved_plan": {
                "approved": True,
                "context_id": "exec-ctx-1",
                "fingerprint": fingerprint,
                "actions": [action],
            },
        },
        session_context={"granted_capabilities": ["system.modify"]},
        execution_backends={
            BackendKind.WORKER: PassThroughWorkerBackend(command_executor)
        },
    )

    assert result.route is RouteKind.COMMAND
    assert result.output == "executed"
    assert result.telemetry_payload is not None
    confirmation = result.telemetry_payload["confirmation_decision"]
    assert isinstance(confirmation, dict)
    assert confirmation["mode"] == "approve_plan"
    assert confirmation["outcome"] == "approved"
    summary = confirmation["summary"]
    assert isinstance(summary, dict)
    assert summary["intent"] == "delete-project"
    assert summary["targets"] == ["repo-01", "repo-02"]
    assert summary["capabilities"] == ["system.modify"]
    assert summary["backend"] == "worker"
    assert summary["risk_level"] == "high"
    assert summary["execution_id"] == result.workflow_output.metadata.execution_id
    assert summary["plan_fingerprint"] == fingerprint
    assert summary["action_count"] == 1
    _assert_summary_id_matches_sanitized_payload(summary)
    assert confirmation["executed_sensitive_actions"] == [action]
    assert command_calls == [("delete-project", ["now"])]


def test_dispatch_sensitive_command_approve_plan_non_interactive_requires_plan() -> None:
    command_calls: list[tuple[str, list[str]]] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "executed"

    result = dispatch_input(
        "/delete-project now",
        command_executor=command_executor,
        conversation_handler=lambda text: text,
        command_context={
            "command_capabilities": {
                "delete-project": ["system.modify"],
            },
            "confirmation_mode": "approve_plan",
            "non_interactive": True,
            "execution_context_id": "exec-ctx-2",
            "confirmation_decision": {
                "outcome": "approved",
            },
        },
        session_context={"granted_capabilities": ["system.modify"]},
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.execution_error is not None
    assert result.execution_error.failure_type == "confirmation_plan_missing"
    assert result.runtime_error is not None
    assert result.runtime_error.status_code == "permission_denied"
    assert command_calls == []


def test_dispatch_sensitive_command_approve_plan_non_interactive_requires_approved_artifact(
) -> None:
    command_calls: list[tuple[str, list[str]]] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "executed"

    action = {
        "operation": "delete-project",
        "capabilities": ["system.modify"],
        "targets": [],
        "backend": "worker",
    }
    fingerprint = routing_module._build_plan_fingerprint([action])

    result = dispatch_input(
        "/delete-project now",
        command_executor=command_executor,
        conversation_handler=lambda text: text,
        command_context={
            "command_capabilities": {
                "delete-project": ["system.modify"],
            },
            "confirmation_mode": "approve_plan",
            "non_interactive": True,
            "execution_context_id": "exec-ctx-2b",
            "confirmation_decision": {
                "outcome": "approved",
            },
            "approved_plan": {
                "approved": False,
                "context_id": "exec-ctx-2b",
                "fingerprint": fingerprint,
                "actions": [action],
            },
        },
        session_context={"granted_capabilities": ["system.modify"]},
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.execution_error is not None
    assert result.execution_error.failure_type == "confirmation_plan_unapproved"
    assert result.runtime_error is not None
    assert result.runtime_error.status_code == "permission_denied"
    assert command_calls == []


def test_dispatch_sensitive_command_approve_plan_non_interactive_invalid_fingerprint() -> None:
    command_calls: list[tuple[str, list[str]]] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "executed"

    action = {
        "operation": "delete-project",
        "capabilities": ["system.modify"],
        "targets": [],
        "backend": "worker",
    }

    result = dispatch_input(
        "/delete-project now",
        command_executor=command_executor,
        conversation_handler=lambda text: text,
        command_context={
            "command_capabilities": {
                "delete-project": ["system.modify"],
            },
            "confirmation_mode": "approve_plan",
            "non_interactive": True,
            "execution_context_id": "exec-ctx-2c",
            "confirmation_decision": {
                "outcome": "approved",
            },
            "approved_plan": {
                "approved": True,
                "context_id": "exec-ctx-2c",
                "fingerprint": "deadbeefdeadbeef",
                "actions": [action],
            },
        },
        session_context={"granted_capabilities": ["system.modify"]},
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.execution_error is not None
    assert result.execution_error.failure_type == "confirmation_plan_invalid"
    assert result.runtime_error is not None
    assert result.runtime_error.status_code == "permission_denied"
    assert command_calls == []


def test_dispatch_sensitive_command_approve_plan_non_interactive_context_mismatch() -> None:
    command_calls: list[tuple[str, list[str]]] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "executed"

    action = {
        "operation": "delete-project",
        "capabilities": ["system.modify"],
        "targets": [],
        "backend": "worker",
    }
    fingerprint = routing_module._build_plan_fingerprint([action])

    result = dispatch_input(
        "/delete-project now",
        command_executor=command_executor,
        conversation_handler=lambda text: text,
        command_context={
            "command_capabilities": {
                "delete-project": ["system.modify"],
            },
            "confirmation_mode": "approve_plan",
            "non_interactive": True,
            "execution_context_id": "exec-ctx-b",
            "confirmation_decision": {
                "outcome": "approved",
            },
            "approved_plan": {
                "approved": True,
                "context_id": "exec-ctx-a",
                "fingerprint": fingerprint,
                "actions": [action],
            },
        },
        session_context={"granted_capabilities": ["system.modify"]},
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.execution_error is not None
    assert result.execution_error.failure_type == "confirmation_plan_context_mismatch"
    assert command_calls == []


def test_dispatch_sensitive_command_approve_plan_blocks_out_of_plan_action() -> None:
    command_calls: list[tuple[str, list[str]]] = []

    def command_executor(name: str, args: list[str]) -> str:
        command_calls.append((name, args))
        return "executed"

    plan_action = {
        "operation": "show-status",
        "capabilities": ["system.modify"],
        "targets": [],
        "backend": "worker",
    }
    fingerprint = routing_module._build_plan_fingerprint([plan_action])

    result = dispatch_input(
        "/delete-project now",
        command_executor=command_executor,
        conversation_handler=lambda text: text,
        command_context={
            "command_capabilities": {
                "delete-project": ["system.modify"],
            },
            "confirmation_mode": "approve_plan",
            "confirmation_decision": {
                "outcome": "approved",
            },
            "approved_plan": {
                "approved": True,
                "context_id": "exec-ctx-3",
                "fingerprint": fingerprint,
                "actions": [plan_action],
            },
        },
        session_context={
            "granted_capabilities": ["system.modify"],
            "execution_context_id": "exec-ctx-3",
        },
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.execution_error is not None
    assert result.execution_error.failure_type == "confirmation_out_of_plan"
    assert result.runtime_error is not None
    assert result.runtime_error.status_code == "permission_denied"
    assert command_calls == []


def test_dispatch_sensitive_command_approve_plan_fingerprint_is_deterministic() -> None:
    def run_with_actions(actions: list[dict[str, object]]) -> DispatchResult:
        fingerprint = routing_module._build_plan_fingerprint(
            sorted(
                actions,
                key=lambda action: (
                    str(action["operation"]),
                    str(action["backend"]),
                    str(action["capabilities"]),
                    str(action["targets"]),
                ),
            )
        )
        return dispatch_input(
            "/delete-project now",
            command_executor=lambda _name, _args: "executed",
            conversation_handler=lambda text: text,
            command_context={
                "command_capabilities": {
                    "delete-project": ["system.modify"],
                },
                "command_targets": {
                    "delete-project": ["repo-01"],
                },
                "confirmation_mode": "approve_plan",
                "confirmation_decision": {
                    "outcome": "approved",
                },
                "approved_plan": {
                    "approved": True,
                    "context_id": "exec-ctx-4",
                    "fingerprint": fingerprint,
                    "actions": actions,
                },
            },
            session_context={
                "granted_capabilities": ["system.modify"],
                "execution_context_id": "exec-ctx-4",
            },
            execution_backends={
                BackendKind.WORKER: PassThroughWorkerBackend(
                    lambda _name, _args: "executed"
                )
            },
        )

    action_a = {
        "operation": "delete-project",
        "capabilities": ["system.modify"],
        "targets": ["repo-01"],
        "backend": "worker",
    }
    action_b = {
        "operation": "rotate-keys",
        "capabilities": ["system.modify"],
        "targets": [],
        "backend": "worker",
    }

    first = run_with_actions([action_a, action_b])
    second = run_with_actions([action_b, action_a])

    assert first.route is RouteKind.COMMAND
    assert second.route is RouteKind.COMMAND
    assert first.telemetry_payload is not None
    assert second.telemetry_payload is not None
    first_summary = first.telemetry_payload["confirmation_decision"]["summary"]
    second_summary = second.telemetry_payload["confirmation_decision"]["summary"]
    assert isinstance(first_summary, dict)
    assert isinstance(second_summary, dict)
    assert first_summary["plan_fingerprint"] == second_summary["plan_fingerprint"]


def test_dispatch_conversation_emits_extended_correlation_chain() -> None:
    def runtime(user_input: str) -> ConversationResult:
        return run_bounded_conversation(
            user_input=user_input,
            max_iterations=3,
            select_action=lambda _text, turns: ConversationAction(
                action_type=(
                    ConversationActionType.TOOL_CALL
                    if len(turns) == 0
                    else ConversationActionType.COMPLETE
                ),
                tool_name="echo",
                tool_args={"query": "status", "request_text": "TOPSECRET"},
                response_text="done",
            ),
            execute_tool=lambda _tool_name, _tool_args: "tool-ok",
            synthesize_response=lambda _text, _turns, refs: f"refs={len(refs)}",
        )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=runtime,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.telemetry_payload is not None
    correlation = result.telemetry_payload["correlation"]
    assert isinstance(correlation, dict)

    extension = result.telemetry_payload["conversation_correlation"]
    assert isinstance(extension, dict)
    assert extension["execution_id"] == correlation["execution_id"]
    assert extension["command_id"] == correlation["command_id"]
    assert extension["workflow_id"] == correlation["workflow_id"]

    events = extension["events"]
    assert isinstance(events, list)
    assert [event["component"] for event in events] == [
        "step",
        "agent",
        "tool_call",
        "step",
        "agent",
    ]

    step_event = events[0]
    agent_event = events[1]
    tool_event = events[2]
    assert step_event["parent"] == {"workflow_id": extension["workflow_id"]}
    assert agent_event["parent"]["workflow_id"] == extension["workflow_id"]
    assert agent_event["parent"]["step_id"] == step_event["correlation"]["step_id"]
    assert tool_event["parent"]["workflow_id"] == extension["workflow_id"]
    assert tool_event["parent"]["step_id"] == step_event["correlation"]["step_id"]
    assert tool_event["parent"]["agent_id"] == agent_event["correlation"]["agent_id"]
    tool_payload = tool_event["tool_call"]
    assert isinstance(tool_payload, dict)
    assert tool_payload["arg_keys"] == ["query"]


def test_dispatch_conversation_parent_linkage_failure_is_structured_and_deterministic() -> None:
    invalid_result = ConversationResult(
        status=ConversationResultStatus.FAILURE,
        payload=ConversationPayload(response_text="invalid", tool_references=[]),
        metadata=ConversationMetadata(
            termination_reason=ConversationTerminationReason.TOOL_FAILURE,
            iterations=1,
            max_iterations=3,
            turns=[
                ConversationTurnRecord(
                    iteration=0,
                    action=ConversationAction(
                        action_type=ConversationActionType.COMPLETE,
                        response_text="done",
                    ),
                    observation=None,
                )
            ],
            runtime_error=None,
        ),
    )

    result_first = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=lambda _text: invalid_result,
    )
    result_second = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=lambda _text: invalid_result,
    )

    for result in (result_first, result_second):
        assert result.route is RouteKind.CONVERSATION
        assert result.runtime_error is not None
        assert result.runtime_error.code == "observability_parent_linkage_invalid"
        assert result.runtime_error.component is RuntimeErrorComponent.WORKFLOW
        assert result.runtime_error.status_code == "invalid_contract"
        assert result.runtime_error.details["error"] == {
            "type": "runtime_error",
            "code": "observability_parent_linkage_invalid",
            "component": "workflow",
        }
        assert result.runtime_error.details["event_component"] == "step"
        assert result.runtime_error.details["reason"] == "invalid_step_iteration"
        assert result.telemetry_payload is not None
        telemetry_runtime_error = result.telemetry_payload["runtime_error"]
        assert isinstance(telemetry_runtime_error, dict)
        assert telemetry_runtime_error == {
            "type": "runtime_error",
            "code": "observability_parent_linkage_invalid",
            "component": "workflow",
            "status_code": "invalid_contract",
        }

    assert result_first.runtime_error.details == result_second.runtime_error.details
    assert result_first.telemetry_payload is not None
    assert result_second.telemetry_payload is not None
    assert (
        result_first.telemetry_payload["conversation_correlation"]["execution_id"]
        == result_second.telemetry_payload["conversation_correlation"]["execution_id"]
    )


def test_dispatch_conversation_duplicate_step_identifier_is_structured_failure() -> None:
    invalid_result = ConversationResult(
        status=ConversationResultStatus.FAILURE,
        payload=ConversationPayload(response_text="invalid", tool_references=[]),
        metadata=ConversationMetadata(
            termination_reason=ConversationTerminationReason.MAX_ITERATIONS,
            iterations=2,
            max_iterations=3,
            turns=[
                ConversationTurnRecord(
                    iteration=1,
                    action=ConversationAction(
                        action_type=ConversationActionType.COMPLETE,
                        response_text="one",
                    ),
                    observation=None,
                ),
                ConversationTurnRecord(
                    iteration=1,
                    action=ConversationAction(
                        action_type=ConversationActionType.COMPLETE,
                        response_text="two",
                    ),
                    observation=None,
                ),
            ],
            runtime_error=None,
        ),
    )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=lambda _text: invalid_result,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.runtime_error is not None
    assert result.runtime_error.code == "observability_parent_linkage_invalid"
    assert result.runtime_error.component is RuntimeErrorComponent.WORKFLOW
    assert result.runtime_error.status_code == "invalid_contract"
    assert result.runtime_error.details["event_component"] == "step"
    assert result.runtime_error.details["reason"] == "duplicate_step_identifier"
    assert result.telemetry_payload is not None
    telemetry_runtime_error = result.telemetry_payload["runtime_error"]
    assert isinstance(telemetry_runtime_error, dict)
    assert telemetry_runtime_error == {
        "type": "runtime_error",
        "code": "observability_parent_linkage_invalid",
        "component": "workflow",
        "status_code": "invalid_contract",
    }


def test_dispatch_conversation_orphan_tool_observation_is_structured_failure() -> None:
    invalid_result = ConversationResult(
        status=ConversationResultStatus.FAILURE,
        payload=ConversationPayload(response_text="invalid", tool_references=[]),
        metadata=ConversationMetadata(
            termination_reason=ConversationTerminationReason.TOOL_FAILURE,
            iterations=1,
            max_iterations=3,
            turns=[
                ConversationTurnRecord(
                    iteration=1,
                    action=ConversationAction(
                        action_type=ConversationActionType.COMPLETE,
                        response_text="done",
                    ),
                    observation=ToolObservation(
                        reference_id="tool-001",
                        tool_name="echo",
                        summary="ok",
                    ),
                )
            ],
            runtime_error=None,
        ),
    )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=lambda _text: invalid_result,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.runtime_error is not None
    assert result.runtime_error.code == "observability_parent_linkage_invalid"
    assert result.runtime_error.component is RuntimeErrorComponent.WORKFLOW
    assert result.runtime_error.status_code == "invalid_contract"
    assert result.runtime_error.details["event_component"] == "tool_call"
    assert result.runtime_error.details["reason"] == "orphan_tool_observation"
    assert result.runtime_error.details["iteration"] == 1


def test_dispatch_conversation_missing_tool_name_is_structured_failure() -> None:
    invalid_result = ConversationResult(
        status=ConversationResultStatus.FAILURE,
        payload=ConversationPayload(response_text="invalid", tool_references=[]),
        metadata=ConversationMetadata(
            termination_reason=ConversationTerminationReason.TOOL_FAILURE,
            iterations=1,
            max_iterations=3,
            turns=[
                ConversationTurnRecord(
                    iteration=1,
                    action=ConversationAction(
                        action_type=ConversationActionType.TOOL_CALL,
                        tool_name="",
                        tool_args={},
                    ),
                    observation=None,
                )
            ],
            runtime_error=None,
        ),
    )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=lambda _text: invalid_result,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.runtime_error is not None
    assert result.runtime_error.code == "observability_parent_linkage_invalid"
    assert result.runtime_error.component is RuntimeErrorComponent.WORKFLOW
    assert result.runtime_error.status_code == "invalid_contract"
    assert result.runtime_error.details["event_component"] == "tool_call"
    assert result.runtime_error.details["reason"] == "missing_tool_name"
    assert result.runtime_error.details["iteration"] == 1


def test_dispatch_conversation_missing_tool_call_identifier_is_structured_failure() -> None:
    invalid_result = ConversationResult(
        status=ConversationResultStatus.FAILURE,
        payload=ConversationPayload(response_text="invalid", tool_references=[]),
        metadata=ConversationMetadata(
            termination_reason=ConversationTerminationReason.TOOL_FAILURE,
            iterations=1,
            max_iterations=3,
            turns=[
                ConversationTurnRecord(
                    iteration=1,
                    action=ConversationAction(
                        action_type=ConversationActionType.TOOL_CALL,
                        tool_name="echo",
                        tool_args={},
                    ),
                    observation=ToolObservation(
                        reference_id="   ",
                        tool_name="echo",
                        summary="ok",
                    ),
                )
            ],
            runtime_error=None,
        ),
    )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=lambda _text: invalid_result,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.runtime_error is not None
    assert result.runtime_error.code == "observability_parent_linkage_invalid"
    assert result.runtime_error.component is RuntimeErrorComponent.WORKFLOW
    assert result.runtime_error.status_code == "invalid_contract"
    assert result.runtime_error.details["event_component"] == "tool_call"
    assert result.runtime_error.details["reason"] == "missing_tool_call_identifier"
    assert result.runtime_error.details["iteration"] == 1


def test_dispatch_conversation_parent_linkage_invariants_hold_for_multi_turn_chain() -> None:
    def runtime(user_input: str) -> ConversationResult:
        return run_bounded_conversation(
            user_input=user_input,
            max_iterations=3,
            select_action=lambda _text, turns: ConversationAction(
                action_type=(
                    ConversationActionType.TOOL_CALL
                    if len(turns) < 2
                    else ConversationActionType.COMPLETE
                ),
                tool_name="echo",
                tool_args={"query": "status"},
                response_text="done",
            ),
            execute_tool=lambda _tool_name, _tool_args: "tool-ok",
            synthesize_response=lambda _text, _turns, refs: f"refs={len(refs)}",
        )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=runtime,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.telemetry_payload is not None
    extension = result.telemetry_payload["conversation_correlation"]
    assert isinstance(extension, dict)
    events = extension["events"]
    assert isinstance(events, list)

    workflow_id = extension["workflow_id"]
    step_ids: set[str] = set()
    agent_ids: set[str] = set()
    for event in events:
        assert isinstance(event, dict)
        component = event["component"]
        correlation = event["correlation"]
        parent = event["parent"]
        assert isinstance(correlation, dict)
        assert isinstance(parent, dict)

        if component == "step":
            assert parent == {"workflow_id": workflow_id}
            step_id = correlation["step_id"]
            assert isinstance(step_id, str)
            assert step_id
            step_ids.add(step_id)
            continue

        if component == "agent":
            assert parent["workflow_id"] == workflow_id
            parent_step_id = parent["step_id"]
            assert isinstance(parent_step_id, str)
            assert parent_step_id in step_ids
            agent_id = correlation["agent_id"]
            assert isinstance(agent_id, str)
            assert agent_id
            agent_ids.add(agent_id)
            continue

        if component == "tool_call":
            assert parent["workflow_id"] == workflow_id
            parent_step_id = parent["step_id"]
            parent_agent_id = parent["agent_id"]
            assert isinstance(parent_step_id, str)
            assert isinstance(parent_agent_id, str)
            assert parent_step_id in step_ids
            assert parent_agent_id in agent_ids

def test_dispatch_conversation_parity_with_command_shared_boundaries() -> None:
    command_result = dispatch_input(
        "/show-status now",
        command_executor=lambda _name, _args: "ok",
        conversation_handler=lambda text: text,
    )
    conversation_result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: f"echo:{text}",
    )

    assert command_result.telemetry_payload is not None
    assert conversation_result.telemetry_payload is not None

    command_envelope = command_result.telemetry_payload["envelope"]
    conversation_envelope = conversation_result.telemetry_payload["envelope"]
    assert isinstance(command_envelope, dict)
    assert isinstance(conversation_envelope, dict)
    assert set(command_envelope) == set(conversation_envelope)

    command_correlation = command_result.telemetry_payload["correlation"]
    conversation_correlation = conversation_result.telemetry_payload["correlation"]
    assert isinstance(command_correlation, dict)
    assert isinstance(conversation_correlation, dict)
    for shared_field in (
        "route",
        "session_id",
        "execution_id",
        "command_id",
        "workflow_id",
    ):
        assert shared_field in command_correlation
        assert shared_field in conversation_correlation
    assert "termination_reason" not in command_correlation
    assert "termination_reason" in conversation_correlation


def test_dispatch_conversation_extension_sanitizes_sensitive_payloads() -> None:
    secret_value = "TOPSECRET-RAW-VALUE"

    def runtime(user_input: str) -> ConversationResult:
        return run_bounded_conversation(
            user_input=user_input,
            max_iterations=2,
            select_action=lambda _text, turns: ConversationAction(
                action_type=(
                    ConversationActionType.TOOL_CALL
                    if len(turns) == 0
                    else ConversationActionType.COMPLETE
                ),
                tool_name="echo",
                tool_args={"request_text": secret_value, "query": "status"},
                response_text="done",
            ),
            execute_tool=lambda _tool_name, _tool_args: secret_value,
            synthesize_response=lambda _text, _turns, _refs: "done",
        )

    result = dispatch_input(
        "hello",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=runtime,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.telemetry_payload is not None
    extension = result.telemetry_payload["conversation_correlation"]
    assert isinstance(extension, dict)
    events = extension["events"]
    assert isinstance(events, list)
    tool_event = events[2]
    tool_payload = tool_event["tool_call"]
    assert isinstance(tool_payload, dict)
    assert tool_payload["arg_keys"] == ["query"]
    serialized_telemetry = str(result.telemetry_payload)
    assert "request_text" not in serialized_telemetry
    assert secret_value not in serialized_telemetry


def test_dispatch_conversation_emits_approve_plan_confirmation_decision_from_runtime_error(
) -> None:
    runtime_error = RuntimeErrorEnvelope(
        code="confirmation_out_of_plan",
        component=RuntimeErrorComponent.WORKFLOW,
        message="Sensitive action not present in approved plan.",
        status_code="permission_denied",
        details={
            "mode": "approve_plan",
            "required": True,
            "outcome": "approved",
            "summary": {
                "plan_fingerprint": "abc123def4567890",
                "action_count": 2,
            },
            "execution_id": "exec-plan-1",
        },
    )

    def runtime(_: str) -> ConversationResult:
        return ConversationResult(
            status=ConversationResultStatus.FAILURE,
            payload=ConversationPayload(response_text="blocked", tool_references=[]),
            metadata=ConversationMetadata(
                termination_reason=ConversationTerminationReason.POLICY_DENIED,
                iterations=1,
                max_iterations=3,
                turns=[],
                runtime_error=runtime_error,
            ),
        )

    result = dispatch_input(
        "please execute approved plan",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=runtime,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.telemetry_payload is not None
    confirmation = result.telemetry_payload["confirmation_decision"]
    assert isinstance(confirmation, dict)
    assert confirmation["mode"] == "approve_plan"
    assert confirmation["required"] is True
    assert confirmation["outcome"] == "approved"
    assert confirmation["correlation"] == {"execution_id": "exec-plan-1"}


def test_backend_selection_matrix_uses_locked_v1_defaults() -> None:
    repo_read = resolve_backend_selection(
        required_capabilities=["repo.read"],
        context={},
    )
    assert repo_read.selected_backend is BackendKind.LOCAL

    shell_exec = resolve_backend_selection(
        required_capabilities=["shell.exec"],
        context={},
    )
    assert shell_exec.selected_backend is BackendKind.WORKER

    mixed = resolve_backend_selection(
        required_capabilities=["repo.read", "shell.exec"],
        context={},
    )
    assert mixed.selected_backend is BackendKind.WORKER
    assert mixed.required_capabilities == ("repo.read", "shell.exec")


def test_backend_selection_blocks_locked_capability_downgrade_override() -> None:
    selection = resolve_backend_selection(
        required_capabilities=["system.modify"],
        context={
            "runtime": {
                "capability_backends": {
                    "system.modify": "local",
                }
            }
        },
    )

    assert selection.selected_backend is BackendKind.WORKER
    assert selection.mapped_capabilities["system.modify"] == "worker"


def test_backend_selection_is_deterministic_for_identical_inputs() -> None:
    first = resolve_backend_selection(
        required_capabilities=["system.modify", "repo.read"],
        context={
            "runtime": {
                "default_backend": "local",
                "capability_backends": {
                    "system.modify": "worker",
                    "repo.read": "local",
                },
            }
        },
    )
    second = resolve_backend_selection(
        required_capabilities=["repo.read", "system.modify"],
        context={
            "runtime": {
                "capability_backends": {
                    "repo.read": "local",
                    "system.modify": "worker",
                },
                "default_backend": "local",
            }
        },
    )

    assert first == second
    assert backend_selection_metadata(first) == backend_selection_metadata(second)


def test_backend_interface_contracts_are_explicit_and_type_safe() -> None:
    local_backend = LocalBackend(command_executor=lambda _name, _args: "ok")
    assert isinstance(local_backend, ExecutionBackend)
    assert local_backend.kind is BackendKind.LOCAL
    assert_type(local_backend, ExecutionBackend)

    def expects_worker(_backend: WorkerBackend) -> None:
        return None

    def expects_container(_backend: ContainerBackend) -> None:
        return None

    def expects_remote(_backend: RemoteBackend) -> None:
        return None

    assert callable(expects_worker)
    assert callable(expects_container)
    assert callable(expects_remote)


def test_dispatch_command_emits_backend_selection_for_authorization_and_confirmation() -> None:
    def command_executor(_name: str, _args: list[str]) -> str:
        return "executed"

    result = dispatch_input(
        "/delete-project now",
        command_executor=command_executor,
        conversation_handler=lambda text: text,
        command_context={
            "command_capabilities": {
                "delete-project": ["system.modify"],
            },
            "confirmation_decision": {
                "outcome": "approved",
                "actor_id": "operator-9",
            },
        },
        session_context={"granted_capabilities": ["system.modify"]},
        execution_backends={
            BackendKind.WORKER: PassThroughWorkerBackend(command_executor)
        },
    )

    assert result.route is RouteKind.COMMAND
    assert result.telemetry_payload is not None

    backend_selection = result.telemetry_payload["backend_selection"]
    assert isinstance(backend_selection, dict)
    assert backend_selection["selected_backend"] == "worker"
    assert backend_selection["selection_reason"] == {
        "mode": "highest_isolation_wins",
        "selected_capabilities": ["system.modify"],
    }

    authorization = result.telemetry_payload["authorization_decision"]
    assert isinstance(authorization, dict)
    authorization_backend_selection = authorization["backend_selection"]
    assert isinstance(authorization_backend_selection, dict)
    assert authorization_backend_selection["selected_backend"] == "worker"

    confirmation = result.telemetry_payload["confirmation_decision"]
    assert isinstance(confirmation, dict)
    confirmation_backend_selection = confirmation["backend_selection"]
    assert isinstance(confirmation_backend_selection, dict)
    assert confirmation_backend_selection["selected_backend"] == "worker"


def test_dispatch_conversation_emits_backend_selection_from_runtime_error() -> None:
    runtime_error = RuntimeErrorEnvelope(
        code="confirmation_declined",
        component=RuntimeErrorComponent.WORKFLOW,
        message="Per-action confirmation declined.",
        status_code="permission_denied",
        details={
            "mode": "per_action",
            "required": True,
            "outcome": "declined",
            "backend_selection": {
                "selected_backend": "worker",
                "selected_isolation": 1,
                "mapped_capabilities": {"system.modify": "worker"},
                "selection_reason": {
                    "mode": "highest_isolation_wins",
                    "selected_capabilities": ["system.modify"],
                },
            },
        },
    )

    def runtime(_: str) -> ConversationResult:
        return ConversationResult(
            status=ConversationResultStatus.FAILURE,
            payload=ConversationPayload(response_text="denied", tool_references=[]),
            metadata=ConversationMetadata(
                termination_reason=ConversationTerminationReason.POLICY_DENIED,
                iterations=1,
                max_iterations=3,
                turns=[],
                runtime_error=runtime_error,
            ),
        )

    result = dispatch_input(
        "please delete repository",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=runtime,
    )

    assert result.route is RouteKind.CONVERSATION
    assert result.telemetry_payload is not None
    backend_selection = result.telemetry_payload["backend_selection"]
    assert isinstance(backend_selection, dict)
    assert backend_selection["selected_backend"] == "worker"
    assert backend_selection["selected_isolation"] == 1
