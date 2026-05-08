# Story MVP-05.3: Confirmation UX and Operation Summary Consistency

Status: done

## Metadata
- **Story ID:** `MVP-05.3`
- **Story Key:** `mvp-05-3-confirmation-ux-and-operation-summary-consistency`
- **Epic:** `EPIC-MVP-05` Terminal UX & Operator Experience (Terminal-native)
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 4`
- **Type:** `Safety UX Contract`

## Story
As an incident responder, I want concise, standardized pre-execution summaries, so that I can approve high-impact actions with confidence.

## Objective
Deliver a deterministic confirmation-summary contract and rendering path that keeps sensitive-action approval UX consistent across command and conversational boundaries, and auditable via stable summary linkage.

## Traceability
- **Functional Requirements:** `FR-010`, `FR-005`
- **Architecture Constraints:** `ADR-018`, `ADR-006`, `ADR-002`, `ADR-011`

## Scope

### In Scope
- Normalize confirmation summary schema for sensitive actions with required fields: `intent`, `targets`, `capabilities`, `backend`, `risk_level`, and `execution_id`.
- Ensure equivalent summary ordering/formatting across command/workflow/agent-triggered sensitive actions at shared runtime boundaries.
- Persist stable summary linkage (hash/fingerprint/identifier) together with confirmation decision telemetry/audit records.
- Preserve sensitive-by-default handling in displayed summaries and persisted linkage metadata.

### Out of Scope
- Non-terminal approval channels (GUI/web/mobile).
- Multi-user collaborative approval workflow semantics.
- New confirmation modes beyond existing per-action and approved-plan behavior.

## Acceptance Criteria
1. **Required summary fields before execution:** Sensitive operations render standardized summary fields (`intent`, `targets`, `capabilities`, `backend`, `risk_level`, `execution_id`) before confirmation.
2. **Cross-path consistency:** Summary format remains consistent across command, workflow, and agent-triggered sensitive action entry paths where boundaries are shared.
3. **Audit linkage integrity:** Confirmation outcomes include deterministic linkage to the exact displayed summary via stable identifier/fingerprint.
4. **Operator clarity:** Summary output clearly communicates risk level and target scope for high-impact operations.
5. **Deterministic rendering contract:** Equivalent summary inputs produce stable field ordering and output structure.
6. **Sensitive-by-default safeguards:** Raw sensitive text/secrets are not exposed in summaries or linkage payloads unless explicitly opted in.

## Acceptance Criteria Traceability
- **AC1** ← `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md` `Story MVP-05.3` + `_bmad-output/planning-artifacts/endi-terminal-ux-mini-spec.md` `Confirmation Summary Panel`.
- **AC2** ← `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md` `Story MVP-05.3` + `_bmad-output/planning-artifacts/endi-architecture-final.md` `5.1 CLI Layer` and `5.2 Command Routing`.
- **AC3** ← `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md` `Story MVP-05.3` + `FR-010` audit linkage requirement in `_bmad-output/planning-artifacts/endi-prd.md`.
- **AC4** ← `_bmad-output/planning-artifacts/endi-terminal-ux-mini-spec.md` `Design Principles` and `Visual Conventions`.
- **AC5** ← `_bmad-output/planning-artifacts/endi-architecture-final.md` `2. Architecture Principles (Locked)` deterministic operations.
- **AC6** ← `project-context.md` sensitive-by-default guardrail + established runtime sanitization patterns.

## Tasks / Subtasks
- [x] Define canonical confirmation summary contract (AC: 1, 2, 5, 6)
  - [x] Declare required fields and deterministic ordering rules.
  - [x] Define sanitized serialization shape for linkage fingerprinting.
- [x] Implement shared summary builder across sensitive-action boundaries (AC: 1, 2, 5, 6)
  - [x] Reuse existing high-impact summary generation paths where available.
  - [x] Ensure command and conversational surfaces stay semantically aligned at shared boundaries.
- [x] Implement/align confirmation summary rendering behavior (AC: 1, 2, 4, 5)
  - [x] Ensure summary displays before sensitive execution.
  - [x] Preserve readability and non-color-only distinguishability expectations.
- [x] Persist deterministic summary linkage with confirmation outcomes (AC: 3, 6)
  - [x] Attach summary identifier/fingerprint to audit/telemetry confirmation records.
  - [x] Keep linkage payload sanitized by default.
- [x] Add strict-gate regression tests (AC: 1-6)
  - [x] Summary field completeness and ordering tests.
  - [x] Cross-path consistency tests for command and conversational boundaries.
  - [x] Audit-link integrity and sensitive-by-default regression tests.

## Dev Notes

### Previous Story Intelligence (`MVP-05.2`)
- Discoverability panels were centralized and keyed off resolved command identity to avoid output-sentinel collisions; preserve this style of contract-first routing and shared presentation helpers.
- Regression patterns already exist for command/conversation shared boundary behavior in `tests/test_dual_mode_routing.py`; extend those patterns for confirmation-summary consistency instead of introducing isolated test strategies.
- Shared Rich presentation helpers in `src/endi/presentation.py` are now the established rendering baseline for operator-facing terminal panels.

### ENDI Guardrails (Must Preserve)
- Deterministic behavior: stable summary fields, ordering, and linkage for equivalent input.
- Safety-by-default: sensitive actions require explicit confirmation before execution.
- Command/conversation parity: equivalent sensitive-action boundaries preserve the same externally observable summary semantics.
- Sensitive-by-default handling: treat raw request/response/user text as sensitive unless explicit opt-in exists.

### Technical Requirements
- Keep confirmation summary as an explicit contract consumed by both renderer and audit/telemetry linkage.
- Reuse existing confirmation policy paths (`per_action`, optional approved-plan behavior) without altering existing enforcement semantics.
- Align summary `risk_level` and `backend` fields with capability and backend selection metadata already produced by routing.
- Preserve structured runtime error and telemetry envelope conventions when summary/linkage contract validation fails.

### Concrete File-level Guidance
- `src/endi/routing.py`: enforce canonical summary contract generation and deterministic linkage payload creation for sensitive actions.
- `src/endi/presentation.py`: centralize/reuse confirmation summary panel rendering with stable field ordering and sanitized display behavior.
- `src/endi/cli.py`: keep confirmation panel output wired through shared presentation helpers and resolved command context.
- `tests/test_dual_mode_routing.py`: add parity and linkage regressions across command/conversation boundaries.
- `tests/test_presentation.py`: add deterministic ordering/readability/sanitization checks for confirmation summary rendering.
- `tests/test_conversational_loop.py` (only if required by touched code paths): add focused coverage for conversational confirmation-summary boundaries.

### Testing Requirements (Strict Gate)
- **Gate Level:** `Strict` (safety confirmation UX contract).
- Execute quality gates in WSL project `.venv`:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`
- Required test focus:
  - Required summary fields and deterministic ordering.
  - Cross-path summary consistency and command/conversation parity at shared boundaries.
  - Confirmation-decision to summary-linkage integrity.
  - Sensitive-by-default sanitization regressions in display and telemetry persistence.

