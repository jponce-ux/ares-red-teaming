"""Tests for manifest-only plugin discovery."""

import json

from endi.plugins import discover_plugin_commands


def test_discover_plugin_commands_loads_valid_manifest(tmp_path) -> None:
    manifest = {
        "name": "demo",
        "version": "0.1.0",
        "commands": [
            {
                "name": "demo-command",
                "description": "Run demo command.",
                "arg_schema": "[value]",
                "examples": ["/demo-command"],
                "execution_target": "plugin",
            }
        ],
    }
    (tmp_path / "demo.json").write_text(json.dumps(manifest), encoding="utf-8")

    result = discover_plugin_commands(str(tmp_path))

    assert result.diagnostics == ()
    assert [command.name for command in result.commands] == ["demo-command"]


def test_discover_plugin_commands_reports_invalid_manifest(tmp_path) -> None:
    (tmp_path / "bad.json").write_text(json.dumps({"commands": [{}]}), encoding="utf-8")

    result = discover_plugin_commands(str(tmp_path))

    assert result.commands == ()
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].code == "invalid_plugin_manifest"
