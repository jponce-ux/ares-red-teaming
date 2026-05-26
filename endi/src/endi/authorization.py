"""Deterministic capability authorization model for runtime execution paths."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum


class AuthorizationSurface(StrEnum):
    """Execution surface requesting authorization."""

    COMMAND = "command"
    WORKFLOW = "workflow"
    TOOL = "tool"


@dataclass(frozen=True)
class AuthorizationDecision:
    """Stable authorization decision envelope."""

    allowed: bool
    granted_capabilities: tuple[str, ...]
    required_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]


def _normalize_capabilities(capabilities: Iterable[str] | None) -> tuple[str, ...]:
    if capabilities is None:
        return ()

    normalized = {
        value.strip()
        for value in capabilities
        if isinstance(value, str) and value.strip()
    }
    return tuple(sorted(normalized))


def evaluate_capabilities(
    *,
    required_capabilities: Iterable[str] | None,
    granted_capabilities: Iterable[str] | None,
) -> AuthorizationDecision:
    """Evaluate required capabilities against granted capabilities deterministically."""
    required = _normalize_capabilities(required_capabilities)
    granted = _normalize_capabilities(granted_capabilities)

    if not required:
        return AuthorizationDecision(
            allowed=True,
            granted_capabilities=granted,
            required_capabilities=required,
            missing_capabilities=(),
        )

    missing = tuple(cap for cap in required if cap not in granted)
    return AuthorizationDecision(
        allowed=not missing,
        granted_capabilities=granted,
        required_capabilities=required,
        missing_capabilities=missing,
    )


def authorization_metadata(
    *,
    decision: AuthorizationDecision,
    surface: AuthorizationSurface,
    operation: str,
) -> dict[str, object]:
    """Build structured authorization metadata for telemetry and error details."""
    return {
        "surface": surface.value,
        "operation": operation,
        "allowed": decision.allowed,
        "required_capabilities": list(decision.required_capabilities),
        "missing_capabilities": list(decision.missing_capabilities),
    }
