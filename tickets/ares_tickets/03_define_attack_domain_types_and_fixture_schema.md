# Ticket: Define Attack Domain Types and Fixture Schema

## Scope
ARES

## Context
ARES must run categorized, reproducible red-team attacks against ENDI. Attack definitions need strong Rust domain types and a machine-readable fixture format.

Before creating Spec Kit artifacts or implementation, always read:

- `AGENTS.md`
- `.specify/memory/constitution.md`

## Goal
Define the core attack domain model and fixture schema used by ARES automated attacks.

## Required Spec Kit Flow

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-analyze`
5. `$speckit-implement`

## Functional Requirements

- Define attack categories.
- Define target rules under test.
- Define attack variants.
- Define expected violation types.
- Define severity levels.
- Define attack IDs and run IDs.
- Define fixture input format using JSON, JSONL, TOML, or YAML.
- Validate fixture data before execution.

## Required MVP Categories

- Prompt injection
- Jailbreak or role-play manipulation
- System prompt extraction

## Technical Requirements

- Use strong Rust enums and structs.
- Use `serde` for serialization and deserialization.
- Avoid untyped string maps for domain concepts.
- Make invalid states hard to represent.
- Include fixture examples for each MVP category.

## Acceptance Criteria

- ARES can load attack fixtures from disk.
- Invalid fixtures produce clear errors.
- Each attack records category, prompt/template, expected policy violation, and target rule under test.
- At least one fixture example exists for each required MVP category.
- Tests cover fixture parsing and validation.

## Validation Commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```
