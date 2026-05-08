"""Tests for bounded conversational tool loop runtime."""

from endi.conversation import (
    ConversationAction,
    ConversationActionType,
    ConversationResultStatus,
    ConversationTerminationReason,
    RuntimeErrorComponent,
    SynthesisResult,
    run_bounded_conversation,
)


def test_loop_completes_with_tool_references_in_payload() -> None:
    def select_action(_text: str, turns: list[object]) -> ConversationAction:
        if not turns:
            return ConversationAction(
                action_type=ConversationActionType.TOOL_CALL,
                tool_name="weather.lookup",
                tool_args={"city": "Montevideo"},
            )
        return ConversationAction(
            action_type=ConversationActionType.COMPLETE,
            response_text="It is 24C and clear.",
        )

    result = run_bounded_conversation(
        user_input="weather in Montevideo",
        max_iterations=3,
        select_action=select_action,
        execute_tool=lambda _tool, _args: "24C and clear",
        synthesize_response=lambda _text, _turns, refs: f"used={len(refs)}",
    )

    assert result.status is ConversationResultStatus.SUCCESS
    assert result.metadata.termination_reason is ConversationTerminationReason.COMPLETED
    assert result.metadata.runtime_error is None
    assert result.payload.response_text == "It is 24C and clear."
    assert [ref.reference_id for ref in result.payload.tool_references] == ["tool-001"]


def test_loop_stops_at_max_iterations_with_explicit_reason() -> None:
    result = run_bounded_conversation(
        user_input="keep iterating",
        max_iterations=2,
        select_action=lambda _text, _turns: ConversationAction(
            action_type=ConversationActionType.TOOL_CALL,
            tool_name="echo",
            tool_args={},
        ),
        execute_tool=lambda _tool, _args: "ok",
        synthesize_response=lambda _text, _turns, refs: f"partial via {len(refs)} refs",
    )

    assert result.status is ConversationResultStatus.FAILURE
    assert result.metadata.termination_reason is ConversationTerminationReason.MAX_ITERATIONS
    assert result.metadata.iterations == 2
    assert result.payload.response_text == "partial via 2 refs"


def test_loop_stops_on_tool_failure() -> None:
    def fail_tool(_tool: str, _args: dict[str, object]) -> object:
        raise RuntimeError("tool crashed")

    result = run_bounded_conversation(
        user_input="run risky tool",
        max_iterations=3,
        select_action=lambda _text, _turns: ConversationAction(
            action_type=ConversationActionType.TOOL_CALL,
            tool_name="risky",
            tool_args={},
        ),
        execute_tool=fail_tool,
        synthesize_response=lambda _text, _turns, refs: f"failed after {len(refs)} refs",
    )

    assert result.status is ConversationResultStatus.FAILURE
    assert result.metadata.termination_reason is ConversationTerminationReason.TOOL_FAILURE
    assert result.metadata.runtime_error is not None
    assert result.metadata.runtime_error.code == "tool_execution_error"
    assert result.metadata.runtime_error.component is RuntimeErrorComponent.TOOL
    assert result.metadata.runtime_error.status_code == "execution_error"
    assert result.payload.response_text == "failed after 0 refs"


def test_loop_stops_on_policy_denied_before_tool_execution() -> None:
    execute_calls = 0

    def execute_tool(_tool: str, _args: dict[str, object]) -> object:
        nonlocal execute_calls
        execute_calls += 1
        return "ok"

    result = run_bounded_conversation(
        user_input="delete everything",
        max_iterations=3,
        select_action=lambda _text, _turns: ConversationAction(
            action_type=ConversationActionType.TOOL_CALL,
            tool_name="danger.delete",
            tool_args={},
        ),
        execute_tool=execute_tool,
        synthesize_response=lambda _text, _turns, _refs: "denied",
        policy_check=lambda _tool, _args: False,
    )

    assert result.status is ConversationResultStatus.FAILURE
    assert result.metadata.termination_reason is ConversationTerminationReason.POLICY_DENIED
    assert execute_calls == 0


def test_loop_stops_on_timeout_condition() -> None:
    result = run_bounded_conversation(
        user_input="long running",
        max_iterations=3,
        select_action=lambda _text, _turns: ConversationAction(
            action_type=ConversationActionType.TOOL_CALL,
            tool_name="echo",
            tool_args={},
        ),
        execute_tool=lambda _tool, _args: "ok",
        synthesize_response=lambda _text, _turns, _refs: "timed out",
        timeout_check=lambda _iteration: True,
    )

    assert result.status is ConversationResultStatus.FAILURE
    assert result.metadata.termination_reason is ConversationTerminationReason.TIMEOUT
    assert result.metadata.iterations == 0


def test_loop_treats_missing_tool_name_as_tool_failure() -> None:
    result = run_bounded_conversation(
        user_input="run unknown tool",
        max_iterations=2,
        select_action=lambda _text, _turns: ConversationAction(
            action_type=ConversationActionType.TOOL_CALL,
            tool_name=None,
            tool_args={},
        ),
        execute_tool=lambda _tool, _args: "ok",
        synthesize_response=lambda _text, _turns, _refs: "failed",
    )

    assert result.status is ConversationResultStatus.FAILURE
    assert result.metadata.termination_reason is ConversationTerminationReason.TOOL_FAILURE
    assert result.metadata.runtime_error is not None
    assert result.metadata.runtime_error.code == "missing_tool_name"
    assert result.metadata.runtime_error.component is RuntimeErrorComponent.AGENT
    assert result.metadata.runtime_error.status_code == "invalid_contract"
    assert result.metadata.iterations == 1


def test_loop_includes_only_consumed_references_in_payload() -> None:
    def select_action(_text: str, turns: list[object]) -> ConversationAction:
        if len(turns) < 2:
            return ConversationAction(
                action_type=ConversationActionType.TOOL_CALL,
                tool_name="echo",
                tool_args={"turn": len(turns) + 1},
            )
        return ConversationAction(action_type=ConversationActionType.COMPLETE)

    result = run_bounded_conversation(
        user_input="two tools",
        max_iterations=3,
        select_action=select_action,
        execute_tool=lambda _tool, args: f"out-{args['turn']}",
        synthesize_response=lambda _text, _turns, _refs: SynthesisResult(
            response_text="used second",
            consumed_reference_ids=["tool-002"],
        ),
    )

    assert result.status is ConversationResultStatus.SUCCESS
    assert result.metadata.termination_reason is ConversationTerminationReason.COMPLETED
    assert [ref.reference_id for ref in result.payload.tool_references] == ["tool-002"]
