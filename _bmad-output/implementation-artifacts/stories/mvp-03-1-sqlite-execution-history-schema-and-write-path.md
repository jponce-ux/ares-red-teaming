# Story MVP-03.1: SQLite Execution History Schema and Write Path

Status: done

## Metadata
- **Story ID:** `MVP-03.1`
- **Story Key:** `mvp-03-1-sqlite-execution-history-schema-and-write-path`
- **Epic:** `EPIC-MVP-03` Persistence and Observability Baseline
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 2`
- **Type:** `Persistence Core`

## Story
As an SRE, I want durable run history, so that I can audit and diagnose workflow outcomes.

## Traceability
- **Functional Requirements:** `FR-007`, `FR-002`
- **Architecture Constraints:** `ADR-007`, `ADR-010`, `ADR-019`, `ADR-011`

## Acceptance Criteria
1. SQLite stores sessions, commands, workflows, steps, tool calls, status, and timing metadata needed to reconstruct a complete execution timeline.
2. Persistence writes are atomic for each lifecycle stage transition so partial writes cannot leave inconsistent timeline state.
3. Querying by execution/correlation identifiers reconstructs deterministic end-to-end run traces.
4. Persistence/runtime failures surface structured `runtime_error` envelopes with correlation continuity and without raw-text leakage.
5. Externally observable shared boundaries preserve command/conversation parity where overlap exists (especially error envelope semantics and sanitization behavior).

## Scope

### In Scope
- SQLite schema and migration path for durable execution history entities.
- Atomic repository write path for lifecycle transitions.
- Deterministic query path for timeline reconstruction using correlation hierarchy.
- Structured failure mapping for persistence contract violations and runtime errors.
- Sensitive-by-default sanitization for persisted metadata and observability artifacts.

### Out of Scope
- Remote/distributed database support.
- Data warehouse export and analytics pipelines.
- Retention/prune implementation details beyond compatibility hooks (`MVP-03.3`).

## Tasks / Subtasks
- [x] Define v1 SQLite schema and migration strategy (AC: 1)
  - [x] Model `session`, `command`, `workflow`, `step`, and `tool_call` entities with stable identifiers.
  - [x] Capture status, timestamps, duration/timing metadata, and parent linkage fields.
- [x] Implement atomic lifecycle-stage write path (AC: 2)
  - [x] Ensure transaction boundaries align to stage transition semantics.
  - [x] Guarantee deterministic rollback/structured failure behavior on write errors.
- [x] Implement timeline reconstruction query path (AC: 3)
  - [x] Provide read helpers that reconstruct ordered history from session down to step/tool boundaries.
  - [x] Validate deterministic ordering and parent-child linkage integrity.
- [x] Implement structured runtime error integration for persistence failures (AC: 4, 5)
  - [x] Ensure persistence faults map to structured `runtime_error` envelope fields.
  - [x] Preserve shared externally observable parity with existing command/conversation error semantics.
- [x] Add strict-gate tests for schema, migration, atomicity, reconstruction, sanitization, and parity (AC: 1, 2, 3, 4, 5)
  - [x] Include FR-007 boundary assertions for required matrix rows.
  - [x] Include sanitization regression minimum set `SAN-mvp-03-1-01` through `SAN-mvp-03-1-05`.

## Dev Notes

### Technical Requirements
- Preserve deterministic behavior: identical logical inputs produce stable persistence/trace shape and deterministic error/status mapping.
- Enforce safety-by-default: raw/free-form request/response/conversation text is sensitive by default and must not be persisted or emitted unless explicit opt-in exists.
- Maintain command/conversation parity at shared externally observable boundaries (especially runtime error envelope behavior and sanitized metadata exposure).
- Keep local-first persistence architecture and artifact-by-reference behavior aligned with ADR-007.
- Keep retention compatibility hooks for ADR-019 (30 days / 2 GB / auto-prune) without implementing prune logic in this story.

### Architecture Compliance
- Persistence model must align with architecture `8. Context and Persistence Model` and `8.2 Durable Execution History (Local)`.
- Observability envelope/correlation continuity must align with architecture `10. Observability Architecture`.
- Runtime/test rigor must align with architecture `11. Testing and CI Quality Model` strict-gate intent for core runtime/persistence.
- Guardrails must remain consistent with architecture principles: deterministic operation, observability-first, and safety-by-default.

### File Structure Requirements
- Keep implementation in existing runtime modules under `src/endi/` and add dedicated persistence module(s) only when needed by established structure.
- Keep tests under `tests/` with focused persistence and routing/runtime parity coverage.
- Do not introduce unrelated structural refactors.

### FR-007 Boundary Coverage (Required Matrix Rows)
- [x] `session` boundary implemented with deterministic envelope fields and root correlation semantics.
- [x] `command` boundary implemented with valid `session_id -> command_id` parent linkage.
- [x] `workflow` boundary implemented with valid `command_id -> workflow_id` parent linkage.
- [x] `step` boundary implemented with valid `workflow_id -> step_id` parent linkage.
- [x] `runtime_error` envelope implemented with structured error fields and boundary correlation continuity.

### Determinism Requirements
- [x] Repeated identical logical inputs produce stable envelope keys/status mapping.
- [x] Missing parent-linkage fails as deterministic structured contract violation.

### Testing Requirements (Strict Gate)
- **Gate Level:** `Strict`
- Execute quality gates in WSL project `.venv`:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`
- Core persistence tests:
  - Schema + migration correctness tests.
  - Atomicity tests for mid-stage failure/rollback scenarios.
  - Timeline reconstruction completeness and ordering tests.
  - Deterministic contract-failure tests for broken/missing parent linkage.
  - Command/conversation parity regression tests for shared externally observable boundaries.

