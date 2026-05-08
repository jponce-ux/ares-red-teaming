# Story MVP-03.3: Retention and Auto-prune Policy Implementation

Status: done

## Metadata
- **Story ID:** `MVP-03.3`
- **Story Key:** `mvp-03-3-retention-and-auto-prune-policy-implementation`
- **Epic:** `EPIC-MVP-03` Persistence and Observability Baseline
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 4`
- **Type:** `Persistence Reliability`

## Story
As a workstation owner, I want bounded local storage, so that ENDI history does not grow unbounded.

## Traceability
- **Functional Requirements:** `FR-007`
- **Architecture Constraints:** `ADR-019`, `ADR-007`, `ADR-010`, `ADR-011`

## Acceptance Criteria
1. Runtime enforces default retention limits (`30 days`, `2 GB`) with auto-prune enabled by default.
2. Pruning executes deterministically in the locked order: prune by age first, then prune oldest runs until total storage is under threshold.
3. Prune operations emit structured observability artifacts with affected record counts and artifact/path reference impact.
4. Retention execution is safe and deterministic under concurrent command/workflow execution (no parent-link corruption or partial inconsistent outcomes).
5. Sensitive-by-default behavior is preserved in retention and prune telemetry/persistence artifacts (no raw free-form text leakage unless explicit opt-in exists).
6. Command/conversation externally observable parity remains preserved for shared runtime/persistence boundaries touched by retention execution.

## Scope

### In Scope
- Implement and enforce default local retention policy (`history_days: 30`, `max_storage_gb: 2`, `auto_prune: true`).
- Implement deterministic prune sequencing (`age-first`, then `oldest-run` deletion until under size budget).
- Integrate prune execution with local execution-history persistence and artifact-reference cleanup behavior.
- Emit structured retention/prune events and summaries compatible with existing FR-007 envelope/correlation conventions.
- Add strict-gate regression coverage for retention simulation, ordering, determinism, concurrency safety, and sanitization.

### Out of Scope
- Cloud archival tiering, remote retention services, or cold-storage migration.
- New external observability backends/export pipelines.
- User-facing storage dashboard or advanced retention UI beyond existing CLI/runtime output conventions.

## Tasks / Subtasks
- [x] Define deterministic retention policy evaluation contract (AC: 1, 2)
  - [x] Resolve effective defaults from locked configuration profile (`30 days`, `2 GB`, `auto_prune=true`).
  - [x] Ensure policy evaluation is repeatable and idempotent for identical state snapshots.
- [x] Implement prune planner and executor with locked ordering (AC: 2, 4)
  - [x] Execute age-based pruning first.
  - [x] If still above threshold, prune oldest runs iteratively until under storage budget.
  - [x] Guarantee deterministic tie-breaking for equally old/large candidates.
- [x] Integrate persistence and artifact-reference cleanup path (AC: 3, 4)
  - [x] Remove/update artifact references consistently with retained execution-history rows.
  - [x] Avoid orphaned rows or orphaned filesystem references across prune operations.
- [x] Implement structured retention observability outputs (AC: 3, 5, 6)
  - [x] Emit event payloads with prune counts, threshold state, and impacted artifact references.
  - [x] Preserve correlation hierarchy and sensitive-by-default sanitization requirements.
- [x] Add strict-gate tests and regression coverage (AC: 1, 2, 3, 4, 5, 6)
  - [x] Retention simulation tests for age-only, size-only, and mixed pressure cases.
  - [x] Deterministic ordering and repeatability tests for equivalent inputs.
  - [x] Concurrency/idempotency tests to prevent inconsistent prune outcomes.
  - [x] Sanitization tests for retention/prune event payloads and persistence artifacts.
  - [x] Parity regression checks for shared command/conversation observable boundaries.

## Dev Notes

### Technical Requirements
- Enforce locked ADR-019 defaults (`30 days` or `2 GB`, whichever first, auto-prune enabled) unless explicit user/config override is introduced and validated.
- Keep prune algorithm deterministic and stable for identical datasets and timestamps.
- Preserve safety-by-default: never persist or emit raw request/response/conversation text in prune/retention metadata by default.
- Maintain command/conversation parity at shared externally observable boundaries touched by retention execution.
- Reuse existing persistence/telemetry contracts and sanitization helpers; do not introduce parallel ad-hoc retention logging formats.

### Architecture Compliance
- Retention behavior must align with architecture `14. Locked v1 Default Configuration Profile` and `Retention behavior` ordering rules.
- Persistence interaction must remain consistent with architecture `8.2 Durable Execution History (Local)` and local artifact-by-reference approach.
- Observability event shape/correlation behavior must remain consistent with architecture `10. Observability Architecture` and FR-007 matrix expectations.
- Quality rigor must follow architecture `11. Testing and CI Quality Model` strict-gate expectations for persistence core stories.

### File Structure Requirements
- Prefer retention logic integration in established persistence/runtime modules under `src/endi/` (for example, alongside or near `persistence.py` and routing integration points).
- Keep focused regression coverage in `tests/` with retention simulation and contract behavior assertions.
- Avoid unrelated refactors, renames, or architecture-layer changes outside retention scope.

### Testing Requirements (Strict Gate)
- **Gate Level:** `Strict`
- Execute quality gates in WSL project `.venv`:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`
- Required test focus:
  - Deterministic age-first then oldest-run prune sequencing assertions.
  - Mixed-threshold pressure simulations (`age`, `size`, and combined).
  - Concurrency/idempotency safety assertions for repeated and overlapping retention execution.
  - Structured retention/prune telemetry envelope and correlation continuity assertions.
  - Sensitive-by-default sanitization assertions for prune summaries and metadata payloads.

