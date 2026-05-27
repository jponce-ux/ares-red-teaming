# Feature Specification: Attack Domain Types and Fixture Schema

**Feature Branch**: `[005-attack-domain-fixture-schema]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/03_define_attack_domain_types_and_fixture_schema.md`
**Project Scope**: ARES root Rust project
**Implementation Boundary**: Rust domain and fixture files in ARES paths.

## User Scenarios & Testing

### User Story 1 - Load Reproducible Attack Fixtures (Priority: P1)

As a red-team operator, I can load attack fixtures from disk and know each attack has category, prompt/template, target rule, expected violation, severity, and stable ID.

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
- Unknown category or severity.
- Missing target rule or expected violation.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST define attack categories as strong Rust types.
- **FR-002**: ARES MUST define target rules under test.
- **FR-003**: ARES MUST define attack variants with stable attack IDs.
- **FR-004**: ARES MUST define expected violation types.
- **FR-005**: ARES MUST define severity levels.
- **FR-006**: ARES MUST define run IDs and attack IDs.
- **FR-007**: ARES MUST support a machine-readable fixture format.
- **FR-008**: ARES MUST validate fixture data before execution.
- **FR-009**: Fixture examples MUST exist for prompt injection, jailbreak/role-play, and system prompt extraction.
- **FR-010**: ARES MUST avoid untyped string maps for core domain concepts.

### Key Entities

- **AttackCase**: One reproducible attack definition.
- **AttackCategory**: Prompt injection, jailbreak/role-play, system prompt extraction, and future categories.
- **TargetRule**: Behavior rule under test.
- **ExpectedViolation**: Policy violation being tested.
- **Severity**: Critical, high, medium, low.
- **RunId / AttackId**: Stable identifiers.
- **AttackFixture**: Machine-readable collection of attacks.

## Success Criteria

- **SC-001**: ARES loads valid fixture examples for all MVP categories.
- **SC-002**: Invalid fixtures return clear errors before execution.
- **SC-003**: Tests cover parsing, validation, duplicate IDs, and unknown enum values.

## Assumptions

- JSONL is preferred for streaming-friendly attack fixtures unless implementation planning chooses JSON for simplicity.