### Sensitive-by-Default Regression Cases (Minimum Set)
- [x] `SAN-mvp-03-1-01` — CLI output sanitization (success + runtime_error path)
- [x] `SAN-mvp-03-1-02` — telemetry payload sanitization for command/workflow/step events
- [x] `SAN-mvp-03-1-03` — session snapshot sanitization with recursive nested-field checks
- [x] `SAN-mvp-03-1-04` — persistence record sanitization for execution history rows
- [x] `SAN-mvp-03-1-05` — runtime_error envelope sanitization (no raw text leakage)

### Test Evidence Requirements
- [x] At least one recursive sanitization test included.
- [x] Correlation continuity assertions included for `session -> command -> workflow -> step`.
- [x] Structured `runtime_error` assertions include `error.type`, `error.code`, `error.component`.
- [x] Strict WSL `.venv` quality gates recorded: `ruff check src tests`, `mypy src`, `pytest`.

### Review-Ready Exit Conditions
- [x] Matrix row coverage for `mvp-03-1` is demonstrably satisfied.
- [x] Sanitization regressions are green and would fail on raw-text leakage.
- [x] No command/conversation parity regressions introduced at shared externally observable boundaries.

## Dependencies
- Existing lifecycle and correlation conventions in routing/workflow runtime.
- Shared structured runtime error model/envelope contract.
- Follow-on observability stories in `EPIC-MVP-03` (`mvp-03-2`, `mvp-03-4`) and retention story (`mvp-03-3`).

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-03.1 — SQLite execution history schema and write path]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-007 Observability and Diagnostics]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-002 Deterministic Workflow Execution]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#8. Context and Persistence Model]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#10. Observability Architecture]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `_bmad-output/implementation-artifacts/mvp-03-kickoff-checklist.md`#Go-Forward Sequence (Do not start implementation in step 1-2)]
- [Source: `_bmad-output/implementation-artifacts/mvp-03-fr-007-compliance-matrix.md`]
- [Source: `_bmad-output/implementation-artifacts/mvp-03-sensitive-data-sanitization-regression-template.md`]
- [Source: `_bmad-output/implementation-artifacts/mvp-03-1-create-story-checklist-snippet.md`]
- [Source: `_bmad-output/implementation-artifacts/status-consistency-preflight-checklist.md`]

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used
- Cascade (GPT-5)

### Debug Log References
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`

### Completion Notes List
- Implemented `src/endi/persistence.py` SQLite execution-history store with schema migration, atomic stage-transition writes, tool-call/runtime-error rows, and timeline reconstruction by `execution_id`.
- Integrated command-route persistence in `src/endi/routing.py` behind `execution_history_db` context opt-in with structured persistence failure mapping to `runtime_error` envelope.
- Extended sensitive-by-default key handling in `src/endi/context.py` to treat raw text fields as sensitive for durable persistence/telemetry sanitization.
- Added strict FR-007/SAN regression coverage in `tests/test_persistence.py` including parent-linkage contract failure and structured/sanitized runtime_error assertions.
- Verified strict WSL `.venv` gates: `ruff check src tests`, `mypy src`, and `pytest` (80 passed).

### File List
- `src/endi/persistence.py`
- `src/endi/routing.py`
- `src/endi/context.py`
- `tests/test_persistence.py`
- `_bmad-output/implementation-artifacts/stories/mvp-03-1-sqlite-execution-history-schema-and-write-path.md`
