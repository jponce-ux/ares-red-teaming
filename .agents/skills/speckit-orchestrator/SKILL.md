---
  name: speckit-orchestrator
  description: Orchestrate GitHub Spec Kit skills in Codex CLI for one or many tasks using a strict test-driven development workflow. Use when input is a ticket, pasted requirement, BMAD/spec-driven folder, feature request, task list, bug report, refactor request, or red-team/stress-test requirement and Codex must create Spec Kit artifacts sequentially, write failing tests first, then implement. Always read AGENTS.md and .specify/memory/constitution.md before any spec, plan, tasks, test, or implementation work.
  compatibility: "Requires spec-kit project structure with .specify/ directory"
  metadata:
    author: "juan.ponce@endava.com"
---

# Spec Kit Orchestrator

You are a Codex CLI orchestrator for GitHub Spec Kit workflows in the Red Teaming AI Chat project.

This project has two implementation areas:

- `ares`: Rust components.
- `endi`: Python components.

Codex skills mode uses `$speckit-*` commands rather than slash commands. The core sequence is:

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-implement`

Optional quality gates:

- `$speckit-clarify`
- `$speckit-analyze`

## Non-negotiable preflight

Before doing anything else, always inspect:

1. `AGENTS.md`
2. `.specify/memory/constitution.md`

If either file is missing, stop and report which file is missing. Do not continue to specification, planning, task generation, testing, or implementation until both files are present or the user explicitly authorizes creating/updating them.

After reading both files, summarize the constraints that affect the work, including:

- project stack
- Rust `ares` boundaries
- Python `endi` boundaries
- language/runtime requirements
- architecture constraints
- TDD/testing requirements
- security requirements
- repository conventions
- prohibited changes

Do not default the whole project to Rust. Route each artifact and implementation decision to the correct project area:

- Use Rust defaults for `ares` work.
- Use Python defaults for `endi` work.
- Use both stacks only when the feature crosses the `ares`/`endi` boundary.
- If repository instructions disagree with these defaults, follow `AGENTS.md` and `.specify/memory/constitution.md`.

## TDD mandate

All plan, tasks, and implementation artifacts must enforce test-driven development.

Non-negotiable TDD rules:

- Write a failing unit test before production code for every new behavior.
- Do not add feature implementation code until the related unit test exists and has been run.
- Treat the expected initial failure as evidence that the test can catch the missing behavior.
- Implement the smallest production change needed to make the test pass.
- Refactor only after the test is green.
- Keep tests traceable to specific requirements, acceptance criteria, and tasks.
- Prefer deterministic unit tests before integration, stress, load, or end-to-end tests.
- Do not mark a task complete if the test was skipped, ignored, or not run, unless the reason is explicitly documented.

Use the loop:

1. Red: create or update the failing unit test.
2. Green: implement the minimum code required to pass.
3. Refactor: improve structure while tests remain green.
4. Validate: run the relevant targeted tests, then the broader suite.

## Inputs this skill accepts

The user may provide:

- one ticket
- many tickets
- pasted chat/task text
- a BMAD-generated spec folder
- an existing Spec Kit feature folder
- a vague feature request
- a bug report
- a refactor request
- a red-team/stress-test requirement

Treat each independent deliverable as a separate feature candidate.

## Work mode detection

Determine whether the input represents single-feature mode or batch mode.

### Single-feature mode

Use this when the input describes one coherent feature, fix, refactor, or implementation unit.

Flow:

1. Read `AGENTS.md`.
2. Read `.specify/memory/constitution.md`.
3. Normalize the request into a clear feature brief.
4. Determine whether the feature targets `ares`, `endi`, or both.
5. Run `$speckit-specify`.
6. Run `$speckit-plan` with explicit TDD strategy.
7. Run `$speckit-tasks` with test-first task ordering.
8. Run `$speckit-analyze` when available or when artifacts look inconsistent.
9. Run `$speckit-implement` using the red-green-refactor loop.

### Batch mode

Use this when the input contains multiple independent features, tickets, modules, or implementation units.

Flow:

1. Read `AGENTS.md`.
2. Read `.specify/memory/constitution.md`.
3. Decompose the input into an ordered feature queue.
4. For each feature, identify whether it targets `ares`, `endi`, or both.
5. For every feature in the queue, create all Spec Kit artifacts first:
   - `$speckit-specify`
   - `$speckit-plan`
   - `$speckit-tasks`
   - `$speckit-analyze` when available or useful
6. Only after every feature has complete artifacts, implement features in dependency order:
   - `$speckit-implement` for feature 1
   - `$speckit-implement` for feature 2
   - continue until complete

Never implement feature 1 before specs/plans/tasks have been created for all features in batch mode.

## Stack defaults

Use repository files as the source of truth. When they are silent, use these defaults.

### Rust defaults for `ares`

- language: Rust
- package manager/build tool: Cargo
- project shape: Cargo workspace when multiple crates are needed
- async runtime: Tokio
- CLI parsing: clap
- serialization: serde / serde_json
- error handling: anyhow for application boundaries, thiserror for domain errors
- logging/telemetry: tracing
- formatting: rustfmt
- linting: clippy
- unit tests: colocated `#[cfg(test)]` modules when testing private behavior
- integration tests: `tests/` when testing public crate behavior or CLI flows
- async tests: `#[tokio::test]` when async behavior is required
- security posture: safe Rust by default; avoid `unsafe` unless justified, isolated, and tested

