"""Canonical tool contract models and deterministic registry/invocation behavior."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from endi.authorization import (
    AuthorizationSurface,
    authorization_metadata,
    evaluate_capabilities,
)


class ToolStatus(StrEnum):
    """High-level invocation outcome."""

    SUCCESS = "success"
    ERROR = "error"


class ToolStatusCode(StrEnum):
    """Deterministic status codes for registration and invocation."""

    OK = "ok"
    INVALID_CONTRACT = "invalid_contract"
    INVALID_INPUT = "invalid_input"
    PERMISSION_DENIED = "permission_denied"
    NOT_FOUND = "not_found"
    EXECUTION_ERROR = "execution_error"


@dataclass(frozen=True)
class ToolError:
    """Structured tool error payload."""

    code: str
    message: str
    details: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolResult:
    """Structured tool response envelope."""

    status: ToolStatus
    status_code: ToolStatusCode
    payload: object | None
    error: ToolError | None
    tool_name: str | None


ToolHandler = Callable[[dict[str, object]], object]


@dataclass(frozen=True)
class ToolContract:
    """Canonical tool registration contract."""

    identifier: str
    description: str
    capability: str
    input_schema: dict[str, type[object] | tuple[type[object], ...]]
    handler: ToolHandler
    metadata: dict[str, object] = field(default_factory=dict)


def _is_supported_schema_type(value: object) -> bool:
    if isinstance(value, type):
        return True
    if isinstance(value, tuple):
        return bool(value) and all(isinstance(item, type) for item in value)
    return False


def _normalize_contract_mapping(contract: Mapping[str, object]) -> ToolContract | None:
    identifier = contract.get("identifier")
    description = contract.get("description")
    capability = contract.get("capability")
    input_schema = contract.get("input_schema")
    handler = contract.get("handler")
    metadata = contract.get("metadata")

    if not isinstance(metadata, dict):
        metadata = {}

    if (
        not isinstance(identifier, str)
        or not isinstance(description, str)
        or not isinstance(capability, str)
        or not isinstance(input_schema, dict)
        or not callable(handler)
    ):
        return None

    return ToolContract(
        identifier=identifier,
        description=description,
        capability=capability,
        input_schema=input_schema,
        handler=handler,
        metadata=metadata,
    )


class ToolRegistry:
    """Registry with strict contract and invocation validation."""

    def __init__(self) -> None:
        self._contracts: dict[str, ToolContract] = {}

    def list_tools(self) -> list[str]:
        return sorted(self._contracts)

    def register(self, contract: ToolContract | Mapping[str, object]) -> ToolResult:
        normalized = (
            contract
            if isinstance(contract, ToolContract)
            else _normalize_contract_mapping(contract)
        )

        if normalized is None:
            missing_fields: list[str] = []
            invalid_fields: list[str] = []
            if isinstance(contract, Mapping):
                identifier = contract.get("identifier")
                description = contract.get("description")
                capability = contract.get("capability")
                input_schema = contract.get("input_schema")
                handler = contract.get("handler")

                if not callable(handler):
                    missing_fields.append("handler")
                if not isinstance(identifier, str) or not identifier:
                    invalid_fields.append("identifier")
                if not isinstance(description, str) or not description:
                    invalid_fields.append("description")
                if not isinstance(capability, str) or not capability:
                    invalid_fields.append("capability")
                if not isinstance(input_schema, dict) or not input_schema:
                    invalid_fields.append("input_schema")
            else:
                missing_fields.extend(
                    [
                        "identifier",
                        "description",
                        "capability",
                        "input_schema",
                        "handler",
                    ]
                )

            return ToolResult(
                status=ToolStatus.ERROR,
                status_code=ToolStatusCode.INVALID_CONTRACT,
                payload=None,
                error=ToolError(
                    code="invalid_contract",
                    message="Tool contract is malformed.",
                    details={
                        "missing_fields": sorted(set(missing_fields)),
                        "invalid_fields": sorted(set(invalid_fields)),
                    },
                ),
                tool_name=None,
            )

        normalized_missing_fields: list[str] = []
        normalized_invalid_fields: list[str] = []

        if not normalized.identifier:
            normalized_invalid_fields.append("identifier")
        if not normalized.description:
            normalized_invalid_fields.append("description")
        if not normalized.capability:
            normalized_invalid_fields.append("capability")
        if not normalized.input_schema:
            normalized_invalid_fields.append("input_schema")

        for field_name, field_type in normalized.input_schema.items():
            if not isinstance(field_name, str) or not field_name:
                normalized_invalid_fields.append("input_schema")
                break
            if not _is_supported_schema_type(field_type):
                normalized_invalid_fields.append("input_schema")
                break

        if not callable(normalized.handler):
            normalized_missing_fields.append("handler")

        if normalized_missing_fields or normalized_invalid_fields:
            return ToolResult(
                status=ToolStatus.ERROR,
                status_code=ToolStatusCode.INVALID_CONTRACT,
                payload=None,
                error=ToolError(
                    code="invalid_contract",
                    message="Tool contract validation failed.",
                    details={
                        "missing_fields": sorted(set(normalized_missing_fields)),
                        "invalid_fields": sorted(set(normalized_invalid_fields)),
                    },
                ),
                tool_name=normalized.identifier or None,
            )

        self._contracts[normalized.identifier] = ToolContract(
            identifier=normalized.identifier,
            description=normalized.description,
            capability=normalized.capability,
            input_schema=dict(normalized.input_schema),
            handler=normalized.handler,
            metadata=dict(normalized.metadata),
        )

        return ToolResult(
            status=ToolStatus.SUCCESS,
            status_code=ToolStatusCode.OK,
            payload={"identifier": normalized.identifier},
            error=None,
            tool_name=normalized.identifier,
        )

    def invoke(
        self,
        tool_name: str,
        payload: dict[str, object] | None,
        *,
        granted_capabilities: Iterable[str] | None = None,
    ) -> ToolResult:
        contract = self._contracts.get(tool_name)
        if contract is None:
            return ToolResult(
                status=ToolStatus.ERROR,
                status_code=ToolStatusCode.NOT_FOUND,
                payload=None,
                error=ToolError(
                    code="tool_not_found",
                    message=f"Tool '{tool_name}' is not registered.",
                    details={"tool_name": tool_name},
                ),
                tool_name=tool_name,
            )

        if payload is None:
            payload = {}

        decision = evaluate_capabilities(
            required_capabilities=[contract.capability],
            granted_capabilities=granted_capabilities,
        )
        if not decision.allowed:
            return ToolResult(
                status=ToolStatus.ERROR,
                status_code=ToolStatusCode.PERMISSION_DENIED,
                payload=None,
                error=ToolError(
                    code="capability_denied",
                    message=(
                        f"Missing required capability '{contract.capability}' "
                        f"for tool '{tool_name}'."
                    ),
                    details=authorization_metadata(
                        decision=decision,
                        surface=AuthorizationSurface.TOOL,
                        operation=tool_name,
                    ),
                ),
                tool_name=tool_name,
            )

        if not isinstance(payload, dict):
            return ToolResult(
                status=ToolStatus.ERROR,
                status_code=ToolStatusCode.INVALID_INPUT,
                payload=None,
                error=ToolError(
                    code="invalid_tool_input",
                    message="Tool payload must be an object.",
                    details={"tool_name": tool_name},
                ),
                tool_name=tool_name,
            )

        missing_fields: list[str] = []
        type_mismatches: list[dict[str, str]] = []

        for field_name, expected_type in contract.input_schema.items():
            if field_name not in payload:
                missing_fields.append(field_name)
                continue

            value = payload[field_name]
            expected_types: tuple[type[object], ...] = (
                expected_type if isinstance(expected_type, tuple) else (expected_type,)
            )
            if not isinstance(value, expected_types):
                type_mismatches.append(
                    {
                        "field": field_name,
                        "expected": " | ".join(t.__name__ for t in expected_types),
                        "actual": type(value).__name__,
                    }
                )

        if missing_fields or type_mismatches:
            return ToolResult(
                status=ToolStatus.ERROR,
                status_code=ToolStatusCode.INVALID_INPUT,
                payload=None,
                error=ToolError(
                    code="invalid_tool_input",
                    message="Tool input schema validation failed.",
                    details={
                        "tool_name": tool_name,
                        "missing_fields": sorted(missing_fields),
                        "type_mismatches": type_mismatches,
                    },
                ),
                tool_name=tool_name,
            )

        try:
            output = contract.handler(dict(payload))
        except Exception as exc:
            return ToolResult(
                status=ToolStatus.ERROR,
                status_code=ToolStatusCode.EXECUTION_ERROR,
                payload=None,
                error=ToolError(
                    code="tool_execution_error",
                    message=str(exc),
                    details={"tool_name": tool_name},
                ),
                tool_name=tool_name,
            )

        return ToolResult(
            status=ToolStatus.SUCCESS,
            status_code=ToolStatusCode.OK,
            payload=output,
            error=None,
            tool_name=tool_name,
        )
