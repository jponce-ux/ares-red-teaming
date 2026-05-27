# Ticket: Implement ENDI CLI Command Adapter

## Scope
Cross-project integration: ARES calls ENDI, but ENDI implementation files remain under `endi/`.

## Context
ARES must attack the existing ENDI CLI chatbot target. The first required integration is a Rust adapter that can execute ENDI CLI commands safely and capture outputs.

Before creating Spec Kit artifacts or implementation, always read:

- `AGENTS.md`
- `.specify/memory/constitution.md`

## Goal
Implement an ARES-side ENDI command adapter with methods to execute ENDI CLI commands, send prompts, capture responses, and surface execution failures without panics.

## Required Spec Kit Flow

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-analyze`
5. `$speckit-implement`

## Functional Requirements

- Add an `EndiClient` or equivalent Rust type.
- Provide methods for executing ENDI chat commands.
- Support configurable ENDI command path or working directory.
- Support sending a prompt to ENDI.
- Capture stdout, stderr, exit status, duration, and timeout outcome.
- Return typed execution results.
- Return typed errors for missing executable, non-zero exit, timeout, malformed output, and process spawn failure.
- Avoid shell injection by using structured process arguments instead of raw shell strings.

## Expected Behavior

ARES should be able to run an ENDI chat prompt through a Rust interface similar to:

```text
EndiClient::chat(prompt) -> EndiCommandResult
```

The exact API should follow Rust idioms and project conventions.

## Technical Requirements

- Use `tokio::process::Command` if the app is async.
- Use bounded timeout handling.
- Use `thiserror` for adapter/domain errors where useful.
- Use `tracing` spans/events around command execution.
- Redact sensitive prompt content from logs unless explicitly retained as controlled evidence.

## Acceptance Criteria

- ARES can execute at least one ENDI chat prompt.
- stdout, stderr, status code, and duration are captured.
- Timeout behavior is implemented and tested.
- Command execution does not use unsafe shell interpolation.
- Unit or integration tests cover success, non-zero exit, missing command, and timeout paths.
- ENDI source remains unchanged unless a later ticket explicitly targets ENDI.

## Validation Commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```
