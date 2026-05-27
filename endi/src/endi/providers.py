"""Capability-split provider contracts with deterministic registration validation."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, runtime_checkable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


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


class ProviderAdapterError(RuntimeError):
    """Structured failure raised by concrete provider adapters."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = dict(details or {})


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


@dataclass(frozen=True)
class ChatProviderConfig:
    """Runtime chat provider selection and connection settings."""

    identifier: str
    model: str
    base_url: str | None = None
    api_key_env: str | None = None
    timeout_seconds: float = 30.0
    local_fallback_enabled: bool = False


def _message_content(message: Mapping[str, object]) -> str:
    content = message.get("content")
    return content if isinstance(content, str) else ""


def _json_http_post(
    url: str,
    payload: Mapping[str, object],
    *,
    headers: Mapping[str, str] | None = None,
    timeout_seconds: float = 30.0,
) -> dict[str, object]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            **dict(headers or {}),
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw_body = response.read().decode("utf-8")
    except HTTPError as exc:
        error_body = _read_http_error_body(exc)
        error_code = _http_provider_error_code(exc, error_body)
        raise ProviderAdapterError(
            error_code,
            _http_provider_error_message(exc, error_code, error_body),
            details={
                "status_code": exc.code,
                "url": url,
                **_http_provider_error_details(error_code, error_body),
            },
        ) from exc
    except TimeoutError as exc:
        raise ProviderAdapterError(
            "timeout",
            "Provider request timed out.",
            details={"url": url},
        ) from exc
    except URLError as exc:
        raise ProviderAdapterError(
            "provider_connection_failed",
            "Provider request failed.",
            details={"url": url, "reason": str(exc.reason)},
        ) from exc

    try:
        decoded = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise ProviderAdapterError(
            "provider_malformed_response",
            "Provider returned malformed JSON.",
            details={"url": url},
        ) from exc
    if not isinstance(decoded, dict):
        raise ProviderAdapterError(
            "provider_malformed_response",
            "Provider JSON response must be an object.",
            details={"url": url},
        )
    return decoded


def _read_http_error_body(exc: HTTPError) -> dict[str, object]:
    try:
        raw_body = exc.read().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return {}
    try:
        decoded = json.loads(raw_body)
    except json.JSONDecodeError:
        return {"error": raw_body}
    return decoded if isinstance(decoded, dict) else {}


def _http_provider_error_code(exc: HTTPError, body: Mapping[str, object]) -> str:
    error = body.get("error")
    normalized_error = error.lower() if isinstance(error, str) else ""
    if exc.code == 404 and "model" in normalized_error and "not found" in normalized_error:
        return "provider_missing_model"
    return "provider_failure"


def _http_provider_error_message(
    exc: HTTPError,
    error_code: str,
    body: Mapping[str, object],
) -> str:
    error = body.get("error")
    if error_code == "provider_missing_model" and isinstance(error, str) and error:
        return error
    return f"Provider returned HTTP {exc.code}."


def _http_provider_error_details(
    error_code: str,
    body: Mapping[str, object],
) -> dict[str, object]:
    if error_code != "provider_missing_model":
        return {}
    error = body.get("error")
    details: dict[str, object] = {}
    if isinstance(error, str) and error:
        details["provider_error"] = error
        match = re.search(r'model\s+"?([^"\s]+)"?\s+not found', error, re.IGNORECASE)
        if match is not None:
            details["model"] = match.group(1)
    return details


