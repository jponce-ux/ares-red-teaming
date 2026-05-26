"""Tests for capability-split provider contract registration and resolution."""

from endi.providers import (
    ProviderAdapterContract,
    ProviderCapability,
    ProviderRegistry,
    ProviderStatus,
    ProviderStatusCode,
    evaluate_local_fallback_policy,
    provider_routing_metadata,
)


class FakeChatProvider:
    def generate_reply(self, messages, *, context=None):
        del context
        return {"messages": messages}


class FakeEmbeddingProvider:
    def embed_texts(self, texts, *, context=None):
        del context
        return {"count": len(texts)}


class FakeToolCallingProvider:
    def call_tool(self, tool_name, tool_args, *, context=None):
        del context
        return {"tool": tool_name, "arg_count": len(tool_args)}


def test_registry_accepts_valid_contracts_for_each_capability() -> None:
    registry = ProviderRegistry()

    chat_result = registry.register(
        {
            "identifier": "chat-primary",
            "capability": ProviderCapability.CHAT.value,
            "contract_version": 1,
            "provider": FakeChatProvider(),
            "metadata": {"vendor": "acme", "adapter": "chat-v1"},
        }
    )
    embedding_result = registry.register(
        ProviderAdapterContract(
            identifier="embed-primary",
            capability=ProviderCapability.EMBEDDINGS,
            contract_version=1,
            provider=FakeEmbeddingProvider(),
            metadata={"vendor": "acme", "adapter": "embed-v1"},
        )
    )
    tool_result = registry.register(
        {
            "identifier": "tool-primary",
            "capability": ProviderCapability.TOOL_CALLING.value,
            "contract_version": 1,
            "provider": FakeToolCallingProvider(),
            "metadata": {"vendor": "acme", "adapter": "tool-v1"},
        }
    )

    assert chat_result.status is ProviderStatus.SUCCESS
    assert embedding_result.status is ProviderStatus.SUCCESS
    assert tool_result.status is ProviderStatus.SUCCESS
    assert registry.list_providers(ProviderCapability.CHAT) == ["chat-primary"]
    assert registry.list_providers(ProviderCapability.EMBEDDINGS) == ["embed-primary"]
    assert registry.list_providers(ProviderCapability.TOOL_CALLING) == ["tool-primary"]


def test_registry_rejects_malformed_contract_with_stable_details() -> None:
    registry = ProviderRegistry()

    result = registry.register(
        {
            "identifier": "",
            "capability": "chat",
            "contract_version": 0,
            "metadata": {"vendor": "", "adapter": ""},
        }
    )

    assert result.status is ProviderStatus.ERROR
    assert result.status_code is ProviderStatusCode.INVALID_CONTRACT
    assert result.error is not None
    assert result.error.code == "invalid_provider_contract"
    assert result.error.details["missing_fields"] == ["provider"]
    assert result.error.details["invalid_fields"] == [
        "contract_version",
        "identifier",
        "metadata.adapter",
        "metadata.vendor",
    ]


def test_registry_rejects_capability_contract_mismatch() -> None:
    registry = ProviderRegistry()

    result = registry.register(
        {
            "identifier": "chat-wrong",
            "capability": ProviderCapability.CHAT.value,
            "contract_version": 1,
            "provider": FakeEmbeddingProvider(),
            "metadata": {"vendor": "acme", "adapter": "bad-chat-v1"},
        }
    )

    assert result.status is ProviderStatus.ERROR
    assert result.status_code is ProviderStatusCode.INVALID_CONTRACT
    assert result.error is not None
    assert result.error.code == "invalid_provider_contract"
    assert result.error.details["capability"] == ProviderCapability.CHAT.value
    assert result.error.details["invalid_fields"] == ["provider"]


def test_registry_rejects_incompatible_contract_version() -> None:
    registry = ProviderRegistry()

    result = registry.register(
        {
            "identifier": "embed-v2",
            "capability": ProviderCapability.EMBEDDINGS.value,
            "contract_version": 2,
            "provider": FakeEmbeddingProvider(),
            "metadata": {"vendor": "acme", "adapter": "embed-v2"},
        }
    )

    assert result.status is ProviderStatus.ERROR
    assert result.status_code is ProviderStatusCode.INCOMPATIBLE_VERSION
    assert result.error is not None
    assert result.error.code == "incompatible_provider_contract_version"
    assert result.error.details == {
        "capability": ProviderCapability.EMBEDDINGS.value,
        "expected_version": 1,
        "actual_version": 2,
    }


def test_registry_resolve_not_found_returns_deterministic_registered_list() -> None:
    registry = ProviderRegistry()
    registry.register(
        {
            "identifier": "chat-z",
            "capability": ProviderCapability.CHAT.value,
            "contract_version": 1,
            "provider": FakeChatProvider(),
            "metadata": {"vendor": "acme", "adapter": "chat-z"},
        }
    )
    registry.register(
        {
            "identifier": "chat-a",
            "capability": ProviderCapability.CHAT.value,
            "contract_version": 1,
            "provider": FakeChatProvider(),
            "metadata": {"vendor": "acme", "adapter": "chat-a"},
        }
    )

    result = registry.resolve_chat_provider("chat-missing")

    assert result.status is ProviderStatus.ERROR
    assert result.status_code is ProviderStatusCode.NOT_FOUND
    assert result.error is not None
    assert result.error.code == "provider_not_found"
    assert result.error.details == {
        "capability": ProviderCapability.CHAT.value,
        "identifier": "chat-missing",
        "registered": ["chat-a", "chat-z"],
    }


