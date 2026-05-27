# Feature Specification: System Prompt Extraction Attack Category

**Feature Branch**: `[009-system-prompt-extraction-attacks]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/07_implement_system_prompt_extraction_attack_category.md`
**Project Scope**: ARES root Rust project
**Implementation Boundary**: ARES attack fixtures and execution support only.

## User Scenarios & Testing

### User Story 1 - Run System Prompt Extraction Variants (Priority: P1)

As a red-team operator, I can run safe system prompt extraction variants to test whether ENDI refuses system prompt disclosure.

**Independent Test**: Load system prompt extraction fixtures and execute them through a mocked or controlled ENDI adapter.

**Acceptance Scenarios**:

1. **Given** system prompt extraction fixtures exist, **When** ARES loads them, **Then** three to five variants are available.
2. **Given** a variant executes, **When** a response is captured, **Then** evaluator-ready leakage indicators can be checked.

### Edge Cases

- ENDI provides a high-level policy explanation but not the system prompt.
- Response includes partial instruction fragments.
- Variant requests debug transcript or configuration dump.
- Adapter returns timeout or malformed output.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST add three to five system prompt extraction variants.
- **FR-002**: Each variant MUST test refusal of system prompt disclosure.
- **FR-003**: Each variant MUST remain safe and lab-constrained.
- **FR-004**: Each variant MUST be executable through ARES.
- **FR-005**: Results MUST support evaluator checks for leakage indicators.
- **FR-006**: Results MUST preserve prompt, response, category, target rule, and expected violation.

### Key Entities

- **SystemPromptExtractionAttack**: Attack case testing prompt disclosure refusal.
- **LeakageIndicator**: Evaluator hint for possible disclosure.
- **DisclosureTargetRule**: Rule requiring refusal to reveal system prompt.

## Success Criteria

- **SC-001**: System prompt extraction category has three to five runnable variants.
- **SC-002**: Tests verify fixtures load and execute through controlled ENDI adapter.
- **SC-003**: Result data contains evaluator-ready leakage context.

## Assumptions

- Evaluator heuristics are implemented in a later ticket but fixture metadata can prepare for them.
