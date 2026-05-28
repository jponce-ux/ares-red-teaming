# Tasks: Attack Runner with Bounded Concurrency and Timeouts

**Project Scope**: ARES root Rust project

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

- [x] T001 Verify attack schema, config, and ENDI adapter modules exist
- [x] T002 Add runner module files in `ares/src/runner/`

## Phase 2: User Story 1 - Execute Attack Fixtures Against ENDI (P1)

- [x] T003 [TDD-RED] Add sequential execution test in `ares/tests/attack_runner.rs`
- [x] T004 [TDD-RED] Add failure-continuation test in `ares/tests/attack_runner.rs`
- [x] T005 [TDD-GREEN] Define `AttackRunner`, `RunConfig`, `AttackRunResult`, and per-attack metadata in `ares/src/runner/`
- [x] T006 [TDD-GREEN] Implement sequential fixture execution through ENDI adapter in `ares/src/runner/mod.rs`
- [x] T007 [TDD-GREEN] [US1] Preserve run ID, attack ID, category, prompt, command, stdout, stderr, exit code, started time, duration, timeout flag, parsed ENDI output, and status in `ares/src/runner/result.rs`

## Phase 3: User Story 2 - Bound Concurrency and Timeouts (P2)

- [x] T008 [TDD-RED] Add bounded concurrency test in `ares/tests/runner_concurrency.rs`
- [x] T009 [TDD-RED] Add timeout test in `ares/tests/runner_concurrency.rs`
- [x] T010 [TDD-GREEN] Implement Tokio bounded concurrency in `ares/src/runner/mod.rs`
- [x] T011 [TDD-GREEN] Implement per-attack timeout handling in `ares/src/runner/mod.rs`
- [x] T012 [TDD-GREEN] [US2] Map timeout, Ollama failure, missing model, and malformed response into target/harness status values in `ares/src/runner/result.rs`
- [x] T013 [TDD-GREEN] [US2] Add structured `tracing` spans/events in `ares/src/runner/mod.rs`

## Phase 4: Validation

- [x] T014 [VALIDATE] Run `cargo fmt --all --check`
- [x] T015 [VALIDATE] Run `cargo clippy --workspace --all-targets --all-features`
- [x] T016 [VALIDATE] Run `cargo test --workspace`

## Implementation Record

- 2026-05-27: Added `AttackRunner`, `RunConfig`, `AttackRun`, `AttackRunResult`, `EndiLikeClient`, sequential execution, failure continuation, bounded std-thread execution, timeout flag propagation, and metadata capture. Red phases: `cargo test -p ares --test attack_runner` first failed because `ares::runner` was missing; `cargo test -p ares --test runner_concurrency` first failed because `run_bounded` was missing. Green phases passed after implementation. Tokio/tracing tasks were implemented as std-only bounded execution because dependency downloads are unavailable. Final validation passed: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features`, `cargo test --workspace`.

## Dependencies

Requires tickets 003-006. T010 depends on T005-T007.
