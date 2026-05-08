"""Tests for SQLite execution history persistence and routing integration."""

from __future__ import annotations

import json
import sqlite3
import threading

import pytest

from endi.conversation import RuntimeErrorComponent, RuntimeErrorEnvelope
from endi.persistence import (
    ExecutionHistoryStore,
    PersistenceContractError,
    _database_size_bytes,
)
from endi.routing import RouteKind, dispatch_input
from endi.workflow import EventType, StageEvent, WorkflowStage, WorkflowStatus


def _events(execution_id: str = "exec-001") -> list[StageEvent]:
    return [
        StageEvent(
            sequence=1,
            execution_id=execution_id,
            stage=WorkflowStage.INITIALIZE,
            event_type=EventType.STAGE_STARTED,
            failure_type=None,
            timestamp="2026-03-20T12:00:00+00:00",
            duration_ms=0,
        ),
        StageEvent(
            sequence=2,
            execution_id=execution_id,
            stage=WorkflowStage.EXECUTE,
            event_type=EventType.STAGE_COMPLETED,
            failure_type=None,
            timestamp="2026-03-20T12:00:01+00:00",
            duration_ms=12,
        ),
        StageEvent(
            sequence=3,
            execution_id=execution_id,
            stage=WorkflowStage.FINALIZE,
            event_type=EventType.STAGE_COMPLETED,
            failure_type=None,
            timestamp="2026-03-20T12:00:02+00:00",
            duration_ms=5,
        ),
    ]


