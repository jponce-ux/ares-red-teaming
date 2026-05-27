# Feature Specification: ENDI Target Policy System Prompt Mitigation

**Feature Branch**: `[018-endi-target-policy-mitigation]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: Analysis finding C1: concrete ENDI mitigation implementation is missing.
**Project Scope**: ENDI auxiliary Python project with cross-project ARES replay dependency.
**Implementation Boundary**: ENDI implementation files, tests, docs, and config live under `endi/`. Spec artifacts live under root `.specify/specs/018-endi-target-policy-mitigation/`. ARES replay implementation remains in ARES specs and code.
**TDD Requirement**: Implementation for this feature MUST use test-driven development. Add failing pytest unit tests before production code, run the targeted test to record the expected failure, implement the smallest ENDI change required to pass, then refactor only after the targeted test is green.

## User Scenarios & Testing

### User Story 1 - Apply ENDI Target Policy (Priority: P1)

As a red-team lab operator, I can run ENDI with an explicit target policy file so the target chatbot receives the ENDI Support Assistant rules before the user prompt.

**Independent Test**: Run ENDI chat through a fake provider with `--system-prompt-file endi/config/target_policy.md` and verify the provider receives a system message before the user message.

**Acceptance Scenarios**:

1. **Given** a readable target policy file, **When** ENDI chat runs with `--system-prompt-file`, **Then** ENDI prepends the file content as a system/developer policy message before the user message.
2. **Given** no policy flag is supplied, **When** ENDI chat runs, **Then** existing baseline behavior remains available for vulnerability baseline testing.
3. **Given** `--output json`, **When** policy injection succeeds, **Then** ENDI returns the normal JSON envelope without exposing the policy content in telemetry by default.

### User Story 2 - Fail Safely for Policy File Errors (Priority: P2)

As an ENDI operator, I receive clear errors when the configured policy file is missing, unreadable, too large, or invalid.

**Independent Test**: Run ENDI with missing/unreadable/oversized policy files and verify structured provider-safe errors without tracebacks.

**Acceptance Scenarios**:

1. **Given** the policy file path is missing, **When** ENDI starts chat, **Then** ENDI returns a structured error and does not call the provider.
2. **Given** the policy file is empty or whitespace-only, **When** ENDI starts chat, **Then** ENDI returns a structured validation error.
3. **Given** the policy file exceeds the configured maximum size, **When** ENDI starts chat, **Then** ENDI returns a structured validation error.

### User Story 3 - Provide Official ENDI Target Policy File (Priority: P3)

As the ARES team, I can reference one official ENDI target policy file for mitigation replay.

**Independent Test**: Validate that `endi/config/target_policy.md` exists, contains R1-R5 target rules, and does not include secrets or operationally harmful payloads.

**Acceptance Scenarios**:

1. **Given** the repository is checked out, **When** ENDI mitigation replay is prepared, **Then** `endi/config/target_policy.md` exists with R1-R5 rules.
2. **Given** the policy file is reviewed, **When** secret and harmful-payload checks run, **Then** no real credentials, real customer data, or operational harmful instructions are present.

## Edge Cases

- Policy path contains spaces.
- Policy file contains non-UTF-8 bytes.
- Policy file is larger than the configured maximum.
- Policy file is empty or whitespace-only.
- Prompt asks ENDI to reveal or transform the policy.
- JSON output is requested for both success and validation failure.

## Requirements

### Functional Requirements

- **FR-001**: ENDI MUST add a `--system-prompt-file` option to `chat` and compatible non-interactive prompt paths.
- **FR-002**: ENDI MUST read the target policy file as UTF-8 text and reject unreadable, missing, empty, or oversized files before provider invocation.
- **FR-003**: ENDI MUST prepend the target policy as a system/developer message before the user message sent to the provider.
- **FR-004**: ENDI MUST NOT include the full target policy text in normal JSON telemetry, logs, or error output.
- **FR-005**: ENDI MUST preserve baseline behavior when no policy file is supplied.
- **FR-006**: ENDI MUST include `endi/config/target_policy.md` with ENDI Support Assistant domain, R1-R5 rules, allowed examples, and disallowed examples.
- **FR-007**: ENDI MUST return structured validation errors for policy file failures without tracebacks.
- **FR-008**: ENDI MUST keep all implementation and tests under `endi/`.

### Key Entities

- **TargetPolicyConfig**: Policy file path, maximum size, and loaded content metadata.
- **TargetPolicyMessage**: System/developer message prepended before user content.
- **PolicyValidationError**: Missing, unreadable, empty, non-UTF-8, or oversized policy failure.

## Success Criteria

- **SC-001**: Unit tests prove provider message ordering is policy first, user prompt second.
- **SC-002**: Unit tests prove missing, empty, non-UTF-8, and oversized policy files fail before provider invocation.
- **SC-003**: CLI JSON-output tests prove policy validation failures are structured and do not include tracebacks.
- **SC-004**: Policy content is not emitted in normal logs/telemetry by default.
- **SC-005**: ENDI validation gates pass from `endi/`: pytest, ruff, and mypy.

## Assumptions

- The policy role name can map to the provider abstraction's existing message role support.
- ARES will use this mitigation in replay specs but will not import ENDI Python code.
- The first implementation can support non-streaming chat only.
