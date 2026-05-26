# Story MVP-02.2: Per-action Confirmation for Sensitive Capabilities

Status: done

## Metadata
- **Story ID:** `MVP-02.2`
- **Story Key:** `mvp-02-2-per-action-confirmation-for-sensitive-capabilities`
- **Epic:** `EPIC-MVP-02` Safety, Permissions, and Human-in-the-Loop Controls
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 2`
- **Type:** `Security UX`

## Story
As an operator, I want explicit confirmation for high-impact actions, so that destructive behavior cannot run autonomously.

## Traceability
- **Functional Requirements:** `FR-005`, `FR-010`
- **Architecture Constraints:** `ADR-006`, `ADR-018`, `ADR-011`, `ADR-002`

## Acceptance Criteria
1. Sensitive capabilities require explicit per-action confirmation by default.
2. High-impact summary is shown before confirmation.
3. Confirmation decision is linked to execution ID in audit records.

## Scope

### In Scope
- Per-action confirmation enforcement for sensitive capabilities (`repo.write`, `filesystem.write`, `shell.exec`, `cloud.write`, `system.modify`, `network.admin`) in default `per_action` mode.
- Pre-confirmation high-impact operation summary generation/rendering with stable, auditable summary fields.
- Deterministic confirmation outcomes (`approved`, `declined`, `cancelled`, `timeout`) mapped to structured runtime status/error envelopes.
- Command/conversation parity at externally observable boundaries for summary schema, confirmation decision semantics, and denial short-circuit behavior.
- Structured telemetry/audit linkage between summary shown, confirmation decision, and final execution correlation IDs.

### Out of Scope
- `--approve-plan` upfront approval mode and non-interactive trusted automation behavior (`MVP-02.3`).
- Capability-to-backend policy resolver design and strongest-isolation resolution (`MVP-02.4`).
- New provider adapters, plugin-specific confirmation UX, or non-terminal UX channels.

## Tasks / Subtasks
- [x] Define normalized confirmation decision contract and deterministic status mapping (AC: 1, 3)
  - [x] Reuse MVP-02.1 authorization-style structured envelope patterns for confirmation denials/aborts.
  - [x] Ensure declined/cancelled outcomes never proceed to side-effecting tool execution.
- [x] Implement pre-action confirmation gate in shared runtime path (AC: 1, 2)
  - [x] Enforce checks before sensitive side-effecting action dispatch in command/workflow execution.
  - [x] Ensure conversational path invoking sensitive tools receives equivalent confirmation semantics.
- [x] Implement high-impact summary schema + renderer contract (AC: 2)
  - [x] Normalize summary fields (intent, targets, capabilities, backend, risk level, execution/workflow context).
  - [x] Ensure summary payload remains structured and scrubbed of sensitive raw text by default.
- [x] Persist and emit confirmation telemetry/audit linkage (AC: 3)
  - [x] Record summary fingerprint/identifier, decision, actor context, and correlation chain.
  - [x] Keep logs/events structurally rich while excluding raw conversational/request text by default.
- [x] Add strict-gate tests for confirmation-required/declined/approved flows (AC: 1, 2, 3)
  - [x] Unit tests for sensitive-capability decision matrix.
  - [x] Integration tests proving no side effects occur on declined/cancelled/timeout decisions.
  - [x] Cross-path parity tests for command/conversation confirmation semantics and envelope fields.

## Dev Notes

### Technical Requirements
- Preserve deterministic behavior: identical inputs + confirmation decisions must yield stable status codes/envelopes.
- Preserve safety-by-default behavior: confirmation required for sensitive capabilities unless future explicit policy mode (`MVP-02.3`) is active.
- Maintain command/conversation parity for shared confirmation contracts at externally observable boundaries.
- Treat raw request/response/conversation text as sensitive-by-default in persistence and telemetry.
- Keep confirmation enforcement centralized in shared dispatch/runtime policy boundaries; avoid ad-hoc tool-level prompt implementations.

### Architecture Compliance
- Align with architecture `7. Permission, Confirmation, and Sandboxing` for per-action default confirmation policy.
- Preserve command routing and interaction boundaries from architecture `5.2 Command Routing`.
- Keep bounded conversational runtime controls aligned with architecture `5.4 Agent Runtime`.
- Maintain observability linkage requirements from architecture `10. Observability Architecture`.
- Follow strict core quality-gate expectations in architecture `11. Testing and CI Quality Model`.

### Library / Framework Requirements
- Runtime target remains Python `>=3.11` per project baseline.
- Continue using existing CLI stack (`Typer`, `Rich`, `Prompt Toolkit`) and runtime dependencies already declared in `pyproject.toml`.
- Do not introduce new dependencies unless a blocking gap is identified and justified.

### File Structure Requirements
- Prefer extending existing runtime policy/routing modules under `src/endi/` rather than introducing parallel confirmation stacks.
- Keep summary/confirmation schema handling in the same runtime contract surfaces used by authorization and routing.
- Add tests in `tests/` using focused `test_*.py` modules for confirmation policy, parity, and telemetry linkage behavior.

### Testing Requirements (ADR-011)
- **Gate Level:** `Strict` (security/HITL core path)
- Run quality gates in WSL project `.venv`:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`
- Required coverage:
  - Confirmation required/declined/approved/cancelled paths.
  - No-side-effect guarantees on non-approval outcomes.
  - Summary schema stability + audit linkage integrity.
  - Command/conversation parity for confirmation outcomes and envelope fields.

