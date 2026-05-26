"""Manifest-only plugin discovery for ENDI command metadata."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from endi.routing import CommandDiscoverability


@dataclass(frozen=True)
class PluginDiagnostic:
    """Structured plugin discovery diagnostic."""

    path: str
    code: str
    message: str


@dataclass(frozen=True)
class PluginDiscoveryResult:
    """Plugin discovery output."""

    commands: tuple[CommandDiscoverability, ...]
    diagnostics: tuple[PluginDiagnostic, ...]


def _load_manifest(path: Path) -> dict[str, object]:
    try:
        decoded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Manifest cannot be read: {exc}") from exc
    if not isinstance(decoded, dict):
        raise ValueError("Manifest must be a JSON object.")
    return decoded


def _command_from_manifest_item(item: object) -> CommandDiscoverability:
    if not isinstance(item, dict):
        raise ValueError("Command entry must be an object.")
    name = item.get("name")
    description = item.get("description")
    arg_schema = item.get("arg_schema", "")
    examples = item.get("examples", [])
    execution_target = item.get("execution_target", "plugin")
    if not isinstance(name, str) or not name:
        raise ValueError("Command name is required.")
    if not isinstance(description, str) or not description:
        raise ValueError("Command description is required.")
    if not isinstance(arg_schema, str):
        raise ValueError("Command arg_schema must be a string.")
    if not isinstance(examples, list) or not all(isinstance(example, str) for example in examples):
        raise ValueError("Command examples must be a list of strings.")
    if not isinstance(execution_target, str) or not execution_target:
        raise ValueError("Command execution_target must be a string.")
    return CommandDiscoverability(
        name=name,
        description=description,
        arg_schema=arg_schema,
        examples=tuple(examples),
        execution_target=execution_target,
    )


def discover_plugin_commands(plugin_dir: str | None) -> PluginDiscoveryResult:
    """Discover command metadata from JSON plugin manifests."""
    if plugin_dir is None or not plugin_dir:
        return PluginDiscoveryResult(commands=(), diagnostics=())

    root = Path(plugin_dir).expanduser()
    if not root.exists():
        return PluginDiscoveryResult(
            commands=(),
            diagnostics=(
                PluginDiagnostic(
                    path=str(root),
                    code="plugin_directory_missing",
                    message="Plugin directory does not exist.",
                ),
            ),
        )

    commands: list[CommandDiscoverability] = []
    diagnostics: list[PluginDiagnostic] = []
    seen: set[str] = set()
    for manifest_path in sorted(root.glob("*.json")):
        try:
            manifest = _load_manifest(manifest_path)
            raw_commands = manifest.get("commands", [])
            if not isinstance(raw_commands, list):
                raise ValueError("Manifest commands must be a list.")
            for raw_command in raw_commands:
                command = _command_from_manifest_item(raw_command)
                if command.name in seen:
                    raise ValueError(f"Duplicate command '{command.name}'.")
                seen.add(command.name)
                commands.append(command)
        except ValueError as exc:
            diagnostics.append(
                PluginDiagnostic(
                    path=str(manifest_path),
                    code="invalid_plugin_manifest",
                    message=str(exc),
                )
            )

    return PluginDiscoveryResult(
        commands=tuple(sorted(commands, key=lambda command: command.name)),
        diagnostics=tuple(diagnostics),
    )
