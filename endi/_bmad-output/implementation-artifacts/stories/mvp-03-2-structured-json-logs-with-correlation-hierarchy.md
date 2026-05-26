# Story MVP-03.2: Structured JSON Logs with Baseline Correlation Hierarchy

Status: done

## Metadata
- **Story ID:** `MVP-03.2`
- **Story Key:** `mvp-03-2-structured-json-logs-with-correlation-hierarchy`
- **Epic:** `EPIC-MVP-03` Persistence and Observability Baseline
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 3`
- **Type:** `Observability Core`

## Story
As an operator, I want end-to-end correlated logs, so that failures can be traced quickly.

## Traceability
- **Functional Requirements:** `FR-007`
- **Architecture Constraints:** `ADR-010`, `ADR-011`, `ADR-019`

## Acceptance Criteria
1. Every emitted execution event includes deterministic envelope fields: correlation identifiers, component, action, status, duration, and timestamp.
2. Baseline correlation hierarchy is continuous for command path boundaries: `session -> command -> workflow -> step`.
3. Error events use structured classification fields (`type`, `code`, `component`) and preserve correlation continuity.
4. Command and conversation paths preserve parity at shared externally observable boundaries (event envelope semantics, error classification semantics, and sanitization behavior).
5. Emitted logs and associated artifacts do not leak sensitive raw text by default unless explicit opt-in is provided.

## Scope

### In Scope
- Structured JSON event envelope design and baseline instrumentation for runtime boundaries.
- Deterministic correlation propagation across `session`, `command`, `workflow`, and `step` events.
- Structured error event schema and mapping for runtime/contract failures.
- Sanitized event emission behavior for command and conversation shared boundaries.

### Out of Scope
- OpenTelemetry exporter rollout or external sink integration.
- Distributed tracing backends and centralized log shipping.
- Retention/prune policy implementation details (handled by `MVP-03.3`).

## Tasks / Subtasks
- [x] Define canonical event envelope + schema invariants (AC: 1, 3)
  - [x] Lock deterministic field names/types for envelope and metadata payload.
  - [x] Define structured `runtime_error` event mapping with stable code/component taxonomy.
- [x] Implement baseline correlation propagation and emission points (AC: 1, 2)
  - [x] Ensure parent linkage continuity across `session -> command -> workflow -> step`.
  - [x] Enforce deterministic status/action mapping for equivalent logical outcomes.
- [x] Preserve command/conversation parity at shared boundaries (AC: 4)
  - [x] Ensure common boundary envelopes share schema-compatible fields and deterministic error classification semantics.
  - [x] Keep conversation-specific extra fields additive only (no shared boundary drift).
- [x] Apply sensitive-by-default sanitization to emitted event payloads (AC: 5)
  - [x] Prevent raw `request_text`/`response_text`/`conversation_text` style field leakage by default.
  - [x] Ensure recursive sanitization for nested payload structures.
- [x] Add strict-gate tests for envelope schema, correlation continuity, parity, and sanitization (AC: 1, 2, 3, 4, 5)
  - [x] Include deterministic regression assertions for stable event structure.
  - [x] Include structured error envelope assertions for `type`, `code`, `component`.

## Dev Notes

### Carry-Forward Guardrails (Mandatory)
- Deterministic behavior: identical logical execution outcomes must produce stable event envelope/status/code mappings.
- Safety-by-default: default emission and persistence paths must avoid side effects that bypass existing confirmation/authorization control boundaries.
- Command/conversation parity: at shared externally observable boundaries, maintain equivalent envelope semantics and deterministic error classification.
- Sensitive-by-default handling: raw free-form text and similarly sensitive fields remain excluded/redacted unless explicit opt-in exists.

### Architecture Compliance
- Align with architecture observability model for structured envelopes and correlation continuity.
- Keep strict-gate quality bar for core runtime/observability stories per `ADR-011`.
- Ensure retention compatibility with local-first observability/persistence constraints (`ADR-019`) without implementing retention logic here.

### File Structure Requirements
- Keep observability/runtime implementation changes inside existing `src/endi/` modules.
- Keep tests under `tests/` and focus on baseline schema + correlation + parity + sanitization behavior.
- Avoid unrelated refactors or module moves.

### Testing Requirements (Strict Gate)
- **Gate Level:** `Strict`
- Execute quality gates in WSL project `.venv`:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`
- Required test focus:
  - Event envelope schema validity and deterministic shape assertions.
  - Correlation chain continuity assertions for `session -> command -> workflow -> step`.
  - Structured runtime error event mapping assertions.
  - Command/conversation parity regression checks at shared externally observable boundaries.
  - Sensitive-by-default recursive sanitization checks.

### Review-Ready Exit Conditions
- [x] Acceptance criteria are traceably covered by tests.
- [x] Deterministic event schema mapping is stable under repeated runs.
- [x] No shared-boundary command/conversation parity regressions.
- [x] No raw-text leakage in emitted observability artifacts by default.

## Dependencies
- Existing lifecycle/execution correlation conventions in runtime routing.
- Structured runtime error envelope conventions already used by command and conversation paths.
- Story sequencing with `MVP-03.1` baseline persistence and follow-on `MVP-03.4` conversational extension.

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-03.2 — Structured JSON logs with baseline correlation hierarchy]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-007 Observability and Diagnostics]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#10. Observability Architecture]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `project-context.md`#Execution Environment]
- [Source: `project-context.md`#Agent Command Rules]

## Dev Agent Record

### Debug Log
- Added deterministic stage event timing (`timestamp`, `duration_ms`) in workflow lifecycle emission.
- Added canonical telemetry envelope fields and command execution event stream with correlation chain continuity.
- Added persistence metadata envelope fields for `session`, `command`, `workflow`, and `step` boundaries.
- Added/updated tests for envelope schema, runtime error classification parity, and baseline correlation continuity.

### Completion Notes
- Implemented canonical envelope semantics across emitted command and conversation telemetry: `timestamp`, `component`, `action`, `status`, `duration_ms`.
- Implemented deterministic command-path correlation continuity for shared observable boundaries with `session_id`, `command_id`, `workflow_id`, `execution_id`, and deterministic `step_id` on execution events.
- Preserved structured runtime error classification semantics with explicit `runtime_error.type`, `runtime_error.code`, and `runtime_error.component` in shared telemetry boundaries.
- Preserved sensitive-by-default behavior by keeping raw text fields excluded/sanitized from emitted telemetry and persistence artifacts.
- Post-review hardening aligned persistence step rows with emitted `StageEvent` envelope fields and linked `tool_calls.step_id` to execute completion/failure step events.
- Validation run results:
  - `ruff check src tests` ✅
  - `mypy src` ✅
  - `pytest` ✅ (`83 passed`)

## File List
- src/endi/workflow.py
- src/endi/routing.py
- src/endi/persistence.py
- tests/test_dual_mode_routing.py
- tests/test_persistence.py

## Change Log
- 2026-03-20: Implemented structured JSON telemetry envelopes with baseline correlation hierarchy continuity (`session -> command -> workflow -> step`), added runtime error classification parity at shared command/conversation boundaries, and extended strict-gate tests.
- 2026-03-20: Post-review hardening fixed persistence parity drift for step row fields and execute-step tool call linkage; regression tests added and strict gates re-run.
