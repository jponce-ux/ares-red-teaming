# Tasks: Stress Test Mode for ENDI CLI

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

- [x] T001 Create stress module files in `ares/src/stress/`
- [x] T002 Add stress command shape to `ares/src/cli.rs`

## Phase 2: User Story 1 - Run Controlled ENDI Stress Test (P1)

- [x] T003 [TDD-RED] Add bounded concurrency stress test in `ares/tests/stress_mode.rs`
- [x] T004 [TDD-RED] Add metric aggregation test for success, target error, harness error, timeout, and non-zero exit counts in `ares/tests/stress_mode.rs`
- [x] T005 [TDD-GREEN] Define `StressRunConfig`, `StressTargetConfig`, `StressSample`, and `StressSummary` in `ares/src/stress/metrics.rs`
- [x] T006 [TDD-GREEN] Implement stress execution through ENDI adapter with Tokio bounded concurrency in `ares/src/stress/mod.rs`
- [x] T007 [TDD-GREEN] Implement latency and failure aggregation in `ares/src/stress/metrics.rs`
- [x] T008 [TDD-GREEN] Wire stress command into ARES CLI in `ares/src/cli.rs`
- [x] T009 [TDD-GREEN] [US1] Reuse ENDI MVP target defaults from ARES runtime config unless explicitly overridden

## Phase 3: Validation

- [x] T010 [VALIDATE] Run `cargo fmt --all --check`
- [x] T011 [VALIDATE] Run `cargo clippy --workspace --all-targets --all-features`
- [x] T012 [VALIDATE] Run `cargo test --workspace`

## Implementation Record

- 2026-05-27: Added stress run config, target defaults, sample statuses, summary aggregation, and CLI action recognition for `stress`. Red phase: `cargo test -p ares --test stress_mode` first failed because `ares::stress` was missing. A follow-up red phase added `stress_mode_executes_repeated_prompts_through_endi_contract`, which first failed because `run_stress` was missing. Green phase implemented stress execution through the ENDI contract and Tokio-backed bounded runner, mapping timeout, non-zero exit, target-error, harness-error, and success samples into a summary. Final validation passed: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features -- -D warnings`, `cargo test --workspace --all-features`.
- 2026-05-28: Completed CLI wiring for stress mode. Red phase: `cargo test -p ares --test cli_stress cli_stress_runs_endi_contract_and_prints_summary` failed because the CLI printed only the placeholder `ARES stress mode`. Green phase added `stress` CLI options for request count, concurrency, prompt, ENDI executable, working directory, timeout, provider, model, and base URL, then executed stress mode through `EndiClient` and printed a deterministic summary. Targeted green commands passed: `cargo test -p ares --test cli_stress cli_stress_runs_endi_contract_and_prints_summary` and `cargo test -p ares cli::tests::stress_action_accepts_runtime_options`. Final validation passed: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features -- -D warnings`, `cargo test --workspace --all-features`.

## Dependencies

Requires ENDI adapter and config modules.
