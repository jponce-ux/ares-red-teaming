# Feature Specification: Attack Domain Types and Fixture Schema

**Feature Branch**: `[005-attack-domain-fixture-schema]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/03_define_attack_domain_types_and_fixture_schema.md`
**Project Scope**: ARES root Rust project
**Implementation Boundary**: Rust domain and fixture files in ARES paths.
**TDD Requirement**: Implementation for this feature MUST use test-driven development. For every new behavior, bug fix, or behavior-changing modification, add or update a failing unit test first, run the targeted test to record the expected failure, implement the smallest production change required to pass, then refactor only after the targeted test is green. Acceptance criteria are not complete until tests are traceable to the requirement they verify.

## User Scenarios & Testing

### User Story 1 - Load Reproducible Attack Fixtures (Priority: P1)

As a red-team operator, I can load attack fixtures from disk and know each attack has category, prompt/template, ENDI target rule, expected violation, severity, result status, and stable ID.

**Independent Test**: Load valid fixture examples for each MVP category and verify typed Rust values are produced.

**Acceptance Scenarios**:

1. **Given** valid fixtures exist, **When** ARES loads them, **Then** each attack is represented by strong Rust domain types.
2. **Given** a fixture omits a required field, **When** ARES validates it, **Then** a clear validation error is returned.

### User Story 2 - Reject Invalid Attack States (Priority: P2)

As a contributor, I cannot accidentally represent invalid attack categories, severities, target rules, or run IDs as arbitrary strings.

**Independent Test**: Unit tests verify invalid category, severity, missing target rule, and malformed IDs fail validation.

**Acceptance Scenarios**:

1. **Given** an unknown category appears in a fixture, **When** parsing occurs, **Then** parsing fails with a clear error.
2. **Given** duplicate attack IDs appear, **When** validation occurs, **Then** loading fails before execution.

### Edge Cases

- Empty fixture file.
- Duplicate attack IDs.
- Long prompts and multiline prompts.
- Unknown category, severity, result status, or target rule.
- Missing target rule or expected violation.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST define attack categories as strong Rust types.
- **FR-002**: ARES MUST define target rules under test.
- **FR-002a**: ARES MUST include the ENDI target rules R1_SYSTEM_PROMPT_CONFIDENTIALITY, R2_NO_MALICIOUS_CODE, R3_SUPPORT_DOMAIN_ONLY, R4_NO_DESTRUCTIVE_ACTIONS_WITHOUT_CONFIRMATION, and R5_NO_FAKE_SECRETS_OR_INTERNAL_DATA.
- **FR-003**: ARES MUST define attack variants with stable attack IDs.
- **FR-004**: ARES MUST define expected violation types.
- **FR-005**: ARES MUST define severity levels.
- **FR-005a**: ARES MUST define result statuses `blocked`, `success`, `partial`, `inconclusive`, `target_error`, and `harness_error`.
- **FR-005b**: Severity MUST apply only to `success` or `partial`; execution failures and timeouts MUST be represented as run statuses rather than vulnerabilities.
- **FR-006**: ARES MUST define run IDs and attack IDs.
- **FR-007**: ARES MUST support JSONL as the MVP machine-readable attack fixture format.
- **FR-008**: ARES MUST validate fixture data before execution.
- **FR-009**: Fixture examples MUST exist for prompt injection, jailbreak/role-play, and system prompt extraction.
- **FR-009a**: ARES MUST define the ENDI Support Assistant target fixture at `ares/fixtures/targets/endi_support.toml`.
- **FR-010**: ARES MUST avoid untyped string maps for core domain concepts.

### Key Entities

- **AttackCase**: One reproducible attack definition.
- **AttackCategory**: Prompt injection, jailbreak/role-play, system prompt extraction, and future categories.
- **TargetRule**: Behavior rule under test.
- **ExpectedViolation**: Policy violation being tested.
- **Severity**: Critical, high, medium, low, with N/A represented for non-vulnerability execution outcomes.
- **ResultStatus**: Blocked, success, partial, inconclusive, target error, or harness error.
- **RunId / AttackId**: Stable identifiers.
- **AttackFixture**: Machine-readable collection of attacks.

## Success Criteria

- **SC-001**: ARES loads valid fixture examples for all MVP categories.
- **SC-002**: Invalid fixtures return clear errors before execution.
- **SC-003**: Tests cover parsing, validation, duplicate IDs, and unknown enum values.

## Assumptions

- JSONL is the required MVP format for attack fixtures. Other serde-supported formats are future work and must not be introduced in this feature.
- Product-level target rules and status semantics are defined in `.specify/specs/017-endi-target-profile-decisions/target-profile-endi.md` and `.specify/specs/017-endi-target-profile-decisions/evaluator-success-criteria.md`.
