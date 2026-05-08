# MVP-03 FR-007 Compliance Matrix

Source:
- `_bmad-output/planning-artifacts/endi-prd.md` (`FR-007`)
- `_bmad-output/planning-artifacts/endi-architecture-final.md` (observability/correlation boundaries)
- `_bmad-output/implementation-artifacts/epic-mvp-02-retro-2026-03-19.md` (MVP-03 risk-reduction actions)

Purpose: Define a compact, review-ready matrix for deterministic observability envelopes, correlation continuity, and sensitive-by-default redaction expectations across MVP-03 boundaries.

## Scope
Applies to MVP-03 stories:
- `mvp-03-1-sqlite-execution-history-schema-and-write-path`
- `mvp-03-2-structured-json-logs-with-correlation-hierarchy`
- `mvp-03-4-extended-correlation-for-conversational-tool-path`
- `mvp-03-3-retention-and-auto-prune-policy-implementation`

## Compliance Matrix

| Boundary | Required deterministic envelope fields | Correlation requirement | Sensitive-by-default requirement | Primary evidence artifact | Verification status |
|---|---|---|---|---|---|
| `session` | `timestamp`, `component`, `action`, `status`, `session_id` | Root of correlation chain | No raw request/response/conversation text persisted unless explicit opt-in | tests + structured event snapshots | `pending` |
| `command` | `timestamp`, `component`, `action`, `status`, `session_id`, `command_id` | `command_id` must reference valid parent `session_id` | Command payload excludes raw text by default; only normalized/sanitized metadata | tests + CLI/telemetry parity assertions | `pending` |
| `workflow` | `timestamp`, `component`, `action`, `status`, `session_id`, `command_id`, `workflow_id` | `workflow_id` must reference valid parent `command_id` | Workflow metadata excludes raw text fields by default | tests + runtime envelope assertions | `pending` |
| `step` | `timestamp`, `component`, `action`, `status`, `session_id`, `command_id`, `workflow_id`, `step_id` | `step_id` must reference valid parent `workflow_id` | Step-level artifacts must sanitize free-form text fields by default | tests + schema validation checks | `pending` |
| `agent` (conversational) | `timestamp`, `component`, `action`, `status`, `session_id`, `command_id`, `workflow_id`, `step_id`, `agent_id` | `agent_id` must reference valid parent `step_id` | No raw conversation/request/response text in persisted/telemetry artifacts by default | conversation-path regressions | `pending` |
| `tool_call` (conversational) | `timestamp`, `component`, `action`, `status`, `session_id`, `command_id`, `workflow_id`, `step_id`, `agent_id`, `tool_call_id` | `tool_call_id` must reference valid parent `agent_id` | Tool input/output telemetry must remain sanitized unless explicit opt-in | end-to-end correlation regressions | `pending` |
| `runtime_error` envelope | `status`, `error.type`, `error.code`, `error.message`, `error.component` (+ correlation fields at emitting boundary) | Error must preserve the boundary’s correlation chain fields | Error metadata must not embed raw text context by default | runtime error parity tests | `pending` |

## Deterministic Rules
- Identical logical inputs at a given boundary must produce stable envelope keys and status mapping.
- Correlation IDs must be structurally complete for the boundary depth being emitted.
- Missing required parent linkage is a contract violation and must surface deterministic structured failure.

## Redaction Rules
- Treat `request_text`, `response_text`, `conversation_text`, and equivalent raw/free-form payload fields as sensitive by default.
- Persist and emit sanitized structured metadata instead of raw text.
- If any explicit opt-in for raw text is introduced later, it must be scoped, auditable, and test-covered.

## Story-Level Traceability
- `mvp-03-1`: must satisfy matrix rows `session`, `command`, `workflow`, `step`, and `runtime_error` for durable history writes.
- `mvp-03-2`: must satisfy matrix rows `session`, `command`, `workflow`, `step`, and `runtime_error` for JSON log emission.
- `mvp-03-4`: must satisfy matrix rows `agent`, `tool_call`, and conversational `runtime_error` chain continuity.
- `mvp-03-3`: must preserve deterministic retention/prune events without violating redaction requirements.

## Review Checklist (Use in code review)
- [ ] Envelope field set is deterministic and complete for each touched boundary.
- [ ] Parent-child correlation links are present and valid.
- [ ] Raw text fields are excluded/sanitized by default in persistence and telemetry.
- [ ] Runtime errors preserve structured contract + correlation without sensitive leakage.
- [ ] Command/conversation externally observable parity is preserved where boundaries overlap.
