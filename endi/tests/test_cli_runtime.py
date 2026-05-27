"""Tests for ENDI CLI runtime controls."""

import json

import pytest
from typer.testing import CliRunner

from endi import cli
from endi.cli import app


@pytest.fixture(autouse=True)
def isolated_endi_config(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("ENDI_CONFIG_PATH", str(tmp_path / "config.json"))


class FakeProvider:
    def generate_reply(self, messages, *, context=None):
        del context
        return {
            "response_text": f"fake: {messages[0]['content']}",
            "provider": "fake",
        }


class RaisingProvider:
    def __init__(self, code: str) -> None:
        self._code = code

    def generate_reply(self, messages, *, context=None):
        del messages, context
        from endi.providers import ProviderAdapterError

        raise ProviderAdapterError(self._code, f"simulated {self._code}")


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


def test_chat_json_uses_ollama_provider_options(monkeypatch) -> None:
    observed = {}

    def fake_build_chat_provider(config):
        observed["identifier"] = config.identifier
        observed["model"] = config.model
        observed["base_url"] = config.base_url
        observed["timeout_seconds"] = config.timeout_seconds
        return FakeProvider()

    monkeypatch.setattr(cli, "build_chat_provider", fake_build_chat_provider)
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "chat",
            "hello",
            "--provider",
            "ollama",
            "--model",
            "llama3.2",
            "--output",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["route"] == "conversation"
    assert payload["output"] == "fake: hello"
    assert observed == {
        "identifier": "ollama:llama3.2",
        "model": "llama3.2",
        "base_url": "http://localhost:11434",
        "timeout_seconds": 30.0,
    }


def test_submit_remains_compatible_with_ollama_provider(monkeypatch) -> None:
    observed = {}

    def fake_build_chat_provider(config):
        observed["identifier"] = config.identifier
        observed["model"] = config.model
        return FakeProvider()

    monkeypatch.setattr(cli, "build_chat_provider", fake_build_chat_provider)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["submit", "hello", "--provider", "ollama", "--model", "mistral", "--output", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["output"] == "fake: hello"
    assert observed == {"identifier": "ollama:mistral", "model": "mistral"}


def test_chat_json_preserves_ollama_provider_error_code(monkeypatch) -> None:
    monkeypatch.setattr(
        cli,
        "build_chat_provider",
        lambda config: RaisingProvider("provider_missing_model"),
    )
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "chat",
            "hello",
            "--provider",
            "ollama",
            "--model",
            "missing",
            "--output",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "Provider error (provider_missing_model)" in payload["output"]


def test_chat_json_success_contract_for_ollama(monkeypatch) -> None:
    observed = {}

    def fake_build_chat_provider(config):
        observed["identifier"] = config.identifier
        observed["model"] = config.model
        observed["base_url"] = config.base_url
        observed["timeout_seconds"] = config.timeout_seconds
        return FakeProvider()

    monkeypatch.setattr(cli, "build_chat_provider", fake_build_chat_provider)
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "chat",
            "hello",
            "--provider",
            "ollama",
            "--model",
            "mistral",
            "--base-url",
            "http://127.0.0.1:11434",
            "--timeout-seconds",
            "1.5",
            "--output",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["route"] == "conversation"
    assert payload["output"] == "fake: hello"
    assert observed == {
        "identifier": "ollama:mistral",
        "model": "mistral",
        "base_url": "http://127.0.0.1:11434",
        "timeout_seconds": 1.5,
    }


def test_chat_provider_selection_is_remembered_for_later_submit(monkeypatch) -> None:
    observed: list[dict[str, object]] = []

    def fake_build_chat_provider(config):
        observed.append(
            {
                "identifier": config.identifier,
                "model": config.model,
                "base_url": config.base_url,
            }
        )
        return FakeProvider()

    monkeypatch.setattr(cli, "build_chat_provider", fake_build_chat_provider)
    runner = CliRunner()

    chat_result = runner.invoke(
        app,
        [
            "chat",
            "Hello",
            "--provider",
            "ollama",
            "--model",
            "granite4.1:3b",
            "--output",
            "json",
        ],
    )
    submit_result = runner.invoke(app, ["submit", "test", "--output", "json"])

    assert chat_result.exit_code == 0
    assert submit_result.exit_code == 0
    assert observed == [
        {
            "identifier": "ollama:granite4.1:3b",
            "model": "granite4.1:3b",
            "base_url": "http://localhost:11434",
        },
        {
            "identifier": "ollama:granite4.1:3b",
            "model": "granite4.1:3b",
            "base_url": "http://localhost:11434",
        },
    ]


def test_remembered_provider_timeout_is_actionable(monkeypatch) -> None:
    monkeypatch.setattr(
        cli,
        "build_chat_provider",
        lambda config: RaisingProvider("timeout"),
    )
    runner = CliRunner()

    remember_result = runner.invoke(
        app,
        [
            "chat",
            "Hello",
            "--provider",
            "ollama",
            "--model",
            "granite4.1:3b",
            "--timeout-seconds",
            "45",
            "--output",
            "json",
        ],
    )
    submit_result = runner.invoke(app, ["submit", "test", "--output", "json"])

    assert remember_result.exit_code == 0
    assert submit_result.exit_code == 0
    payload = json.loads(submit_result.stdout)
    assert payload["output"] == (
        "Remembered provider ollama:granite4.1:3b model granite4.1:3b timed out "
        "after 45s. The provider is set, but the local model did not respond in time. "
        "Try again, warm the model with `ollama run`, or set `--timeout-seconds 120`."
    )
