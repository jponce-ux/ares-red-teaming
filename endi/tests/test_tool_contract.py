"""Tests for standardized tool contract registration and invocation."""

from endi.conversation import ConversationAction, ConversationActionType, run_bounded_conversation
from endi.routing import RouteKind, dispatch_input
from endi.tools import ToolContract, ToolRegistry, ToolStatus, ToolStatusCode


def test_registry_rejects_tool_missing_required_contract_fields() -> None:
    registry = ToolRegistry()

    result = registry.register(
        {
            "identifier": "",
            "description": "",
            "capability": "",
            "input_schema": {"text": str},
        }
    )

    assert result.status is ToolStatus.ERROR
    assert result.status_code is ToolStatusCode.INVALID_CONTRACT
    assert result.error is not None
    assert "handler" in result.error.details["missing_fields"]
    assert "identifier" in result.error.details["invalid_fields"]
    assert registry.list_tools() == []


def test_registry_accepts_valid_tool_contract() -> None:
    registry = ToolRegistry()
    contract = ToolContract(
        identifier="echo",
        description="Echo text payload",
        capability="utility.echo",
        input_schema={"text": str},
        handler=lambda payload: payload["text"],
    )

    result = registry.register(contract)

    assert result.status is ToolStatus.SUCCESS
    assert result.status_code is ToolStatusCode.OK
    assert registry.list_tools() == ["echo"]


def test_registry_rejects_non_string_schema_field_names() -> None:
    registry = ToolRegistry()

    result = registry.register(
        ToolContract(
            identifier="bad-schema",
            description="Invalid schema key type",
            capability="utility.invalid",
            input_schema={"ok": str, 1: str},
            handler=lambda payload: payload,
        )
    )

    assert result.status is ToolStatus.ERROR
    assert result.status_code is ToolStatusCode.INVALID_CONTRACT
    assert result.error is not None
    assert "input_schema" in result.error.details["invalid_fields"]
    assert registry.list_tools() == []


def test_invoke_blocks_handler_execution_when_input_schema_is_invalid() -> None:
    execution_count = 0

    def handler(payload: dict[str, object]) -> object:
        nonlocal execution_count
        execution_count += 1
        return payload["text"]

    registry = ToolRegistry()
    registry.register(
        ToolContract(
            identifier="echo",
            description="Echo text payload",
            capability="utility.echo",
            input_schema={"text": str},
            handler=handler,
        )
    )

    result = registry.invoke("echo", {}, granted_capabilities=["utility.echo"])

    assert result.status is ToolStatus.ERROR
    assert result.status_code is ToolStatusCode.INVALID_INPUT
    assert result.error is not None
    assert result.error.details["missing_fields"] == ["text"]
    assert execution_count == 0


def test_invoke_returns_deterministic_success_and_error_status_codes() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolContract(
            identifier="echo",
            description="Echo text payload",
            capability="utility.echo",
            input_schema={"text": str},
            handler=lambda payload: payload["text"],
        )
    )
    registry.register(
        ToolContract(
            identifier="boom",
            description="Always fails",
            capability="utility.fail",
            input_schema={"text": str},
            handler=lambda _payload: (_ for _ in ()).throw(RuntimeError("boom")),
        )
    )

    success = registry.invoke("echo", {"text": "ok"}, granted_capabilities=["utility.echo"])
    not_found = registry.invoke("missing", {"text": "ok"})
    invalid = registry.invoke("echo", {"text": 1}, granted_capabilities=["utility.echo"])
    execution_failure = registry.invoke(
        "boom",
        {"text": "x"},
        granted_capabilities=["utility.fail"],
    )

    assert success.status_code is ToolStatusCode.OK
    assert success.status is ToolStatus.SUCCESS
    assert success.payload == "ok"

    assert not_found.status_code is ToolStatusCode.NOT_FOUND
    assert not_found.status is ToolStatus.ERROR

    assert invalid.status_code is ToolStatusCode.INVALID_INPUT
    assert invalid.status is ToolStatus.ERROR

    assert execution_failure.status_code is ToolStatusCode.EXECUTION_ERROR
    assert execution_failure.status is ToolStatus.ERROR


def test_command_and_conversation_paths_share_same_tool_contract() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolContract(
            identifier="echo",
            description="Echo text payload",
            capability="utility.echo",
            input_schema={"text": str},
            handler=lambda payload: f"echo:{payload['text']}",
        )
    )

    command_result = registry.invoke(
        "echo",
        {"text": "hello"},
        granted_capabilities=["utility.echo"],
    )

    conversation_result = run_bounded_conversation(
        user_input="run echo",
        max_iterations=2,
        select_action=lambda _text, turns: ConversationAction(
            action_type=(
                ConversationActionType.TOOL_CALL
                if len(turns) == 0
                else ConversationActionType.COMPLETE
            ),
            tool_name="echo",
            tool_args={"text": "hello"},
            response_text="done",
        ),
        execute_tool=lambda tool_name, tool_args: registry.invoke(
            tool_name,
            tool_args,
            granted_capabilities=["utility.echo"],
        ),
        synthesize_response=lambda _text, _turns, _refs: "done",
    )

    assert command_result.status is ToolStatus.SUCCESS
    assert command_result.status_code is ToolStatusCode.OK
    assert command_result.payload == "echo:hello"

    assert conversation_result.payload.tool_references[0].summary == "echo:hello"


