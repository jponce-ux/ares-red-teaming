# Ticket: Create ARES Rust CLI Scaffold and Workspace Baseline

## Scope
ARES

## Context
ARES is the Rust-based attacker CLI in the repository root. ENDI is an auxiliary Python chatbot target under `endi/`. This ticket establishes the Rust CLI foundation for ARES without modifying ENDI.

Before creating Spec Kit artifacts or implementation, always read:

- `AGENTS.md`
- `.specify/memory/constitution.md`

## Goal
Create the initial ARES Rust CLI project structure using Cargo, aligned with the project constitution and agent instructions.

## Required Spec Kit Flow

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-analyze`
5. `$speckit-implement`

## Functional Requirements

- Create or validate the ARES Rust CLI project folder.
- Ensure ARES is a runnable binary CLI.
- Add baseline CLI command structure.
- Add baseline configuration for formatting, linting, and tests.
- Ensure the repository remains a single Git project.
- Do not create a nested Git repository inside `ares/`.

## Technical Requirements

- Use Rust and Cargo.
- Use `clap` for CLI parsing.
- Use `anyhow` at the CLI boundary.
- Use `tracing` for logging foundation.
- Prefer a structure that can later support modules for targets, attacks, evaluators, runners, and reports.

## Suggested Structure

```text
repo-root/
  ares/
    Cargo.toml
    src/
      main.rs
      cli.rs
      config.rs
      targets/
      attacks/
      runner/
      evaluator/
      reporting/
```

## Acceptance Criteria

- `cargo run` starts the ARES CLI.
- The CLI exposes a useful help command.
- No ENDI source files are modified.
- No nested `.git/` folder is created inside `ares/`.
- Rust quality gates are documented in the plan and tasks.

## Validation Commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```

Adapt commands if the repository is not yet a Cargo workspace.
