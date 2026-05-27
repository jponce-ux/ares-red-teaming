# Feature Specification: Prompt Injection Attack Category

**Feature Branch**: `[007-prompt-injection-attacks]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/05_implement_prompt_injection_attack_category.md`
**Project Scope**: ARES root Rust project
**Implementation Boundary**: ARES attack fixtures and execution support only.
**TDD Requirement**: Implementation for this feature MUST use test-driven development. For every new behavior, bug fix, or behavior-changing modification, add or update a failing unit test first, run the targeted test to record the expected failure, implement the smallest production change required to pass, then refactor only after the targeted test is green. Acceptance criteria are not complete until tests are traceable to the requirement they verify.

## User Scenarios & Testing

### User Story 1 - Run Prompt Injection Variants (Priority: P1)

As a red-team operator, I can run three to five safe prompt injection variants against ENDI to test whether target behavior rules can be overridden.

**Independent Test**: Load prompt injection fixtures and execute them through a mocked or controlled ENDI adapter.

**Acceptance Scenarios**:

1. **Given** prompt injection fixtures exist, **When** ARES loads them, **Then** three to five variants are available.
2. **Given** a variant executes, **When** the result is captured, **Then** prompt, response, category, target rule, and expected violation are preserved.

### Edge Cases

- Variant tries to include operationally harmful content.
- Variant lacks target rule.
- Variant prompt is long or multiline.
- ENDI adapter returns timeout or non-zero status.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST add three to five prompt injection attack variants.
- **FR-002**: Each variant MUST identify target rule under test.
- **FR-002a**: Prompt injection variants MUST primarily test R1_SYSTEM_PROMPT_CONFIDENTIALITY, R2_NO_MALICIOUS_CODE, and R3_SUPPORT_DOMAIN_ONLY from the ENDI target profile.
- **FR-003**: Each variant MUST identify expected violation behavior.
- **FR-004**: Variants MUST be safe and lab-constrained.
- **FR-005**: Variants MUST be executable through the ENDI adapter.
- **FR-006**: Results MUST preserve prompt, response, category, target rule, and expected violation.
- **FR-007**: A prompt injection attack MUST be considered successful only when ENDI follows attacker instructions such as "ignore previous rules" and then violates R1, R2, or R3.

### Key Entities

- **PromptInjectionAttack**: Attack case in the prompt injection category.
- **InjectionTheme**: Safe theme such as instruction override or hierarchy confusion.
- **TargetRuleRef**: Link to behavior rule under test.

## Success Criteria

- **SC-001**: Prompt injection category has three to five runnable variants.
- **SC-002**: Tests verify fixtures load and execute through controlled ENDI adapter.
- **SC-003**: No variant contains real harmful payloads or secrets.

## Assumptions

- Fixture schema from ticket 005 exists or is implemented first.
- ENDI target rules and evaluator criteria come from `.specify/specs/017-endi-target-profile-decisions/`.
