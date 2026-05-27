# Tasks: CLI Observability, Run IDs, and Audit Logging

**Project Scope**: ARES root Rust project

## Phase 1: Setup

- [ ] T001 Add observability dependencies to `ares/Cargo.toml`
- [ ] T002 Create observability module files in `ares/src/observability/`

## Phase 2: User Story 1 - Trace Every ARES Run (P1)

- [ ] T003 [P] [US1] Add run ID generation and propagation tests in `ares/tests/observability.rs`
- [ ] T004 [US1] Define typed `RunId` in `ares/src/observability/mod.rs`
- [ ] T005 [US1] Add CLI option to accept run ID in `ares/src/cli.rs`
- [ ] T006 [US1] Propagate run ID into runner results and report metadata in ARES modules

## Phase 3: User Story 2 - Emit Safe Structured Audit Logs (P2)

- [ ] T007 [P] [US2] Add log redaction tests in `ares/tests/observability.rs`
- [ ] T008 [P] [US2] Add structured event tests for command, attack, evaluator, timeout, and report stages in `ares/tests/observability.rs`
- [ ] T009 [US2] Implement `tracing-subscriber` initialization and verbosity settings in `ares/src/observability/mod.rs`
- [ ] T010 [US2] Implement redaction policy in `ares/src/observability/redaction.rs`
- [ ] T011 [US2] Add structured tracing events across CLI, runner, evaluator, adapter, and reporting modules

## Phase 4: Validation

- [ ] T012 Run `cargo fmt --all --check`
- [ ] T013 Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T014 Run `cargo test --workspace`

## Dependencies

Should be integrated after core runner/evaluator/report modules exist, but run ID type can be introduced earlier.
