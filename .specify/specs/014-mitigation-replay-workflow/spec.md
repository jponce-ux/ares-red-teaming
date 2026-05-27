# Feature Specification: Mitigation Replay Workflow

**Feature Branch**: `[014-mitigation-replay-workflow]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/12_implement_mitigation_replay_workflow.md`
**Project Scope**: Cross-project integration: ARES verifies mitigation effectiveness against ENDI.
**Implementation Boundary**: Replay logic in ARES paths. The required MVP mitigation is implemented by `.specify/specs/018-endi-target-policy-mitigation/`; any ENDI implementation files for that mitigation must stay under `endi/`.
**TDD Requirement**: Implementation for this feature MUST use test-driven development. For every new behavior, bug fix, or behavior-changing modification, add or update a failing unit test first, run the targeted test to record the expected failure, implement the smallest production change required to pass, then refactor only after the targeted test is green. Acceptance criteria are not complete until tests are traceable to the requirement they verify.

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
- ENDI mitigation changes target behavior but ARES replay still uses the same stable attack IDs.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST select relevant attacks for replay.
- **FR-002**: ARES MUST run attacks before mitigation or load a previous baseline result.
- **FR-003**: ARES MUST run attacks after mitigation.
- **FR-003a**: The required MVP mitigation to replay MUST be an ENDI-side explicit target policy/system prompt applied before the user message.
- **FR-003b**: ARES replay MUST treat `.specify/specs/018-endi-target-policy-mitigation/` as the ENDI-side mitigation dependency and MUST NOT duplicate ENDI implementation inside ARES.
- **FR-004**: ARES MUST compare evaluator decisions using stable attack IDs.
- **FR-005**: ARES MUST classify mitigation result as closed, partially reduced, unchanged, or regressed.
- **FR-006**: ARES MUST include replay findings in the report.
- **FR-007**: Replay logic MUST be independent from report rendering where practical.
- **FR-008**: ARES MUST record that ENDI owns target behavior changes while ARES owns replay proof, evidence, evaluation, and reporting.

### Key Entities

- **ReplayBaseline**: Previous run results.
- **ReplayCandidate**: Attack selected for replay.
- **ReplayComparison**: Before/after decision comparison.
- **MitigationStatus**: Closed, partially reduced, unchanged, regressed.
- **EndiTargetPolicyMitigation**: ENDI-side policy/system prompt enforcement applied before replay.

## Success Criteria

- **SC-001**: ARES compares two runs for the same attack set.
- **SC-002**: Replay output identifies closed, reduced, unchanged, and regressed findings.
- **SC-003**: Markdown report includes mitigation replay status.
- **SC-004**: Tests cover comparison logic.

## Assumptions

- Product decisions require one concrete ENDI-side mitigation for MVP. The ENDI implementation is specified in `.specify/specs/018-endi-target-policy-mitigation/`; this feature owns replaying relevant attacks through ARES after that mitigation exists.
