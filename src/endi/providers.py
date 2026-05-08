"""Capability-split provider contracts with deterministic registration validation."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, runtime_checkable


class ProviderCapability(StrEnum):
    """First-class provider capability contract identifiers."""

    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    TOOL_CALLING = "tool-calling"


class ProviderStatus(StrEnum):
    """Structured provider contract operation status."""

    SUCCESS = "success"
    ERROR = "error"


class ProviderStatusCode(StrEnum):
    """Deterministic provider contract status code values."""

    OK = "ok"
    INVALID_CONTRACT = "invalid_contract"
    INCOMPATIBLE_VERSION = "incompatible_version"
    NOT_FOUND = "not_found"


@dataclass(frozen=True)
class ProviderContractError:
    """Machine-readable provider contract failure envelope."""

    code: str
    message: str
    details: dict[str, object]


@dataclass(frozen=True)
class ProviderResult:
    """Structured provider registry result envelope."""

    status: ProviderStatus
    status_code: ProviderStatusCode
    payload: object | None
    error: ProviderContractError | None
    provider_name: str | None
    capability: ProviderCapability | None


@runtime_checkable
class ChatProvider(Protocol):
    """Chat capability provider contract."""

    def generate_reply(
        self,
        messages: list[dict[str, object]],
        *,
        context: Mapping[str, object] | None = None,
    ) -> object:
        """Generate a chat response from ordered message inputs."""


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Embedding capability provider contract."""

    def embed_texts(
        self,
        texts: list[str],
        *,
        context: Mapping[str, object] | None = None,
    ) -> object:
        """Generate embedding vectors for text inputs."""


@runtime_checkable
class ToolCallingProvider(Protocol):
    """Tool-calling capability provider contract."""

    def call_tool(
        self,
        tool_name: str,
        tool_args: Mapping[str, object],
        *,
        context: Mapping[str, object] | None = None,
    ) -> object:
        """Execute a tool call through provider-mediated semantics."""


@dataclass(frozen=True)
class ProviderAdapterContract:
    """Provider adapter registration contract."""

    identifier: str
    capability: ProviderCapability
    contract_version: int
    provider: object
    metadata: dict[str, object] = field(default_factory=dict)


_SUPPORTED_CONTRACT_VERSIONS: dict[ProviderCapability, int] = {
    ProviderCapability.CHAT: 1,
    ProviderCapability.EMBEDDINGS: 1,
    ProviderCapability.TOOL_CALLING: 1,
}

_REQUIRED_METADATA_FIELDS = ("vendor", "adapter")
_PROVIDER_IDENTIFIER_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9_-]*:[a-z0-9][a-z0-9._-]*$"
)
_DEFAULT_PROVIDER_SELECTIONS: dict[ProviderCapability, str] = {
    ProviderCapability.CHAT: "openai:gpt-4o-mini",
    ProviderCapability.TOOL_CALLING: "anthropic:claude-3.7-sonnet",
    ProviderCapability.EMBEDDINGS: "openai:text-embedding-3-large",
}
_LOCAL_FALLBACK_PROVIDER = "ollama"
_LOCAL_FALLBACK_MODE = "explicit_only"
_LOCAL_FALLBACK_REASON_VALUES = frozenset(
    {"missing_credentials", "provider_failure", "timeout"}
)


def _parse_capability(value: object) -> ProviderCapability | None:
    if isinstance(value, ProviderCapability):
        return value
    if not isinstance(value, str):
        return None

    normalized = value.strip().lower()
    if normalized == ProviderCapability.CHAT.value:
        return ProviderCapability.CHAT
    if normalized == ProviderCapability.EMBEDDINGS.value:
        return ProviderCapability.EMBEDDINGS
    if normalized == ProviderCapability.TOOL_CALLING.value:
        return ProviderCapability.TOOL_CALLING
    return None


def _is_vendor_qualified_identifier(value: str) -> bool:
    return bool(_PROVIDER_IDENTIFIER_PATTERN.fullmatch(value.strip().lower()))


