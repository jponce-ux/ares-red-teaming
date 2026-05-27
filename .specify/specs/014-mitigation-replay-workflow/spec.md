# Feature Specification: Mitigation Replay Workflow

**Feature Branch**: `[014-mitigation-replay-workflow]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/12_implement_mitigation_replay_workflow.md`
**Project Scope**: Cross-project integration: ARES verifies mitigation effectiveness against ENDI.
**Implementation Boundary**: Replay logic in ARES paths. Do not modify ENDI unless a separate ENDI ticket explicitly scopes that work.

## User Scenarios & Testing

### User Story 1 - Compare Baseline and Mitigated Runs (Priority: P1)

As a red-team operator, I can compare a previous vulnerable run with a post-mitigation run and see whether each finding closed, reduced, stayed unchanged, or regressed.

**Independent Test**: Load two controlled result files with stable attack IDs and verify comparison classifications.

**Acceptance Scenarios**:

1. **Given** baseline and post-mitigation results share attack IDs, **When** replay comparison runs, **Then** ARES classifies each comparable finding.
2. **Given** an attack is missing from one run, **When** comparison runs, **Then** ARES reports the missing comparison clearly.

### User Story 2 - Include Replay in Report (Priority: P2)

As a reviewer, I can see mitigation replay status in the Markdown report.

**Independent Test**: Render a report with replay comparison data and verify closed/reduced/unchanged/regressed statuses appear.

**Acceptance Scenarios**:

1. **Given** replay comparison exists, **When** the report is generated, **Then** report includes replay status for relevant findings.
2. **Given** a result regressed, **When** report renders, **Then** regression is clearly visible.

### Edge Cases

- Baseline result file is missing or malformed.
- Attack IDs do not match.
- Evaluator decision changes from success to inconclusive.
- Post-mitigation execution error occurs.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST select relevant attacks for replay.
- **FR-002**: ARES MUST run attacks before mitigation or load a previous baseline result.
- **FR-003**: ARES MUST run attacks after mitigation.
- **FR-004**: ARES MUST compare evaluator decisions using stable attack IDs.
- **FR-005**: ARES MUST classify mitigation result as closed, partially reduced, unchanged, or regressed.
- **FR-006**: ARES MUST include replay findings in the report.
- **FR-007**: Replay logic MUST be independent from report rendering where practical.

### Key Entities

- **ReplayBaseline**: Previous run results.
- **ReplayCandidate**: Attack selected for replay.
- **ReplayComparison**: Before/after decision comparison.
- **MitigationStatus**: Closed, partially reduced, unchanged, regressed.

## Success Criteria

- **SC-001**: ARES compares two runs for the same attack set.
- **SC-002**: Replay output identifies closed, reduced, unchanged, and regressed findings.
- **SC-003**: Markdown report includes mitigation replay status.
- **SC-004**: Tests cover comparison logic.

## Assumptions

- Mitigations themselves are applied outside this ticket unless a separate ENDI ticket scopes them.
