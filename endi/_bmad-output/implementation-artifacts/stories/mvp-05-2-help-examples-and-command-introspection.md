# Story MVP-05.2: Help, Examples, and Command Introspection

Status: done

## Metadata
- **Story ID:** `MVP-05.2`
- **Story Key:** `mvp-05-2-help-examples-and-command-introspection`
- **Epic:** `EPIC-MVP-05` Terminal UX & Operator Experience (Terminal-native)
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 4`
- **Type:** `CLI Discoverability + Command UX`

## Story
As a new operator, I want discoverable commands and usage examples, so that I can self-serve workflows.

## Objective
Deliver deterministic, terminal-native help and command introspection surfaces so new operators can discover commands, understand argument expectations, recover quickly from invalid invocations, and see command execution targets without leaving the terminal.

## Traceability
- **Functional Requirements:** `FR-009`, `FR-001`
- **Architecture Constraints:** `ADR-002`, `ADR-011`

## Scope

### In Scope
- Enrich command discoverability output with descriptions, argument schema, and executable examples.
- Return actionable invalid-invocation hints with nearest valid command suggestions.
- Add command introspection output that includes each command's primary execution target.
- Preserve command and interactive shell parity at shared discoverability boundaries.
- Preserve deterministic behavior and sensitive-by-default safeguards in help/introspection and validation surfaces.

### Out of Scope
- GUI or web documentation systems.
- Remote dynamic documentation synchronization.
- Plugin command discoverability parity (covered by `POST-01.3`).
- Confirmation summary normalization and audit-link schema changes (covered by `MVP-05.3`).

## Acceptance Criteria
1. **Help contract completeness:** `help` output includes command descriptions, argument schema, and examples for supported commands.
2. **Actionable invalid-invocation UX:** Invalid command invocations return actionable hints and nearest valid command suggestions.
3. **Execution-target introspection:** Introspection output lists command primary execution target.
4. **Command/interactive discoverability parity:** Equivalent discoverability interactions are available in direct command mode and interactive shell mode.
5. **Deterministic discoverability output:** Equivalent command metadata inputs produce stable ordering/formatting of help and introspection sections.
6. **Sensitive-by-default handling:** Help, hints, and introspection surfaces do not leak raw sensitive text/secrets by default.

## Acceptance Criteria Traceability
- **AC1** ← `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md` `Story MVP-05.2`.
- **AC2** ← backlog `Story MVP-05.2` + existing validation error hint contract in `src/endi/routing.py`.
- **AC3** ← backlog `Story MVP-05.2` + architecture execution-backend model in `_bmad-output/planning-artifacts/endi-architecture-final.md` §5.5.
- **AC4** ← architecture `_bmad-output/planning-artifacts/endi-architecture-final.md` §5.1 (direct + interactive shell support) and shared command-routing boundaries.
- **AC5** ← `_bmad-output/planning-artifacts/endi-architecture-final.md` §2 architecture principle: deterministic operations.
- **AC6** ← `project-context.md` guardrails + established sensitive-by-default runtime handling conventions.

## Tasks / Subtasks
- [x] Define canonical command discoverability metadata shape (AC: 1, 3, 5)
  - [x] Specify fields for description, args schema, examples, and execution target.
  - [x] Enforce deterministic command ordering for help/introspection output.
- [x] Implement enriched help rendering surface (AC: 1, 4, 5)
  - [x] Ensure help sections include description, arguments, and examples.
  - [x] Keep output grammar aligned with existing Rich presentation patterns.
- [x] Implement actionable invalid-invocation guidance (AC: 2, 4)
  - [x] Add nearest valid command suggestion behavior.
  - [x] Preserve existing deterministic validation error shape and hint semantics.
- [x] Implement command introspection surface (AC: 3, 4, 5)
  - [x] Surface each command's primary execution target from canonical metadata.
  - [x] Keep shared-boundary behavior aligned between command and interactive shell paths.
- [x] Add strict-gate focused regression coverage (AC: 1-6)
  - [x] Help/introspection contract tests.
  - [x] Invalid-invocation actionable hint + nearest suggestion tests.
  - [x] Deterministic ordering and sensitive-by-default regressions.

## Dev Notes

### ENDI Guardrails (Must Preserve)
- Deterministic behavior: stable ordering and stable message contracts for equivalent metadata/input.
- Safety-by-default: invalid command handling must remain non-executing and explicit.
- Command/conversation parity: shared discoverability boundaries must be semantically aligned.
- Sensitive-by-default handling: avoid exposing raw text or secret-bearing fields in discoverability output.

### Technical Requirements
- Reuse existing command classification/validation logic in `src/endi/routing.py`; extend behavior without weakening current contract shape.
- Keep presentation consistent with `src/endi/presentation.py` helpers and existing CLI rendering patterns in `src/endi/cli.py`.
- Prefer a single canonical source of command discoverability metadata to avoid drift between help and introspection outputs.
- Preserve deterministic structured error conventions for invalid command syntax and argument guidance.

### Implementation Notes Aligned with Existing Patterns
- `src/endi/cli.py` currently centralizes submit behavior and Rich panels; discoverability output should integrate through this surface or adjacent command handlers without introducing parallel formatting stacks.
- `src/endi/routing.py` already emits actionable hints (`/help` guidance); nearest-command suggestions should build on this path with deterministic behavior.
- `tests/test_dual_mode_routing.py` already covers CLI validation UX and command/conversation parity conventions; extend these tests rather than creating disconnected patterns.

### Concrete File-level Guidance
- `src/endi/cli.py`: add/extend help + introspection presentation entry points and render contracts.
- `src/endi/routing.py`: enrich invalid invocation hint path with deterministic nearest-command suggestions.
- `src/endi/presentation.py`: optionally add reusable discoverability rendering helpers if needed for consistency.
- `tests/test_dual_mode_routing.py`: add help/introspection/invalid-invocation UX and parity regressions.
- `tests/` (additional focused test module only if necessary): command metadata contract tests.

### Testing Requirements (Strict Gate)
- **Gate Level:** `Strict` (command spec compliance and operator UX contract).
- Execute quality gates in WSL project `.venv`:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`
- Required test focus:
  - Help output includes description/args/examples for supported commands.
  - Invalid invocations provide actionable hints and nearest valid command suggestions.
  - Introspection output includes primary execution target mapping.
  - Direct command and interactive shell discoverability parity at shared boundaries.
  - Deterministic ordering/formatting and sensitive-by-default regressions.

