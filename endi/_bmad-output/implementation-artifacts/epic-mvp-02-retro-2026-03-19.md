# Epic Retrospective: epic-mvp-02

Date: 2026-03-19
Facilitator: Scrum Master workflow (`bmad-retrospective`)
Scope: `EPIC-MVP-02` (stories `mvp-02-1` through `mvp-02-4`)

## Epic Outcome Snapshot
- Stories completed: 4/4 (`done`)
- Current sprint status state before closeout update: `epic-mvp-02: backlog` while all child stories were `done`
- Retrospective status before this artifact: `epic-mvp-02-retrospective: optional`
- Previous epic retrospective available: `_bmad-output/implementation-artifacts/epic-mvp-01-retro-2026-03-18.md`

## Continuity Check from EPIC-MVP-01 Retro
1. **Epic closeout checklist and status synchronization**
   - Status: ⏳ In Progress
   - Evidence: MVP-02 stories reached `done`, but parent `epic-mvp-02` remained `backlog` until epic closeout.
2. **Contract parity checklist for command vs conversation boundaries**
   - Status: ✅ Completed
   - Evidence: MVP-02 stories consistently required and validated externally observable command/conversation parity behavior.
3. **WSL + `.venv` pre-flight execution guidance**
   - Status: ✅ Completed
   - Evidence: story records repeatedly captured strict WSL `.venv` quality-gate commands and results.
4. **Retrospective continuity review at epic start**
   - Status: ✅ Completed
   - Evidence: `_bmad-output/implementation-artifacts/mvp-02-kickoff-checklist.md` includes explicit continuity record and first-story sequencing.
5. **Status consistency verification before reporting snapshots**
   - Status: ⏳ In Progress
   - Evidence: parent epic/story mismatch still surfaced at epic closeout.

## What Went Well
- Security controls were implemented as layered, deterministic policy boundaries: authorization (`MVP-02.1`), per-action confirmation (`MVP-02.2`), approve-plan mode (`MVP-02.3`), and backend isolation resolver (`MVP-02.4`).
- Safety-by-default posture remained intact across the epic: fail-fast blocking before side effects for denied/declined/out-of-plan/unavailable-backend paths.
- Command/conversation parity remained a first-class acceptance criterion, with parity evidence present in story-level tests and completion notes.
- Sensitive-by-default handling was preserved and strengthened through follow-up fixes (notably conversation snapshot/telemetry raw-text exclusion hardening in `MVP-02.2` and review hardening in `MVP-02.3`).
- Quality discipline stayed strong: strict WSL `.venv` gates were run repeatedly and passed after implementation and post-review fixes.

## What Didn’t Go Well
- Epic status hygiene drift persisted: all MVP-02 stories were `done` while `epic-mvp-02` remained `backlog`, indicating closeout governance is still manual and error-prone.
- Some critical safety/contract gaps were detected only during story review rather than prevented earlier by acceptance-test coverage (notably in `MVP-02.4`).
- Review/fix cycles had to correct externally observable mismatches (selected backend metadata vs actual execution path), creating avoidable late hardening work.

## Key Risks Discovered and Mitigations
1. **Risk:** Unauthorized or unconfirmed sensitive actions causing side effects.
   - Mitigation: centralized pre-execution authorization + confirmation enforcement in shared routing/runtime boundaries; deterministic denial envelopes.
2. **Risk:** Automation mode (`approve_plan`) could permit drift or bypass intent.
   - Mitigation: deterministic approved-plan fingerprinting, non-interactive validation, and out-of-plan blocking before execution.
3. **Risk:** Telemetry/context could leak sensitive raw text.
   - Mitigation: sensitive-by-default exclusion/sanitization of raw request/response/conversation fields, including conversation-path follow-up hardening.
4. **Risk:** Isolation downgrade gap between policy resolution and execution backend behavior.
   - Mitigation: post-review hardening in `MVP-02.4` aligned actual command execution with selected backend and added `backend_unavailable` fail-safe blocking.
