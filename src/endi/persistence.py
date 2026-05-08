"""SQLite execution history persistence for deterministic run timeline reconstruction."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from endi.context import sanitize_for_persistence
from endi.conversation import RuntimeErrorEnvelope
from endi.workflow import EventType, StageEvent, WorkflowStage, WorkflowStatus

DEFAULT_RETENTION_DAYS = 30
DEFAULT_MAX_STORAGE_GB = 2
_BYTES_PER_GB = 1024 * 1024 * 1024


@dataclass(frozen=True)
class PersistenceContractError(ValueError):
    """Deterministic structured persistence contract violation."""

    message: str
    code: str
    details: dict[str, object]


@dataclass(frozen=True)
class RetentionPolicy:
    history_days: int
    max_storage_bytes: int
    auto_prune: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "history_days": self.history_days,
            "max_storage_gb": self.max_storage_bytes / _BYTES_PER_GB,
            "max_storage_bytes": self.max_storage_bytes,
            "auto_prune": self.auto_prune,
        }


class ExecutionHistoryStore:
    """SQLite-backed persistence for execution history entities and correlation queries."""

    def __init__(
        self,
        database_path: str,
        *,
        retention_days: int = DEFAULT_RETENTION_DAYS,
        max_storage_gb: int = DEFAULT_MAX_STORAGE_GB,
        auto_prune: bool = True,
        max_storage_bytes: int | None = None,
    ) -> None:
        self._database_path = str(Path(database_path))
        if retention_days <= 0:
            raise ValueError("retention_days must be positive")
        if max_storage_bytes is not None and max_storage_bytes <= 0:
            raise ValueError("max_storage_bytes must be positive")
        if max_storage_bytes is None and max_storage_gb <= 0:
            raise ValueError("max_storage_gb must be positive")
        self._retention_policy = RetentionPolicy(
            history_days=retention_days,
            max_storage_bytes=(
                max_storage_bytes
                if max_storage_bytes is not None
                else max_storage_gb * _BYTES_PER_GB
            ),
            auto_prune=auto_prune,
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def migrate(self) -> None:
        """Create v1 schema if it does not already exist."""
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS commands (
                    command_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    command_name TEXT NOT NULL,
                    route TEXT NOT NULL,
                    status TEXT NOT NULL,
                    command_arg_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id TEXT PRIMARY KEY,
                    command_id TEXT NOT NULL,
                    execution_id TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    duration_ms INTEGER,
                    metadata_json TEXT NOT NULL,
                    FOREIGN KEY (command_id) REFERENCES commands(command_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS steps (
                    step_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    stage TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    failure_type TEXT,
                    occurred_at TEXT NOT NULL,
                    duration_ms INTEGER,
                    metadata_json TEXT NOT NULL,
                    UNIQUE(workflow_id, sequence),
                    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS tool_calls (
                    tool_call_id TEXT PRIMARY KEY,
                    step_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    status_code TEXT,
                    created_at TEXT NOT NULL,
                    duration_ms INTEGER,
                    metadata_json TEXT NOT NULL,
                    FOREIGN KEY (step_id) REFERENCES steps(step_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS runtime_errors (
                    runtime_error_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    command_id TEXT,
                    workflow_id TEXT,
                    step_id TEXT,
                    error_type TEXT NOT NULL,
                    error_code TEXT NOT NULL,
                    error_component TEXT NOT NULL,
                    status_code TEXT,
                    created_at TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
                    FOREIGN KEY (command_id) REFERENCES commands(command_id) ON DELETE CASCADE,
                    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE,
                    FOREIGN KEY (step_id) REFERENCES steps(step_id) ON DELETE SET NULL
                );

                CREATE INDEX IF NOT EXISTS idx_commands_session_id ON commands(session_id);
                CREATE INDEX IF NOT EXISTS idx_workflows_execution_id ON workflows(execution_id);
                CREATE INDEX IF NOT EXISTS idx_steps_workflow_sequence
                    ON steps(workflow_id, sequence);
                CREATE INDEX IF NOT EXISTS idx_runtime_errors_workflow_id
                    ON runtime_errors(workflow_id);
                """
            )

    def record_command_dispatch(
        self,
        *,
        session_id: str,
        command_id: str,
        workflow_id: str,
        execution_id: str,
        command_name: str,
        command_arg_count: int,
        route: str,
        workflow_status: WorkflowStatus,
        events: list[StageEvent],
        context: Mapping[str, object],
        telemetry_payload: Mapping[str, object] | None,
        runtime_error: RuntimeErrorEnvelope | None,
    ) -> dict[str, object]:
        """Persist command/workflow timeline rows and optional runtime error envelope."""
        try:
            self.migrate()
        except sqlite3.Error as exc:
            raise PersistenceContractError(
                message="Execution history storage is unavailable.",
                code="persistence_stage_write_error",
                details={
                    "execution_id": execution_id,
                    "workflow_id": workflow_id,
                },
            ) from exc
        started_at = _utc_now()
        metadata_context = sanitize_for_persistence(dict(context))
        metadata_telemetry = (
            sanitize_for_persistence(dict(telemetry_payload))
            if telemetry_payload is not None
            else {}
        )
        workflow_duration_ms = _workflow_duration_ms(events)

        for event in events:
            step_id = _step_id(workflow_id, event.sequence)
            try:
                with self._connect() as connection:
                    now = _utc_now()
                    session_metadata = {
                        "correlation": {"session_id": session_id},
                        "event": {
                            "timestamp": started_at,
                            "component": "session",
                            "action": "command_dispatch",
                            "status": workflow_status.value,
                            "duration_ms": workflow_duration_ms,
                        },
                    }
                    command_metadata = {
                        "correlation": {
                            "session_id": session_id,
                            "command_id": command_id,
                        },
                        "event": {
                            "timestamp": started_at,
                            "component": "command",
                            "action": "command_dispatch",
                            "status": workflow_status.value,
                            "duration_ms": workflow_duration_ms,
                        },
                        "context": metadata_context,
                    }
                    workflow_metadata = {
                        "correlation": {
                            "session_id": session_id,
                            "command_id": command_id,
                            "workflow_id": workflow_id,
                            "execution_id": execution_id,
                        },
                        "event": {
                            "timestamp": started_at,
                            "component": "workflow",
                            "action": "workflow_dispatch",
                            "status": workflow_status.value,
                            "duration_ms": workflow_duration_ms,
                        },
                        "telemetry": metadata_telemetry,
                    }
                    step_metadata = {
                        "correlation": {
                            "session_id": session_id,
                            "command_id": command_id,
                            "workflow_id": workflow_id,
                            "step_id": step_id,
                            "execution_id": execution_id,
                        },
                        "event": {
                            "timestamp": event.timestamp,
                            "component": event.stage.value,
                            "action": event.event_type.value,
                            "status": _event_status(event.event_type),
                            "duration_ms": event.duration_ms,
                        },
                    }

                    connection.execute(
                        """
                        INSERT INTO sessions (session_id, created_at, metadata_json)
                        VALUES (?, ?, ?)
                        ON CONFLICT(session_id) DO NOTHING
                        """,
                        (session_id, started_at, _json_dump(session_metadata)),
                    )
                    connection.execute(
                        """
                        INSERT INTO commands (
                            command_id,
                            session_id,
                            command_name,
                            route,
                            status,
                            command_arg_count,
                            created_at,
                            metadata_json
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(command_id) DO UPDATE SET
                            route = excluded.route,
                            status = excluded.status,
                            command_arg_count = excluded.command_arg_count,
                            metadata_json = excluded.metadata_json
                        """,
                        (
                            command_id,
                            session_id,
                            command_name,
                            route,
                            workflow_status.value,
                            command_arg_count,
                            started_at,
                            _json_dump(command_metadata),
                        ),
                    )
                    connection.execute(
                        """
                        INSERT INTO workflows (
                            workflow_id,
                            command_id,
                            execution_id,
                            status,
                            started_at,
                            completed_at,
                            duration_ms,
                            metadata_json
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(workflow_id) DO UPDATE SET
                            status = excluded.status,
                            completed_at = excluded.completed_at,
                            duration_ms = excluded.duration_ms,
                            metadata_json = excluded.metadata_json
                        """,
                        (
                            workflow_id,
                            command_id,
                            execution_id,
                            workflow_status.value,
                            started_at,
                            now,
                            _duration_ms(started_at, now),
                            _json_dump(workflow_metadata),
                        ),
                    )
                    connection.execute(
                        """
                        INSERT INTO steps (
                            step_id,
                            workflow_id,
                            sequence,
                            stage,
                            event_type,
                            status,
                            failure_type,
                            occurred_at,
                            duration_ms,
                            metadata_json
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(step_id) DO UPDATE SET
                            stage = excluded.stage,
                            event_type = excluded.event_type,
                            status = excluded.status,
                            failure_type = excluded.failure_type,
                            occurred_at = excluded.occurred_at,
                            duration_ms = excluded.duration_ms,
                            metadata_json = excluded.metadata_json
                        """,
                        (
                            step_id,
                            workflow_id,
                            event.sequence,
                            event.stage.value,
                            event.event_type.value,
                            _event_status(event.event_type),
                            event.failure_type,
                            event.timestamp,
                            event.duration_ms,
                            _json_dump(step_metadata),
                        ),
                    )
            except sqlite3.Error as exc:
                raise PersistenceContractError(
                    message="Atomic stage transition persistence failed.",
                    code="persistence_stage_write_error",
                    details={
                        "execution_id": execution_id,
                        "workflow_id": workflow_id,
                        "step_id": step_id,
                        "stage": event.stage.value,
                        "event_type": event.event_type.value,
                    },
                ) from exc

        execute_step = next(
            (
                event
                for event in reversed(events)
                if event.stage is WorkflowStage.EXECUTE
                and event.event_type in {EventType.STAGE_COMPLETED, EventType.STAGE_FAILED}
            ),
            None,
        )
        if execute_step is None:
            execute_step = next(
                (event for event in events if event.stage is WorkflowStage.EXECUTE),
                None,
            )
        if execute_step is not None:
            execute_step_id = _step_id(workflow_id, execute_step.sequence)
            try:
                with self._connect() as connection:
                    connection.execute(
                        """
                        INSERT INTO tool_calls (
                            tool_call_id,
                            step_id,
                            tool_name,
                            status_code,
                            created_at,
                            duration_ms,
                            metadata_json
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(tool_call_id) DO UPDATE SET
                            status_code = excluded.status_code,
                            metadata_json = excluded.metadata_json
                        """,
                        (
                            f"tool-{command_id}",
                            execute_step_id,
                            command_name,
                            runtime_error.status_code if runtime_error is not None else "success",
                            _utc_now(),
                            None,
                            _json_dump(
                                {
                                    "correlation": {
                                        "session_id": session_id,
                                        "command_id": command_id,
                                        "workflow_id": workflow_id,
                                        "step_id": execute_step_id,
                                    },
                                    "command_arg_count": command_arg_count,
                                }
                            ),
                        ),
                    )
            except sqlite3.Error as exc:
                raise PersistenceContractError(
                    message="Tool call persistence failed.",
                    code="persistence_tool_call_write_error",
                    details={
                        "execution_id": execution_id,
                        "workflow_id": workflow_id,
                        "step_id": execute_step_id,
                        "tool_call_id": f"tool-{command_id}",
                    },
                ) from exc

        if runtime_error is not None:
            runtime_error_payload = {
                "error": {
                    "type": "runtime_error",
                    "code": runtime_error.code,
                    "component": runtime_error.component.value,
                    "status_code": runtime_error.status_code,
                    "details": sanitize_for_persistence(runtime_error.details),
                }
            }
            runtime_error_step_id = _resolve_runtime_error_step_id(
                workflow_id=workflow_id,
                runtime_error=runtime_error,
                events=events,
            )
            try:
                with self._connect() as connection:
                    connection.execute(
                        """
                        INSERT INTO runtime_errors (
                            runtime_error_id,
                            session_id,
                            command_id,
                            workflow_id,
                            step_id,
                            error_type,
                            error_code,
                            error_component,
                            status_code,
                            created_at,
                            details_json
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(runtime_error_id) DO UPDATE SET
                            error_code = excluded.error_code,
                            error_component = excluded.error_component,
                            status_code = excluded.status_code,
                            details_json = excluded.details_json
                        """,
                        (
                            f"err-{command_id}",
                            session_id,
                            command_id,
                            workflow_id,
                            runtime_error_step_id,
                            "runtime_error",
                            runtime_error.code,
                            runtime_error.component.value,
                            runtime_error.status_code,
                            _utc_now(),
                            _json_dump(runtime_error_payload),
                        ),
                    )
            except sqlite3.Error as exc:
                raise PersistenceContractError(
                    message="Runtime error persistence failed.",
                    code="persistence_runtime_error_write_error",
                    details={
                        "execution_id": execution_id,
                        "workflow_id": workflow_id,
                        "runtime_error_id": f"err-{command_id}",
                        "step_id": runtime_error_step_id,
                    },
                ) from exc

        try:
            retention_summary = self._apply_retention_policy(
                protected_workflow_id=workflow_id,
                reference_timestamp=_utc_now(),
            )
            self._attach_retention_summary(
                workflow_id=workflow_id,
                retention_summary=retention_summary,
            )
        except sqlite3.Error as exc:
            raise PersistenceContractError(
                message="Retention and auto-prune execution failed.",
                code="persistence_retention_prune_error",
                details={
                    "execution_id": execution_id,
                    "workflow_id": workflow_id,
                },
            ) from exc

        return retention_summary

    def timeline_by_execution_id(self, execution_id: str) -> dict[str, object]:
        """Reconstruct deterministic timeline data from execution correlation ID."""
        with self._connect() as connection:
            workflow_row = connection.execute(
                "SELECT * FROM workflows WHERE execution_id = ?",
                (execution_id,),
            ).fetchone()
            if workflow_row is None:
                raise PersistenceContractError(
                    message="Execution ID not found.",
                    code="persistence_missing_execution",
                    details={"execution_id": execution_id},
                )

            command_id = str(workflow_row["command_id"])
            command_row = connection.execute(
                "SELECT * FROM commands WHERE command_id = ?",
                (command_id,),
            ).fetchone()
            if command_row is None:
                raise PersistenceContractError(
                    message="Missing command parent linkage for workflow.",
                    code="persistence_missing_parent_linkage",
                    details={"execution_id": execution_id, "command_id": command_id},
                )

            session_id = str(command_row["session_id"])
            session_row = connection.execute(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if session_row is None:
                raise PersistenceContractError(
                    message="Missing session parent linkage for command.",
                    code="persistence_missing_parent_linkage",
                    details={"execution_id": execution_id, "session_id": session_id},
                )

            steps = connection.execute(
                "SELECT * FROM steps WHERE workflow_id = ? ORDER BY sequence ASC",
                (str(workflow_row["workflow_id"]),),
            ).fetchall()
            runtime_error = connection.execute(
                (
                    "SELECT * FROM runtime_errors "
                    "WHERE workflow_id = ? "
                    "ORDER BY created_at ASC LIMIT 1"
                ),
                (str(workflow_row["workflow_id"]),),
            ).fetchone()
            tool_calls = connection.execute(
                """
                SELECT t.*
                FROM tool_calls AS t
                JOIN steps AS s ON s.step_id = t.step_id
                WHERE s.workflow_id = ?
                ORDER BY s.sequence ASC, t.created_at ASC
                """,
                (str(workflow_row["workflow_id"]),),
            ).fetchall()

        return {
            "session": _row_to_dict(session_row),
            "command": _row_to_dict(command_row),
            "workflow": _row_to_dict(workflow_row),
            "steps": [_row_to_dict(step) for step in steps],
            "tool_calls": [_row_to_dict(tool_call) for tool_call in tool_calls],
            "runtime_error": _row_to_dict(runtime_error) if runtime_error is not None else None,
        }

    def _apply_retention_policy(
        self,
        *,
        protected_workflow_id: str,
        reference_timestamp: str,
    ) -> dict[str, object]:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            storage_before = _database_size_bytes(connection)
            rows_before = _table_counts(connection)
            prune_summary = {
                "order": ["age", "size"],
                "pruned_workflow_ids": [],
                "executed": self._retention_policy.auto_prune,
                "by_age_workflow_count": 0,
                "by_size_workflow_count": 0,
                "affected_rows": {
                    "sessions": 0,
                    "commands": 0,
                    "workflows": 0,
                    "steps": 0,
                    "tool_calls": 0,
                    "runtime_errors": 0,
                },
                "artifact_reference_impact": {
                    "artifact_reference_count": 0,
                    "path_reference_count": 0,
                },
                "storage": {
                    "before_bytes": storage_before,
                    "after_bytes": storage_before,
                },
            }
            if self._retention_policy.auto_prune:
                cutoff = (
                    datetime.fromisoformat(reference_timestamp)
                    - timedelta(days=self._retention_policy.history_days)
                ).isoformat()
                by_age = self._workflow_prune_candidates(
                    connection=connection,
                    protected_workflow_id=protected_workflow_id,
                    older_than=cutoff,
                )
                for workflow in by_age:
                    pruned_workflow_ids = prune_summary["pruned_workflow_ids"]
                    assert isinstance(pruned_workflow_ids, list)
                    pruned_workflow_ids.append(str(workflow["workflow_id"]))
                    _accumulate_reference_impact(
                        prune_summary,
                        self._collect_reference_impact(
                            connection=connection,
                            command_id=str(workflow["command_id"]),
                        ),
                    )
                    self._delete_command(connection, command_id=str(workflow["command_id"]))
                prune_summary["by_age_workflow_count"] = len(by_age)

                while _database_size_bytes(connection) > self._retention_policy.max_storage_bytes:
                    oldest = self._oldest_workflow_candidate(
                        connection=connection,
                        protected_workflow_id=protected_workflow_id,
                    )
                    if oldest is None:
                        break
                    pruned_workflow_ids = prune_summary["pruned_workflow_ids"]
                    assert isinstance(pruned_workflow_ids, list)
                    pruned_workflow_ids.append(str(oldest["workflow_id"]))
                    _accumulate_reference_impact(
                        prune_summary,
                        self._collect_reference_impact(
                            connection=connection,
                            command_id=str(oldest["command_id"]),
                        ),
                    )
                    self._delete_command(connection, command_id=str(oldest["command_id"]))
                    by_size_count = prune_summary["by_size_workflow_count"]
                    assert isinstance(by_size_count, int)
                    prune_summary["by_size_workflow_count"] = by_size_count + 1

                connection.execute(
                    """
                    DELETE FROM sessions
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM commands
                        WHERE commands.session_id = sessions.session_id
                    )
                    """
                )

            rows_after = _table_counts(connection)
            storage_after = _database_size_bytes(connection)
            prune_summary["storage"] = {
                "before_bytes": storage_before,
                "after_bytes": storage_after,
            }
            affected_rows = prune_summary["affected_rows"]
            assert isinstance(affected_rows, dict)
            for table in rows_before:
                affected_rows[table] = max(
                    rows_before[table] - rows_after[table],
                    0,
                )

        return {
            "policy": self._retention_policy.as_dict(),
            "prune": prune_summary,
        }

    def _attach_retention_summary(
        self,
        *,
        workflow_id: str,
        retention_summary: Mapping[str, object],
    ) -> None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT metadata_json FROM workflows WHERE workflow_id = ?",
                (workflow_id,),
            ).fetchone()
            if row is None:
                return
            metadata = _json_load(str(row["metadata_json"]))
            metadata["retention"] = sanitize_for_persistence(dict(retention_summary))
            connection.execute(
                "UPDATE workflows SET metadata_json = ? WHERE workflow_id = ?",
                (_json_dump(metadata), workflow_id),
            )

    def _workflow_prune_candidates(
        self,
        *,
        connection: sqlite3.Connection,
        protected_workflow_id: str,
        older_than: str,
    ) -> list[sqlite3.Row]:
        return list(
            connection.execute(
                """
                SELECT workflow_id, command_id
                FROM workflows
                WHERE workflow_id != ?
                  AND COALESCE(completed_at, started_at) < ?
                ORDER BY COALESCE(completed_at, started_at) ASC, workflow_id ASC
                """,
                (protected_workflow_id, older_than),
            ).fetchall()
        )

    def _oldest_workflow_candidate(
        self,
        *,
        connection: sqlite3.Connection,
        protected_workflow_id: str,
    ) -> sqlite3.Row | None:
        row = connection.execute(
            """
            SELECT workflow_id, command_id
            FROM workflows
            WHERE workflow_id != ?
            ORDER BY COALESCE(completed_at, started_at) ASC, workflow_id ASC
            LIMIT 1
            """,
            (protected_workflow_id,),
        ).fetchone()
        if row is None:
            return None
        assert isinstance(row, sqlite3.Row)
        return row

    def _delete_command(
        self,
        connection: sqlite3.Connection,
        *,
        command_id: str,
    ) -> None:
        connection.execute(
            "DELETE FROM commands WHERE command_id = ?",
            (command_id,),
        )

    def _collect_reference_impact(
        self,
        *,
        connection: sqlite3.Connection,
        command_id: str,
    ) -> dict[str, int]:
        payloads: list[str] = []
        command_payload = connection.execute(
            "SELECT metadata_json FROM commands WHERE command_id = ?",
            (command_id,),
        ).fetchone()
        if command_payload is not None:
            payloads.append(str(command_payload["metadata_json"]))

        workflow_payloads = connection.execute(
            "SELECT metadata_json FROM workflows WHERE command_id = ?",
            (command_id,),
        ).fetchall()
        payloads.extend(str(row["metadata_json"]) for row in workflow_payloads)

        step_payloads = connection.execute(
            """
            SELECT s.metadata_json
            FROM steps AS s
            JOIN workflows AS w ON w.workflow_id = s.workflow_id
            WHERE w.command_id = ?
            """,
            (command_id,),
        ).fetchall()
        payloads.extend(str(row["metadata_json"]) for row in step_payloads)

        tool_payloads = connection.execute(
            """
            SELECT t.metadata_json
            FROM tool_calls AS t
            JOIN steps AS s ON s.step_id = t.step_id
            JOIN workflows AS w ON w.workflow_id = s.workflow_id
            WHERE w.command_id = ?
            """,
            (command_id,),
        ).fetchall()
        payloads.extend(str(row["metadata_json"]) for row in tool_payloads)

        runtime_payloads = connection.execute(
            "SELECT details_json FROM runtime_errors WHERE command_id = ?",
            (command_id,),
        ).fetchall()
        payloads.extend(str(row["details_json"]) for row in runtime_payloads)

        artifact_references = 0
        path_references = 0
        for payload in payloads:
            parsed_payload = _json_load(payload)
            counts = _count_artifact_and_path_references(parsed_payload)
            artifact_references += counts["artifact_reference_count"]
            path_references += counts["path_reference_count"]
        return {
            "artifact_reference_count": artifact_references,
            "path_reference_count": path_references,
        }


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _duration_ms(started_at_iso: str, completed_at_iso: str) -> int:
    started_at = datetime.fromisoformat(started_at_iso)
    completed_at = datetime.fromisoformat(completed_at_iso)
    return int((completed_at - started_at).total_seconds() * 1000)


