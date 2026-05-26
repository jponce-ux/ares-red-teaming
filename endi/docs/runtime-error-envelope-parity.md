# Runtime Error Envelope Parity (Command + Conversation)

## Purpose

Document the unified runtime error contract introduced to preserve deterministic tool error semantics across command and conversation execution paths.

This is the reference for MVP-01.5 parity expectations at externally observable runtime surfaces.

## Shared Error Envelope

Defined in `src/endi/conversation.py`:

- `RuntimeErrorComponent`: `command | workflow | agent | tool`
- `RuntimeErrorEnvelope`:
  - `code: str`
  - `component: RuntimeErrorComponent`
  - `message: str`
  - `status_code: str | None`
  - `details: dict[str, object]`

## Where It Is Exposed

### Conversation Path

- `ConversationMetadata.runtime_error` (in `src/endi/conversation.py`)
- Also propagated to `DispatchResult.runtime_error` in `dispatch_input` (`src/endi/routing.py`)

Conversation keeps loop-level termination via `termination_reason` and now also carries tool-level deterministic error semantics when available.

### Command Path

- `DispatchResult.runtime_error` (in `src/endi/routing.py`)
- Command validation and workflow execution failures are mapped to `RuntimeErrorEnvelope`
- Command executors returning `ToolResult` are now interpreted natively:
  - tool success: output unwraps to tool payload
  - tool error: route becomes `execution_error` and envelope preserves deterministic tool status/error fields

## Runtime Surface Presentation

### CLI Output

In `src/endi/cli.py`, error rendering now prints `runtime_error` context when present.

- Validation and execution failure paths both print:
  - runtime `code`
  - runtime `component`
  - runtime `status_code`
- Selected context fields are surfaced when available:
  - `execution_id`
  - `tool_name`

This keeps existing validation/execution messages while exposing deterministic runtime contract details to operators.

### Conversation Telemetry

In `src/endi/routing.py`, conversation telemetry now includes a `runtime_error` object when conversation execution terminates with structured runtime error details.

Telemetry `runtime_error` fields:

- `code`
- `component`
- `status_code`

To avoid leaking sensitive values from free-form error content, conversation telemetry intentionally excludes `message` and `details`.

Payload continues to flow through `build_safe_telemetry_payload(...)` to preserve redaction/sanitization guarantees.

## Mapping Rules (Current)

### Conversation Runtime

1. Tool call action without tool name
   - `termination_reason = tool-failure`
   - `runtime_error.component = agent`
   - `runtime_error.code = missing_tool_name`
   - `runtime_error.status_code = invalid_contract`

2. Tool executor raises exception
   - `termination_reason = tool-failure`
   - `runtime_error.component = tool`
   - `runtime_error.code = tool_execution_error`
   - `runtime_error.status_code = execution_error`

3. Tool returns `ToolResult(status=error, status_code=...)`
   - `termination_reason = tool-failure`
   - `runtime_error.component = tool`
   - `runtime_error.code = tool_output.error.code` (fallback: `tool_execution_error`)
   - `runtime_error.status_code = tool_output.status_code`
   - `runtime_error.details` includes structured tool details + `tool_name` when present

### Command Dispatch

1. Command syntax/validation classification failure
   - `route = validation_error`
   - `runtime_error.component = command`
   - `runtime_error.code = validation_error.code`

2. Workflow validation failure
   - `route = validation_error`
   - `runtime_error.component = workflow`
   - `runtime_error.code = invalid_command_execution`
   - `runtime_error.details` includes execution id, stage, and failure type

3. Workflow runtime failure
   - `route = execution_error`
   - `runtime_error.component = workflow`
   - `runtime_error.code = failure_type`
   - `runtime_error.details` includes execution id, stage, and failure type

4. Command executor returns `ToolResult(status=error, status_code=...)`
   - `route = execution_error`
   - `runtime_error.component = tool`
   - `runtime_error.code = tool_result.error.code` (fallback: `tool_execution_error`)
   - `runtime_error.status_code = tool_result.status_code`
   - `runtime_error.details` includes structured tool details + `tool_name` when present

## Additional Contract Hardening

In `src/endi/tools.py`, registration now rejects invalid input schemas with non-string field names.

Rule:
- each schema key must be a non-empty `str`

This ensures malformed schemas cannot enter active registry state.

## Test Coverage

Primary tests validating parity and hardening:

- `tests/test_tool_contract.py`
  - non-string schema field rejection
  - dispatch-level parity for command/conversation tool error envelopes
- `tests/test_conversational_loop.py`
  - runtime_error presence/shape on failure paths
  - runtime_error absence on success path
- `tests/test_dual_mode_routing.py`
  - route behavior and dispatch invariants remain stable

## Quality Gates Run

Validated in WSL project `.venv`:

- `pytest -q tests/test_tool_contract.py tests/test_conversational_loop.py tests/test_dual_mode_routing.py`
- `ruff check .`
- `mypy src`
- `pytest -q`

All passing at implementation time.

## Notes for Future Evolution

To maintain compatibility guarantees for core contracts:

- Treat `RuntimeErrorEnvelope` as a core runtime contract surface.
- Prefer additive changes (`details` keys, optional fields) over breaking shape changes.
- Keep command/conversation parity tests strict for deterministic status mapping (`invalid_contract`, `invalid_input`, `not_found`, `execution_error`, `ok`).

## Discoverability

The runtime parity reference is linked from `README.md` under the "For full details" section:

- `docs/runtime-error-envelope-parity.md`
