"""Tests for concrete chat provider adapters."""

from __future__ import annotations

import json
from typing import Any

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
    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        del request, timeout
        return FakeResponse({"message": {"role": "assistant", "content": "hello local"}})

    monkeypatch.setattr(providers, "urlopen", fake_urlopen)
    provider = OllamaChatProvider()

    output = provider.generate_reply([{"role": "user", "content": "hello"}])

    assert extract_chat_response_text(output) == "hello local"


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
