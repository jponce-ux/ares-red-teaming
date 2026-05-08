# Story MVP-03.4: Extended Correlation for Conversational Tool Path

Status: done

## Metadata
- **Story ID:** `MVP-03.4`
- **Story Key:** `mvp-03-4-extended-correlation-for-conversational-tool-path`
- **Epic:** `EPIC-MVP-03` Persistence and Observability Baseline
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 3`
- **Type:** `Observability Core`

## Story
As an SRE, I want correlated agent and tool-call telemetry, so that conversational executions can be reconstructed end-to-end.

## Traceability
- **Functional Requirements:** `FR-007`
- **Architecture Constraints:** `ADR-010`, `ADR-019`, `ADR-011`

## Acceptance Criteria
1. When conversational/agent execution is enabled, correlation chain extends to `session -> command -> workflow -> step -> agent -> tool_call`.
2. `agent` and `tool_call` events include valid parent identifiers linking back to workflow/step context.
3. Missing or broken parent linkage is surfaced as deterministic structured observability validation failure.
4. Command/conversation parity is preserved at shared externally observable boundaries, with conversational extension fields additive-only.
5. Emitted telemetry and persisted observability artifacts remain sensitive-by-default (no raw free-form text leakage unless explicit opt-in exists).

## Scope

### In Scope
- Extend conversational observability event envelopes to include `agent` and `tool_call` boundaries.
- Define and enforce deterministic parent-linkage validation for conversational correlation hierarchy.
- Emit structured validation/runtime errors for correlation contract failures.
- Keep telemetry contract compatibility with existing `MVP-03.1` persistence and `MVP-03.2` baseline correlation semantics.
- Add strict-gate regression tests for conversational chain continuity, parent-link integrity, and sanitization/parity guarantees.

### Out of Scope
- New external observability backends/exporters.
- Retention and pruning logic (`MVP-03.3`).
- Provider/model routing changes unrelated to conversational correlation envelope boundaries.

## Tasks / Subtasks
- [x] Define conversational extension envelope fields and invariants (AC: 1, 2)
  - [x] Lock deterministic identifier field names/types for `agent` and `tool_call` events.
  - [x] Specify allowed parent identifiers and required linkage constraints for each event type.
- [x] Implement correlation propagation for conversational path (AC: 1, 2, 4)
  - [x] Ensure valid parent lineage from `step` into `agent` and `tool_call` boundaries.
  - [x] Keep shared boundary semantics aligned with command-path envelope conventions.
- [x] Implement deterministic linkage-failure handling (AC: 3)
  - [x] Surface broken/missing parent linkages as structured observability validation failures.
  - [x] Preserve stable error classification (`type`, `code`, `component`) for identical failure modes.
- [x] Preserve sensitive-by-default behavior in conversational telemetry (AC: 5)
  - [x] Prevent raw-text fields from leaking in agent/tool_call payloads by default.
  - [x] Ensure sanitization remains recursive for nested metadata.
- [x] Add strict-gate tests and regression coverage (AC: 1, 2, 3, 4, 5)
  - [x] Conversational chain continuity assertions for `session -> command -> workflow -> step -> agent -> tool_call`.
  - [x] Parent-link integrity and deterministic structured-failure assertions.
  - [x] Parity assertions at shared externally observable boundaries.
  - [x] Sensitive-by-default sanitization assertions for conversational extension payloads.

## Dev Notes

### Technical Requirements
- Deterministic behavior is mandatory: identical logical inputs must produce stable correlation hierarchy and stable structured error classification.
- Safety-by-default is mandatory: raw conversational/request/response text remains sensitive by default and must be excluded or redacted unless explicit opt-in exists.
- Command/conversation parity is mandatory at shared externally observable boundaries; conversational-specific extension fields must be additive and must not alter shared semantics.
- Correlation hierarchy integrity is mandatory: no `agent` or `tool_call` event can be emitted without valid parent context.
- Prefer extension of existing runtime/telemetry primitives over introducing parallel observability paths.

### Architecture Compliance
- Align correlation/event envelope behavior with architecture observability model for deterministic structured telemetry.
- Preserve local-first persistence/observability behavior and compatibility with existing SQLite-backed execution history artifacts.
- Maintain strict-gate quality rigor for core runtime/observability stories per `ADR-011`.

### File Structure Requirements
- Keep runtime/telemetry implementation changes under existing `src/endi/` modules already responsible for routing/workflow/observability boundaries.
- Keep regression tests in `tests/` with focused coverage for conversational-path correlation and parity behavior.
- Avoid unrelated refactors, renames, or module moves.

### Testing Requirements (Strict Gate)
- **Gate Level:** `Strict`
- Execute quality gates in WSL project `.venv`:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`
- Required test focus:
  - Conversational correlation continuity assertions with deterministic parent chains.
  - Contract-failure assertions for missing/broken parent linkage.
  - Structured `runtime_error`/validation envelope assertions (`type`, `code`, `component`).
  - Command/conversation parity regression checks at shared externally observable boundaries.
  - Sensitive-by-default recursive sanitization checks for conversational extension fields.

### Review-Ready Exit Conditions
- [x] Acceptance criteria are each covered by explicit tests.
- [x] Conversational correlation extension does not break existing baseline chain semantics.
- [x] Broken parent-linkage paths fail deterministically with structured observability errors.
- [x] No raw-text leakage in conversational telemetry/persistence artifacts by default.

## Dependencies
- `mvp-03-1-sqlite-execution-history-schema-and-write-path` (durable local execution history baseline).
- `mvp-03-2-structured-json-logs-with-correlation-hierarchy` (baseline envelope + `session -> command -> workflow -> step` chain).
- Existing structured runtime/validation error model in runtime routing/telemetry.

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-03.4 — Extended correlation for conversational tool path]
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#EPIC-MVP-03: Persistence and Observability Baseline]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-007 Observability and Diagnostics]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#10. Observability Architecture]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `project-context.md`#Execution Environment]
- [Source: `project-context.md`#Agent Command Rules]

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used
- Cascade (GPT-5)

### Debug Log References
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest tests/test_dual_mode_routing.py"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`

### Completion Notes List
- Extended conversational telemetry with additive correlation envelope fields (`execution_id`, `command_id`, `workflow_id`) and a deterministic event chain at `conversation_correlation.events` for `step -> agent -> tool_call` boundaries.
- Enforced deterministic parent-link validation for conversational observability and surfaced invalid lineage as structured `runtime_error` (`type=runtime_error`, `code=observability_parent_linkage_invalid`, `component=workflow`, `status_code=invalid_contract`).
- Preserved command/conversation parity at shared externally observable boundaries by keeping common envelope/correlation semantics intact while restricting conversational-only fields to additive extensions.
- Preserved sensitive-by-default behavior for conversational extension payloads by excluding raw free-form text and emitting only safe `tool_call.arg_keys` (with raw-text key filtering).
- Added focused regression tests for continuity, parent-link integrity failures, deterministic failure behavior, parity at shared boundaries, and sanitization regressions.

### File List
- `src/endi/routing.py`
- `tests/test_dual_mode_routing.py`
- `_bmad-output/implementation-artifacts/stories/mvp-03-4-extended-correlation-for-conversational-tool-path.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log
- 2026-03-23: Implemented MVP-03.4 conversational correlation extension, deterministic parent-link validation failures, focused regression coverage, and strict WSL `.venv` quality-gate verification.