def test_dispatch_surfaces_preserve_matching_tool_error_contracts() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolContract(
            identifier="echo",
            description="Echo text payload",
            capability="utility.echo",
            input_schema={"text": str},
            handler=lambda payload: payload["text"],
        )
    )

    command_result = dispatch_input(
        "/echo",
        command_executor=lambda _name, _args: registry.invoke(
            "echo",
            {"text": 1},
            granted_capabilities=["utility.echo"],
        ),
        conversation_handler=lambda text: text,
    )

    conversation_result = dispatch_input(
        "run echo",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=lambda user_input: run_bounded_conversation(
            user_input=user_input,
            max_iterations=2,
            select_action=lambda _text, turns: ConversationAction(
                action_type=(
                    ConversationActionType.TOOL_CALL
                    if len(turns) == 0
                    else ConversationActionType.COMPLETE
                ),
                tool_name="echo",
                tool_args={"text": 1},
                response_text="done",
            ),
            execute_tool=lambda tool_name, tool_args: registry.invoke(
                tool_name,
                tool_args,
                granted_capabilities=["utility.echo"],
            ),
            synthesize_response=lambda _text, _turns, _refs: "done",
        ),
    )

    assert command_result.route is RouteKind.EXECUTION_ERROR
    assert command_result.runtime_error is not None
    assert command_result.runtime_error.component.value == "tool"
    assert command_result.runtime_error.code == "invalid_tool_input"
    assert command_result.runtime_error.status_code == ToolStatusCode.INVALID_INPUT.value

    assert conversation_result.route is RouteKind.CONVERSATION
    assert conversation_result.runtime_error is not None
    assert conversation_result.runtime_error.component.value == "tool"
    assert conversation_result.runtime_error.code == "invalid_tool_input"
    assert (
        conversation_result.runtime_error.status_code
        == ToolStatusCode.INVALID_INPUT.value
    )


def test_invoke_denied_capability_blocks_handler_side_effects() -> None:
    execution_count = 0

    def handler(_payload: dict[str, object]) -> object:
        nonlocal execution_count
        execution_count += 1
        return "ok"

    registry = ToolRegistry()
    registry.register(
        ToolContract(
            identifier="dangerous",
            description="Dangerous operation",
            capability="system.write",
            input_schema={"target": str},
            handler=handler,
        )
    )

    denied = registry.invoke("dangerous", {"target": "x"}, granted_capabilities=[])

    assert denied.status is ToolStatus.ERROR
    assert denied.status_code is ToolStatusCode.PERMISSION_DENIED
    assert denied.error is not None
    assert denied.error.code == "capability_denied"
    assert denied.error.details["surface"] == "tool"
    assert denied.error.details["operation"] == "dangerous"
    assert denied.error.details["missing_capabilities"] == ["system.write"]
    assert execution_count == 0


def test_dispatch_surfaces_preserve_matching_authorization_denied_contracts() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolContract(
            identifier="dangerous",
            description="Dangerous operation",
            capability="system.write",
            input_schema={"target": str},
            handler=lambda payload: f"ok:{payload['target']}",
        )
    )

    command_result = dispatch_input(
        "/dangerous",
        command_executor=lambda _name, _args: registry.invoke(
            "dangerous",
            {"target": "x"},
            granted_capabilities=[],
        ),
        conversation_handler=lambda text: text,
    )

    conversation_result = dispatch_input(
        "run dangerous",
        command_executor=lambda _name, _args: "unused",
        conversation_handler=lambda text: text,
        conversation_runtime=lambda user_input: run_bounded_conversation(
            user_input=user_input,
            max_iterations=2,
            select_action=lambda _text, turns: ConversationAction(
                action_type=(
                    ConversationActionType.TOOL_CALL
                    if len(turns) == 0
                    else ConversationActionType.COMPLETE
                ),
                tool_name="dangerous",
                tool_args={"target": "x"},
                response_text="done",
            ),
            execute_tool=lambda tool_name, tool_args: registry.invoke(
                tool_name,
                tool_args,
                granted_capabilities=[],
            ),
            synthesize_response=lambda _text, _turns, _refs: "done",
        ),
    )

    assert command_result.route is RouteKind.EXECUTION_ERROR
    assert command_result.runtime_error is not None
    assert command_result.runtime_error.component.value == "tool"
    assert command_result.runtime_error.code == "capability_denied"
    assert command_result.runtime_error.status_code == ToolStatusCode.PERMISSION_DENIED.value

    assert conversation_result.route is RouteKind.CONVERSATION
    assert conversation_result.runtime_error is not None
    assert conversation_result.runtime_error.component.value == "tool"
    assert conversation_result.runtime_error.code == "capability_denied"
    assert (
        conversation_result.runtime_error.status_code
        == ToolStatusCode.PERMISSION_DENIED.value
    )
    assert conversation_result.telemetry_payload is not None
    authorization = conversation_result.telemetry_payload["authorization_decision"]
    assert isinstance(authorization, dict)
    assert authorization == {
        "surface": "tool",
        "operation": "dangerous",
        "allowed": False,
        "required_capabilities": ["system.write"],
        "missing_capabilities": ["system.write"],
    }