### Review-Ready Exit Conditions
- [x] All acceptance criteria are covered by automated tests.
- [x] Help and introspection outputs are deterministic and complete.
- [x] Invalid-invocation guidance is actionable and non-executing.
- [x] Shared command/interactive discoverability boundaries preserve semantic parity.
- [x] Sensitive-by-default safeguards are maintained.

## Dependencies
- `mvp-05-1-rich-terminal-theming-and-readability-baseline` (done): shared presentation grammar baseline.
- Existing command validation and hint contracts in `src/endi/routing.py`.
- Existing CLI rendering integration in `src/endi/cli.py`.

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#EPIC-MVP-05: Terminal UX & Operator Experience (Terminal-native)]
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-05.2 — Help, examples, and command introspection]
- [Source: `_bmad-output/planning-artifacts/endi-terminal-ux-mini-spec.md`#Story Linkage]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#2. Architecture Principles (Locked)]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#5.1 CLI Layer]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#5.2 Command Routing]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#5.5 Execution Backends]
- [Source: `project-context.md`#Execution Environment]
- [Source: `project-context.md`#Agent Command Rules]

## Story Completion Note
Implemented, post-review hardened, and validated; ready for review.

## Dev Agent Record

### Agent Model Used
- Cascade (GPT-5)

### Debug Log References
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"` (pass)
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"` (pass)
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"` (pass, 142 passed)

### Completion Notes List
- Added canonical discoverability metadata in `src/endi/routing.py` for supported commands with deterministic ordering fields: command name, description, argument schema, executable examples, and primary execution target.
- Added deterministic nearest-command suggestion logic to invalid command validation hints using `difflib.get_close_matches`, preserving existing validation error contract shape and non-executing safety behavior.
- Added reusable Rich discoverability renderers in `src/endi/presentation.py` for help and introspection panels, including literal-safe argument schema/example rendering and execution target display.
- Integrated discoverability rendering into `src/endi/cli.py` submit flow so `/help` and `/introspect` route through shared metadata and presentation contracts without introducing parallel formatting paths.
- Added focused regressions in `tests/test_presentation.py` and `tests/test_dual_mode_routing.py` for help/introspection completeness, deterministic ordering, nearest-command suggestions, and command-mode discoverability behavior.
- Applied post-review hardening in `src/endi/cli.py` so discoverability panels are keyed by resolved command identity (`command_name`) instead of output-string sentinels, preventing accidental panel rendering collisions when unrelated commands emit `help` or `introspect` as output.
- Added regression coverage in `tests/test_dual_mode_routing.py` for output-string collision scenarios to ensure non-help commands continue to render standard result panels.
- Re-ran strict WSL `.venv` quality gates after final lint and typing corrections: `ruff`, `mypy`, and `pytest` all pass.

### File List
- `src/endi/routing.py`
- `src/endi/presentation.py`
- `src/endi/cli.py`
- `tests/test_presentation.py`
- `tests/test_dual_mode_routing.py`
- `_bmad-output/implementation-artifacts/stories/mvp-05-2-help-examples-and-command-introspection.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log
- 2026-03-24: Implemented MVP-05.2 help/examples/introspection discoverability contract with canonical command metadata, deterministic help and introspection Rich panels, and actionable invalid-invocation nearest-command suggestions while preserving command/conversation guardrails and sensitive-by-default behavior.
- 2026-03-24: Added and stabilized regression coverage for discoverability rendering and validation hints; final strict WSL `.venv` gates passed (`ruff check src tests`, `mypy src`, `pytest` with 140 passed).
- 2026-03-24: Closed post-review finding by replacing output-string sentinel routing in `src/endi/cli.py` with resolved command-name routing and adding collision regressions in `tests/test_dual_mode_routing.py`; strict WSL `.venv` gates re-run and passing (`ruff`, `mypy`, `pytest` with 142 passed).
