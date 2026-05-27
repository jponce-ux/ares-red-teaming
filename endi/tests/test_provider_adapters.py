"""Tests for concrete chat provider adapters."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError

import pytest

from endi import providers
from endi.providers import (
    AnthropicChatProvider,
    OllamaChatProvider,
    OpenAIChatProvider,
    ProviderAdapterError,
    build_chat_provider,
    extract_chat_response_text,
    resolve_chat_provider_config,
)


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


class FakeRawResponse:
    def __init__(self, raw_body: bytes) -> None:
        self._raw_body = raw_body

    def __enter__(self) -> FakeRawResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._raw_body

    def close(self) -> None:
        return None


def test_openai_chat_provider_extracts_response(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        del request, timeout
        return FakeResponse({"choices": [{"message": {"content": "hello from openai"}}]})

    monkeypatch.setattr(providers, "urlopen", fake_urlopen)
    provider = OpenAIChatProvider(api_key="test-key")

    output = provider.generate_reply([{"role": "user", "content": "hello"}])

    assert extract_chat_response_text(output) == "hello from openai"


def test_anthropic_chat_provider_extracts_response(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        del request, timeout
        return FakeResponse({"content": [{"type": "text", "text": "hello from anthropic"}]})

    monkeypatch.setattr(providers, "urlopen", fake_urlopen)
    provider = AnthropicChatProvider(api_key="test-key")

    output = provider.generate_reply([{"role": "user", "content": "hello"}])

    assert extract_chat_response_text(output) == "hello from anthropic"


def test_ollama_chat_provider_extracts_response(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: dict[str, object] = {}

    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        observed["url"] = request.full_url
        observed["timeout"] = timeout
        observed["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse({"message": {"role": "assistant", "content": "hello local"}})

    monkeypatch.setattr(providers, "urlopen", fake_urlopen)
    provider = OllamaChatProvider(
        model="mistral",
        base_url="http://127.0.0.1:11434",
        timeout_seconds=2.5,
    )

    output = provider.generate_reply([{"role": "user", "content": "hello"}])

    assert extract_chat_response_text(output) == "hello local"
    assert observed["url"] == "http://127.0.0.1:11434/api/chat"
    assert observed["timeout"] == 2.5
    assert observed["payload"] == {
        "model": "mistral",
        "messages": [{"role": "user", "content": "hello"}],
        "stream": False,
    }


def test_ollama_unqualified_provider_uses_model_and_default_base_url() -> None:
    config = resolve_chat_provider_config(
        {
            "chat_provider": "ollama",
            "chat_model": "gemma4:e2b",
        }
    )

    assert config.identifier == "ollama:gemma4:e2b"
    assert config.model == "gemma4:e2b"
    assert config.base_url == "http://localhost:11434"
    assert isinstance(build_chat_provider(config), OllamaChatProvider)


def test_ollama_connection_failure_is_categorized(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        del request, timeout
        raise URLError("connection refused")

    monkeypatch.setattr(providers, "urlopen", fake_urlopen)
    provider = OllamaChatProvider()

    with pytest.raises(ProviderAdapterError) as exc_info:
        provider.generate_reply([{"role": "user", "content": "hello"}])

    assert exc_info.value.code == "provider_connection_failed"


def test_ollama_missing_model_is_categorized(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        del request, timeout
        raise HTTPError(
            url="http://localhost:11434/api/chat",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=FakeRawResponse(b'{"error":"model \\"missing\\" not found"}'),
        )

    monkeypatch.setattr(providers, "urlopen", fake_urlopen)
    provider = OllamaChatProvider(model="missing")

    with pytest.raises(ProviderAdapterError) as exc_info:
        provider.generate_reply([{"role": "user", "content": "hello"}])

    assert exc_info.value.code == "provider_missing_model"
    assert exc_info.value.details["model"] == "missing"


def test_ollama_timeout_is_categorized(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        del request, timeout
        raise TimeoutError("timed out")

    monkeypatch.setattr(providers, "urlopen", fake_urlopen)
    provider = OllamaChatProvider()

    with pytest.raises(ProviderAdapterError) as exc_info:
        provider.generate_reply([{"role": "user", "content": "hello"}])

    assert exc_info.value.code == "timeout"


def test_ollama_malformed_response_is_categorized(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: Any, timeout: float) -> FakeRawResponse:
        del request, timeout
        return FakeRawResponse(b"not-json")

    monkeypatch.setattr(providers, "urlopen", fake_urlopen)
    provider = OllamaChatProvider()

    with pytest.raises(ProviderAdapterError) as exc_info:
        provider.generate_reply([{"role": "user", "content": "hello"}])

    assert exc_info.value.code == "provider_malformed_response"


def test_ollama_missing_message_content_is_categorized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        del request, timeout
        return FakeResponse({"message": {"role": "assistant"}})

    monkeypatch.setattr(providers, "urlopen", fake_urlopen)
    provider = OllamaChatProvider()

    with pytest.raises(ProviderAdapterError) as exc_info:
        provider.generate_reply([{"role": "user", "content": "hello"}])

    assert exc_info.value.code == "provider_malformed_response"


def test_openai_provider_requires_api_key() -> None:
    provider = OpenAIChatProvider(api_key=None)

    with pytest.raises(ProviderAdapterError) as exc_info:
        provider.generate_reply([{"role": "user", "content": "hello"}])

    assert exc_info.value.code == "missing_credentials"


def test_resolve_chat_provider_config_for_endi_context() -> None:
    config = resolve_chat_provider_config(
        {
            "chat_provider": "ollama:llama3.2",
            "chat_model": "llama3.2:latest",
            "chat_base_url": "http://localhost:11434",
            "provider_local_fallback_enabled": True,
        }
    )

    assert config.identifier == "ollama:llama3.2"
    assert config.model == "llama3.2:latest"
    assert config.local_fallback_enabled is True
    assert isinstance(build_chat_provider(config), OllamaChatProvider)
