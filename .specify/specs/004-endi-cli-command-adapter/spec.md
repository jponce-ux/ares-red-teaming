# Feature Specification: ENDI CLI Command Adapter

**Feature Branch**: `[004-endi-cli-command-adapter]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/02_implement_endi_cli_command_adapter.md`
**Project Scope**: Cross-project integration: ARES calls ENDI, ENDI source remains unchanged.
**Implementation Boundary**: Implement Rust adapter code in ARES paths. Do not edit ENDI implementation files.

## User Scenarios & Testing

### User Story 1 - Send Prompt Through ENDI (Priority: P1)

As an ARES runner, I can send a prompt to ENDI through a Rust adapter and receive the captured response.

**Independent Test**: Use a controlled ENDI executable or test command and verify stdout, stderr, status, duration, and response are captured.

**Acceptance Scenarios**:

1. **Given** ENDI is configured, **When** ARES sends a chat prompt, **Then** the adapter returns captured stdout, stderr, status code, and duration.
2. **Given** ENDI returns non-zero, **When** ARES sends a prompt, **Then** the adapter returns a typed non-zero-exit error/result without panicking.

### User Story 2 - Bound ENDI Process Execution (Priority: P2)

As a red-team operator, I can configure ENDI path, working directory, and timeout so ARES process execution remains safe.

**Independent Test**: Run adapter tests for missing command, spawn failure, timeout, and safe argument construction.

**Acceptance Scenarios**:

1. **Given** ENDI is missing, **When** the adapter runs, **Then** a typed missing-executable error is returned.
2. **Given** ENDI exceeds timeout, **When** the adapter runs, **Then** the process is terminated and a typed timeout result is returned.

### Edge Cases

- ENDI executable path contains spaces.
- Prompt contains shell metacharacters.
- ENDI emits malformed or empty output.
- ENDI writes useful diagnostic data to stderr.
- Process spawn fails before execution.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST expose an `EndiClient` or equivalent Rust type.
- **FR-002**: The adapter MUST send prompts to ENDI chat commands.
- **FR-003**: The adapter MUST support configurable ENDI command path and working directory.
- **FR-004**: The adapter MUST capture stdout, stderr, exit status, duration, and timeout outcome.
- **FR-005**: The adapter MUST return typed results for successful command execution.
- **FR-006**: The adapter MUST return typed errors for missing executable, non-zero exit, timeout, malformed output, and spawn failure.
- **FR-007**: The adapter MUST avoid shell injection by using structured process arguments, not raw shell strings.
- **FR-008**: The adapter MUST emit structured tracing events around command execution with sensitive prompt content redacted by default.
- **FR-009**: ENDI implementation files MUST remain unchanged.

### Key Entities

- **EndiClient**: Rust adapter for invoking ENDI.
- **EndiCommandResult**: Captured process output and metadata.
- **EndiCommandError**: Typed execution failure.
- **EndiExecutionConfig**: Command path, working directory, timeout, and output parsing settings.

## Success Criteria

- **SC-001**: ARES can execute at least one ENDI chat prompt through the adapter.
- **SC-002**: Success, non-zero exit, missing command, and timeout paths are covered by tests.
- **SC-003**: No adapter code uses shell interpolation for prompts.
- **SC-004**: ENDI source remains unchanged.

## Assumptions

- ENDI has a CLI command that can accept a prompt and print a response.
- Adapter tests may use controlled local binaries or scripts instead of the real ENDI runtime.
