# Feature Specification: Evidence Capture and Rule Violation Evaluation

**Feature Branch**: `[011-evidence-evaluator]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/09_capture_evidence_and_evaluate_rule_violations.md`
**Project Scope**: ARES root Rust project
**Implementation Boundary**: Rust evaluator and evidence models in ARES paths.

## User Scenarios & Testing

### User Story 1 - Preserve Attack Evidence (Priority: P1)

As a reviewer, I can inspect attack prompt, ENDI response, and command metadata for each run result.

**Independent Test**: Convert controlled runner results into evidence records and verify all required fields are retained according to evidence settings.

**Acceptance Scenarios**:

1. **Given** an attack executes, **When** evidence is captured, **Then** prompt, response, category, target rule, and command metadata are retained.
2. **Given** evidence retention is restricted, **When** telemetry/logging occurs, **Then** sensitive evidence is not logged outside controlled output.

### User Story 2 - Evaluate Target Rule Violations (Priority: P2)

As a red-team operator, I can get an evaluator decision, severity, rationale, and matched heuristic for each attack result.

**Independent Test**: Run evaluator fixtures for positive, negative, inconclusive, and execution-error cases.

**Acceptance Scenarios**:

1. **Given** response contains system prompt leakage indicators, **When** evaluator runs, **Then** it returns a success decision with rationale.
2. **Given** response safely refuses, **When** evaluator runs, **Then** it returns failure or safe-completion decision with rationale.
3. **Given** response is ambiguous, **When** evaluator runs, **Then** it returns inconclusive with rationale.

### Edge Cases

- Empty ENDI response.
- Execution error with no model response.
- Partial policy violation.
- Ambiguous response.
- Malicious-code simulation text.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST store attack prompt.
- **FR-002**: ARES MUST store ENDI response.
- **FR-003**: ARES MUST store command execution metadata.
- **FR-004**: ARES MUST evaluate whether target rules were violated.
- **FR-005**: ARES MUST assign decision: success, failure, inconclusive, or execution error.
- **FR-006**: ARES MUST assign severity.
- **FR-007**: ARES MUST store evaluator rationale.
- **FR-008**: ARES MUST store matched heuristic where applicable.
- **FR-009**: Initial deterministic heuristics MUST cover system prompt leakage, domain boundary violations, unsafe malicious-code assistance, and refusal/safe completion.
- **FR-010**: Sensitive evidence MUST NOT be logged outside controlled evidence/report output.

### Key Entities

- **EvidenceRecord**: Attack prompt, response, metadata, and rule context.
- **EvaluatorDecision**: Success, failure, inconclusive, execution error.
- **Severity**: Critical, high, medium, low.
- **HeuristicMatch**: Deterministic rule matched by evaluator.
- **EvaluatorRationale**: Human-readable explanation.

## Success Criteria

- **SC-001**: Every attack result receives an evaluator decision.
- **SC-002**: Every decision includes rationale and severity where applicable.
- **SC-003**: Tests cover positive, negative, inconclusive, and execution-error evaluator cases.

## Assumptions

- MVP starts with deterministic heuristics; LLM-as-judge can be added later.
