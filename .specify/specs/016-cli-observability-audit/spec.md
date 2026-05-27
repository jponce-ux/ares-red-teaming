# Feature Specification: CLI Observability, Run IDs, and Audit Logging

**Feature Branch**: `[016-cli-observability-audit]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/14_add_cli_observability_run_ids_and_audit_logging.md`
**Project Scope**: ARES root Rust project
**Implementation Boundary**: ARES observability and logging code only.
**TDD Requirement**: Implementation for this feature MUST use test-driven development. For every new behavior, bug fix, or behavior-changing modification, add or update a failing unit test first, run the targeted test to record the expected failure, implement the smallest production change required to pass, then refactor only after the targeted test is green. Acceptance criteria are not complete until tests are traceable to the requirement they verify.

## User Scenarios & Testing

### User Story 1 - Trace Every ARES Run (Priority: P1)

As a red-team operator, I can see a run ID attached to attack execution, evaluator decisions, and reports so results are auditable.

**Independent Test**: Run controlled workflow and verify run ID appears in execution results and report metadata.

**Acceptance Scenarios**:

1. **Given** the user does not provide a run ID, **When** ARES starts a run, **Then** ARES generates one and propagates it.
2. **Given** the user provides a run ID, **When** ARES starts a run, **Then** ARES uses that run ID consistently.

### User Story 2 - Emit Safe Structured Audit Logs (Priority: P2)

As a reviewer, I can inspect structured logs for command start/end, attack start/end, evaluator decisions, timeouts, retries, and report generation without leaking secrets by default.

**Independent Test**: Capture logs from controlled run and verify required event fields and redaction.

**Acceptance Scenarios**:

1. **Given** a run executes, **When** logs are emitted, **Then** major workflow stages include run ID and structured fields.
2. **Given** prompt content is sensitive, **When** default logging is used, **Then** raw prompt content is redacted.

### Edge Cases

- Invalid user-provided run ID.
- Logging disabled or quiet mode.
- Verbose mode with evidence retention enabled.
- Timeout and retry events.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST generate or accept a run ID.
- **FR-002**: ARES MUST attach run ID to attack execution results.
- **FR-003**: ARES MUST attach run ID to report output.
- **FR-004**: ARES MUST emit structured tracing events.
- **FR-005**: Events MUST include command start/end, attack start/end, evaluator decisions, timeouts, and report generation.
- **FR-005a**: Events and retained evidence metadata MUST include run ID, attack ID, category, ENDI command metadata, exit code, duration, timeout flag, evaluator decision, severity, and evidence reference when available.
- **FR-006**: ARES MUST redact secrets and sensitive values by default.
- **FR-006a**: Raw prompts and raw ENDI responses MUST be redacted from logs by default and retained only in controlled evidence/report artifacts when configured.
- **FR-007**: ARES MUST support configurable log verbosity.
- **FR-008**: Audit metadata SHOULD be machine-readable where practical.

### Key Entities

- **RunId**: Stable identifier for one ARES run.
- **AuditEvent**: Structured event emitted during execution.
- **EvidenceReference**: Pointer from audit logs to controlled evidence/report output without duplicating sensitive content.
- **LogVerbosity**: User-selected logging level.
- **RedactionPolicy**: Rules for sensitive values and prompt content.

## Success Criteria

- **SC-001**: Every attack run has a run ID.
- **SC-002**: Logs include structured events for major workflow stages.
- **SC-003**: Reports include run ID and execution metadata.
- **SC-004**: Tests or validation cover run ID propagation.

## Assumptions

- `tracing` and `tracing-subscriber` are the standard observability stack.
- Required capture fields come from `.specify/specs/017-endi-target-profile-decisions/ares-endi-contract.md`.
