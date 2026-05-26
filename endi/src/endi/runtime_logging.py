"""Structured JSON Lines runtime logging for ENDI CLI dispatches."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from endi.context import sanitize_for_telemetry


def write_json_event(path: str | None, event: dict[str, object]) -> None:
    """Append one sanitized JSON event when a log path is configured."""
    if path is None or not path:
        return
    log_path = Path(path).expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        **sanitize_for_telemetry(event),
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        handle.write("\n")
