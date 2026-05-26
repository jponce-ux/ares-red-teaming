"""Tests for ENDI CLI runtime controls."""

import json

from typer.testing import CliRunner

from endi import cli
from endi.cli import app


class FakeProvider:
    def generate_reply(self, messages, *, context=None):
        del context
        return {
            "response_text": f"fake: {messages[0]['content']}",
            "provider": "fake",
        }


def test_submit_json_uses_provider_backed_conversation(monkeypatch) -> None:
    monkeypatch.setattr(cli, "build_chat_provider", lambda config: FakeProvider())
    runner = CliRunner()

    result = runner.invoke(app, ["submit", "hello", "--output", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["route"] == "conversation"
    assert payload["output"] == "fake: hello"
    assert payload["output"] != "[conversation] hello"


def test_submit_help_includes_plugin_command(tmp_path) -> None:
    manifest = {
        "commands": [
            {
                "name": "plugin-status",
                "description": "Show plugin status.",
                "arg_schema": "",
                "examples": ["/plugin-status"],
                "execution_target": "plugin",
            }
        ]
    }
    (tmp_path / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
    runner = CliRunner()

    result = runner.invoke(app, ["submit", "/help", "--plugin-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "plugin-status" in result.stdout


def test_submit_writes_json_log(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(cli, "build_chat_provider", lambda config: FakeProvider())
    log_path = tmp_path / "endi.jsonl"
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["submit", "hello", "--output", "json", "--log-json", str(log_path)],
    )

    assert result.exit_code == 0
    log_payload = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert log_payload["route"] == "conversation"
    assert log_payload["status"] == "success"
