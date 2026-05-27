# Ticket: Implement Jailbreak and Role-Play Attack Category

## Scope
ARES

## Context
The MVP requires automated attacks in the jailbreak or role-play manipulation category with three to five reproducible variants.

Before creating Spec Kit artifacts or implementation, always read:

- `AGENTS.md`
- `.specify/memory/constitution.md`

## Goal
Add jailbreak and role-play attack fixtures and execution support for ENDI.

## Required Spec Kit Flow

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-analyze`
5. `$speckit-implement`

## Functional Requirements

- Add 3 to 5 jailbreak or role-play attack variants.
- Each variant must be safe and lab-constrained.
- Each variant must target a documented ENDI behavior rule.
- Variants must test whether ENDI can be manipulated into ignoring guardrails.
- Variants must be executable through ARES.

## Example Variant Themes

- Pretend mode / role-play bypass.
- Fictional authorization bypass.
- Emergency exception framing.
- Alternate persona manipulation.
- Policy-disabled simulation.

## Acceptance Criteria

- Jailbreak/role-play category is represented in fixtures.
- 3 to 5 variants exist and are runnable.
- Results capture prompt, response, category, target rule, and expected violation.
- Tests verify fixtures load and execute through a mocked or controlled ENDI adapter.

## Validation Commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```
