# Ticket: Capture Evidence and Evaluate Rule Violations

## Scope
ARES

## Context
The constitution requires every attack execution to produce evidence supporting a success or failure decision. The MVP can use deterministic heuristics, LLM-as-judge, or both. This ticket starts with auditable deterministic evaluation.

Before creating Spec Kit artifacts or implementation, always read:

- `AGENTS.md`
- `.specify/memory/constitution.md`

## Goal
Implement evidence capture and rule-violation evaluation for ARES attack results.

## Required Spec Kit Flow

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-analyze`
5. `$speckit-implement`

## Functional Requirements

- Store attack prompt.
- Store ENDI response.
- Store command execution metadata.
- Evaluate whether target rules were violated.
- Assign decision: success, failure, inconclusive, or execution error.
- Assign severity.
- Store evaluator rationale.
- Store matched heuristic where applicable.

## Initial Evaluation Rules

Include deterministic heuristics for:

- System prompt leakage indicators.
- Domain boundary violations.
- Unsafe malicious-code assistance indicators.
- Refusal/safe-completion indicators.

## Technical Requirements

- Use explicit domain types for evaluator decisions and severities.
- Keep evaluator logic testable and isolated.
- Preserve enough evidence for human inspection.
- Do not log sensitive evidence outside controlled report/evidence output.

## Acceptance Criteria

- Each attack result receives an evaluator decision.
- Each decision includes rationale.
- Severity is applied consistently.
- Tests cover positive, negative, and inconclusive evaluator cases.

## Validation Commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```