def _resolve_provider_override(
    *,
    capability: ProviderCapability,
    context: Mapping[str, object] | None,
) -> str:
    default_identifier = _DEFAULT_PROVIDER_SELECTIONS[capability]
    if context is None:
        return default_identifier

    provider_defaults = context.get("provider_defaults")
    if not isinstance(provider_defaults, Mapping):
        return default_identifier

    override_value = provider_defaults.get(capability.value)
    if not isinstance(override_value, str):
        return default_identifier

    normalized = override_value.strip().lower()
    if not _is_vendor_qualified_identifier(normalized):
        return default_identifier
    return normalized


def _resolve_local_fallback_enabled(context: Mapping[str, object] | None) -> bool:
    if context is None:
        return False

    explicit_enabled = context.get("provider_local_fallback_enabled")
    if isinstance(explicit_enabled, bool):
        return explicit_enabled

    fallback_config = context.get("provider_local_fallback")
    if isinstance(fallback_config, Mapping):
        nested_enabled = fallback_config.get("enabled")
        if isinstance(nested_enabled, bool):
            return nested_enabled

    return False


def provider_routing_metadata(
    context: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Resolve deterministic provider routing metadata with locked v1 defaults."""
    defaults = {
        ProviderCapability.CHAT.value: _resolve_provider_override(
            capability=ProviderCapability.CHAT,
            context=context,
        ),
        ProviderCapability.TOOL_CALLING.value: _resolve_provider_override(
            capability=ProviderCapability.TOOL_CALLING,
            context=context,
        ),
        ProviderCapability.EMBEDDINGS.value: _resolve_provider_override(
            capability=ProviderCapability.EMBEDDINGS,
            context=context,
        ),
    }
    local_fallback_enabled = _resolve_local_fallback_enabled(context)
    return {
        "defaults": defaults,
        "local_fallback": {
            "provider": _LOCAL_FALLBACK_PROVIDER,
            "mode": _LOCAL_FALLBACK_MODE,
            "enabled": local_fallback_enabled,
        },
    }


def evaluate_local_fallback_policy(
    *,
    capability: ProviderCapability,
    selected_provider: str,
    failure_reason: str,
    context: Mapping[str, object] | None = None,
) -> ProviderResult:
    """Evaluate explicit-only local fallback policy with deterministic outcomes."""
    routing = provider_routing_metadata(context)
    local_fallback = routing["local_fallback"]
    assert isinstance(local_fallback, dict)

    fallback_provider = local_fallback["provider"]
    assert isinstance(fallback_provider, str)

    fallback_mode = local_fallback["mode"]
    assert isinstance(fallback_mode, str)

    fallback_enabled = local_fallback["enabled"]
    assert isinstance(fallback_enabled, bool)

    normalized_reason = (
        failure_reason
        if failure_reason in _LOCAL_FALLBACK_REASON_VALUES
        else "provider_failure"
    )

    details: dict[str, object] = {
        "capability": capability.value,
        "selected_provider": selected_provider,
        "fallback_provider": fallback_provider,
        "fallback_mode": fallback_mode,
        "fallback_enabled": fallback_enabled,
        "reason": normalized_reason,
    }

    if fallback_enabled:
        return ProviderResult(
            status=ProviderStatus.SUCCESS,
            status_code=ProviderStatusCode.OK,
            payload={
                "decision": "fallback_allowed",
                "provider": fallback_provider,
                **details,
            },
            error=None,
            provider_name=fallback_provider,
            capability=capability,
        )

    return ProviderResult(
        status=ProviderStatus.ERROR,
        status_code=ProviderStatusCode.INVALID_CONTRACT,
        payload=None,
        error=ProviderContractError(
            code="provider_fallback_blocked",
            message="Local fallback is disabled unless explicitly enabled.",
            details={
                "decision": "fallback_blocked",
                **details,
            },
        ),
        provider_name=selected_provider,
        capability=capability,
    )


def _validate_metadata(
    metadata: object,
    *,
    invalid_fields: list[str],
) -> dict[str, object] | None:
    if not isinstance(metadata, dict):
        invalid_fields.append("metadata")
        return None

    normalized_metadata = dict(metadata)
    for field_name in _REQUIRED_METADATA_FIELDS:
        field_value = normalized_metadata.get(field_name)
        if not isinstance(field_value, str) or not field_value.strip():
            invalid_fields.append(f"metadata.{field_name}")

    return normalized_metadata


def _normalize_contract_mapping(
    contract: Mapping[str, object],
) -> tuple[ProviderAdapterContract | None, list[str], list[str]]:
    missing_fields: list[str] = []
    invalid_fields: list[str] = []

    identifier = contract.get("identifier")
    capability = _parse_capability(contract.get("capability"))
    contract_version = contract.get("contract_version")
    provider = contract.get("provider")
    metadata = contract.get("metadata")

    if provider is None:
        missing_fields.append("provider")

    if not isinstance(identifier, str) or not identifier:
        invalid_fields.append("identifier")

    if capability is None:
        invalid_fields.append("capability")

    if type(contract_version) is not int or contract_version < 1:
        invalid_fields.append("contract_version")

    normalized_metadata = _validate_metadata(metadata, invalid_fields=invalid_fields)

    if (
        missing_fields
        or invalid_fields
        or capability is None
        or not isinstance(identifier, str)
        or type(contract_version) is not int
    ):
        return None, sorted(set(missing_fields)), sorted(set(invalid_fields))

    assert provider is not None
    return (
        ProviderAdapterContract(
            identifier=identifier,
            capability=capability,
            contract_version=contract_version,
            provider=provider,
            metadata=normalized_metadata if normalized_metadata is not None else {},
        ),
        [],
        [],
    )


def _provider_matches_capability(provider: object, capability: ProviderCapability) -> bool:
    if capability is ProviderCapability.CHAT:
        return isinstance(provider, ChatProvider)
    if capability is ProviderCapability.EMBEDDINGS:
        return isinstance(provider, EmbeddingProvider)
    return isinstance(provider, ToolCallingProvider)


def _invalid_contract_result(
    *,
    missing_fields: list[str],
    invalid_fields: list[str],
    capability: ProviderCapability | None,
    provider_name: str | None,
    message: str,
) -> ProviderResult:
    return ProviderResult(
        status=ProviderStatus.ERROR,
        status_code=ProviderStatusCode.INVALID_CONTRACT,
        payload=None,
        error=ProviderContractError(
            code="invalid_provider_contract",
            message=message,
            details={
                "missing_fields": sorted(set(missing_fields)),
                "invalid_fields": sorted(set(invalid_fields)),
                "capability": capability.value if capability is not None else None,
            },
        ),
        provider_name=provider_name,
        capability=capability,
    )


class ProviderRegistry:
    """Registry with deterministic provider contract and compatibility validation."""

    def __init__(self) -> None:
        self._contracts: dict[ProviderCapability, dict[str, ProviderAdapterContract]] = {
            ProviderCapability.CHAT: {},
            ProviderCapability.EMBEDDINGS: {},
            ProviderCapability.TOOL_CALLING: {},
        }

    def register(
        self,
        contract: ProviderAdapterContract | Mapping[str, object],
    ) -> ProviderResult:
        missing_fields: list[str] = []
        invalid_fields: list[str] = []
        normalized: ProviderAdapterContract | None
        capability: ProviderCapability | None = None
        provider_name: str | None = None

        if isinstance(contract, ProviderAdapterContract):
            normalized = contract
            metadata = _validate_metadata(contract.metadata, invalid_fields=invalid_fields)
            if metadata is None:
                normalized = ProviderAdapterContract(
                    identifier=contract.identifier,
                    capability=contract.capability,
                    contract_version=contract.contract_version,
                    provider=contract.provider,
                    metadata={},
                )
            else:
                normalized = ProviderAdapterContract(
                    identifier=contract.identifier,
                    capability=contract.capability,
                    contract_version=contract.contract_version,
                    provider=contract.provider,
                    metadata=metadata,
                )
            if not normalized.identifier:
                invalid_fields.append("identifier")
            if type(normalized.contract_version) is not int or normalized.contract_version < 1:
                invalid_fields.append("contract_version")
            provider_name = (
                normalized.identifier if isinstance(normalized.identifier, str) else None
            )
            capability = (
                normalized.capability
                if isinstance(normalized.capability, ProviderCapability)
                else _parse_capability(normalized.capability)
            )
        else:
            normalized, missing_fields, invalid_fields = _normalize_contract_mapping(contract)
            if normalized is None:
                identifier_value = contract.get("identifier")
                return _invalid_contract_result(
                    missing_fields=missing_fields,
                    invalid_fields=invalid_fields,
                    capability=_parse_capability(contract.get("capability")),
                    provider_name=(
                        identifier_value
                        if isinstance(identifier_value, str) and identifier_value
                        else None
                    ),
                    message="Provider contract is malformed.",
                )

            provider_name = normalized.identifier if normalized.identifier else None
            capability = normalized.capability

        if missing_fields or invalid_fields:
            return _invalid_contract_result(
                missing_fields=missing_fields,
                invalid_fields=invalid_fields,
                capability=capability,
                provider_name=provider_name,
                message="Provider contract validation failed.",
            )

        if normalized is None:
            return _invalid_contract_result(
                missing_fields=missing_fields,
                invalid_fields=invalid_fields,
                capability=capability,
                provider_name=provider_name,
                message="Provider contract validation failed.",
            )

        capability = normalized.capability

        if not _provider_matches_capability(normalized.provider, capability):
            return ProviderResult(
                status=ProviderStatus.ERROR,
                status_code=ProviderStatusCode.INVALID_CONTRACT,
                payload=None,
                error=ProviderContractError(
                    code="invalid_provider_contract",
                    message="Provider does not implement required capability contract.",
                    details={
                        "missing_fields": sorted(set(missing_fields)),
                        "invalid_fields": sorted(set(invalid_fields + ["provider"])),
                        "capability": capability.value,
                    },
                ),
                provider_name=normalized.identifier or None,
                capability=capability,
            )

        expected_version = _SUPPORTED_CONTRACT_VERSIONS[capability]
        if normalized.contract_version != expected_version:
            return ProviderResult(
                status=ProviderStatus.ERROR,
                status_code=ProviderStatusCode.INCOMPATIBLE_VERSION,
                payload=None,
                error=ProviderContractError(
                    code="incompatible_provider_contract_version",
                    message="Provider contract version is incompatible.",
                    details={
                        "capability": capability.value,
                        "expected_version": expected_version,
                        "actual_version": normalized.contract_version,
                    },
                ),
                provider_name=normalized.identifier,
                capability=capability,
            )

        self._contracts[capability][normalized.identifier] = normalized
        return ProviderResult(
            status=ProviderStatus.SUCCESS,
            status_code=ProviderStatusCode.OK,
            payload={
                "identifier": normalized.identifier,
                "capability": capability.value,
                "contract_version": normalized.contract_version,
            },
            error=None,
            provider_name=normalized.identifier,
            capability=capability,
        )

    def list_providers(self, capability: ProviderCapability) -> list[str]:
        """List provider identifiers for one capability in deterministic order."""
        return sorted(self._contracts[capability])

    def resolve_provider(
        self,
        *,
        capability: ProviderCapability,
        identifier: str,
    ) -> ProviderResult:
        contract = self._contracts[capability].get(identifier)
        if contract is None:
            return ProviderResult(
                status=ProviderStatus.ERROR,
                status_code=ProviderStatusCode.NOT_FOUND,
                payload=None,
                error=ProviderContractError(
                    code="provider_not_found",
                    message="Provider is not registered for requested capability.",
                    details={
                        "capability": capability.value,
                        "identifier": identifier,
                        "registered": self.list_providers(capability),
                    },
                ),
                provider_name=identifier,
                capability=capability,
            )

        return ProviderResult(
            status=ProviderStatus.SUCCESS,
            status_code=ProviderStatusCode.OK,
            payload=contract.provider,
            error=None,
            provider_name=identifier,
            capability=capability,
        )

    def resolve_chat_provider(self, identifier: str) -> ProviderResult:
        """Resolve a chat capability provider by identifier."""
        return self.resolve_provider(capability=ProviderCapability.CHAT, identifier=identifier)

    def resolve_embedding_provider(self, identifier: str) -> ProviderResult:
        """Resolve an embedding capability provider by identifier."""
        return self.resolve_provider(
            capability=ProviderCapability.EMBEDDINGS,
            identifier=identifier,
        )

    def resolve_tool_calling_provider(self, identifier: str) -> ProviderResult:
        """Resolve a tool-calling capability provider by identifier."""
        return self.resolve_provider(
            capability=ProviderCapability.TOOL_CALLING,
            identifier=identifier,
        )
