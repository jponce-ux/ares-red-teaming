"""Execution backend contracts and deterministic capability-based backend resolution."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import Protocol, runtime_checkable


class BackendKind(StrEnum):
    """Supported execution backend identifiers."""

    LOCAL = "local"
    WORKER = "worker"
    CONTAINER = "container"
    REMOTE = "remote"


class IsolationLevel(IntEnum):
    """Stable isolation ordering for backend selection."""

    LOCAL = 0
    WORKER = 1
    CONTAINER = 2
    REMOTE = 3


_DEFAULT_BACKEND = BackendKind.LOCAL

_DEFAULT_CAPABILITY_BACKENDS: dict[str, BackendKind] = {
    "cloud.read": BackendKind.LOCAL,
    "cloud.write": BackendKind.WORKER,
    "filesystem.read": BackendKind.LOCAL,
    "filesystem.write": BackendKind.WORKER,
    "network.admin": BackendKind.WORKER,
    "network.outbound": BackendKind.LOCAL,
    "repo.read": BackendKind.LOCAL,
    "repo.write": BackendKind.WORKER,
    "shell.exec": BackendKind.WORKER,
    "system.modify": BackendKind.WORKER,
}

_ISOLATION_BY_BACKEND: dict[BackendKind, IsolationLevel] = {
    BackendKind.LOCAL: IsolationLevel.LOCAL,
    BackendKind.WORKER: IsolationLevel.WORKER,
    BackendKind.CONTAINER: IsolationLevel.CONTAINER,
    BackendKind.REMOTE: IsolationLevel.REMOTE,
}


@dataclass(frozen=True)
class BackendSelection:
    """Deterministic backend resolution output."""

    selected_backend: BackendKind
    selected_isolation: IsolationLevel
    required_capabilities: tuple[str, ...]
    mapped_capabilities: dict[str, str]


@runtime_checkable
class ExecutionBackend(Protocol):
    """Execution contract for runtime command dispatch backends."""

    @property
    def kind(self) -> BackendKind:
        """Backend identity for telemetry and policy surfaces."""

    def execute(
        self,
        operation: str,
        args: list[str],
        *,
        context: Mapping[str, object] | None = None,
    ) -> object:
        """Execute a command operation using backend-specific behavior."""


@runtime_checkable
class WorkerBackend(ExecutionBackend, Protocol):
    """Contract marker for worker-isolated execution backend."""


@runtime_checkable
class ContainerBackend(ExecutionBackend, Protocol):
    """Contract marker for container-isolated execution backend."""


@runtime_checkable
class RemoteBackend(ExecutionBackend, Protocol):
    """Contract marker for remote-isolated execution backend."""


@dataclass(frozen=True)
class LocalBackend:
    """v1 concrete backend that executes commands in-process."""

    command_executor: Callable[[str, list[str]], object]

    @property
    def kind(self) -> BackendKind:
        return BackendKind.LOCAL

    def execute(
        self,
        operation: str,
        args: list[str],
        *,
        context: Mapping[str, object] | None = None,
    ) -> object:
        del context
        return self.command_executor(operation, args)


def _normalize_capabilities(value: Sequence[str] | object) -> tuple[str, ...]:
    if isinstance(value, str):
        capabilities: list[object] = [value]
    elif isinstance(value, Sequence):
        capabilities = list(value)
    else:
        capabilities = []

    normalized = {
        capability.strip()
        for capability in capabilities
        if isinstance(capability, str) and capability.strip()
    }
    return tuple(sorted(normalized))


def _parse_backend_kind(value: object) -> BackendKind | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if normalized == BackendKind.LOCAL.value:
        return BackendKind.LOCAL
    if normalized == BackendKind.WORKER.value:
        return BackendKind.WORKER
    if normalized == BackendKind.CONTAINER.value:
        return BackendKind.CONTAINER
    if normalized == BackendKind.REMOTE.value:
        return BackendKind.REMOTE
    return None


def _resolve_default_backend(context: Mapping[str, object]) -> BackendKind:
    resolved = _parse_backend_kind(context.get("default_backend"))
    if resolved is not None:
        return resolved

    runtime_policy = context.get("runtime")
    if isinstance(runtime_policy, Mapping):
        runtime_default = _parse_backend_kind(runtime_policy.get("default_backend"))
        if runtime_default is not None:
            return runtime_default

    return _DEFAULT_BACKEND


def _resolve_capability_backends(
    context: Mapping[str, object],
) -> dict[str, BackendKind]:
    mapping = dict(_DEFAULT_CAPABILITY_BACKENDS)

    override: object | None = context.get("capability_backends")
    if override is None:
        runtime_policy = context.get("runtime")
        if isinstance(runtime_policy, Mapping):
            override = runtime_policy.get("capability_backends")

    if not isinstance(override, Mapping):
        return mapping

    for capability, backend in override.items():
        if not isinstance(capability, str) or not capability.strip():
            continue
        normalized_capability = capability.strip()
        parsed_backend = _parse_backend_kind(backend)
        if parsed_backend is None:
            continue

        locked_backend = _DEFAULT_CAPABILITY_BACKENDS.get(normalized_capability)
        if locked_backend is not None and (
            _ISOLATION_BY_BACKEND[parsed_backend] < _ISOLATION_BY_BACKEND[locked_backend]
        ):
            mapping[normalized_capability] = locked_backend
            continue

        mapping[normalized_capability] = parsed_backend

    return mapping


def resolve_backend_selection(
    *,
    required_capabilities: Sequence[str] | object,
    context: Mapping[str, object],
) -> BackendSelection:
    """Resolve a deterministic backend from capabilities and runtime policy."""
    normalized_capabilities = _normalize_capabilities(required_capabilities)
    default_backend = _resolve_default_backend(context)
    capability_backends = _resolve_capability_backends(context)

    selected_backend = default_backend
    mapped_capabilities: dict[str, str] = {}
    for capability in normalized_capabilities:
        capability_backend = capability_backends.get(capability, default_backend)
        mapped_capabilities[capability] = capability_backend.value
        if _ISOLATION_BY_BACKEND[capability_backend] > _ISOLATION_BY_BACKEND[selected_backend]:
            selected_backend = capability_backend

    return BackendSelection(
        selected_backend=selected_backend,
        selected_isolation=_ISOLATION_BY_BACKEND[selected_backend],
        required_capabilities=normalized_capabilities,
        mapped_capabilities=mapped_capabilities,
    )


def backend_selection_metadata(selection: BackendSelection) -> dict[str, object]:
    """Build stable backend selection metadata for telemetry and policy payloads."""
    selected_capabilities = [
        capability
        for capability in selection.required_capabilities
        if selection.mapped_capabilities.get(capability) == selection.selected_backend.value
    ]
    return {
        "selected_backend": selection.selected_backend.value,
        "selected_isolation": int(selection.selected_isolation),
        "required_capabilities": list(selection.required_capabilities),
        "mapped_capabilities": {
            capability: selection.mapped_capabilities[capability]
            for capability in sorted(selection.mapped_capabilities)
        },
        "selection_reason": {
            "mode": "highest_isolation_wins",
            "selected_capabilities": selected_capabilities,
        },
    }
