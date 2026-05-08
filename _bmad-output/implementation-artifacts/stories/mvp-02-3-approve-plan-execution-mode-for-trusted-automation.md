# Story MVP-02.3: `--approve-plan` Execution Mode for Trusted Automation

Status: done

## Metadata
- **Story ID:** `MVP-02.3`
- **Story Key:** `mvp-02-3-approve-plan-execution-mode-for-trusted-automation`
- **Epic:** `EPIC-MVP-02` Safety, Permissions, and Human-in-the-Loop Controls
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 3`
- **Type:** `Security Policy Variant`

## Story
As a CI/operator user, I want one upfront approval for planned sensitive actions, so that safe automation can run non-interactively.

## Traceability
- **Functional Requirements:** `FR-005`, `FR-010`
- **Architecture Constraints:** `ADR-018`, `ADR-006`, `ADR-011`, `ADR-002`

## Acceptance Criteria
1. `--approve-plan` captures and confirms the planned sensitive action set once before side-effecting execution begins.
2. `--approve-plan --non-interactive` proceeds only when plan approval is valid, complete, and bound to the same execution context.
3. Any sensitive action not present in the approved plan is blocked deterministically and surfaced as structured policy violation.
4. Approved plan fingerprint and executed sensitive actions are linked in telemetry/audit trail with execution correlation IDs.
5. Existing default `per_action` confirmation remains the safe default when `--approve-plan` is not explicitly enabled.

## Scope

### In Scope
- Plan-building flow for sensitive actions prior to execution dispatch in `--approve-plan` mode.
- Upfront confirmation contract for plan approval with deterministic decision outcomes and stable status mapping.
- Non-interactive trusted automation path (`--approve-plan --non-interactive`) with explicit fail-fast validation for missing/invalid approvals.
- Runtime enforcement to block out-of-plan sensitive actions, including structured runtime error reporting.
- Command/conversation parity for externally observable policy behavior where shared runtime pathways are used.
- Structured telemetry/audit linkage for plan summary, approval decision, plan fingerprint, and executed sensitive actions.

### Out of Scope
- Blanket approvals with no disclosed plan content.
- Persistent cross-session approval caching.
- New provider adapters, plugin UX work, or backend isolation policy redesign (`MVP-02.4`).

## Tasks / Subtasks
- [x] Define approved-plan contract and deterministic fingerprint model (AC: 1, 4)
  - [x] Normalize planned sensitive action representation (operation identity, capability set, target metadata, backend context).
  - [x] Define stable plan fingerprint generation inputs and deterministic serialization rules.
- [x] Implement upfront plan approval flow in shared runtime policy boundary (AC: 1, 5)
  - [x] Add explicit approve/deny/cancel handling and deterministic runtime envelope mapping.
  - [x] Keep `per_action` behavior unchanged when `--approve-plan` is absent.
- [x] Implement non-interactive approved-plan validation path (AC: 2)
  - [x] Require explicit valid approval artifact/context prior to execution.
  - [x] Fail fast with structured policy violation when approval state is incomplete or mismatched.
- [x] Enforce out-of-plan action blocking during execution (AC: 3)
  - [x] Compare each sensitive action against approved plan set before side effects.
  - [x] Short-circuit denied execution prior to side-effecting tool invocation.
- [x] Emit auditable plan/approval telemetry with sensitive-text safety defaults (AC: 4)
  - [x] Link plan identifier/fingerprint, decision metadata, and execution correlation chain.
  - [x] Exclude or sanitize raw request/response/conversation text by default.
- [x] Add strict-gate regression tests for approve-plan behavior (AC: 1, 2, 3, 4, 5)
  - [x] Interactive happy-path and denial/cancel paths.
  - [x] Non-interactive validation failures and success path.
  - [x] Planned-vs-actual drift and out-of-plan blocking tests.
  - [x] Command/conversation parity assertions for shared policy outcomes.

## Dev Notes

### Technical Requirements
- Preserve deterministic behavior: identical inputs and approval state produce stable plan fingerprints, status mapping, and error envelopes.
- Preserve safety-by-default behavior: `per_action` confirmation remains default unless `--approve-plan` is explicitly enabled.
- Maintain command/conversation parity for shared runtime policy behavior at externally observable boundaries.
- Treat raw request/response/conversation text as sensitive-by-default in persistence, snapshots, and telemetry.
- Keep policy enforcement centralized in shared routing/runtime boundaries; do not implement ad-hoc bypass logic in individual tools.

### Architecture Compliance
- Follow architecture `7.2 Confirmation Policy` for optional `--approve-plan` mode compatibility with non-interactive automation.
- Preserve capability and policy boundaries defined in architecture `7. Permission, Confirmation, and Sandboxing`.
- Maintain observability linkage requirements from architecture `10. Observability Architecture`.
- Keep strict-gate verification aligned with architecture `11. Testing and CI Quality Model`.

### Library / Framework Requirements
- Runtime target remains Python `>=3.11` under the existing dependency set.
- Continue using existing CLI/runtime stack (`Typer`, `Rich`, `Prompt Toolkit`) and current project dependencies.
- Do not introduce new dependencies unless a blocking gap is identified and explicitly justified.

### File Structure Requirements
- Prefer extending existing policy and routing runtime modules under `src/endi/`.
- Keep approve-plan decision and enforcement logic in the same shared runtime contract surfaces used by authorization/confirmation.
- Add tests in `tests/` with focused modules for policy behavior, drift blocking, and parity coverage.

### Testing Requirements (ADR-011)
- **Gate Level:** `Strict` (security policy runtime path)
- Run quality gates in WSL project `.venv`:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`
- Required coverage:
  - Upfront plan approval required/approved/declined/cancelled outcomes.
  - Non-interactive approved-plan validation behavior.
  - Planned-vs-actual drift detection and out-of-plan side-effect prevention.
  - Plan fingerprint stability and telemetry/audit linkage integrity.
  - Command/conversation parity for shared policy contracts.

