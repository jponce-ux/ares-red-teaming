# Feature Specification: Manual Attack Documentation Artifacts

**Feature Branch**: `[013-manual-attack-documentation]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/11_add_manual_attack_documentation_artifacts.md`
**Project Scope**: ARES documentation and Spec Kit artifacts
**Implementation Boundary**: Documentation artifacts under `.specify/specs/013-manual-attack-documentation/`; no ENDI source changes.
**TDD Requirement**: Implementation for this feature MUST use test-driven development. For every new behavior, bug fix, or behavior-changing modification, add or update a failing unit test first, run the targeted test to record the expected failure, implement the smallest production change required to pass, then refactor only after the targeted test is green. Acceptance criteria are not complete until tests are traceable to the requirement they verify.
**Evidence Status**: The checked-in `manual-attacks.md` and `reflection-checkpoints.md` files are templates until real ENDI executions are recorded. Placeholder rows do not satisfy the MVP evidence requirement.

## User Scenarios & Testing

### User Story 1 - Record Manual Attack Results (Priority: P1)

As a lab team, we can document at least five manual ENDI attacks across distinct categories before or alongside automation.

**Independent Test**: Review `manual-attacks.md` and verify required fields exist for at least five attacks with real ENDI responses.

**Acceptance Scenarios**:

1. **Given** the manual attack template exists, **When** a team records an attack, **Then** ID, date/time, tester, category, attack prompt, ENDI command, raw ENDI response, target rule, expected violation, observed result, decision, severity, evidence excerpt, and notes are captured.
2. **Given** at least five cases exist, **When** the documentation is reviewed, **Then** cases cover distinct categories.

### Edge Cases

- Attack prompt is unsafe or operationally harmful.
- Response contains sensitive data.
- Manual result is ambiguous.
- Manual finding should map to a future automated fixture.

## Requirements

### Functional Requirements

- **FR-001**: ARES docs MUST include a manual attack results template.
- **FR-001a**: The required manual artifact path is `.specify/specs/013-manual-attack-documentation/manual-attacks.md`.
- **FR-002**: Documentation MUST include at least five manual attack cases with real ENDI raw responses, not only templates.
- **FR-003**: Manual cases MUST cover distinct categories: system prompt extraction, prompt injection, jailbreak/role-play manipulation, malicious-code request simulation, and out-of-domain request.
- **FR-004**: Each case MUST record ID, date/time, tester, category, attack prompt, ENDI command used, ENDI raw response, target rule under test, expected violation, observed result, decision, severity, evidence excerpt, and notes.
- **FR-005**: Manual findings SHOULD link to future automated fixtures where applicable.
- **FR-006**: Documentation MUST NOT include real secrets or harmful operational payloads.
- **FR-007**: Reflection checkpoints MUST be captured separately in `.specify/specs/013-manual-attack-documentation/reflection-checkpoints.md`.
- **FR-008**: Reflection checkpoints MUST cover after-manual-attacks learning and after-mitigation-replay learning.
- **FR-009**: Placeholder values such as `TBD` MUST be treated as incomplete evidence and MUST NOT be counted as completed manual attacks or completed reflections.

### Key Entities

- **ManualAttackCase**: Documented manual red-team attempt.
- **ManualAttackResult**: Outcome, severity, evidence summary, and notes.
- **ReflectionCheckpoint**: Separate learning note captured after manual testing and after mitigation replay.
- **AutomationLink**: Reference to future or existing fixture.

## Success Criteria

- **SC-001**: Manual attack documentation exists.
- **SC-002**: At least five manual attacks are represented.
- **SC-003**: No real secrets or harmful payloads are included.

## Assumptions

- Documentation-only work may not require Cargo validation beyond recording why it is not applicable or running current available commands.
- Manual attacks should use the official ENDI MVP target configuration from `.specify/specs/017-endi-target-profile-decisions/target-profile-endi.md`.