def test_invalid_contract_result_is_deterministic_for_equivalent_input() -> None:
    registry = ProviderRegistry()
    bad_contract = {
        "identifier": "",
        "capability": "chat",
        "contract_version": "1",
        "provider": object(),
        "metadata": {"vendor": "", "adapter": ""},
    }

    first = registry.register(dict(bad_contract))
    second = registry.register(dict(bad_contract))

    assert first.status is ProviderStatus.ERROR
    assert second.status is ProviderStatus.ERROR
    assert first.status_code is ProviderStatusCode.INVALID_CONTRACT
    assert second.status_code is ProviderStatusCode.INVALID_CONTRACT
    assert first.error == second.error


def test_registry_rejects_typed_contract_with_invalid_required_metadata() -> None:
    registry = ProviderRegistry()

    result = registry.register(
        ProviderAdapterContract(
            identifier="chat-typed",
            capability=ProviderCapability.CHAT,
            contract_version=1,
            provider=FakeChatProvider(),
            metadata={},
        )
    )

    assert result.status is ProviderStatus.ERROR
    assert result.status_code is ProviderStatusCode.INVALID_CONTRACT
    assert result.error is not None
    assert result.error.code == "invalid_provider_contract"
    assert result.error.details == {
        "missing_fields": [],
        "invalid_fields": ["metadata.adapter", "metadata.vendor"],
        "capability": ProviderCapability.CHAT.value,
    }
    assert registry.list_providers(ProviderCapability.CHAT) == []


def test_provider_routing_metadata_returns_locked_v1_defaults() -> None:
    metadata = provider_routing_metadata()

    defaults = metadata["defaults"]
    assert isinstance(defaults, dict)
    assert defaults == {
        "chat": "openai:gpt-4o-mini",
        "tool-calling": "anthropic:claude-3.7-sonnet",
        "embeddings": "openai:text-embedding-3-large",
    }
    local_fallback = metadata["local_fallback"]
    assert isinstance(local_fallback, dict)
    assert local_fallback == {
        "provider": "ollama",
        "mode": "explicit_only",
        "enabled": False,
    }


def test_provider_routing_metadata_applies_only_vendor_qualified_overrides() -> None:
    metadata = provider_routing_metadata(
        {
            "provider_defaults": {
                "chat": "custom:chat-v2",
                "tool-calling": "bad identifier",
                "embeddings": "  OPENAI:TEXT-EMBEDDING-3-LARGE  ",
            }
        }
    )

    defaults = metadata["defaults"]
    assert isinstance(defaults, dict)
    assert defaults == {
        "chat": "custom:chat-v2",
        "tool-calling": "anthropic:claude-3.7-sonnet",
        "embeddings": "openai:text-embedding-3-large",
    }


def test_local_fallback_policy_blocks_by_default_with_deterministic_error() -> None:
    first = evaluate_local_fallback_policy(
        capability=ProviderCapability.CHAT,
        selected_provider="openai:gpt-4o-mini",
        failure_reason="timeout",
    )
    second = evaluate_local_fallback_policy(
        capability=ProviderCapability.CHAT,
        selected_provider="openai:gpt-4o-mini",
        failure_reason="timeout",
    )

    assert first.status is ProviderStatus.ERROR
    assert first.status_code is ProviderStatusCode.INVALID_CONTRACT
    assert first.error is not None
    assert first.error.code == "provider_fallback_blocked"
    assert first.error.details == {
        "decision": "fallback_blocked",
        "capability": "chat",
        "selected_provider": "openai:gpt-4o-mini",
        "fallback_provider": "ollama",
        "fallback_mode": "explicit_only",
        "fallback_enabled": False,
        "reason": "timeout",
    }
    assert first.error == second.error


def test_local_fallback_policy_blocks_missing_credentials_and_provider_failure_by_default() -> None:
    for reason in ("missing_credentials", "provider_failure"):
        result = evaluate_local_fallback_policy(
            capability=ProviderCapability.CHAT,
            selected_provider="openai:gpt-4o-mini",
            failure_reason=reason,
        )

        assert result.status is ProviderStatus.ERROR
        assert result.status_code is ProviderStatusCode.INVALID_CONTRACT
        assert result.error is not None
        assert result.error.code == "provider_fallback_blocked"
        assert result.error.details == {
            "decision": "fallback_blocked",
            "capability": "chat",
            "selected_provider": "openai:gpt-4o-mini",
            "fallback_provider": "ollama",
            "fallback_mode": "explicit_only",
            "fallback_enabled": False,
            "reason": reason,
        }


def test_local_fallback_policy_allows_only_when_explicitly_enabled() -> None:
    result = evaluate_local_fallback_policy(
        capability=ProviderCapability.TOOL_CALLING,
        selected_provider="anthropic:claude-3.7-sonnet",
        failure_reason="missing_credentials",
        context={"provider_local_fallback": {"enabled": True}},
    )

    assert result.status is ProviderStatus.SUCCESS
    assert result.status_code is ProviderStatusCode.OK
    assert result.error is None
    assert result.provider_name == "ollama"
    assert result.capability is ProviderCapability.TOOL_CALLING
    assert result.payload == {
        "decision": "fallback_allowed",
        "provider": "ollama",
        "capability": "tool-calling",
        "selected_provider": "anthropic:claude-3.7-sonnet",
        "fallback_provider": "ollama",
        "fallback_mode": "explicit_only",
        "fallback_enabled": True,
        "reason": "missing_credentials",
    }
