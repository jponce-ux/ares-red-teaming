# Ticket: Add ARES Configuration and Runtime Settings

## Scope
ARES

## Context
ARES needs repeatable local execution against ENDI with explicit runtime settings for command paths, timeouts, report output, concurrency, and fixture locations.

Before creating Spec Kit artifacts or implementation, always read:

- `AGENTS.md`
- `.specify/memory/constitution.md`

## Goal
Implement ARES configuration loading and CLI overrides for local red-team runs.

## Required Spec Kit Flow

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-analyze`
5. `$speckit-implement`

## Functional Requirements

- Support a config file for ARES runtime settings.
- Support CLI flags overriding config values.
- Configure ENDI path or command.
- Configure ENDI working directory.
- Configure attack fixture path.
- Configure report output path.
- Configure timeout per attack.
- Configure max concurrency.
- Configure evidence retention behavior.

## Technical Requirements

- Use `serde` for config parsing.
- Use typed duration and concurrency values.
- Validate config before execution.
- Do not store credentials or secrets in tracked config examples.
- Provide a safe example config.

## Acceptance Criteria

- ARES can load config from a documented default path or explicit CLI flag.
- CLI overrides work predictably.
- Invalid config fails with clear messages.
- Config supports ENDI command execution settings.
- Tests cover config parsing, defaults, and validation failures.

## Validation Commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```
