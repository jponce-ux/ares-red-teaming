"""Built-in ENDI tool contracts for local filesystem and shell operations."""

from __future__ import annotations

import subprocess
from pathlib import Path

from endi.tools import ToolContract, ToolRegistry


def _resolve_allowed_path(root: str, relative_path: str) -> Path:
    root_path = Path(root).expanduser().resolve()
    candidate = (root_path / relative_path).expanduser().resolve()
    try:
        candidate.relative_to(root_path)
    except ValueError as exc:
        raise ValueError("Path escapes configured root.") from exc
    return candidate


def read_file(payload: dict[str, object]) -> dict[str, object]:
    """Read a UTF-8 file below an allowed root."""
    root = payload.get("root")
    path = payload.get("path")
    if not isinstance(root, str) or not isinstance(path, str):
        raise ValueError("root and path must be strings.")
    resolved = _resolve_allowed_path(root, path)
    content = resolved.read_text(encoding="utf-8")
    return {
        "path": str(resolved),
        "content": content,
        "bytes": len(content.encode("utf-8")),
    }


def write_file(payload: dict[str, object]) -> dict[str, object]:
    """Write UTF-8 content below an allowed root."""
    root = payload.get("root")
    path = payload.get("path")
    content = payload.get("content")
    if not isinstance(root, str) or not isinstance(path, str) or not isinstance(content, str):
        raise ValueError("root, path, and content must be strings.")
    resolved = _resolve_allowed_path(root, path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding="utf-8")
    return {
        "path": str(resolved),
        "bytes": len(content.encode("utf-8")),
    }


def run_shell(payload: dict[str, object]) -> dict[str, object]:
    """Run a shell command with cwd and timeout constraints."""
    command = payload.get("command")
    cwd = payload.get("cwd")
    timeout = payload.get("timeout_seconds", 30)
    if not isinstance(command, str) or not command.strip():
        raise ValueError("command must be a non-empty string.")
    if not isinstance(cwd, str):
        raise ValueError("cwd must be a string.")
    if not isinstance(timeout, int):
        raise ValueError("timeout_seconds must be an integer.")

    resolved_cwd = Path(cwd).expanduser().resolve()
    try:
        completed = subprocess.run(
            command,
            cwd=str(resolved_cwd),
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "cwd": str(resolved_cwd),
            "timed_out": True,
            "timeout_seconds": timeout,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "exit_code": None,
        }

    return {
        "command": command,
        "cwd": str(resolved_cwd),
        "timed_out": False,
        "timeout_seconds": timeout,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_code": completed.returncode,
    }


def build_builtin_tool_registry() -> ToolRegistry:
    """Build a ToolRegistry populated with ENDI built-in local tools."""
    registry = ToolRegistry()
    registry.register(
        ToolContract(
            identifier="filesystem.read",
            description="Read a UTF-8 file under an allowed root.",
            capability="filesystem.read",
            input_schema={"root": str, "path": str},
            handler=read_file,
        )
    )
    registry.register(
        ToolContract(
            identifier="filesystem.write",
            description="Write UTF-8 content under an allowed root.",
            capability="filesystem.write",
            input_schema={"root": str, "path": str, "content": str},
            handler=write_file,
        )
    )
    registry.register(
        ToolContract(
            identifier="shell.exec",
            description="Run a shell command with cwd and timeout constraints.",
            capability="shell.exec",
            input_schema={"command": str, "cwd": str, "timeout_seconds": int},
            handler=run_shell,
        )
    )
    return registry
