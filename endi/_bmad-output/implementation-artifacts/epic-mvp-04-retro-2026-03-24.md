# Epic Retrospective: epic-mvp-04

Date: 2026-03-24
Facilitator: Scrum Master workflow (`bmad-retrospective`)
Scope: `EPIC-MVP-04` (stories `mvp-04-1`, `mvp-04-2`)

## Epic Outcome Snapshot
- Stories completed: 2/2 (`done`)
- Current sprint status state before closeout update: `epic-mvp-04: done` with all child stories `done`
- Retrospective status before this artifact: `epic-mvp-04-retrospective: optional`
- Previous retrospective reference: `_bmad-output/implementation-artifacts/epic-mvp-03-retro-2026-03-23.md`

## Epic Goals vs Outcomes
### Goal 1: Split provider contracts by capability (`MVP-04.1`)
- **Target:** Establish deterministic and capability-specific provider contracts (`ChatProvider`, `EmbeddingProvider`, `ToolCallingProvider`) with load-time validation and stable structured failures.
- **Outcome:** Achieved. Provider contracts, deterministic registration/version validation, and parity-safe contract failure surfacing were implemented and test-backed.

### Goal 2: Deliver locked defaults and explicit fallback behavior (`MVP-04.2`)
- **Target:** Enforce v1 provider defaults and explicit-only local fallback without silent automatic fallback on missing credentials, failures, or timeouts.
- **Outcome:** Achieved. Explicit fallback policy and deterministic failure normalization were implemented and hardened post-review with additional reason-matrix and runtime-path coverage.

## What Went Well
- Capability-first provider contracts reduced vendor coupling while keeping runtime boundaries explicit.
- Deterministic structured error behavior was maintained through registration, routing, and fallback-policy outcomes.
- Command/conversation parity remained a first-class guardrail for shared externally observable surfaces.
- Sensitive-by-default handling was preserved in provider metadata and telemetry extraction.
- Review feedback was absorbed quickly, with focused hardening and regression expansion completed in-story.

## What Didn’t Go Well / Risks Encountered
- Fallback-policy behavior required post-review hardening to fully cover real runtime command failure normalization.
- Some acceptance-criteria edge paths (reason matrix and runtime-path mapping) were validated after review rather than in the first implementation pass.
- Sprint-status epic closeout sequencing remained distributed across story completion and retrospective updates, increasing process drift risk.

## Quality-Gate Evidence Summary
- Gate profile used across implementation: `Strict` for provider contract boundaries and fallback-policy correctness (`MVP-04.2` also included moderate adapter-focused checks within that execution).
- Standard gates used in WSL project `.venv`: `ruff check src tests`, `mypy src`, `pytest`.
- Story-level recorded evidence:
  - `MVP-04.1`: gates passed; `pytest` evidence up to `108 passed` after post-review hardening.
  - `MVP-04.2`: gates passed; `pytest` evidence `117 passed` after post-review hardening.
- Result: no open lint/type/test failures recorded for epic closeout.

## Contract / Guardrail Compliance Summary
### Deterministic behavior
- Provider contract validation, version checks, fallback-policy outcomes, and routing failure mapping remained deterministic and test-backed.

### Safety-by-default
- Runtime blocked implicit fallback by default and required explicit enablement for local fallback paths.

### Command/conversation parity
- Shared boundary outcomes stayed aligned for provider contract and fallback decision semantics.

### Sensitive-by-default handling
- Provider telemetry and surfaced contract/fallback metadata remained sanitized by default with no raw request/response text exposure.

## Key Lessons Learned
- Provider/fallback acceptance criteria should include runtime-path parity checks from the first pass, not only boundary-unit checks.
- Explicit-policy behavior benefits from reason-matrix regression tests early to prevent post-review drift.
- Deterministic contract design scales well when errors are machine-readable and consistently surfaced across command and conversation paths.
- Epic-level process hygiene remains important even when technical quality gates are strong.

## Concrete Action Items for `epic-mvp-05`
1. Add a mandatory pre-review checklist item for operator-facing UX stories to include shared-boundary parity assertions where command/conversation outputs overlap.
2. For `mvp-05-1`, include contrast/non-color differentiation regressions in terminal output snapshots for warning/error/confirmation states.
3. For `mvp-05-2`, enforce deterministic command-help and validation-hint envelope shape checks across malformed invocations.
4. For `mvp-05-3`, add explicit linkage tests that prove the same normalized pre-execution summary is reflected in final confirmation audit artifacts.
5. Preserve sensitive-by-default handling in all UX/help output paths where free-form text could appear.
6. Continue strict WSL `.venv` gate execution discipline as non-optional before status transitions.

## Carry-Forward Guardrails
- Preserve deterministic behavior at all runtime contract boundaries.
- Keep safety-by-default and explicit opt-in for higher-risk execution behavior.
- Maintain command/conversation parity at shared externally observable boundaries.
- Treat raw request/response/user text as sensitive by default.
- Continue strict WSL `.venv` quality gates for runtime-facing stories.

## Recommended Sprint-Status Updates
1. `development_status.epic-mvp-04-retrospective: optional -> done`
2. `last_updated: <set to current timestamp at update time>`