### Python defaults for `endi`

- language: Python
- package/runtime: use the repository's configured tool first (`pyproject.toml`, lockfile, Makefile, or task runner)
- test framework: pytest when no project-specific framework is configured
- async tests: pytest-asyncio or repository-approved equivalent when async behavior is required
- mocking/fakes: unittest.mock or pytest fixtures
- formatting/linting: use configured tools first; otherwise prefer ruff when present
- typing: use configured type checker first; otherwise prefer mypy or pyright when present
- unit tests: `tests/unit/` or existing repository convention
- integration tests: `tests/integration/` or existing repository convention
- security posture: validate inputs, avoid shell injection, avoid leaking secrets, and isolate external calls behind test doubles

### Cross-stack defaults for `ares` and `endi`

For features that cross the Rust/Python boundary:

- define the contract before implementation
- add unit tests on each side of the boundary
- add contract or integration tests for serialized inputs/outputs
- keep fixtures shared, deterministic, and versioned when possible
- document ownership of behavior in the plan and tasks

## Specify phase

When running `$speckit-specify`, describe what and why, not low-level implementation.

Include:

- user story
- target project area: `ares`, `endi`, or both
- red-team or stress-test objective when applicable
- observable behavior
- inputs and outputs
- testable acceptance criteria
- unit-testable behavior boundaries
- edge cases
- failure modes
- non-goals
- assumptions
- security considerations

The specification must be testable. If a requirement cannot be verified by a unit, integration, contract, stress, or regression test, rewrite it until it can be verified.

Do not skip the specify phase.

## Plan phase

When running `$speckit-plan`, provide stack-specific technical direction.

Include:

- target project area: `ares`, `endi`, or both
- Rust stable target for `ares` work
- Python runtime/tooling expectations for `endi` work
- crate/module/package layout
- CLI/API boundaries
- data model
- async/concurrency model
- error handling strategy
- logging/tracing strategy
- TDD strategy
- first failing unit tests to create before implementation
- test fixtures, mocks, fakes, and deterministic data strategy
- contract/integration test strategy for cross-stack behavior
- security constraints
- compatibility with existing project structure
- migration or integration steps

Every plan must include a section named `TDD plan` with:

- the behavior to test first
- the exact unit test file/module to create or update
- the expected failure before implementation
- the minimal production files/modules allowed to change after the failing test exists
- targeted validation commands for red, green, and refactor phases

For `ares`, prefer targeted commands such as:

```bash
cargo test -p <crate> <test_name>
```

For `endi`, prefer targeted commands such as:

```bash
python -m pytest <path-to-test>::<test_name> -q
```

Do not allow plans that contradict `AGENTS.md` or `.specify/memory/constitution.md`.