class OpenAIChatProvider:
    """OpenAI-compatible chat-completions adapter."""

    def __init__(
        self,
        *,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: float = 30.0,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def generate_reply(
        self,
        messages: list[dict[str, object]],
        *,
        context: Mapping[str, object] | None = None,
    ) -> object:
        del context
        if not self._api_key:
            raise ProviderAdapterError(
                "missing_credentials",
                "OPENAI_API_KEY is required for OpenAI chat.",
                details={"provider": "openai"},
            )
        response = _json_http_post(
            f"{self._base_url}/chat/completions",
            {"model": self._model, "messages": messages},
            headers={"authorization": f"Bearer {self._api_key}"},
            timeout_seconds=self._timeout_seconds,
        )
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ProviderAdapterError("provider_failure", "OpenAI response has no choices.")
        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise ProviderAdapterError("provider_failure", "OpenAI choice is malformed.")
        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise ProviderAdapterError("provider_failure", "OpenAI message is malformed.")
        return {
            "provider": "openai",
            "model": self._model,
            "response_text": _message_content(message),
            "raw": response,
        }


class AnthropicChatProvider:
    """Anthropic messages API adapter."""

    def __init__(
        self,
        *,
        model: str = "claude-3.7-sonnet",
        api_key: str | None = None,
        base_url: str = "https://api.anthropic.com/v1",
        timeout_seconds: float = 30.0,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def generate_reply(
        self,
        messages: list[dict[str, object]],
        *,
        context: Mapping[str, object] | None = None,
    ) -> object:
        del context
        if not self._api_key:
            raise ProviderAdapterError(
                "missing_credentials",
                "ANTHROPIC_API_KEY is required for Anthropic chat.",
                details={"provider": "anthropic"},
            )
        response = _json_http_post(
            f"{self._base_url}/messages",
            {"model": self._model, "max_tokens": 1024, "messages": messages},
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
            },
            timeout_seconds=self._timeout_seconds,
        )
        content = response.get("content")
        if not isinstance(content, list) or not content:
            raise ProviderAdapterError("provider_failure", "Anthropic response has no content.")
        first_block = content[0]
        if not isinstance(first_block, dict):
            raise ProviderAdapterError("provider_failure", "Anthropic content is malformed.")
        text = first_block.get("text")
        return {
            "provider": "anthropic",
            "model": self._model,
            "response_text": text if isinstance(text, str) else "",
            "raw": response,
        }


class OllamaChatProvider:
    """Ollama local chat adapter."""

    def __init__(
        self,
        *,
        model: str = "llama3.1",
        base_url: str = "http://localhost:11434",
        timeout_seconds: float = 30.0,
    ) -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def generate_reply(
        self,
        messages: list[dict[str, object]],
        *,
        context: Mapping[str, object] | None = None,
    ) -> object:
        del context
        response = _json_http_post(
            f"{self._base_url}/api/chat",
            {"model": self._model, "messages": messages, "stream": False},
            timeout_seconds=self._timeout_seconds,
        )
        message = response.get("message")
        if not isinstance(message, dict):
            raise ProviderAdapterError(
                "provider_malformed_response",
                "Ollama response message is malformed.",
            )
        content = message.get("content")
        if not isinstance(content, str):
            raise ProviderAdapterError(
                "provider_malformed_response",
                "Ollama response message content is malformed.",
            )
        return {
            "provider": "ollama",
            "model": self._model,
            "response_text": content,
            "raw": response,
        }


_SUPPORTED_CONTRACT_VERSIONS: dict[ProviderCapability, int] = {
    ProviderCapability.CHAT: 1,
    ProviderCapability.EMBEDDINGS: 1,
    ProviderCapability.TOOL_CALLING: 1,
}

_REQUIRED_METADATA_FIELDS = ("vendor", "adapter")
_PROVIDER_IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*:[a-z0-9][a-z0-9._:-]*$")
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


def _is_supported_chat_provider_name(value: str) -> bool:
    return value.strip().lower() in {"anthropic", "ollama", "openai"}


def _vendor_default_model(vendor: str) -> str:
    if vendor == "anthropic":
        return "claude-3.7-sonnet"
    if vendor == "ollama":
        return "llama3.1"
    return "gpt-4o-mini"


def _qualified_chat_identifier(provider: str, model: str | None) -> str | None:
    normalized_provider = provider.strip().lower()
    if _is_vendor_qualified_identifier(normalized_provider):
        return normalized_provider
    if not _is_supported_chat_provider_name(normalized_provider):
        return None
    normalized_model = model.strip() if isinstance(model, str) and model.strip() else None
    return f"{normalized_provider}:{normalized_model or _vendor_default_model(normalized_provider)}"


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
    if _is_vendor_qualified_identifier(normalized):
        return normalized
    if _is_supported_chat_provider_name(normalized):
        return f"{normalized}:{_vendor_default_model(normalized)}"
    return default_identifier


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


def resolve_chat_provider_config(
    context: Mapping[str, object] | None = None,
) -> ChatProviderConfig:
    """Resolve chat provider config from context and environment defaults."""
    provider_identifier = _resolve_provider_override(
        capability=ProviderCapability.CHAT,
        context=context,
    )
    model = provider_identifier.split(":", 1)[1]
    base_url: str | None = None
    api_key_env: str | None = None
    timeout_seconds = 30.0

    if context is not None:
        model_override = context.get("chat_model")
        normalized_model_override = (
            model_override.strip()
            if isinstance(model_override, str) and model_override.strip()
            else None
        )
        provider_override = context.get("chat_provider")
        if isinstance(provider_override, str):
            qualified_identifier = _qualified_chat_identifier(
                provider_override,
                normalized_model_override,
            )
            if qualified_identifier is not None:
                provider_identifier = qualified_identifier
                model = provider_identifier.split(":", 1)[1]

        if normalized_model_override is not None:
            model = normalized_model_override

        base_url_override = context.get("chat_base_url")
        if isinstance(base_url_override, str) and base_url_override.strip():
            base_url = base_url_override.strip()

        api_key_env_override = context.get("chat_api_key_env")
        if isinstance(api_key_env_override, str) and api_key_env_override.strip():
            api_key_env = api_key_env_override.strip()

        timeout_override = context.get("chat_timeout_seconds")
        if isinstance(timeout_override, (int, float)) and timeout_override > 0:
            timeout_seconds = float(timeout_override)

    vendor = provider_identifier.split(":", 1)[0]
    if api_key_env is None:
        if vendor == "anthropic":
            api_key_env = "ANTHROPIC_API_KEY"
        elif vendor == "openai":
            api_key_env = "OPENAI_API_KEY"
    if base_url is None and vendor == "ollama":
        base_url = "http://localhost:11434"

    return ChatProviderConfig(
        identifier=provider_identifier,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        timeout_seconds=timeout_seconds,
        local_fallback_enabled=_resolve_local_fallback_enabled(context),
    )


def build_chat_provider(config: ChatProviderConfig) -> ChatProvider:
    """Build a concrete chat provider for a resolved runtime config."""
    vendor = config.identifier.split(":", 1)[0]
    api_key = os.environ.get(config.api_key_env) if config.api_key_env is not None else None
    if vendor == "anthropic":
        return AnthropicChatProvider(
            model=config.model,
            api_key=api_key,
            base_url=config.base_url or "https://api.anthropic.com/v1",
            timeout_seconds=config.timeout_seconds,
        )
    if vendor == "ollama":
        return OllamaChatProvider(
            model=config.model,
            base_url=config.base_url or "http://localhost:11434",
            timeout_seconds=config.timeout_seconds,
        )
    return OpenAIChatProvider(
        model=config.model,
        api_key=api_key,
        base_url=config.base_url or "https://api.openai.com/v1",
        timeout_seconds=config.timeout_seconds,
    )


def extract_chat_response_text(provider_output: object) -> str:
    """Extract response text from provider output using the ENDI adapter convention."""
    if isinstance(provider_output, str):
        return provider_output
    if isinstance(provider_output, Mapping):
        response_text = provider_output.get("response_text")
        if isinstance(response_text, str):
            return response_text
    return str(provider_output)


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
