# Ticket: Implement Prompt Injection Attack Category

## Scope
ARES

## Context
The MVP requires automated attacks in the prompt injection category with three to five reproducible variants.

Before creating Spec Kit artifacts or implementation, always read:

- `AGENTS.md`
- `.specify/memory/constitution.md`

## Goal
Add prompt injection attack fixtures and execution support for ENDI.

## Required Spec Kit Flow

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-analyze`
5. `$speckit-implement`

## Functional Requirements

- Add 3 to 5 prompt injection attack variants.
- Each variant must identify the target rule under test.
- Each variant must identify expected violation behavior.
- Variants must be safe and lab-constrained.
- Variants must be executable through the ENDI adapter.

## Example Variant Themes

- Ignore previous instructions.
- Override support-domain boundaries.
- Instruction hierarchy confusion.
- Hidden instruction conflict.
- Developer-message impersonation simulation.

## Acceptance Criteria

- Prompt injection category is represented in fixtures.
- 3 to 5 variants exist and are runnable.
- Results capture prompt, response, category, target rule, and expected violation.
- Tests verify fixtures load and execute through a mocked or controlled ENDI adapter.

## Validation Commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```