## Tasks phase

When running `$speckit-tasks`, ensure tasks are:

- ordered
- small enough to implement safely
- testable
- traceable to spec requirements
- grouped by feature or milestone
- explicit about target stack: `ares`, `endi`, or both
- explicit about files/modules/crates/packages
- explicit about tests and validation commands

Tasks must use test-first ordering. For every behavior-changing implementation task, create a test task immediately before it.

Use this task pattern:

1. `[TDD-RED]` Add or update the failing unit test for one behavior.
2. `[TDD-RED]` Run the targeted test and record the expected failure.
3. `[TDD-GREEN]` Implement the minimum production code required to pass that test.
4. `[TDD-GREEN]` Run the targeted test and confirm it passes.
5. `[TDD-REFACTOR]` Refactor only if needed while keeping tests green.
6. `[VALIDATE]` Run the relevant broader test/lint/format command.

Examples:

```markdown
- [ ] T001 [TDD-RED][ares] Add `rejects_empty_prompt` unit test in `ares/src/...` covering REQ-001.
- [ ] T002 [TDD-RED][ares] Run `cargo test -p ares rejects_empty_prompt` and record the expected failure.
- [ ] T003 [TDD-GREEN][ares] Implement minimal validation in `ares/src/...` to pass `rejects_empty_prompt`.
- [ ] T004 [TDD-GREEN][ares] Run `cargo test -p ares rejects_empty_prompt` and confirm it passes.

- [ ] T005 [TDD-RED][endi] Add `test_rejects_empty_prompt` in `endi/tests/unit/...` covering REQ-002.
- [ ] T006 [TDD-RED][endi] Run `python -m pytest endi/tests/unit/...::test_rejects_empty_prompt -q` and record the expected failure.
- [ ] T007 [TDD-GREEN][endi] Implement minimal validation in `endi/...` to pass `test_rejects_empty_prompt`.
- [ ] T008 [TDD-GREEN][endi] Run `python -m pytest endi/tests/unit/...::test_rejects_empty_prompt -q` and confirm it passes.
```

Do not generate tasks that say only "implement feature" without a preceding failing test task.

For red-team tooling, include test-first tasks for:

- malformed input cases
- long prompt cases
- prompt injection cases that are safe to store as fixtures
- concurrency/load behavior
- timeout handling
- crash recovery
- output capture
- reproducible reporting
- regression fixtures
- boundary/serialization behavior between `ares` and `endi` when applicable

## Analyze gate

Run `$speckit-analyze` when available after tasks are generated and before implementation.

Check for:

- missing requirements
- contradictions between spec, plan, and tasks
- missing TDD plan
- implementation tasks without preceding failing test tasks
- tests that are not traceable to requirements
- missing security controls
- implementation tasks not mapped to requirements
- Rust `ares` stack violations
- Python `endi` stack violations
- cross-stack contract gaps
- AGENTS.md or constitution violations

Fix artifacts before implementation.

Do not proceed to `$speckit-implement` until every behavior-changing task has a test-first path.

## Implementation phase

When running `$speckit-implement`:

- implement only from completed artifacts
- follow task order exactly
- write or update the failing unit test before production code
- run the targeted test and capture the expected failure
- implement the smallest production change needed to pass
- rerun the targeted test and confirm it passes
- refactor only while tests remain green
- keep changes scoped
- run formatting
- run linting where available
- run targeted tests first, then broader tests
- report failures honestly
- do not hide skipped tests
- do not introduce components outside `ares` or `endi` unless required by project instructions

Implementation output must report:

- tests added or changed
- production files changed
- red-phase command and expected failure summary
- green-phase command and pass summary
- broader validation commands run
- skipped validations with reasons
- remaining risks or follow-up tasks

Preferred validation commands for `ares`:

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
```

Preferred validation commands for `endi` when configured:

```bash
python -m pytest
python -m ruff check .
python -m mypy .
```

Use repository-specific commands from `AGENTS.md`, `.specify/memory/constitution.md`, `Makefile`, `justfile`, `pyproject.toml`, or CI configuration when they exist.
