"""Tests for ENDI built-in filesystem and shell tools."""

from endi.builtin_tools import build_builtin_tool_registry
from endi.tools import ToolStatus, ToolStatusCode


def test_filesystem_read_requires_capability(tmp_path) -> None:
    target = tmp_path / "input.txt"
    target.write_text("hello", encoding="utf-8")
    registry = build_builtin_tool_registry()

    denied = registry.invoke(
        "filesystem.read",
        {"root": str(tmp_path), "path": "input.txt"},
        granted_capabilities=[],
    )
    allowed = registry.invoke(
        "filesystem.read",
        {"root": str(tmp_path), "path": "input.txt"},
        granted_capabilities=["filesystem.read"],
    )

    assert denied.status is ToolStatus.ERROR
    assert denied.status_code is ToolStatusCode.PERMISSION_DENIED
    assert allowed.status is ToolStatus.SUCCESS
    assert allowed.payload == {
        "path": str(target),
        "content": "hello",
        "bytes": 5,
    }


def test_filesystem_write_denied_before_side_effect(tmp_path) -> None:
    registry = build_builtin_tool_registry()

    result = registry.invoke(
        "filesystem.write",
        {"root": str(tmp_path), "path": "output.txt", "content": "secret"},
        granted_capabilities=[],
    )

    assert result.status is ToolStatus.ERROR
    assert not (tmp_path / "output.txt").exists()


def test_shell_exec_returns_structured_payload(tmp_path) -> None:
    registry = build_builtin_tool_registry()

    result = registry.invoke(
        "shell.exec",
        {"command": "printf hello", "cwd": str(tmp_path), "timeout_seconds": 5},
        granted_capabilities=["shell.exec"],
    )

    assert result.status is ToolStatus.SUCCESS
    assert isinstance(result.payload, dict)
    assert result.payload["stdout"] == "hello"
    assert result.payload["stderr"] == ""
    assert result.payload["exit_code"] == 0
    assert result.payload["timed_out"] is False
