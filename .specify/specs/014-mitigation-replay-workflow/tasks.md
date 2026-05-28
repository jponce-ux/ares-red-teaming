# Tasks: Mitigation Replay Workflow

**Project Scope**: Cross-project integration, implemented in ARES.

## TDD Execution Rules

- Every behavior-changing production task in this file MUST be executed with the red-green-refactor loop.
- Before editing production code, add or update a `[TDD-RED]` unit test covering the requirement or acceptance criterion.
- Run the targeted test and record the expected failure before implementation.
- Implement the smallest `[TDD-GREEN]` production change needed to pass that test.
- Re-run the targeted test and record the pass before moving to the next behavior.
- Refactor only after the targeted test is green, then re-run the targeted test.
- Run broader validation at the end of each user-story phase and at final validation.
- Do not mark a task complete if its test was skipped, ignored, or not run unless the reason is documented next to the task.

### Required TDD task expansion

For every `[TDD-RED]` task, execution MUST include two recorded steps before any `[TDD-GREEN]` task starts: create or update the failing unit test, then run the targeted test command and record the expected failure. For every `[TDD-GREEN]` task, execution MUST include the minimal production change and a targeted test run that confirms the behavior is green. If a behavior-changing task lacks an explicit `[TDD-RED]` predecessor, add that test task before implementation.

**Accepted TDD shorthand**: A single `[TDD-RED]` task may include both creating the failing test and running the targeted command when the task text explicitly names the target test command or the command is listed immediately after it. A single `[TDD-GREEN]` task may include both the minimal production change and the targeted pass-confirmation command when the task text explicitly says to run and confirm the targeted test. Setup, dependency, and documentation-only tasks are not requirement coverage unless a later test or validation task exercises them.


## Phase 1: Setup

- [x] T001 Create replay module files in `ares/src/replay/`
- [x] T002 Verify runner/evaluator/report result types are available
- [x] T003 Verify `.specify/specs/018-endi-target-policy-mitigation/` exists and defines ENDI-owned target policy/system prompt mitigation under `endi/`

## Phase 2: User Story 1 - Compare Baseline and Mitigated Runs (P1)

- [x] T004 [TDD-RED] Add comparison tests for closed, reduced, unchanged, regressed, missing baseline, and execution-error cases in `ares/tests/mitigation_replay.rs`
- [x] T005 [TDD-GREEN] Define `ReplayBaseline`, `ReplayCandidate`, `ReplayComparison`, and `MitigationStatus` in `ares/src/replay/mod.rs`
- [x] T006 [TDD-GREEN] Implement stable attack ID matching and decision comparison in `ares/src/replay/comparison.rs`
- [x] T007 [TDD-GREEN] Implement result-file loading or baseline handoff in `ares/src/replay/mod.rs`
- [x] T008 [TDD-GREEN] [US1] Record mitigation metadata identifying ENDI target policy/system prompt enforcement as the MVP mitigation in `ares/src/replay/mod.rs`

## Phase 3: User Story 2 - Include Replay in Report (P2)

- [x] T009 [TDD-RED] Add report integration test for replay statuses in `ares/tests/mitigation_replay.rs`
- [x] T010 [TDD-GREEN] [US2] Expose replay comparison data to reporting module in `ares/src/replay/mod.rs`
- [x] T011 [TDD-GREEN] [US2] Add replay status section to Markdown report renderer in `ares/src/reporting/markdown.rs`

## Phase 4: Validation

- [x] T012 [VALIDATE] Run `cargo fmt --all --check`
- [x] T013 [VALIDATE] Run `cargo clippy --workspace --all-targets --all-features`
- [x] T014 [VALIDATE] Run `cargo test --workspace`

## Implementation Record

- 2026-05-27: Added replay comparison model, ENDI target-policy mitigation metadata, stable attack-ID matching, status classification, and Markdown report integration. Red phase: `cargo test -p ares --test mitigation_replay` first failed because `ares::replay` and report replay fields were missing. Green phase passed after implementation. Final validation passed: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features`, `cargo test --workspace`.

## Dependencies

Requires runner/evaluator/report artifacts.
