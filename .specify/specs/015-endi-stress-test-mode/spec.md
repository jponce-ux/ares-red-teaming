# Feature Specification: Stress Test Mode for ENDI CLI

**Feature Branch**: `[015-endi-stress-test-mode]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/13_add_stress_test_mode_for_endi_cli.md`
**Project Scope**: ARES root Rust project
**Implementation Boundary**: ARES stress runner code only. ENDI source remains unchanged.
**TDD Requirement**: Implementation for this feature MUST use test-driven development. For every new behavior, bug fix, or behavior-changing modification, add or update a failing unit test first, run the targeted test to record the expected failure, implement the smallest production change required to pass, then refactor only after the targeted test is green. Acceptance criteria are not complete until tests are traceable to the requirement they verify.

## User Scenarios & Testing

### User Story 1 - Run Controlled ENDI Stress Test (Priority: P1)

As a red-team operator, I can run a configured number of ENDI chat prompts under bounded load to inspect resilience, latency, timeouts, and failures.

**Independent Test**: Run stress mode against a controlled ENDI adapter and verify total request count, bounded concurrency, and summary metrics.

**Acceptance Scenarios**:

1. **Given** a request count and concurrency limit, **When** stress mode runs, **Then** exactly the configured number of prompts are attempted and concurrency remains bounded.
2. **Given** some requests fail or time out, **When** stress mode completes, **Then** the summary includes error, timeout, and non-zero-exit counts.

### Edge Cases

- Request count is zero.
- Concurrency exceeds request count.
- ENDI is slow or times out.
- ENDI returns mixed success and failure.
- Prompt fixture is empty.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST run a configured number of ENDI chat prompts.
- **FR-001a**: Stress mode MUST target ENDI Support Assistant through the ENDI adapter and the official MVP provider/model/base URL unless overridden.
- **FR-002**: ARES MUST support bounded concurrency.
- **FR-003**: ARES MUST support per-request timeout.
- **FR-004**: ARES MUST capture latency metrics.
- **FR-005**: ARES MUST capture error counts.
- **FR-005a**: ARES MUST distinguish target errors, harness errors, timeouts, and successful responses in the stress summary.
- **FR-006**: ARES MUST capture non-zero exit counts.
- **FR-007**: ARES MUST capture timeout counts.
- **FR-008**: ARES MUST produce a stress summary.
- **FR-009**: ARES MUST avoid unbounded resource usage.
- **FR-010**: Stress fixtures MUST remain safe and lab-constrained.

### Key Entities

- **StressRunConfig**: Request count, concurrency, timeout, prompt source.
- **StressSample**: Per-request latency and outcome.
- **StressSummary**: Aggregated latency and failure metrics.
- **StressTargetConfig**: ENDI target configuration inherited from ARES runtime config.

## Success Criteria

- **SC-001**: ARES exposes a stress-test command or mode.
- **SC-002**: Stress runs target ENDI through the ENDI adapter.
- **SC-003**: Results include latency and failure summary.
- **SC-004**: Tests cover bounded concurrency and metric aggregation.

## Assumptions

- Stress mode reuses ENDI adapter and Tokio execution patterns from the attack runner.
- Stress mode uses the ARES-to-ENDI subprocess contract from `.specify/specs/017-endi-target-profile-decisions/ares-endi-contract.md`.