### Review-Ready Exit Conditions
- [x] All acceptance criteria are covered by explicit automated tests.
- [x] Locked ADR-019 retention defaults and ordering are demonstrably enforced.
- [x] No orphaned persistence rows or artifact references remain after prune execution.
- [x] Structured prune observability output is deterministic and sanitized.
- [x] No command/conversation parity regression is introduced at shared externally observable boundaries.

## Dependencies
- `mvp-03-1-sqlite-execution-history-schema-and-write-path` (durable local execution-history baseline).
- `mvp-03-2-structured-json-logs-with-correlation-hierarchy` (structured observability envelopes).
- `mvp-03-4-extended-correlation-for-conversational-tool-path` (extended conversational correlation behavior and parity constraints).

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-03.3 — Retention and auto-prune policy implementation]
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#EPIC-MVP-03: Persistence and Observability Baseline]
- [Source: `_bmad-output/planning-artifacts/endi-adr-rationales.md`#ADR-019 — Local Retention Defaults]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#14. Locked v1 Default Configuration Profile]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#8. Context and Persistence Model]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#10. Observability Architecture]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `_bmad-output/implementation-artifacts/mvp-03-fr-007-compliance-matrix.md`]
- [Source: `project-context.md`#Execution Environment]
- [Source: `project-context.md`#Agent Command Rules]

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used
- Cascade (GPT-5)

### Debug Log References
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"` (pass)
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"` (pass)
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"` (pass, 98 passed)

### Completion Notes List
- Implemented retention policy defaults and validation in `ExecutionHistoryStore` (`30 days`, `2 GB`, `auto_prune=true`) with optional explicit overrides from resolved execution-history context.
- Implemented deterministic retention execution (`age` then `size`) with stable ordering, command-level cascading prune, orphan-session cleanup, and transactional safety via SQLite `BEGIN IMMEDIATE`.
- Added structured retention summary artifacts (`policy`, prune counts/order, affected row counts, artifact/path reference impact, storage before/after, pruned workflow IDs), persisted in workflow metadata and surfaced in command telemetry.
- Preserved sensitive-by-default handling by reusing existing persistence sanitization for retention summaries and metadata updates.
- Added focused retention regression coverage for defaults, deterministic age-first/size-second behavior, structured+sanitized summary content, and concurrent retention safety without parent-link corruption.
- Resolved review finding on retention size accounting by switching threshold checks to active SQLite pages (`page_count - freelist_count`) to avoid over-pruning driven by allocated-but-free pages.
- Resolved review finding on invalid retention override handling by enforcing strict positive integer parsing for context overrides and deterministic fallback to locked defaults.

### File List
- `src/endi/persistence.py`
- `src/endi/routing.py`
- `tests/test_persistence.py`
- `_bmad-output/implementation-artifacts/stories/mvp-03-3-retention-and-auto-prune-policy-implementation.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log
- 2026-03-23: Implemented MVP-03.3 retention and auto-prune policy with deterministic age→size pruning, structured/sanitized observability summaries, concurrent retention safety coverage, and strict WSL `.venv` gate validation.
- 2026-03-23: Closed code-review findings for MVP-03.3 by hardening retention size accounting and override validation, with added regressions and strict WSL `.venv` gates passing (`ruff`, `mypy`, `pytest` 98 passed).
