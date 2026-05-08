"""Tests for deterministic capability authorization decisions."""

from endi.authorization import (
    AuthorizationSurface,
    authorization_metadata,
    evaluate_capabilities,
)


def test_evaluate_capabilities_allows_when_required_is_empty() -> None:
    decision = evaluate_capabilities(
        required_capabilities=[],
        granted_capabilities=["system.write"],
    )

    assert decision.allowed is True
    assert decision.required_capabilities == ()
    assert decision.missing_capabilities == ()


def test_evaluate_capabilities_denies_missing_required_capability() -> None:
    decision = evaluate_capabilities(
        required_capabilities=["system.write", "system.delete"],
        granted_capabilities=["system.write"],
    )

    assert decision.allowed is False
    assert decision.required_capabilities == ("system.delete", "system.write")
    assert decision.missing_capabilities == ("system.delete",)


def test_authorization_metadata_is_stable_for_denied_outcome() -> None:
    decision = evaluate_capabilities(
        required_capabilities=["system.delete"],
        granted_capabilities=["system.read"],
    )

    metadata = authorization_metadata(
        decision=decision,
        surface=AuthorizationSurface.COMMAND,
        operation="delete-project",
    )

    assert metadata == {
        "surface": "command",
        "operation": "delete-project",
        "allowed": False,
        "required_capabilities": ["system.delete"],
        "missing_capabilities": ["system.delete"],
    }