def _record_dispatch(
    store: ExecutionHistoryStore,
    *,
    execution_id: str,
    context: dict[str, object] | None = None,
    telemetry_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    return store.record_command_dispatch(
        session_id="session-1",
        command_id=f"cmd-{execution_id}",
        workflow_id=f"wf-{execution_id}",
        execution_id=execution_id,
        command_name="show-status",
        command_arg_count=1,
        route=RouteKind.COMMAND.value,
        workflow_status=WorkflowStatus.SUCCESS,
        events=_events(execution_id),
        context=context or {},
        telemetry_payload=telemetry_payload,
        runtime_error=None,
    )


def test_execution_history_persists_fr007_boundaries_and_reconstructs_timeline(tmp_path) -> None:
    store = ExecutionHistoryStore(str(tmp_path / "history.db"))
    store.record_command_dispatch(
        session_id="session-1",
        command_id="cmd-1",
        workflow_id="wf-1",
        execution_id="exec-001",
        command_name="show-status",
        command_arg_count=1,
        route=RouteKind.COMMAND.value,
        workflow_status=WorkflowStatus.SUCCESS,
        events=_events(),
        context={"session_id": "session-1", "request_id": "req-1"},
        telemetry_payload={"event": "command_dispatch", "request_id": "req-1"},
        runtime_error=None,
    )

    timeline = store.timeline_by_execution_id("exec-001")

    assert timeline["session"]["session_id"] == "session-1"
    assert timeline["command"]["session_id"] == "session-1"
    assert timeline["workflow"]["command_id"] == "cmd-1"
    assert [step["sequence"] for step in timeline["steps"]] == [1, 2, 3]
    assert all(step["workflow_id"] == "wf-1" for step in timeline["steps"])
    assert timeline["tool_calls"][0]["step_id"] == "wf-1:step:002"
    assert timeline["steps"][0]["status"] == "in_progress"
    assert timeline["steps"][0]["occurred_at"] == "2026-03-20T12:00:00+00:00"
    assert timeline["steps"][0]["duration_ms"] == 0
    assert timeline["steps"][1]["status"] == "success"
    assert timeline["steps"][1]["occurred_at"] == "2026-03-20T12:00:01+00:00"
    assert timeline["steps"][1]["duration_ms"] == 12

    session_metadata = timeline["session"]["metadata_json"]
    command_metadata = timeline["command"]["metadata_json"]
    workflow_metadata = timeline["workflow"]["metadata_json"]
    step_metadata = timeline["steps"][1]["metadata_json"]
    assert isinstance(session_metadata, dict)
    assert isinstance(command_metadata, dict)
    assert isinstance(workflow_metadata, dict)
    assert isinstance(step_metadata, dict)

    assert session_metadata["event"]["component"] == "session"
    assert session_metadata["event"]["action"] == "command_dispatch"
    assert command_metadata["event"]["component"] == "command"
    assert workflow_metadata["event"]["component"] == "workflow"

    assert step_metadata["event"] == {
        "timestamp": "2026-03-20T12:00:01+00:00",
        "component": "execute",
        "action": "stage_completed",
        "status": "success",
        "duration_ms": 12,
    }
    assert step_metadata["correlation"] == {
        "session_id": "session-1",
        "command_id": "cmd-1",
        "workflow_id": "wf-1",
        "step_id": "wf-1:step:002",
        "execution_id": "exec-001",
    }


def test_timeline_lookup_raises_structured_contract_error_for_missing_parent_linkage(
    tmp_path,
) -> None:
    db_path = tmp_path / "history.db"
    store = ExecutionHistoryStore(str(db_path))
    store.record_command_dispatch(
        session_id="session-1",
        command_id="cmd-1",
        workflow_id="wf-1",
        execution_id="exec-001",
        command_name="show-status",
        command_arg_count=0,
        route=RouteKind.COMMAND.value,
        workflow_status=WorkflowStatus.SUCCESS,
        events=_events(),
        context={},
        telemetry_payload=None,
        runtime_error=None,
    )

    with sqlite3.connect(str(db_path)) as connection:
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute(
            "UPDATE workflows SET command_id = ? WHERE workflow_id = ?",
            ("cmd-orphan", "wf-1"),
        )

    with pytest.raises(PersistenceContractError) as raised:
        store.timeline_by_execution_id("exec-001")

    assert raised.value.code == "persistence_missing_parent_linkage"


# SAN-mvp-03-1-01

def test_dispatch_persistence_failure_surfaces_structured_runtime_error_without_raw_text(
    tmp_path,
) -> None:
    blocked_db_path = tmp_path / "blocked"
    blocked_db_path.mkdir()

    raw_text = "TOPSECRET-RAW-TEXT"
    result = dispatch_input(
        f"/show-status {raw_text}",
        command_executor=lambda _name, _args: "ok",
        conversation_handler=lambda _text: "unused",
        explicit_context={
            "execution_history_db": str(blocked_db_path),
            "request_text": raw_text,
            "response_text": raw_text,
        },
    )

    assert result.route is RouteKind.EXECUTION_ERROR
    assert result.runtime_error is not None
    assert result.runtime_error.code == "persistence_stage_write_error"
    assert result.runtime_error.details["error"] == {
        "type": "runtime_error",
        "code": "persistence_stage_write_error",
        "component": "workflow",
    }
    assert raw_text not in str(result.runtime_error.details)


# SAN-mvp-03-1-02, SAN-mvp-03-1-04

def test_persistence_rows_store_sanitized_context_and_telemetry(tmp_path) -> None:
    db_path = tmp_path / "history.db"
    store = ExecutionHistoryStore(str(db_path))
    raw_text = "unsafe-response"

    store.record_command_dispatch(
        session_id="session-1",
        command_id="cmd-1",
        workflow_id="wf-1",
        execution_id="exec-001",
        command_name="show-status",
        command_arg_count=1,
        route=RouteKind.COMMAND.value,
        workflow_status=WorkflowStatus.SUCCESS,
        events=_events(),
        context={
            "request_text": raw_text,
            "response_text": raw_text,
            "api_key": "super-secret",
            "nested": {"auth_token": "nested-secret", "ok": True},
        },
        telemetry_payload={
            "command": {"name": "show-status"},
            "context": {"request_text": raw_text, "token": "abc"},
        },
        runtime_error=None,
    )

    timeline = store.timeline_by_execution_id("exec-001")
    command_metadata = timeline["command"]["metadata_json"]
    workflow_metadata = timeline["workflow"]["metadata_json"]
    assert isinstance(command_metadata, dict)
    assert isinstance(workflow_metadata, dict)

    serialized_timeline = json.dumps(timeline, sort_keys=True)
    assert raw_text not in serialized_timeline
    assert "api_key" not in serialized_timeline
    assert "auth_token" not in serialized_timeline
    assert "token" not in serialized_timeline


def test_persistence_sanitizes_command_args_from_context(tmp_path) -> None:
    store = ExecutionHistoryStore(str(tmp_path / "history.db"))

    store.record_command_dispatch(
        session_id="session-1",
        command_id="cmd-1",
        workflow_id="wf-1",
        execution_id="exec-001",
        command_name="show-status",
        command_arg_count=2,
        route=RouteKind.COMMAND.value,
        workflow_status=WorkflowStatus.SUCCESS,
        events=_events(),
        context={
            "command_args": ["--query", "TOPSECRET-ARG"],
            "safe_value": "keep-me",
        },
        telemetry_payload=None,
        runtime_error=None,
    )

    timeline = store.timeline_by_execution_id("exec-001")
    command_metadata = timeline["command"]["metadata_json"]
    assert isinstance(command_metadata, dict)
    context = command_metadata.get("context")
    assert isinstance(context, dict)
    assert "command_args" not in context
    assert context["safe_value"] == "keep-me"


# SAN-mvp-03-1-03

def test_recursive_persistence_sanitization_removes_nested_sensitive_fields(tmp_path) -> None:
    store = ExecutionHistoryStore(str(tmp_path / "history.db"))

    store.record_command_dispatch(
        session_id="session-1",
        command_id="cmd-1",
        workflow_id="wf-1",
        execution_id="exec-001",
        command_name="show-status",
        command_arg_count=0,
        route=RouteKind.COMMAND.value,
        workflow_status=WorkflowStatus.SUCCESS,
        events=_events(),
        context={
            "nested": {
                "level2": {
                    "private_key": "remove-me",
                    "safe": "keep-me",
                }
            }
        },
        telemetry_payload=None,
        runtime_error=None,
    )

    timeline = store.timeline_by_execution_id("exec-001")
    serialized_timeline = json.dumps(timeline, sort_keys=True)
    assert "private_key" not in serialized_timeline
    assert "keep-me" in serialized_timeline


# SAN-mvp-03-1-05

def test_runtime_error_persistence_is_sanitized_and_structured(tmp_path) -> None:
    store = ExecutionHistoryStore(str(tmp_path / "history.db"))

    runtime_error = RuntimeErrorEnvelope(
        code="tool_execution_error",
        component=RuntimeErrorComponent.TOOL,
        message="Tool failed",
        status_code="execution_error",
        details={
            "request_text": "do not leak",
            "error_token": "secret-token",
            "tool_name": "echo",
        },
    )
    store.record_command_dispatch(
        session_id="session-1",
        command_id="cmd-1",
        workflow_id="wf-1",
        execution_id="exec-001",
        command_name="show-status",
        command_arg_count=0,
        route=RouteKind.COMMAND.value,
        workflow_status=WorkflowStatus.FAILURE,
        events=_events(),
        context={},
        telemetry_payload=None,
        runtime_error=runtime_error,
    )

    timeline = store.timeline_by_execution_id("exec-001")
    runtime_error_row = timeline["runtime_error"]
    assert runtime_error_row is not None
    details_json = runtime_error_row["details_json"]
    assert details_json["error"]["type"] == "runtime_error"
    assert details_json["error"]["code"] == "tool_execution_error"
    assert details_json["error"]["component"] == "tool"
    details = details_json["error"]["details"]
    assert "request_text" not in details
    assert "error_token" not in details
    assert details["tool_name"] == "echo"


def test_tool_call_links_to_execute_completion_step_when_start_and_complete_exist(tmp_path) -> None:
    store = ExecutionHistoryStore(str(tmp_path / "history.db"))
    events = [
        StageEvent(
            sequence=1,
            execution_id="exec-002",
            stage=WorkflowStage.EXECUTE,
            event_type=EventType.STAGE_STARTED,
            failure_type=None,
            timestamp="2026-03-20T12:01:00+00:00",
            duration_ms=0,
        ),
        StageEvent(
            sequence=2,
            execution_id="exec-002",
            stage=WorkflowStage.EXECUTE,
            event_type=EventType.STAGE_COMPLETED,
            failure_type=None,
            timestamp="2026-03-20T12:01:01+00:00",
            duration_ms=17,
        ),
    ]

    store.record_command_dispatch(
        session_id="session-2",
        command_id="cmd-2",
        workflow_id="wf-2",
        execution_id="exec-002",
        command_name="show-status",
        command_arg_count=0,
        route=RouteKind.COMMAND.value,
        workflow_status=WorkflowStatus.SUCCESS,
        events=events,
        context={},
        telemetry_payload=None,
        runtime_error=None,
    )

    timeline = store.timeline_by_execution_id("exec-002")
    assert timeline["tool_calls"]
    assert timeline["tool_calls"][0]["step_id"] == "wf-2:step:002"


def test_runtime_error_step_id_is_linked_when_stage_is_known(tmp_path) -> None:
    store = ExecutionHistoryStore(str(tmp_path / "history.db"))

    runtime_error = RuntimeErrorEnvelope(
        code="validation_error",
        component=RuntimeErrorComponent.WORKFLOW,
        message="Validation failed",
        status_code="permission_denied",
        details={
            "workflow_stage": WorkflowStage.EXECUTE.value,
            "failure_type": "authorization_denied",
        },
    )
    store.record_command_dispatch(
        session_id="session-1",
        command_id="cmd-1",
        workflow_id="wf-1",
        execution_id="exec-001",
        command_name="show-status",
        command_arg_count=0,
        route=RouteKind.COMMAND.value,
        workflow_status=WorkflowStatus.FAILURE,
        events=_events(),
        context={},
        telemetry_payload=None,
        runtime_error=runtime_error,
    )

    timeline = store.timeline_by_execution_id("exec-001")
    runtime_error_row = timeline["runtime_error"]
    assert runtime_error_row is not None
    assert runtime_error_row["step_id"] == "wf-1:step:002"


def test_retention_defaults_are_enforced_and_auto_prune_is_enabled(tmp_path) -> None:
    store = ExecutionHistoryStore(str(tmp_path / "history.db"))

    summary = _record_dispatch(store, execution_id="exec-defaults")

    assert summary["policy"] == {
        "history_days": 30,
        "max_storage_gb": 2.0,
        "max_storage_bytes": 2 * 1024 * 1024 * 1024,
        "auto_prune": True,
    }
    prune = summary["prune"]
    assert isinstance(prune, dict)
    assert prune["order"] == ["age", "size"]
    assert prune["executed"] is True


def test_retention_prunes_age_first_then_oldest_by_size_with_stable_order(tmp_path) -> None:
    db_path = tmp_path / "history.db"
    seeding_store = ExecutionHistoryStore(str(db_path), auto_prune=False)
    _record_dispatch(seeding_store, execution_id="exec-age-001")
    _record_dispatch(seeding_store, execution_id="exec-age-002")
    _record_dispatch(seeding_store, execution_id="exec-size-003")

    with sqlite3.connect(str(db_path)) as connection:
        connection.execute(
            "UPDATE workflows SET started_at = ?, completed_at = ? WHERE workflow_id = ?",
            ("2000-01-01T00:00:00+00:00", "2000-01-01T00:00:01+00:00", "wf-exec-age-001"),
        )
        connection.execute(
            "UPDATE workflows SET started_at = ?, completed_at = ? WHERE workflow_id = ?",
            ("2000-01-01T00:00:00+00:00", "2000-01-01T00:00:02+00:00", "wf-exec-age-002"),
        )
        connection.execute(
            "UPDATE workflows SET started_at = ?, completed_at = ? WHERE workflow_id = ?",
            ("2100-03-20T12:00:00+00:00", "2100-03-20T12:00:01+00:00", "wf-exec-size-003"),
        )

    pruning_store = ExecutionHistoryStore(
        str(db_path),
        retention_days=1,
        max_storage_bytes=1,
        auto_prune=True,
    )
    summary = _record_dispatch(pruning_store, execution_id="exec-trigger-999")

    prune = summary["prune"]
    assert isinstance(prune, dict)
    assert prune["order"] == ["age", "size"]
    assert prune["by_age_workflow_count"] == 2
    assert prune["by_size_workflow_count"] >= 1
    pruned_workflow_ids = prune["pruned_workflow_ids"]
    assert isinstance(pruned_workflow_ids, list)
    assert pruned_workflow_ids[:2] == ["wf-exec-age-001", "wf-exec-age-002"]
    assert "wf-exec-size-003" in pruned_workflow_ids


def test_retention_summary_is_structured_and_sanitized(tmp_path) -> None:
    db_path = tmp_path / "history.db"
    seeding_store = ExecutionHistoryStore(str(db_path), auto_prune=False)
    _record_dispatch(
        seeding_store,
        execution_id="exec-sanitization-old",
        context={
            "request_text": "DO-NOT-LEAK",
            "artifact_path": "/tmp/old/file.txt",
        },
        telemetry_payload={
            "artifact_reference": {
                "artifact_path": "/tmp/old/telemetry.json",
            }
        },
    )

    with sqlite3.connect(str(db_path)) as connection:
        connection.execute(
            "UPDATE workflows SET started_at = ?, completed_at = ? WHERE workflow_id = ?",
            (
                "2000-01-01T00:00:00+00:00",
                "2000-01-01T00:00:01+00:00",
                "wf-exec-sanitization-old",
            ),
        )

    pruning_store = ExecutionHistoryStore(str(db_path), retention_days=1, max_storage_bytes=1)
    summary = _record_dispatch(
        pruning_store,
        execution_id="exec-sanitization-new",
        context={"request_text": "DO-NOT-LEAK-NEW"},
        telemetry_payload={
            "artifact_reference": {
                "artifact_path": "/tmp/new/telemetry.json",
            }
        },
    )

    serialized_summary = json.dumps(summary, sort_keys=True)
    assert "DO-NOT-LEAK" not in serialized_summary
    assert "DO-NOT-LEAK-NEW" not in serialized_summary
    prune = summary["prune"]
    assert isinstance(prune, dict)
    impact = prune["artifact_reference_impact"]
    assert isinstance(impact, dict)
    assert impact["artifact_reference_count"] >= 1
    assert impact["path_reference_count"] >= 1

    timeline = pruning_store.timeline_by_execution_id("exec-sanitization-new")
    workflow_metadata = timeline["workflow"]["metadata_json"]
    assert isinstance(workflow_metadata, dict)
    retention = workflow_metadata["retention"]
    assert isinstance(retention, dict)
    assert retention["policy"]["history_days"] == 1
    assert "request_text" not in json.dumps(retention, sort_keys=True)


def test_retention_execution_is_safe_under_concurrent_dispatches(tmp_path) -> None:
    store = ExecutionHistoryStore(str(tmp_path / "history.db"), auto_prune=True)

    errors: list[Exception] = []

    def _worker(index: int) -> None:
        try:
            _record_dispatch(
                store,
                execution_id=f"exec-concurrency-{index:03d}",
                context={"request_id": f"req-{index}"},
            )
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=_worker, args=(index,)) for index in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors

    with sqlite3.connect(str(tmp_path / "history.db")) as connection:
        execution_ids = [
            row[0]
            for row in connection.execute(
                "SELECT execution_id FROM workflows ORDER BY execution_id ASC"
            ).fetchall()
        ]

    assert execution_ids
    for execution_id in execution_ids:
        timeline = store.timeline_by_execution_id(str(execution_id))
        assert timeline["command"]["command_id"] == timeline["workflow"]["command_id"]


