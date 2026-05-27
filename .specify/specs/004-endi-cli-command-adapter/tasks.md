# Tasks: ENDI CLI Command Adapter

**Project Scope**: Cross-project integration; Rust implementation in ARES only.

## Phase 1: Setup

- [ ] T001 Verify existing ARES scaffold paths in `ares/src/`
- [ ] T002 Add Tokio process/test dependencies to `ares/Cargo.toml`

## Phase 2: Foundation

- [ ] T003 [P] Define `EndiExecutionConfig` in `ares/src/targets/endi.rs`
- [ ] T004 [P] Define `EndiCommandResult` and `EndiCommandError` in `ares/src/targets/endi.rs`

## Phase 3: User Story 1 - Send Prompt Through ENDI (P1)

- [ ] T005 [P] [US1] Add success integration test in `ares/tests/endi_adapter.rs`
- [ ] T006 [US1] Implement `EndiClient::chat` with structured arguments in `ares/src/targets/endi.rs`
- [ ] T007 [US1] Capture stdout, stderr, status, and duration in `ares/src/targets/endi.rs`

## Phase 4: User Story 2 - Bound ENDI Process Execution (P2)

- [ ] T008 [P] [US2] Add tests for missing command, non-zero exit, and timeout in `ares/tests/endi_adapter.rs`
- [ ] T009 [US2] Implement timeout handling with `tokio::time::timeout` in `ares/src/targets/endi.rs`
- [ ] T010 [US2] Add `tracing` spans/events with prompt redaction in `ares/src/targets/endi.rs`

## Phase 5: Validation

- [ ] T011 Run `cargo fmt --all --check`
- [ ] T012 Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T013 Run `cargo test --workspace`

## Dependencies

T003-T004 before adapter implementation. Tests precede implementation per story.
