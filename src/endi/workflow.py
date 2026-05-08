"""Deterministic workflow lifecycle engine for ENDI runtime execution."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from time import perf_counter_ns
from typing import Generic, TypeVar
from uuid import uuid4

PayloadT = TypeVar("PayloadT")


class WorkflowStage(StrEnum):
    """Canonical deterministic lifecycle stages."""

    INITIALIZE = "initialize"
    VALIDATE = "validate"
    PLAN = "plan"
    EXECUTE = "execute"
    COLLECT = "collect"
    OUTPUT = "output"
    FINALIZE = "finalize"


class WorkflowStatus(StrEnum):
    """Workflow result status."""

    SUCCESS = "success"
    FAILURE = "failure"


class EventType(StrEnum):
    """Lifecycle event types for stage-level observability."""

    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    STAGE_FAILED = "stage_failed"


@dataclass(frozen=True)
class WorkflowFailure:
    """Structured failure information for observability and callers."""

    component: WorkflowStage
    failure_type: str
    message: str
    details: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class StageEvent:
    """Structured lifecycle stage event with correlation context."""

    sequence: int
    execution_id: str
    stage: WorkflowStage
    event_type: EventType
    failure_type: str | None
    timestamp: str
    duration_ms: int


@dataclass(frozen=True)
class WorkflowMetadata:
    """Workflow metadata included in structured output envelope."""

    execution_id: str
    events: list[StageEvent]
    skipped_stages: list[WorkflowStage]
    finalize_failure: WorkflowFailure | None


@dataclass(frozen=True)
class WorkflowInput:
    """Input passed to lifecycle handlers."""

    payload: object
    execution_id: str | None = None


@dataclass(frozen=True)
class WorkflowOutput(Generic[PayloadT]):
    """Structured workflow envelope returned to callers."""

    status: WorkflowStatus
    payload: PayloadT | None
    metadata: WorkflowMetadata
    failure: WorkflowFailure | None


InitializeStage = Callable[[WorkflowInput], None]
ValidateStage = Callable[[WorkflowInput], None]
PlanStage = Callable[[WorkflowInput], None]
ExecuteStage = Callable[[WorkflowInput], PayloadT]
CollectStage = Callable[[PayloadT, WorkflowInput], PayloadT]
OutputStage = Callable[[PayloadT, WorkflowInput], PayloadT]
FinalizeStage = Callable[[WorkflowInput], None]


def _noop(_: WorkflowInput) -> None:
    return None


def _passthrough(payload: PayloadT, _: WorkflowInput) -> PayloadT:
    return payload


@dataclass(frozen=True)
class WorkflowLifecycleRunner(Generic[PayloadT]):
    """Runs deterministic lifecycle stages with strict ordering and structured failures."""

    initialize: InitializeStage = _noop
    validate: ValidateStage = _noop
    plan: PlanStage | None = None
    execute: ExecuteStage[PayloadT] | None = None
    collect: CollectStage[PayloadT] = _passthrough
    output: OutputStage[PayloadT] = _passthrough
    finalize: FinalizeStage = _noop

    def run(self, workflow_input: WorkflowInput) -> WorkflowOutput[PayloadT]:
        execution_id = workflow_input.execution_id or uuid4().hex
        events: list[StageEvent] = []
        skipped_stages: list[WorkflowStage] = []
        failure: WorkflowFailure | None = None
        finalize_failure: WorkflowFailure | None = None
        payload: PayloadT | None = None
        active_stage: WorkflowStage | None = None
        stage_started_at_ns: dict[WorkflowStage, int] = {}

        def emit(
            stage: WorkflowStage,
            event_type: EventType,
            failure_type: str | None = None,
            duration_ms: int = 0,
            timestamp: str | None = None,
        ) -> None:
            events.append(
                StageEvent(
                    sequence=len(events) + 1,
                    execution_id=execution_id,
                    stage=stage,
                    event_type=event_type,
                    failure_type=failure_type,
                    timestamp=timestamp or datetime.now(UTC).isoformat(),
                    duration_ms=duration_ms,
                )
            )

        def start_stage(stage: WorkflowStage) -> None:
            stage_started_at_ns[stage] = perf_counter_ns()
            emit(stage, EventType.STAGE_STARTED)

        def stage_duration_ms(stage: WorkflowStage) -> int:
            started_at_ns = stage_started_at_ns.get(stage)
            if started_at_ns is None:
                return 0
            elapsed_ns = perf_counter_ns() - started_at_ns
            if elapsed_ns <= 0:
                return 0
            return elapsed_ns // 1_000_000

        def clear_stage_timing(stage: WorkflowStage) -> None:
            stage_started_at_ns.pop(stage, None)

        def run_stage(stage: WorkflowStage, action: Callable[[], None]) -> None:
            nonlocal active_stage
            active_stage = stage
            start_stage(stage)
            action()
            emit(stage, EventType.STAGE_COMPLETED, duration_ms=stage_duration_ms(stage))
            clear_stage_timing(stage)
            active_stage = None

        try:
            run_stage(WorkflowStage.INITIALIZE, lambda: self.initialize(workflow_input))
            run_stage(WorkflowStage.VALIDATE, lambda: self.validate(workflow_input))

            if self.plan is None:
                skipped_stages.append(WorkflowStage.PLAN)
            else:
                plan_stage = self.plan
                run_stage(WorkflowStage.PLAN, lambda: plan_stage(workflow_input))

            if self.execute is None:
                raise RuntimeError("Workflow execute stage is required")

            active_stage = WorkflowStage.EXECUTE
            start_stage(WorkflowStage.EXECUTE)
            executed_payload = self.execute(workflow_input)
            emit(
                WorkflowStage.EXECUTE,
                EventType.STAGE_COMPLETED,
                duration_ms=stage_duration_ms(WorkflowStage.EXECUTE),
            )
            clear_stage_timing(WorkflowStage.EXECUTE)
            active_stage = None

            active_stage = WorkflowStage.COLLECT
            start_stage(WorkflowStage.COLLECT)
            collected_payload = self.collect(executed_payload, workflow_input)
            emit(
                WorkflowStage.COLLECT,
                EventType.STAGE_COMPLETED,
                duration_ms=stage_duration_ms(WorkflowStage.COLLECT),
            )
            clear_stage_timing(WorkflowStage.COLLECT)
            active_stage = None

            active_stage = WorkflowStage.OUTPUT
            start_stage(WorkflowStage.OUTPUT)
            payload = self.output(collected_payload, workflow_input)
            emit(
                WorkflowStage.OUTPUT,
                EventType.STAGE_COMPLETED,
                duration_ms=stage_duration_ms(WorkflowStage.OUTPUT),
            )
            clear_stage_timing(WorkflowStage.OUTPUT)
            active_stage = None
        except Exception as exc:
            failed_stage = active_stage or WorkflowStage.EXECUTE
            failure_type_from_exception = getattr(exc, "failure_type", None)
            if isinstance(failure_type_from_exception, str) and failure_type_from_exception:
                failure_type = failure_type_from_exception
            else:
                failure_type = (
                    "validation_error"
                    if failed_stage is WorkflowStage.VALIDATE and isinstance(exc, ValueError)
                    else "runtime_error"
                )
            failure_details = getattr(exc, "details", {})
            if not isinstance(failure_details, dict):
                failure_details = {}
            failure = WorkflowFailure(
                component=failed_stage,
                failure_type=failure_type,
                message=str(exc),
                details=dict(failure_details),
            )
            emit(
                failed_stage,
                EventType.STAGE_FAILED,
                failure_type=failure_type,
                duration_ms=stage_duration_ms(failed_stage),
            )
            clear_stage_timing(failed_stage)
        finally:
            try:
                run_stage(WorkflowStage.FINALIZE, lambda: self.finalize(workflow_input))
            except Exception as exc:  # pragma: no cover - defensive
                finalize_failure = WorkflowFailure(
                    component=WorkflowStage.FINALIZE,
                    failure_type="runtime_error",
                    message=str(exc),
                )
                emit(WorkflowStage.FINALIZE, EventType.STAGE_FAILED, failure_type="runtime_error")
                if failure is None:
                    failure = finalize_failure

        metadata = WorkflowMetadata(
            execution_id=execution_id,
            events=events,
            skipped_stages=skipped_stages,
            finalize_failure=finalize_failure,
        )

        if failure is not None:
            return WorkflowOutput(
                status=WorkflowStatus.FAILURE,
                payload=None,
                metadata=metadata,
                failure=failure,
            )

        return WorkflowOutput(
            status=WorkflowStatus.SUCCESS,
            payload=payload,
            metadata=metadata,
            failure=None,
        )
