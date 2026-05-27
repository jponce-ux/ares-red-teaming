# Ticket: Add Manual Attack Documentation Artifacts

## Scope
ARES documentation and Spec Kit artifacts

## Context
The lab MVP requires at least five manual attacks across distinct categories, with results documented in a table before or alongside automated execution.

Before creating Spec Kit artifacts or implementation, always read:

- `AGENTS.md`
- `.specify/memory/constitution.md`

## Goal
Create documentation artifacts for manual ENDI attack execution and results capture.

## Required Spec Kit Flow

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-analyze`
5. `$speckit-implement`

## Functional Requirements

- Create a manual attack results template.
- Document at least five manual attack cases.
- Cover distinct categories.
- Record prompt, category, target rule, response summary, success/failure, severity, and notes.
- Link manual findings to future automated fixtures where applicable.

## Suggested Categories

- Prompt injection.
- Jailbreak/role-play.
- System prompt extraction.
- Domain escape.
- Malicious-code request simulation.

## Acceptance Criteria

- Manual attack documentation exists in the repository.
- At least five manual attacks are represented.
- Documentation is compatible with later automation and reporting.
- No real secrets or harmful payloads are included.

## Validation Commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```

If this ticket only creates documentation, record why Cargo validation is not applicable or run the current available validation commands.
