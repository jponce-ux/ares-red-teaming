# Story MVP-01.3: Bounded Conversational Tool Loop

Status: done

## Metadata
- **Story ID:** `MVP-01.3`
- **Story Key:** `mvp-01-3-bounded-conversational-tool-loop`
- **Epic:** `EPIC-MVP-01` Core CLI, Routing, and Deterministic Runtime
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 3`
- **Type:** `Agent Runtime Core`

## Story
As a user, I want conversational orchestration with bounded tool iterations, so that responses are useful and controlled.

## Traceability
- **Functional Requirements:** `FR-003`
- **Architecture Constraints:** `ADR-003`, `ADR-004`, `ADR-006`, `ADR-010`, `ADR-011`, `ADR-012`

## Acceptance Criteria
1. Agent runtime supports iterative `select-action -> execute-tool -> observe-result` cycles for conversational requests.
2. Maximum iteration limit is configurable and enforced per agent/workflow runtime configuration.
3. Loop exits deterministically with explicit termination reason (`completed`, `max-iterations`, `tool-failure`, `policy-denied`, `timeout`) and does not continue after terminal conditions.
4. Final synthesized response includes references to tool outputs used in synthesis with stable identifiers.

## Scope

### In Scope
- Add a bounded conversational loop runtime component for conversational path execution.
- Enforce per-iteration control flow and policy checks before tool execution.
- Capture per-turn execution records to support observability and final reference synthesis.
- Return structured conversational result payload suitable for CLI rendering and future persistence stories.

### Out of Scope
- Multi-agent role chains (generator/reviewer/corrector/validator).
- Graph adapter as default orchestration runtime.
- Provider routing defaults/fallback policy changes.
- Advanced retry/backoff strategies beyond deterministic bounded loop behavior.

## Tasks / Subtasks
- [x] Define conversational loop contracts and types (AC: 1, 2, 3, 4)
  - [x] Add loop state and termination reason enums/types.
  - [x] Define structured turn record shape containing selected action, tool call metadata, and observation summary.
- [x] Implement bounded loop executor (AC: 1, 2, 3)
  - [x] Execute deterministic turn cycles with strict max-iteration checks.
  - [x] Stop immediately on terminal conditions and return explicit reason.
  - [x] Ensure loop is pure-control and delegates actual tool execution to existing tool invocation path.
- [x] Implement synthesis reference tracking (AC: 4)
  - [x] Collect tool output references per completed turn.
  - [x] Include references in final payload returned by conversational runtime.
- [x] Integrate routing path (AC: 1, 2, 3, 4)
  - [x] Keep `dispatch_input` classification behavior unchanged.
  - [x] Route conversation path through bounded loop runtime and structured output adapter.
- [x] Add strict-gate tests (AC: 1, 2, 3, 4)
  - [x] Unit tests for max-iteration enforcement and deterministic termination behavior.
  - [x] Unit tests for reference collection inclusion in final output.
  - [x] Integration tests for success, bound-hit, tool-failure, and policy-denied scenarios.

## Dev Notes

### Technical Requirements
- Preserve deterministic behavior: identical loop inputs and tool outcomes must produce equivalent termination and output shape.
- Enforce capability/policy checks before every tool execution step.
- Prevent unbounded recursion or uncontrolled loop continuation.
- Keep conversational result schema stable and explicit (`status`, `payload`, `metadata` plus tool references).

### Architecture Compliance
- Keep deterministic workflow engine as explicit core and implement conversational loop as bounded runtime behavior, not as uncontrolled free-form agent execution.
- Maintain local-first execution assumptions with policy-driven backend boundaries.
- Ensure observability compatibility with correlation hierarchy (`session -> command -> workflow -> step -> agent -> tool_call`) for conversational paths.

### Library / Framework Requirements
- Runtime implementation remains in Python `>=3.11`.
- Reuse project stack and patterns:
  - `typer>=0.12,<1`
  - `rich>=13,<14`
  - `prompt-toolkit>=3.0,<4`
- Quality tooling expectations:
  - `pytest>=8,<9`
  - `mypy>=1.10,<2`
  - `ruff>=0.4,<1`

### File Structure Requirements
- Keep implementation under `src/endi/` and align naming/style with existing runtime modules (`routing.py`, `workflow.py`).
- Avoid creating alternate entrypoints that bypass `classify_input` and `dispatch_input` contracts.
- Add or extend tests under `tests/` using `test_*.py` naming and strict typing style already used in repo.

### Testing Requirements (ADR-011)
- **Gate Level:** `Strict`
- Validate loop bound and termination invariants under repeated runs.
- Validate explicit stop behavior for policy/tool failure cases.
- Validate final response includes only tool outputs actually consumed by synthesis.
- Run `ruff`, `mypy`, and `pytest` in WSL project `.venv`.

## Previous Story Intelligence (MVP-01.2)
- The deterministic lifecycle runner in `src/endi/workflow.py` already establishes strict stage ordering and structured metadata patterns; conversational loop output should mirror this structured contract style.
- Routing integration in `src/endi/routing.py` currently returns typed dispatch results and explicit execution/validation errors; maintain that contract when integrating conversational loop behavior.
- Existing tests emphasize deterministic and fail-fast behavior; loop tests should follow the same philosophy for bounded and terminal states.

## Git Intelligence
- Recent sequence indicates incremental delivery through MVP-01 runtime stories:
  - `mvp-01-1-dual-mode-cli-entry-and-input-classifier`
  - `mvp-01-2-deterministic-workflow-lifecycle-engine`
- Reuse established coding patterns and avoid introducing parallel architectural paths.

## Latest Tech Information
- No additional external libraries are required for this story.
- Use currently configured project dependency ranges and avoid speculative upgrades during implementation.

## Project Structure Notes
- Story artifact location remains `_bmad-output/implementation-artifacts/stories`.
- No project-structure conflicts identified for this story.

## Dependencies
- Existing dual-mode classification and dispatch path from MVP-01.1.
- Deterministic lifecycle and structured metadata patterns from MVP-01.2.
- Tool invocation contract baseline and capability enforcement stories in upcoming MVP-01.5 / MVP-02.x.

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-01.3 — Bounded conversational tool loop]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-003 Conversational Multi-Step Orchestration]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#5.4 Agent Runtime]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#10. Observability Architecture]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `_bmad-output/implementation-artifacts/stories/mvp-01-2-deterministic-workflow-lifecycle-engine.md`]
- [Source: `project-context.md`]
- [Source: `pyproject.toml`]

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used
- Cascade (GPT-5)

### Debug Log References
- `pytest -q tests/test_conversational_loop.py` (red phase expected failure, missing module)
- `pytest -q tests/test_conversational_loop.py tests/test_dual_mode_routing.py` (green targeted test pass)
- `pytest -q && ruff check . && mypy` (strict gate pass in WSL `.venv`)

### Completion Notes List
- Added `src/endi/conversation.py` bounded conversational runtime with deterministic loop control.
- Implemented explicit terminal reasons: `completed`, `max-iterations`, `tool-failure`, `policy-denied`, `timeout`.
- Added structured conversational envelope (`status`, `payload`, `metadata`) with stable tool output references.
- Integrated conversation routing in `dispatch_input` through bounded runtime while keeping classification behavior unchanged.
- Added strict unit and integration tests for loop behavior, termination reasons, and reference tracking.

### File List
- `src/endi/conversation.py`
- `src/endi/routing.py`
- `tests/test_conversational_loop.py`
- `tests/test_dual_mode_routing.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log
- 2026-03-18: Implemented MVP-01.3 bounded conversational tool loop runtime, routing integration, and strict-gate test coverage; story moved to `review`.
