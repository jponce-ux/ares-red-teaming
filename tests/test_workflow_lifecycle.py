"""Tests for deterministic workflow lifecycle execution."""

from endi.workflow import (
    EventType,
    WorkflowFailure,
    WorkflowInput,
    WorkflowLifecycleRunner,
    WorkflowStage,
    WorkflowStatus,
)


def test_runner_executes_required_stages_in_deterministic_order() -> None:
    stage_trace: list[str] = []

    def initialize(_: WorkflowInput) -> None:
        stage_trace.append("initialize")

    def validate(_: WorkflowInput) -> None:
        stage_trace.append("validate")

    def execute(_: WorkflowInput) -> str:
        stage_trace.append("execute")
        return "result"

    def collect(payload: str, _: WorkflowInput) -> str:
        stage_trace.append("collect")
        return f"{payload}-collected"

    def output(payload: str, _: WorkflowInput) -> str:
        stage_trace.append("output")
        return f"{payload}-output"

    def finalize(_: WorkflowInput) -> None:
        stage_trace.append("finalize")

    runner = WorkflowLifecycleRunner(
        initialize=initialize,
        validate=validate,
        execute=execute,
        collect=collect,
        output=output,
        finalize=finalize,
    )

    result = runner.run(WorkflowInput(payload={"x": 1}))

    assert stage_trace == ["initialize", "validate", "execute", "collect", "output", "finalize"]
    assert result.status is WorkflowStatus.SUCCESS
    assert result.payload == "result-collected-output"
    assert result.failure is None
    assert result.metadata.finalize_failure is None


def test_runner_skips_optional_plan_when_not_configured() -> None:
    stage_trace: list[str] = []

    def initialize(_: WorkflowInput) -> None:
        stage_trace.append("initialize")

    def validate(_: WorkflowInput) -> None:
        stage_trace.append("validate")

    def execute(_: WorkflowInput) -> str:
        stage_trace.append("execute")
        return "ok"

    def finalize(_: WorkflowInput) -> None:
        stage_trace.append("finalize")

    runner = WorkflowLifecycleRunner(
        initialize=initialize,
        validate=validate,
        execute=execute,
        finalize=finalize,
    )

    result = runner.run(WorkflowInput(payload={"x": 1}))

    assert stage_trace == ["initialize", "validate", "execute", "finalize"]
    assert result.metadata.skipped_stages == [WorkflowStage.PLAN]
    assert result.metadata.finalize_failure is None


def test_runner_validation_failure_prevents_execute_side_effects() -> None:
    execute_calls = 0

    def validate(_: WorkflowInput) -> None:
        raise ValueError("missing required field")

    def execute(_: WorkflowInput) -> str:
        nonlocal execute_calls
        execute_calls += 1
        return "should-not-run"

    runner = WorkflowLifecycleRunner(validate=validate, execute=execute)

    result = runner.run(WorkflowInput(payload={}))

    assert result.status is WorkflowStatus.FAILURE
    assert isinstance(result.failure, WorkflowFailure)
    assert result.failure.component == WorkflowStage.VALIDATE
    assert result.failure.failure_type == "validation_error"
    assert execute_calls == 0


def test_runner_runtime_failure_is_structured_and_finalize_still_runs() -> None:
    stage_trace: list[str] = []

    def initialize(_: WorkflowInput) -> None:
        stage_trace.append("initialize")

    def execute(_: WorkflowInput) -> str:
        stage_trace.append("execute")
        raise RuntimeError("boom")

    def finalize(_: WorkflowInput) -> None:
        stage_trace.append("finalize")

    runner = WorkflowLifecycleRunner(
        initialize=initialize,
        execute=execute,
        finalize=finalize,
    )

    result = runner.run(WorkflowInput(payload={"x": 1}))

    assert result.status is WorkflowStatus.FAILURE
    assert result.failure is not None
    assert result.failure.component == WorkflowStage.EXECUTE
    assert result.failure.failure_type == "runtime_error"
    assert stage_trace == ["initialize", "execute", "finalize"]
    assert result.metadata.finalize_failure is None


def test_runner_preserves_primary_failure_when_finalize_also_fails() -> None:
    def execute(_: WorkflowInput) -> str:
        raise RuntimeError("execute failed")

    def finalize(_: WorkflowInput) -> None:
        raise RuntimeError("finalize failed")

    runner = WorkflowLifecycleRunner(execute=execute, finalize=finalize)

    result = runner.run(WorkflowInput(payload={"x": 1}))

    assert result.status is WorkflowStatus.FAILURE
    assert result.failure is not None
    assert result.failure.component == WorkflowStage.EXECUTE
    assert result.failure.failure_type == "runtime_error"
    assert result.failure.message == "execute failed"
    assert result.metadata.finalize_failure is not None
    assert result.metadata.finalize_failure.component == WorkflowStage.FINALIZE
    assert result.metadata.finalize_failure.failure_type == "runtime_error"
    assert result.metadata.finalize_failure.message == "finalize failed"


def test_runner_reports_finalize_failure_when_it_is_only_failure() -> None:
    def execute(_: WorkflowInput) -> str:
        return "ok"

    def finalize(_: WorkflowInput) -> None:
        raise RuntimeError("cleanup failed")

    runner = WorkflowLifecycleRunner(execute=execute, finalize=finalize)

    result = runner.run(WorkflowInput(payload={"x": 1}))

    assert result.status is WorkflowStatus.FAILURE
    assert result.failure is not None
    assert result.failure.component == WorkflowStage.FINALIZE
    assert result.failure.failure_type == "runtime_error"
    assert result.failure.message == "cleanup failed"
    assert result.metadata.finalize_failure is not None
    assert result.metadata.finalize_failure.component == WorkflowStage.FINALIZE


def test_runner_emits_stage_events_with_execution_correlation() -> None:
    runner = WorkflowLifecycleRunner(execute=lambda _: "ok")

    result = runner.run(WorkflowInput(payload={"x": 1}, execution_id="exec-123"))

    assert result.metadata.execution_id == "exec-123"
    assert result.metadata.events
    assert result.metadata.events[0].event_type is EventType.STAGE_STARTED
    assert all(event.execution_id == "exec-123" for event in result.metadata.events)
    assert result.metadata.finalize_failure is None
