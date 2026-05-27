# Tasks: Attack Runner with Bounded Concurrency and Timeouts

**Project Scope**: ARES root Rust project

## Phase 1: Setup

- [ ] T001 Verify attack schema, config, and ENDI adapter modules exist
- [ ] T002 Add runner module files in `ares/src/runner/`

## Phase 2: User Story 1 - Execute Attack Fixtures Against ENDI (P1)

- [ ] T003 [P] [US1] Add sequential execution test in `ares/tests/attack_runner.rs`
- [ ] T004 [P] [US1] Add failure-continuation test in `ares/tests/attack_runner.rs`
- [ ] T005 [US1] Define `AttackRunner`, `RunConfig`, `AttackRunResult`, and per-attack metadata in `ares/src/runner/`
- [ ] T006 [US1] Implement sequential fixture execution through ENDI adapter in `ares/src/runner/mod.rs`
- [ ] T007 [US1] Preserve run IDs, attack IDs, output, errors, and duration in `ares/src/runner/result.rs`

## Phase 3: User Story 2 - Bound Concurrency and Timeouts (P2)

- [ ] T008 [P] [US2] Add bounded concurrency test in `ares/tests/runner_concurrency.rs`
- [ ] T009 [P] [US2] Add timeout test in `ares/tests/runner_concurrency.rs`
- [ ] T010 [US2] Implement Tokio bounded concurrency in `ares/src/runner/mod.rs`
- [ ] T011 [US2] Implement per-attack timeout handling in `ares/src/runner/mod.rs`
- [ ] T012 [US2] Add structured `tracing` spans/events in `ares/src/runner/mod.rs`

## Phase 4: Validation

- [ ] T013 Run `cargo fmt --all --check`
- [ ] T014 Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T015 Run `cargo test --workspace`

## Dependencies

Requires tickets 003-006. T010 depends on T005-T007.
