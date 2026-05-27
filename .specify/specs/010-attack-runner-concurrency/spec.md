# Feature Specification: Attack Runner with Bounded Concurrency and Timeouts

**Feature Branch**: `[010-attack-runner-concurrency]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/08_build_attack_runner_with_bounded_concurrency_and_timeouts.md`
**Project Scope**: ARES root Rust project
**Implementation Boundary**: Rust runner implementation in ARES paths.
**TDD Requirement**: Implementation for this feature MUST use test-driven development. For every new behavior, bug fix, or behavior-changing modification, add or update a failing unit test first, run the targeted test to record the expected failure, implement the smallest production change required to pass, then refactor only after the targeted test is green. Acceptance criteria are not complete until tests are traceable to the requirement they verify.

## User Scenarios & Testing

### User Story 1 - Execute Attack Fixtures Against ENDI (Priority: P1)

As a red-team operator, I can execute validated attack fixtures against ENDI and receive structured run results.

**Independent Test**: Run a fixture file with a controlled ENDI adapter and verify result records are produced for every attack.

**Acceptance Scenarios**:

1. **Given** a validated fixture file, **When** ARES runs attacks sequentially, **Then** every attack produces a structured result.
2. **Given** one attack fails, **When** failure continuation is enabled, **Then** ARES records the failure and continues safely.

### User Story 2 - Bound Concurrency and Timeouts (Priority: P2)

As an operator, I can configure concurrency and per-attack timeouts so runs do not exhaust local resources.

**Independent Test**: Run controlled tests proving concurrency never exceeds the configured max and timeout results are captured.

**Acceptance Scenarios**:

1. **Given** max concurrency is configured, **When** ARES executes many attacks, **Then** no more than the configured number run at once.
2. **Given** an attack exceeds its timeout, **When** the timeout elapses, **Then** the result records a timeout without crashing the run.

### Edge Cases

- Empty fixture set.
- Large fixture set.
- ENDI adapter timeout.
- ENDI adapter process failure.
- Cancellation requested mid-run.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST load validated attack fixtures before execution.
- **FR-002**: ARES MUST execute each attack through the ENDI adapter.
- **FR-003**: ARES MUST support sequential execution.
- **FR-004**: ARES MUST support bounded concurrent execution.
- **FR-005**: ARES MUST enforce per-attack timeout.
- **FR-006**: ARES MUST capture execution metadata.
- **FR-006a**: Per-attack metadata MUST include attack ID, category, prompt, command, stdout, stderr, exit code, started time, duration in milliseconds, timeout flag, and parsed ENDI output.
- **FR-007**: ARES MUST continue safely after individual failures when configured.
- **FR-008**: ARES MUST produce structured run results for evaluator and report generation.
- **FR-008a**: Timeouts, Ollama failures, missing models, and malformed ENDI responses MUST be represented as target/harness status values instead of vulnerability severities.
- **FR-009**: ARES MUST use run IDs and attack IDs.
- **FR-010**: ARES MUST emit structured tracing around attack execution.

### Key Entities

- **AttackRunner**: Executes attack cases against ENDI.
- **RunConfig**: Concurrency, timeout, continuation, and target config.
- **AttackRunResult**: Collection of per-attack execution results.
- **AttackExecutionMetadata**: Duration, status, timestamps, and error data.
- **ParsedEndiOutput**: JSON output captured from ENDI for evaluator and report evidence.

## Success Criteria

- **SC-001**: ARES executes a fixture file against a controlled ENDI adapter.
- **SC-002**: Tests cover sequential execution, bounded concurrency, timeout, and failure continuation.
- **SC-003**: Runner output can be consumed by evaluator and report modules.

## Assumptions

- Attack schema, config, and ENDI adapter are implemented first.
- ENDI is the official MVP target and must be invoked through the adapter using the contract in `.specify/specs/017-endi-target-profile-decisions/ares-endi-contract.md`.