def test_database_size_uses_active_pages_excluding_freelist(tmp_path) -> None:
    db_path = tmp_path / "pages.db"
    with sqlite3.connect(str(db_path)) as connection:
        connection.execute(
            "CREATE TABLE payloads (id INTEGER PRIMARY KEY, payload TEXT NOT NULL)"
        )
        payload = "x" * 4096
        connection.executemany(
            "INSERT INTO payloads (payload) VALUES (?)",
            [(payload,) for _ in range(64)],
        )
        connection.commit()

        before_bytes = _database_size_bytes(connection)

        connection.execute("DELETE FROM payloads")
        connection.commit()

        after_bytes = _database_size_bytes(connection)
        freelist_count = int(
            connection.execute("PRAGMA freelist_count").fetchone()[0]
        )

    assert freelist_count > 0
    assert after_bytes < before_bytes


def test_invalid_execution_history_retention_overrides_fall_back_to_defaults(tmp_path) -> None:
    result = dispatch_input(
        "/show-status",
        command_executor=lambda _name, _args: "ok",
        conversation_handler=lambda text: text,
        explicit_context={
            "execution_history_db": str(tmp_path / "history.db"),
            "execution_history_retention_days": True,
            "execution_history_max_storage_gb": False,
            "execution_history_auto_prune": "invalid",
        },
    )

    assert result.route is RouteKind.COMMAND
    assert result.execution_error is None
    assert result.runtime_error is None
    assert result.telemetry_payload is not None
    retention = result.telemetry_payload["retention"]
    assert isinstance(retention, dict)
    policy = retention["policy"]
    assert isinstance(policy, dict)
    assert policy["history_days"] == 30
    assert policy["max_storage_gb"] == 2.0
    assert policy["max_storage_bytes"] == 2 * 1024 * 1024 * 1024
    assert policy["auto_prune"] is True
