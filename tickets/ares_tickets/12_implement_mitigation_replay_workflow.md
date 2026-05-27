# Ticket: Implement Mitigation Replay Workflow

## Scope
Cross-project integration: ARES verifies mitigation effectiveness against ENDI.

## Context
The constitution requires at least one discovered vulnerability to receive a concrete mitigation, then replay relevant attacks to prove whether the issue was closed, partially reduced, or still open.

Before creating Spec Kit artifacts or implementation, always read:

- `AGENTS.md`
- `.specify/memory/constitution.md`

## Goal
Add an ARES workflow for replaying selected attacks after mitigation and comparing before/after results.

## Required Spec Kit Flow

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-analyze`
5. `$speckit-implement`

## Functional Requirements

- Select relevant attacks for replay.
- Run attacks before or load a previous baseline result.
- Run attacks after mitigation.
- Compare evaluator decisions.
- Classify mitigation result as closed, partially reduced, unchanged, or regressed.
- Include replay findings in the report.

## Technical Requirements

- Use structured result files.
- Use stable attack IDs for comparison.
- Do not require ENDI implementation changes in this ticket unless explicitly scoped by a separate ENDI ticket.
- Keep replay logic independent from report rendering where practical.

## Acceptance Criteria

- ARES can compare two runs for the same attack set.
- Replay output identifies closed, reduced, unchanged, and regressed findings.
- Markdown report includes mitigation replay status.
- Tests cover comparison logic.

## Validation Commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```
