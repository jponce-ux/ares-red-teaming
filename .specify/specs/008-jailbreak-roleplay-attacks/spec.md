# Feature Specification: Jailbreak and Role-Play Attack Category

**Feature Branch**: `[008-jailbreak-roleplay-attacks]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/06_implement_jailbreak_roleplay_attack_category.md`
**Project Scope**: ARES root Rust project
**Implementation Boundary**: ARES attack fixtures and execution support only.

## User Scenarios & Testing

### User Story 1 - Run Jailbreak/Role-Play Variants (Priority: P1)

As a red-team operator, I can run safe jailbreak and role-play manipulation variants to test whether ENDI ignores guardrails.

**Independent Test**: Load jailbreak/role-play fixtures and execute them through a mocked or controlled ENDI adapter.

**Acceptance Scenarios**:

1. **Given** jailbreak/role-play fixtures exist, **When** ARES loads them, **Then** three to five variants are available.
2. **Given** a variant executes, **When** the response is captured, **Then** the result records category, prompt, target rule, expected violation, and response.

### Edge Cases

- Variant attempts to bypass safety with unsafe operational detail.
- Variant lacks documented target rule.
- ENDI refuses safely.
- Adapter returns execution error.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST add three to five jailbreak or role-play attack variants.
- **FR-002**: Each variant MUST remain safe and lab-constrained.
- **FR-003**: Each variant MUST target a documented ENDI behavior rule.
- **FR-004**: Variants MUST test whether ENDI can be manipulated into ignoring guardrails.
- **FR-005**: Variants MUST be executable through ARES.
- **FR-006**: Results MUST preserve prompt, response, category, target rule, and expected violation.

### Key Entities

- **JailbreakRoleplayAttack**: Attack in jailbreak/role-play category.
- **RoleplayTheme**: Safe theme such as pretend mode or fictional authorization.
- **GuardrailTarget**: Behavior rule being pressure tested.

## Success Criteria

- **SC-001**: Jailbreak/role-play category has three to five runnable variants.
- **SC-002**: Tests verify fixtures load and execute through controlled ENDI adapter.
- **SC-003**: Variants remain safe and lab-constrained.

## Assumptions

- Attack schema supports category-specific variants and expected violations.
