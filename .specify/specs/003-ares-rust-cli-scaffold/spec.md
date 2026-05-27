# Feature Specification: ARES Rust CLI Scaffold and Workspace Baseline

**Feature Branch**: `[003-ares-rust-cli-scaffold]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/01_create_ares_rust_cli_scaffold.md`
**Project Scope**: ARES root Rust project
**Implementation Boundary**: Implement the root Cargo workspace and `ares/` Rust binary crate only. Do not modify ENDI source.
**TDD Requirement**: Implementation for this feature MUST use test-driven development. For every new behavior, bug fix, or behavior-changing modification, add or update a failing unit test first, run the targeted test to record the expected failure, implement the smallest production change required to pass, then refactor only after the targeted test is green. Acceptance criteria are not complete until tests are traceable to the requirement they verify.

## User Scenarios & Testing

### User Story 1 - Start ARES CLI (Priority: P1)

As a red-team lab user, I can run the ARES CLI and see useful help so the Rust project has a runnable baseline.

**Independent Test**: Run the ARES binary help command and verify it exits successfully and lists available commands.

**Acceptance Scenarios**:

1. **Given** the repository has no nested ARES git repository, **When** the user runs the ARES CLI help command, **Then** the command exits successfully with useful help text.
2. **Given** the user invokes the ARES binary without subcommands, **When** help is requested, **Then** the CLI identifies itself as the ARES red-team CLI.

### User Story 2 - Validate Rust Quality Gates (Priority: P2)

As a contributor, I can run documented Rust quality gates so future tickets start from a known baseline.

**Independent Test**: Run formatting, linting, and tests against the workspace and verify they pass or are documented if adapted during bootstrap.

**Acceptance Scenarios**:

1. **Given** the scaffold exists, **When** contributors run the documented validation commands, **Then** the commands complete successfully.
2. **Given** the scaffold is created under `ares/`, **When** the repository is inspected, **Then** no nested `.git/` exists under `ares/`.

### Edge Cases

- The repository root is not yet a Cargo workspace and MUST become the workspace owner.
- `ares/` already exists with partial files.
- The user runs validation commands before any feature crates exist.
- ENDI files are present but must remain unchanged.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST have a runnable Rust CLI binary.
- **FR-002**: ARES MUST expose useful help output.
- **FR-003**: ARES MUST include baseline command structure for future target, attack, runner, evaluator, and reporting modules.
- **FR-004**: ARES MUST use Cargo and Rust as the implementation stack.
- **FR-004a**: The repository root MUST contain `Cargo.toml` with `[workspace]`, `members = ["ares"]`, and `resolver = "2"`.
- **FR-004b**: `endi/` MUST NOT be included in the Cargo workspace because ENDI is a separate Python auxiliary project.
- **FR-005**: ARES MUST use `clap` for CLI parsing.
- **FR-006**: ARES MUST use `anyhow` at the CLI boundary.
- **FR-007**: ARES MUST initialize a `tracing` logging foundation.
- **FR-008**: ARES MUST document Rust quality gates.
- **FR-009**: ARES MUST remain part of the existing single Git repository and MUST NOT create a nested `.git/` under `ares/`.
- **FR-010**: This feature MUST NOT modify ENDI implementation files.

### Key Entities

- **ARES CLI**: Runnable Rust binary used by red-team operators.
- **CLI Command**: User-facing operation exposed by the ARES binary.
- **Workspace Baseline**: Root Cargo workspace plus `ares/` binary crate configuration and validation commands.

## Success Criteria

- **SC-001**: The ARES CLI help command exits successfully and displays command information.
- **SC-002**: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features`, and `cargo test --workspace` are documented and runnable or explicitly adapted for bootstrap.
- **SC-003**: No ENDI source file changes are required.
- **SC-004**: No nested Git repository exists under `ares/`.

## Assumptions

- The initial scaffold lives in `ares/` as the first member of the root Cargo workspace while the repository remains a single Git repository.
- Later tickets will add concrete target, attack, evaluator, runner, and report modules.