## Previous Story Intelligence (MVP-02.2)
- Reuse centralized deterministic confirmation contract patterns already established for sensitive-capability decisions.
- Preserve fail-fast no-side-effect guarantees for non-approved or policy-violating sensitive actions.
- Keep summary/context artifacts sanitized with sensitive raw text excluded by default.
- Preserve deterministic precedence behavior for global vs per-operation decision fields when operation-specific values are absent.
- Maintain parity tests as primary guardrails for command/conversation behavioral consistency.

## Dependencies
- Capability authorization layer in `MVP-02.1`.
- Per-action confirmation runtime contracts and telemetry scaffolding in `MVP-02.2`.
- Existing routing/runtime boundaries in `src/endi/routing.py`, `src/endi/workflow.py`, and conversational orchestration modules.
- Existing structured telemetry and runtime error envelope conventions.
- Follow-on compatibility with backend isolation resolver story `MVP-02.4`.

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-02.3 — `--approve-plan` execution mode for trusted automation]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-005 Permission and Confirmation Controls]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-010 Human-in-the-Loop Safeguard]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-006 Context Resolution and Safety]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#7. Permission, Confirmation, and Sandboxing]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#7.2 Confirmation Policy]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#10. Observability Architecture]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `_bmad-output/implementation-artifacts/stories/mvp-02-1-capability-authorization-enforcement-layer.md`]
- [Source: `_bmad-output/implementation-artifacts/stories/mvp-02-2-per-action-confirmation-for-sensitive-capabilities.md`]
- [Source: `project-context.md`]

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Debug Log
- Implemented approve-plan runtime policy path in `src/endi/routing.py` with deterministic plan normalization and fingerprinting helpers.
- Added non-interactive approved-plan validation (`confirmation_plan_missing`, `confirmation_plan_unapproved`, `confirmation_plan_invalid`, `confirmation_plan_context_mismatch`) and out-of-plan denial (`confirmation_out_of_plan`) before command execution.
- Preserved default `per_action` behavior when `confirmation_mode` is absent.
- Added approve-plan telemetry linkage with plan fingerprint, planned actions, and executed sensitive actions; existing safe telemetry/snapshot sanitization path remains unchanged.
- Added approve-plan regression coverage in `tests/test_dual_mode_routing.py` for success, fail-fast validation, out-of-plan drift blocking, deterministic fingerprint behavior, and conversation telemetry parity extraction.

### Completion Notes
- AC1 implemented via approve-plan mode support and deterministic pre-execution plan summary/fingerprint in validation pathway.
- AC2 implemented via explicit non-interactive approved-plan artifact validation (approval state, fingerprint integrity, context binding) with deterministic structured failures.
- AC3 implemented via sensitive action membership enforcement against approved plan before side-effect execution.
- AC4 implemented via confirmation telemetry fields linking plan fingerprint + action set and execution correlation IDs, with sensitive text still excluded by default via existing sanitization helpers.
- AC5 preserved: default confirmation mode remains `per_action` unless `confirmation_mode=approve_plan` is explicitly set.
- Strict gates passed in WSL `.venv`:
  - `ruff check src tests`
  - `mypy src`
  - `pytest` (`67 passed`)
- Review follow-up fixes applied and verified: conversation confirmation telemetry summary now strips raw-text fields recursively, and non-interactive approve-plan regression coverage now includes `confirmation_plan_unapproved` and fingerprint-invalid `confirmation_plan_invalid` paths.

## File List
- `src/endi/routing.py`
- `tests/test_dual_mode_routing.py`
- `_bmad-output/implementation-artifacts/stories/mvp-02-3-approve-plan-execution-mode-for-trusted-automation.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log
- 2026-03-19: Implemented `--approve-plan` runtime enforcement path with deterministic approved-plan fingerprinting, non-interactive validation, out-of-plan blocking, and telemetry/audit linkage updates.
- 2026-03-19: Added strict regression tests for approve-plan behavior and parity outcomes; strict WSL `.venv` quality gates passed.
- 2026-03-19: Applied post-review hardening to strip raw-text fields from conversation confirmation summary telemetry and added missing non-interactive regression coverage for `confirmation_plan_unapproved` and fingerprint-invalid `confirmation_plan_invalid` paths.
