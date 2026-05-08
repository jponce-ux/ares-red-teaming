# Epic Retrospective: epic-mvp-01

Date: 2026-03-18
Facilitator: Scrum Master workflow (`bmad-retrospective`)
Scope: `EPIC-MVP-01` (stories `mvp-01-1` through `mvp-01-5`)

## Epic Outcome Snapshot
- Stories completed: 5/5 (`done`)
- Current sprint status state: `epic-mvp-01: done` with all epic stories marked `done`
- Retrospective status before this artifact: `epic-mvp-01-retrospective: optional`
- Previous epic retrospective available: none found for `epic-mvp-00`

## Wins
- Deterministic runtime foundation was delivered incrementally and coherently across routing, workflow lifecycle, conversational loop, context safety, and tool contracts.
- Strong quality discipline on core runtime stories: repeated evidence of strict gate runs (`ruff`, `mypy`, `pytest`) and passing validation after each story.
- Command/conversation parity improved over the epic, culminating in normalized, externally observable contract behavior and structured error semantics.
- Security posture improved materially in MVP-01.4 via explicit precedence rules and safe-by-default handling for sensitive/raw text in persistence and telemetry.
- Tooling baseline hardened in MVP-01.5 with schema-first validation, deterministic status codes, and blocked side effects on invalid input.

## Pain Points
- Status hygiene drift: all MVP-01 stories are `done`, but the parent epic remained `in-progress`, creating potential reporting confusion.
- Process continuity gap: no prior epic retrospective artifact was found, reducing explicit carry-over accountability from earlier work.
- Environment friction surfaced in implementation logs (safe-directory limitations, WSL command nuances), introducing avoidable execution overhead.
- Some cross-story wording/contract clarifications had to be normalized late (story/backlog/PRD alignment), indicating requirements interpretation drift.

## Lessons Learned
- Deterministic behavior plus structured envelopes across all paths significantly reduces integration ambiguity as the runtime grows.
- Security and observability requirements should be specified as parity constraints early (command and conversation), not retrofitted per story.
- Enforcing strict gates story-by-story works; quality debt stayed controlled because checks were part of normal completion criteria.
- Story-level completion is insufficient for governance unless epic-level statuses are updated in lockstep.

## Root Causes (Issues/Risks)
1. **Issue:** Epic status lagged behind story completion.  
   **Root cause:** Manual epic transition step (`in-progress -> done`) was not consistently executed when the final story moved to `done`.
2. **Issue:** Cross-artifact contract wording required late normalization.  
   **Root cause:** Acceptance-criteria wording for parity/error semantics was distributed across multiple planning artifacts without a single synchronization checkpoint.
3. **Issue:** Execution environment guardrails were learned during delivery.  
   **Root cause:** Operational conventions (WSL venv invocation pattern, command sequencing constraints) were not enforced early as explicit working agreements.

## Action Items (Owner + Priority)
1. Add an explicit “epic closeout checklist” to the workflow including parent epic status transition and retrospective status update.  
   - Owner: Scrum Master / Process Owner  
   - Priority: High
2. Introduce a single-source “contract parity checklist” for command vs conversation behavior when updating FR-004/FR-007-adjacent stories.  
   - Owner: Architect + Lead Developer  
   - Priority: High
3. Add pre-flight environment guidance enforcement (WSL venv, command pattern, sequential execution expectations) to the working agreement template used before story implementation.  
   - Owner: Lead Developer  
   - Priority: Medium
4. Require retrospective continuity review at epic start (previous action items: completed/in-progress/not-addressed).  
   - Owner: Scrum Master  
   - Priority: Medium
5. Add a status consistency check in planning cadence (epic state vs child story states) before sprint/epic reporting snapshots.  
   - Owner: Project Lead  
   - Priority: High

## Carry-Forward Guardrails
- Preserve deterministic, typed result/error envelopes at all external runtime boundaries.
- Keep command/conversation parity as a non-negotiable acceptance criterion for shared runtime contracts.
- Treat raw request/response/conversation text as sensitive by default for persistence and telemetry unless explicitly opted in.
- Continue strict core quality gates (`ruff`, `mypy`, `pytest`) in WSL project `.venv` for every core-runtime story.
- Update parent epic and retrospective statuses immediately when epic completion conditions are met.

## Next-Epic Preparation Focus (epic-mvp-02)
- Start MVP-02 with the same deterministic + safety-by-default standards already established in MVP-01.
- Use MVP-01 contract/telemetry parity decisions as baseline constraints for capability authorization and confirmation stories.
- Track any required architecture/PRD wording changes up front before implementing the first MVP-02 story.

## Recommended Sprint-Status Updates
1. `development_status.epic-mvp-01: in-progress -> done`
2. `development_status.epic-mvp-01-retrospective: optional -> done`
3. `last_updated: <set to current timestamp at update time>`
