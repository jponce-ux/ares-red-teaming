"""Deterministic context resolution and sensitive-state sanitization utilities."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from enum import StrEnum

REDACTED_VALUE = "***REDACTED***"

_SENSITIVE_EXACT_KEYS = {
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "client_secret",
    "command_args",
    "credential",
    "credentials",
    "conversation_text",
    "input_text",
    "password",
    "private_key",
    "raw_input",
    "refresh_token",
    "request_text",
    "response_text",
    "secret",
    "target_policy_content",
    "token",
    "user_input",
}

_SENSITIVE_SUFFIXES = (
    "_api_key",
    "_key",
    "_password",
    "_secret",
    "_token",
)


class ContextLayer(StrEnum):
    """Canonical context layers in strict precedence order."""

    EXPLICIT_INPUT = "explicit_input"
    COMMAND_INPUTS = "command_inputs"
    SESSION = "session"
    PROJECT = "project"
    ENVIRONMENT = "environment"
    DEFAULTS = "defaults"


CONTEXT_PRECEDENCE_ORDER: tuple[ContextLayer, ...] = (
    ContextLayer.EXPLICIT_INPUT,
    ContextLayer.COMMAND_INPUTS,
    ContextLayer.SESSION,
    ContextLayer.PROJECT,
    ContextLayer.ENVIRONMENT,
    ContextLayer.DEFAULTS,
)


def _normalized_key(key: str) -> str:
    return key.strip().lower()


def is_sensitive_key(key: str) -> bool:
    """Return whether a key should be treated as sensitive."""
    normalized = _normalized_key(key)
    if normalized in _SENSITIVE_EXACT_KEYS:
        return True
    return any(normalized.endswith(suffix) for suffix in _SENSITIVE_SUFFIXES)


def resolve_context_layers(
    *,
    explicit_input: Mapping[str, object] | None = None,
    command_inputs: Mapping[str, object] | None = None,
    session: Mapping[str, object] | None = None,
    project: Mapping[str, object] | None = None,
    environment: Mapping[str, object] | None = None,
    defaults: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Resolve context values with strict deterministic precedence semantics."""
    resolved: dict[str, object] = {}
    layers = (
        defaults,
        environment,
        project,
        session,
        command_inputs,
        explicit_input,
    )
    for layer in layers:
        if layer is None:
            continue
        for key in sorted(layer):
            resolved[key] = deepcopy(layer[key])
    return resolved


def _sanitize_value(value: object, *, redact: bool) -> object:
    if isinstance(value, Mapping):
        sanitized: dict[str, object] = {}
        for key in sorted(value):
            normalized_key = str(key)
            item_value = value[key]
            if is_sensitive_key(normalized_key):
                if redact:
                    sanitized[normalized_key] = REDACTED_VALUE
                continue
            sanitized[normalized_key] = _sanitize_value(item_value, redact=redact)
        return sanitized

    if isinstance(value, Sequence) and not isinstance(value, str):
        return [_sanitize_value(item, redact=redact) for item in value]

    return deepcopy(value)


def sanitize_for_persistence(payload: Mapping[str, object]) -> dict[str, object]:
    """Exclude sensitive keys from durable payloads."""
    sanitized = _sanitize_value(payload, redact=False)
    assert isinstance(sanitized, dict)
    return sanitized


def sanitize_for_telemetry(payload: Mapping[str, object]) -> dict[str, object]:
    """Redact sensitive keys while preserving telemetry payload structure."""
    sanitized = _sanitize_value(payload, redact=True)
    assert isinstance(sanitized, dict)
    return sanitized


def build_safe_session_snapshot(state: Mapping[str, object]) -> dict[str, object]:
    """Build a safe-by-default session snapshot that excludes sensitive values."""
    return sanitize_for_persistence(state)


def build_safe_telemetry_payload(payload: Mapping[str, object]) -> dict[str, object]:
    """Build a telemetry-safe payload that keeps shape and correlation metadata."""
    return sanitize_for_telemetry(payload)
