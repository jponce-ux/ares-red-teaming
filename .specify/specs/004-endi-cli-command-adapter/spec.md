# Feature Specification: ENDI CLI Command Adapter

**Feature Branch**: `[004-endi-cli-command-adapter]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/02_implement_endi_cli_command_adapter.md`
**Project Scope**: Cross-project integration: ARES calls ENDI as the official MVP target chatbot; ENDI source remains unchanged.
**Implementation Boundary**: Implement Rust adapter code in ARES paths. Do not edit ENDI implementation files.
**TDD Requirement**: Implementation for this feature MUST use test-driven development. For every new behavior, bug fix, or behavior-changing modification, add or update a failing unit test first, run the targeted test to record the expected failure, implement the smallest production change required to pass, then refactor only after the targeted test is green. Acceptance criteria are not complete until tests are traceable to the requirement they verify.

## User Scenarios & Testing

### User Story 1 - Send Prompt Through ENDI (Priority: P1)

As an ARES runner, I can send a prompt to ENDI Support Assistant through a Rust adapter and receive the captured JSON response.

**Independent Test**: Use a controlled ENDI executable or test command and verify stdout, stderr, status, duration, parsed JSON output, and response are captured.

**Acceptance Scenarios**:

1. **Given** ENDI is configured for `ollama`, `granite4.1:3b`, and `http://localhost:11434`, **When** ARES sends a chat prompt, **Then** the adapter returns captured stdout, stderr, status code, duration, and parsed ENDI JSON envelope.
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
- ENDI returns valid process output that is not a valid ENDI JSON envelope.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST expose an `EndiClient` or equivalent Rust type.
- **FR-002**: The adapter MUST send prompts to ENDI chat commands.
- **FR-002a**: ARES MUST prefer ENDI `chat` for attack execution and MUST expose `submit` for compatibility with the ARES-to-ENDI contract.
- **FR-002b**: `EndiClient` MUST expose `version()`, `chat(prompt, options)`, `submit(prompt, options)`, and `validate_environment()` methods or equivalents.
- **FR-003**: The adapter MUST support configurable ENDI command path and working directory.
- **FR-003a**: The default MVP target configuration MUST be provider `ollama`, model `granite4.1:3b`, base URL `http://localhost:11434`, timeout 60 seconds, and `--output json`.
- **FR-004**: The adapter MUST capture command, stdout, stderr, exit status, started time, duration, timeout outcome, and parsed ENDI output when available.
- **FR-005**: The adapter MUST return typed results for successful command execution.
- **FR-006**: The adapter MUST return typed errors for missing executable, non-zero exit, timeout, malformed output, and spawn failure.
- **FR-007**: The adapter MUST avoid shell injection by using structured process arguments, not raw shell strings.
- **FR-008**: The adapter MUST emit structured tracing events around command execution with sensitive prompt content redacted by default.
- **FR-009**: ENDI implementation files MUST remain unchanged.
- **FR-010**: ARES MUST execute ENDI through subprocess execution only and MUST NOT import ENDI Python code.

### Key Entities

- **EndiClient**: Rust adapter for invoking ENDI.
- **EndiCommandResult**: Captured process output and metadata.
- **ParsedEndiOutput**: Machine-readable ENDI JSON envelope including route, output, status, errors, and telemetry when present.
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
- Product-level ENDI target decisions are defined in `.specify/specs/017-endi-target-profile-decisions/ares-endi-contract.md`.