### Review-Ready Exit Conditions
- [x] All acceptance criteria are covered by automated tests.
- [x] Sensitive actions consistently render normalized summary contract before execution.
- [x] Confirmation outcomes include deterministic, sanitized summary linkage.
- [x] Shared command/conversation boundaries preserve equivalent confirmation-summary semantics.
- [x] Strict WSL `.venv` quality gates pass.

## Dependencies
- `mvp-05-1-rich-terminal-theming-and-readability-baseline` (done): shared terminal panel baseline.
- `mvp-05-2-help-examples-and-command-introspection` (done): shared presentation/routing conventions for deterministic CLI UX.
- Existing confirmation and backend-selection metadata paths in `src/endi/routing.py`.

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-05.3 — Confirmation UX and operation summary consistency]
- [Source: `_bmad-output/planning-artifacts/endi-terminal-ux-mini-spec.md`#Confirmation Summary Panel (sensitive operations)]
- [Source: `_bmad-output/planning-artifacts/endi-terminal-ux-mini-spec.md`#Design Principles]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#2. Architecture Principles (Locked)]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#5.1 CLI Layer]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#5.2 Command Routing]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#7.2 Confirmation Policy]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-005 Permission and Confirmation Controls]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-010 Human-in-the-Loop Safeguard]
- [Source: `project-context.md`#Execution Environment]
- [Source: `project-context.md`#Agent Command Rules]

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used
- Cascade (GPT-5)

### Debug Log References
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"` (pass)
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"` (pass)
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"` (pass, 142 passed)

### Completion Notes List
- Added canonical confirmation summary contract in routing with required fields (`intent`, `targets`, `capabilities`, `backend`, `risk_level`, `execution_id`) and deterministic `summary_id` linkage from sanitized payload content.
- Updated command-path summary construction for both `per_action` and `approve_plan` confirmation modes to include consistent required fields and stable summary linkage metadata.
- Seeded command workflow `execution_id` before validation to ensure pre-confirmation summaries include execution correlation consistently before sensitive execution.
- Aligned confirmation summary rendering order/labels in presentation to canonical contract fields while preserving deterministic ordering and sensitive-field filtering.
- Expanded routing and CLI regression tests for required fields, parity expectations, summary-link integrity, and sensitive-by-default handling.
- Hardened summary-linkage regression coverage in `tests/test_dual_mode_routing.py` to assert `summary_id` deterministically matches sanitized summary payload and changes when canonical fields mutate.

### File List
- `src/endi/routing.py`
- `src/endi/presentation.py`
- `tests/test_dual_mode_routing.py`
- `tests/test_presentation.py`
- `_bmad-output/implementation-artifacts/stories/mvp-05-3-confirmation-ux-and-operation-summary-consistency.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log
- 2026-03-24: Refreshed story artifact to implementation-ready `ready-for-dev` format with explicit AC traceability, strict-gate testing guidance, and ENDI guardrail preservation.
- 2026-03-24: Implemented canonical confirmation-summary contract and deterministic summary linkage across sensitive command confirmation paths; aligned presentation ordering/labels and added strict regression coverage; quality gates passed in WSL `.venv` (`ruff`, `mypy`, `pytest`).
- 2026-03-25: Post-review hardening added deterministic `summary_id` linkage integrity assertions (including mutation sensitivity) in dual-mode routing tests; targeted and full strict WSL `.venv` gates passed.