5. **Risk:** Runtime overrides could weaken locked backend mapping safety.
   - Mitigation: anti-downgrade protection for locked capability mappings with added regressions.

## Regressions and Follow-Ups Caught in Review
- `MVP-02.2` follow-up: conversation session snapshot/telemetry contexts now exclude raw-text fields before sanitization; deterministic confirmation fallback precedence fixed when per-action override key is absent.
- `MVP-02.3` review hardening: conversation confirmation telemetry summary now strips raw-text fields recursively; missing non-interactive regressions for `confirmation_plan_unapproved` and fingerprint-invalid `confirmation_plan_invalid` added.
- `MVP-02.4` review finding (high severity): backend selection metadata indicated stronger isolation but command execution still used local backend.
  - Follow-up hardening applied: execution path now uses resolved backend selection, unconfigured non-local backend fails safe (`backend_unavailable`), and locked-capability downgrade overrides are blocked.

## Quality-Gate Evidence Summary
- Gate model remained `Strict` for all MVP-02 stories (`ADR-011` alignment).
- Standard gates used throughout: `ruff check src tests`, `mypy src`, `pytest` in WSL project `.venv`.
- Story-level evidence highlights:
  - `MVP-02.1`: strict gates recorded and passed.
  - `MVP-02.2`: strict gates passed (`pytest` evidence includes 59 passed after follow-up fixes).
  - `MVP-02.3`: strict gates passed (`pytest` evidence includes 67 passed) and post-review hardening verified.
  - `MVP-02.4`: strict gates passed pre-review (`72 passed`) and after hardening (`74 passed`).
- Result: no open quality-gate failures carried into epic closeout.

## Lessons Learned
- Deterministic policy artifacts (decision envelopes, plan fingerprints, backend selection metadata) are effective only when execution-path enforcement is explicitly covered by regression tests.
- Command/conversation parity requirements reduce integration ambiguity, but parity must include both reported metadata and real execution behavior.
- Sensitive-by-default data handling needs recursive and path-specific test coverage, especially for conversation telemetry/snapshot paths.
- Story-level completion discipline is strong; epic-level status transition discipline still needs stronger automation/checklist enforcement.

## Actionable Improvements for MVP-03
1. Add an epic-closeout preflight check that blocks closeout if parent epic status does not match child-story completion state (`done` consistency gate).
2. Add an explicit test requirement for policy-to-execution alignment in MVP-03 stories that expose policy metadata (ensure observed metadata cannot diverge from runtime behavior).
3. Add regression templates for sensitive-data sanitization at all externally observable boundaries (CLI output, telemetry payload, session snapshot) with recursive field checks.
4. Add a mandatory review checklist item for “reported contract vs actual execution path parity” for security/runtime stories.
5. Define a small compliance matrix for MVP-03 observability/persistence work mapping each FR-007 boundary to deterministic envelope + redaction expectations.
6. Add one status-consistency validation step before each sprint snapshot update to prevent epic/story drift.

## Carry-Forward Guardrails
- Preserve deterministic behavior at all policy and execution boundaries.
- Keep safety-by-default enforcement fail-fast and side-effect blocking for unsafe paths.
- Maintain command/conversation parity at externally observable boundaries, including metadata-to-execution alignment.
- Treat raw request/response/conversation text as sensitive by default for context persistence and telemetry.
- Continue strict WSL `.venv` quality gates (`ruff`, `mypy`, `pytest`) for core runtime/security stories.

## Missing Context Check
- No required retrospective context files were missing for this run.

## Continuity Reference
- MVP-03 kickoff checklist created from this retrospective: `_bmad-output/implementation-artifacts/mvp-03-kickoff-checklist.md`

## Recommended Sprint-Status Updates
1. `development_status.epic-mvp-02: backlog -> done`
2. `development_status.epic-mvp-02-retrospective: optional -> done`
3. `last_updated: <set to current timestamp at update time>`
