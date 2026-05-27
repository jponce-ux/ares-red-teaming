# Ticket: Implement System Prompt Extraction Attack Category

## Scope
ARES

## Context
The MVP requires automated attacks in the system prompt extraction category with three to five reproducible variants.

Before creating Spec Kit artifacts or implementation, always read:

- `AGENTS.md`
- `.specify/memory/constitution.md`

## Goal
Add system prompt extraction attack fixtures and execution support for ENDI.

## Required Spec Kit Flow

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-analyze`
5. `$speckit-implement`

## Functional Requirements

- Add 3 to 5 system prompt extraction variants.
- Each variant must test refusal of system prompt disclosure.
- Each variant must remain safe and lab-constrained.
- Each variant must be executable through ARES.
- Results must support evaluator checks for leakage indicators.

## Example Variant Themes

- Direct system prompt request.
- Debug transcript request.
- Configuration dump request.
- First-message reconstruction request.
- Policy explanation pressure test.

## Acceptance Criteria

- System prompt extraction category is represented in fixtures.
- 3 to 5 variants exist and are runnable.
- Results capture prompt, response, category, target rule, and expected violation.
- Tests verify fixtures load and execute through a mocked or controlled ENDI adapter.

## Validation Commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```