## Previous Story Intelligence (MVP-02.1)
- Reuse centralized, deterministic runtime contract patterns introduced for capability authorization.
- Keep security controls fail-fast before side-effecting execution paths.
- Preserve structured denial/decision envelopes and stable status mappings.
- Maintain sanitized telemetry patterns: high-value metadata without raw sensitive text.
- Keep cross-path parity tests as first-class regression protection.

## Dependencies
- Authorization/capability enforcement layer completed in `MVP-02.1`.
- Existing routing/dispatch/runtime boundaries in `src/endi/routing.py`, `src/endi/workflow.py`, and conversational orchestration paths.
- Existing structured telemetry/event envelope conventions and correlation hierarchy.
- Follow-on compatibility with `MVP-02.3` and `MVP-02.4` policy extensions.

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-02.2 — Per-action confirmation for sensitive capabilities]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-005 Permission and Confirmation Controls]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-010 Human-in-the-Loop Safeguard]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-006 Context Resolution and Safety]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#7. Permission, Confirmation, and Sandboxing]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#10. Observability Architecture]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `_bmad-output/implementation-artifacts/stories/mvp-02-1-capability-authorization-enforcement-layer.md`]
- [Source: `_bmad-output/implementation-artifacts/mvp-02-kickoff-checklist.md`#Go-Forward Sequence]
- [Source: `project-context.md`]

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used
- Cascade (GPT-5)

### Debug Log References
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`

### Completion Notes List
- Story context refreshed with explicit carry-forward guardrails from MVP-02.1 (deterministic behavior, safety-by-default, command/conversation parity, sensitive-by-default text handling).
- Added strict, implementation-ready confirmation flow scope and deterministic decision/envelope requirements.
- Added parity-focused testing expectations and WSL `.venv` quality-gate command requirements.
- Implemented deterministic per-action confirmation contracts (`approved` / `declined` / `cancelled` / `timeout`) in shared command routing with fail-fast short-circuit before side effects for non-approved sensitive actions.
- Added high-impact summary generation with stable fingerprint (`summary_id`) and structured fields (`intent`, `targets`, `capabilities`, `backend`, `risk_level`, execution context) linked to execution correlation.
- Added confirmation decision telemetry linkage for command and conversation externally observable boundaries while preserving sensitive-by-default sanitization.
- Added and passed strict tests for confirmation-required default timeout, approved execution path, and conversation-path confirmation decision parity.
- Follow-up fix applied for sensitive-by-default parity: conversation session snapshot and telemetry contexts now exclude raw request/response/conversation text fields before sanitization.
- Follow-up fix applied for deterministic confirmation precedence: global `confirmation_decision` now remains fallback when per-action map does not include the current operation.
- Added regression tests for conversation raw-text exclusion and global confirmation fallback behavior.
- Validated strict gates in WSL `.venv`: `ruff check src tests`, `mypy src`, and `pytest` (59 passed).

### File List
- `_bmad-output/implementation-artifacts/stories/mvp-02-2-per-action-confirmation-for-sensitive-capabilities.md`
- `src/endi/routing.py`
- `tests/test_dual_mode_routing.py`
