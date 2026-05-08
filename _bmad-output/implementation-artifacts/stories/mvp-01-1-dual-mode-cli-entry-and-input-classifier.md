# Story MVP-01.1: Dual-mode CLI Entry and Input Classifier

Status: done

## Metadata
- **Story ID:** `MVP-01.1`

- **Epic:** `EPIC-MVP-01` Core CLI, Routing, and Deterministic Runtime

- **Priority:** `P1`

- **Suggested Sprint:** `Sprint 1`

- **Type:** `Core Runtime`

## User Story
As a terminal operator, I want `/command` and free-text inputs to be classified reliably, so that command and conversational paths route correctly.

## Traceability
- **Functional Requirements:** `FR-001`, `FR-009`

- **Architecture Constraints:** `ADR-001`, `ADR-002`, `ADR-003`, `ADR-012`

## Scope

### In Scope
- Input classifier that distinguishes `/`-prefixed command input vs free-text input.

- Routing to command workflow executor for `/`-prefixed input.

- Routing to conversational agent path for non-prefixed input.

- Structured validation errors for unsupported command syntax.

### Out of Scope
- Command business logic implementations.

- Advanced typo-correction/autonomous intent rewriting.

## Acceptance Criteria
1. Given input prefixed with `/`, when submitted, then it routes to command workflow execution.
2. Given non-prefixed free text, when submitted, then it routes to conversational agent path.
3. Given unsupported command syntax, then a structured validation error is returned and no execution occurs.
4. Command validation errors include actionable hint text and preserve terminal-safe output formatting.

## Implementation Notes
- Implement within the Typer + Prompt Toolkit CLI flow and keep rendering consistent with Rich output patterns.

- Keep routing deterministic and side-effect free at classification phase.

- Ensure command names remain lowercase kebab-case compliant (`FR-009`).

## Tasks
- [x] Add/complete input classification module for prefix-based mode detection.

- [x] Wire classifier output into command vs conversational dispatcher.

- [x] Add structured error model for malformed/unsupported command syntax.

- [x] Add CLI-level tests for classification and dispatch behavior.

- [x] Add error UX tests for malformed commands.

## Testing Notes (ADR-011)
- **Gate Level:** `Strict`

- Add unit tests for classifier rules and boundary cases.

- Add integration tests for route outcomes (`command`, `conversation`, `validation_error`).

- Add regression tests confirming malformed command input does not execute any workflow/tool path.

## Dependencies
- Runtime CLI bootstrap and command registry skeleton.

- Structured error response schema shared by router/CLI output.

## Definition of Done
- All acceptance criteria pass.

- Strict gate checks pass (tests, lint, typing for touched core modules).

- Story traceability and ADR constraints remain satisfied.

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Debug Log
- Implemented deterministic classifier and dispatcher in `src/endi/routing.py`.
- Added CLI submit path in `src/endi/cli.py` using Prompt Toolkit prompt fallback and Rich output.
- Added coverage tests for classifier, dispatch, malformed command handling, and CLI validation UX in `tests/test_dual_mode_routing.py`.
- Ran validations in WSL project venv: `ruff check src tests`, `mypy src`, and `pytest -q`.
- Applied lint modernization in `src/endi/routing.py` (`Callable` import source, `StrEnum`, import ordering) to satisfy strict gate checks.

### Completion Notes
- `/`-prefixed input is classified and routed to command executor.
- Non-prefixed input is classified and routed to conversation handler.
- Unsupported command syntax returns structured validation error with actionable hint text.
- Malformed command path returns validation result and does not execute command or conversation handlers.
- Strict gate checks passed in WSL project venv (tests, lint, typing) and story is ready for review.

## File List
- `src/endi/cli.py` (modified)
- `src/endi/routing.py` (new)
- `tests/test_dual_mode_routing.py` (new)

## Change Log
- 2026-03-18: Implemented dual-mode classifier/dispatcher, structured validation errors, and CLI/test wiring for MVP-01.1.
- 2026-03-18: Ran strict gate validation (`ruff`, `mypy`, `pytest`) in WSL venv and moved story to review.

## Status
done
