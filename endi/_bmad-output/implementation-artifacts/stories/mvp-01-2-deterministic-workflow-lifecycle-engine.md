# Story MVP-01.2: Deterministic Workflow Lifecycle Engine

Status: done

## Metadata
- **Story ID:** `MVP-01.2`
- **Story Key:** `mvp-01-2-deterministic-workflow-lifecycle-engine`
- **Epic:** `EPIC-MVP-01` Core CLI, Routing, and Deterministic Runtime
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 1`
- **Type:** `Core Runtime`

## Story
As a workflow author, I want fixed lifecycle stages, so that execution is reproducible and auditable.

## Traceability
- **Functional Requirements:** `FR-002`
- **Architecture Constraints:** `ADR-001`, `ADR-003`, `ADR-010`, `ADR-011`, `ADR-012`

## Acceptance Criteria
1. Lifecycle stages execute in deterministic order: `initialize -> validate -> plan(optional) -> execute -> collect -> output -> finalize`.
2. Required input validation fails fast before `execute` and prevents side effects.
3. Structured workflow output contains `status`, `payload` (result), and `metadata`.
4. Failure states are explicit and include structured failure type/component for observability.

## Scope

### In Scope
- Deterministic lifecycle model and transition enforcement for workflow runs.
- Optional `plan` stage support without changing required stage order.
- Fail-fast required-input validation in `validate` stage.
- Standardized workflow result envelope for command/workflow callers.
- Stage-level observability hooks aligned with structured JSON event model.

### Out of Scope
- Graph adapter as default orchestration mode.
- Multi-branch workflow DSL or dynamic runtime topology changes.
- Provider/backend policy changes not required for lifecycle sequencing.

## Tasks / Subtasks
- [x] Define lifecycle contracts and runtime types (AC: 1, 3, 4)
  - [x] Add lifecycle stage enum/type and allowed transition map.
  - [x] Define typed workflow output envelope with `status`, `payload`, `metadata`.
- [x] Implement deterministic lifecycle runner (AC: 1, 2)
  - [x] Execute stages strictly in documented order.
  - [x] Preserve optional `plan` stage as no-op/skipped path when not configured.
  - [x] Ensure `finalize` runs for both success and failure paths.
- [x] Enforce fail-fast validation and error shape (AC: 2, 4)
  - [x] Validate required inputs before any execution side effects.
  - [x] Return structured error payload with component/failure type.
- [x] Add observability integration points (AC: 4)
  - [x] Emit stage start/end/failure events with stable identifiers.
  - [x] Ensure events can be correlated to command/workflow execution IDs.
- [x] Add strict-gate tests (AC: 1, 2, 3, 4)
  - [x] Unit tests for transition order and invalid transition rejection.
  - [x] Integration tests for success, validation-fail, and runtime-fail lifecycle paths.
  - [x] Contract tests for output envelope and structured error shape.

## Dev Notes

### Technical Requirements
- Keep deterministic orchestration as the default runtime path.
- Do not introduce agent-loop or graph-execution behavior in this story.
- Keep error and output shapes stable for downstream CLI rendering and future persistence/telemetry stories.

### Architecture Compliance
- Workflow sequencing must follow architecture lifecycle exactly.
- Runtime remains local-first and policy-driven; this story only defines lifecycle behavior.
- Observability hooks must preserve correlation continuity for later persistence/logging stories.

### File Structure Requirements
- Reuse existing ENDI runtime module structure in `src/endi/`.
- Extend current routing/CLI integration points rather than adding parallel execution entry paths.
- Keep tests under `tests/` with names matching current `test_*.py` style.

### Testing Requirements (ADR-011)
- **Gate Level:** `Strict`
- Validate deterministic behavior under repeated identical inputs.
- Ensure validation failures prevent `execute` side effects.
- Verify structured output/error contracts and stage event consistency.
- Run `ruff`, `mypy`, and `pytest` in WSL project venv.

## Previous Story Intelligence (MVP-01.1)
- Routing/classification behavior is already implemented and should remain the single entry to command workflow execution.
- Existing patterns use deterministic dispatch and structured validation errors; lifecycle errors should match this style.
- Tests already assert non-executing behavior for malformed command input; extend this principle to workflow validation failures.

## Git Intelligence
- Git history analysis was not executed due local repository safe-directory restriction on this environment path.

## Latest Tech Information
- Project uses Python `>=3.11`.
- Runtime/tooling dependencies currently pinned to major ranges:
  - `typer>=0.12,<1`
  - `rich>=13,<14`
  - `prompt-toolkit>=3.0,<4`
- Dev quality gates currently use:
  - `pytest>=8,<9`
  - `mypy>=1.10,<2`
  - `ruff>=0.4,<1`

## Project Structure Notes
- Story output remains in `_bmad-output/implementation-artifacts/stories`.
- No project-structure conflicts identified for this story.

## Dependencies
- Existing CLI/router dispatch path from MVP-01.1.
- Shared structured error/result models consumed by CLI output and future observability layers.

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-01.2 — Deterministic Workflow Lifecycle Engine]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-002 Deterministic Workflow Execution]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#5.3 Workflow Engine (Deterministic Core)]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#10. Observability Architecture]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `_bmad-output/implementation-artifacts/stories/mvp-01-1-dual-mode-cli-entry-and-input-classifier.md`]
- [Source: `project-context.md`]
- [Source: `pyproject.toml`]

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used
- Cascade (GPT-5)

### Debug Log References
- `wsl.exe bash -lc "source /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi/.venv/bin/activate && cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi && pytest -q tests/test_workflow_lifecycle.py"` (fails in red phase before implementation)
- `wsl.exe bash -lc "source /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi/.venv/bin/activate && cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi && pytest -q tests/test_workflow_lifecycle.py tests/test_dual_mode_routing.py"`
- `wsl.exe bash -lc "source /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi/.venv/bin/activate && cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi && ruff check ."`
- `wsl.exe bash -lc "source /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi/.venv/bin/activate && cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi && mypy src/endi tests"`
- `wsl.exe bash -lc "source /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi/.venv/bin/activate && cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi && pytest -q"`

### Completion Notes List
- Implemented deterministic lifecycle engine in `src/endi/workflow.py` with canonical stage enums, structured output envelope (`status`, `payload`, `metadata`), structured failure payload, optional `plan` stage skip tracking, and stage-level event emission.
- Integrated lifecycle runner into command dispatch path in `src/endi/routing.py`, preserving existing classifier entrypoint and adding explicit structured execution errors for runtime failures.
- Updated CLI submit command in `src/endi/cli.py` to surface structured execution failures with component/failure type/execution ID.
- Added strict-gate lifecycle tests in `tests/test_workflow_lifecycle.py` and expanded routing integration coverage in `tests/test_dual_mode_routing.py`.
- Verified deterministic and fail-fast behavior, structured contracts, and regression safety through `ruff`, scoped `mypy`, and full `pytest`.

### File List
- `src/endi/workflow.py`
- `src/endi/routing.py`
- `src/endi/cli.py`
- `tests/test_workflow_lifecycle.py`
- `tests/test_dual_mode_routing.py`

## Change Log
- 2026-03-18: Implemented deterministic workflow lifecycle engine with structured outputs/errors, observability events, command-path integration, and strict-gate test coverage; story moved to `review`.