def _workflow_duration_ms(events: list[StageEvent]) -> int:
    duration_ms = sum(
        event.duration_ms
        for event in events
        if event.event_type in {EventType.STAGE_COMPLETED, EventType.STAGE_FAILED}
    )
    return max(duration_ms, 0)


def _event_status(event_type: EventType) -> str:
    if event_type is EventType.STAGE_FAILED:
        return "failure"
    if event_type is EventType.STAGE_COMPLETED:
        return "success"
    return "in_progress"


def _json_dump(payload: Mapping[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _json_load(raw_payload: str) -> dict[str, object]:
    try:
        loaded = json.loads(raw_payload)
    except json.JSONDecodeError:
        return {}
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _step_id(workflow_id: str, sequence: int) -> str:
    return f"{workflow_id}:step:{sequence:03d}"


def _resolve_runtime_error_step_id(
    *,
    workflow_id: str,
    runtime_error: RuntimeErrorEnvelope,
    events: list[StageEvent],
) -> str | None:
    details = runtime_error.details
    if not isinstance(details, Mapping):
        return None

    workflow_stage = details.get("workflow_stage")
    if not isinstance(workflow_stage, str) or not workflow_stage:
        return None

    for event in sorted(events, key=lambda event: event.sequence, reverse=True):
        if event.stage.value == workflow_stage:
            return _step_id(workflow_id, event.sequence)
    return None


def _row_to_dict(row: sqlite3.Row) -> dict[str, object]:
    result: dict[str, object] = {}
    for key in row.keys():
        value = row[key]
        if isinstance(value, str) and key.endswith("_json"):
            try:
                result[key] = json.loads(value)
            except json.JSONDecodeError:
                result[key] = {}
        else:
            result[key] = value
    return result


def _table_counts(connection: sqlite3.Connection) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table in ("sessions", "commands", "workflows", "steps", "tool_calls", "runtime_errors"):
        row = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
        count = int(row["count"]) if row is not None else 0
        counts[table] = count
    return counts


def _database_size_bytes(connection: sqlite3.Connection) -> int:
    page_size_row = connection.execute("PRAGMA page_size").fetchone()
    page_count_row = connection.execute("PRAGMA page_count").fetchone()
    freelist_count_row = connection.execute("PRAGMA freelist_count").fetchone()
    page_size = int(page_size_row[0]) if page_size_row is not None else 0
    page_count = int(page_count_row[0]) if page_count_row is not None else 0
    freelist_count = int(freelist_count_row[0]) if freelist_count_row is not None else 0
    used_pages = max(page_count - freelist_count, 0)
    return page_size * used_pages


def _accumulate_reference_impact(
    prune_summary: dict[str, object],
    impact: Mapping[str, int],
) -> None:
    artifact_impact = prune_summary["artifact_reference_impact"]
    assert isinstance(artifact_impact, dict)
    artifact_impact["artifact_reference_count"] = int(
        artifact_impact["artifact_reference_count"]
    ) + int(impact["artifact_reference_count"])
    artifact_impact["path_reference_count"] = int(
        artifact_impact["path_reference_count"]
    ) + int(impact["path_reference_count"])


def _count_artifact_and_path_references(payload: object) -> dict[str, int]:
    artifact_count = 0
    path_count = 0

    if isinstance(payload, Mapping):
        for key, value in payload.items():
            normalized_key = str(key).lower()
            if "artifact" in normalized_key:
                artifact_count += 1
            if "path" in normalized_key:
                path_count += 1
            nested = _count_artifact_and_path_references(value)
            artifact_count += nested["artifact_reference_count"]
            path_count += nested["path_reference_count"]
    elif isinstance(payload, Sequence) and not isinstance(payload, str):
        for item in payload:
            nested = _count_artifact_and_path_references(item)
            artifact_count += nested["artifact_reference_count"]
            path_count += nested["path_reference_count"]

    return {
        "artifact_reference_count": artifact_count,
        "path_reference_count": path_count,
    }
