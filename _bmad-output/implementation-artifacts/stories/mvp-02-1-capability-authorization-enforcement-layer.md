# Story MVP-02.1: Capability Authorization Enforcement Layer

Status: done

## Metadata
- **Story ID:** `MVP-02.1`
- **Story Key:** `mvp-02-1-capability-authorization-enforcement-layer`
- **Epic:** `EPIC-MVP-02` Safety, Permissions, and Human-in-the-Loop Controls
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 1`
- **Type:** `Security Core`

## Story
As a security/compliance engineer, I want sensitive operations blocked without required capability, so that unauthorized actions cannot execute.

## Traceability
- **Functional Requirements:** `FR-005`, `FR-010`
- **Architecture Constraints:** `ADR-006`, `ADR-017`, `ADR-018`, `ADR-011`

## Acceptance Criteria
1. Sensitive capability checks run before command/workflow/tool execution.
2. Missing permission returns explicit structured denial error.
3. Denied operations do not execute any side-effecting tool step.

## Scope

### In Scope
- Capability model enforcement at command dispatch, workflow execution, and tool-invocation boundaries.
- Deterministic denial envelopes and status mapping aligned with existing runtime error contract behavior.
- Command/conversation parity for shared authorization semantics when both paths invoke the same guarded capabilities.
- Telemetry/audit event continuity for authorization decisions with correlation linkage.

### Out of Scope
- External identity provider integration.
- Organization-wide RBAC/SSO federation.
- Policy UX flows for user confirmation (`MVP-02.2`) and approve-plan mode (`MVP-02.3`).
- Backend isolation resolver implementation (`MVP-02.4`) beyond keeping interfaces compatible.

## Tasks / Subtasks
- [x] Define capability authorization decision model and deterministic denial envelope (AC: 1, 2)
  - [x] Specify required authorization inputs (requested capability set, execution context, operation metadata).
  - [x] Define stable denial/error fields and deterministic status mapping for unauthorized outcomes.
- [x] Integrate pre-execution authorization checks across runtime surfaces (AC: 1, 3)
  - [x] Enforce checks in command/workflow path before side-effecting actions.
  - [x] Enforce checks in conversational tool-invocation path where shared tool execution occurs.
  - [x] Verify denied paths short-circuit before side effects.
- [x] Preserve command/conversation parity for shared runtime contracts (AC: 1, 2, 3)
  - [x] Ensure authorization validation semantics remain externally equivalent across both surfaces.
  - [x] Align unauthorized error structure/status with existing deterministic runtime contract style.
- [x] Emit auditable authorization telemetry with sensitive-text safety defaults (AC: 2)
  - [x] Include correlation metadata and authorization decision metadata in structured events.
  - [x] Keep raw request/response/conversation text excluded or sanitized by default.
- [x] Add strict-gate tests for allow/deny matrix and side-effect blocking (AC: 1, 2, 3)
  - [x] Unit tests for policy evaluator allow/deny decisions across capability combinations.
  - [x] Integration tests proving denied operations do not execute side-effecting tool handlers.
  - [x] Cross-path tests for command/conversation parity on shared authorization outcomes.

## Dev Notes

### Technical Requirements
- Preserve deterministic + safety-by-default behavior established in MVP-01 runtime stories.
- Authorization checks must be fail-fast and pre-execution for any side-effecting action path.
- Denial responses must remain structured, explicit, and stable for CLI output and telemetry consumers.
- Treat raw request/response/conversation text as sensitive by default in persistence and telemetry artifacts.
- Avoid bypass paths around centralized dispatch/runtime policy checks.

### Architecture Compliance
- Implement capability gating aligned with architecture `7. Permission, Confirmation, and Sandboxing`.
- Keep backend-mapping compatibility with architecture `5.5 Execution Backends` and `14. Locked v1 Default Configuration Profile`.
- Preserve observability-first constraints from architecture `10. Observability Architecture`.
- Maintain command/conversation runtime boundaries from architecture `5.2 Command Routing` and `5.4 Agent Runtime`.

### Library / Framework Requirements
- Runtime remains Python `>=3.11` in the existing project dependency set.
- Reuse existing project tooling and dependencies in `pyproject.toml`.
- Do not introduce new libraries unless a blocker is identified and justified.

### File Structure Requirements
- Keep implementation changes within existing runtime boundaries under `src/endi/`.
- Extend existing routing/runtime/policy modules before introducing new files.
- Place tests in `tests/` with focused `test_*.py` coverage for authorization and parity behavior.

### Testing Requirements (ADR-011)
- **Gate Level:** `Strict` (core runtime/security story)
- Run quality gates in WSL project `.venv` using:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`
- Add deny/allow matrix tests by capability and operation class.
- Add regression tests proving denied paths are side-effect free.
- Add command/conversation parity tests for shared authorization decisions and error envelopes.

## Previous Story Intelligence (MVP-01.5)
- Reuse deterministic structured envelope patterns and status mapping conventions from tool contract baseline.
- Keep shared runtime behavior externally equivalent between command and conversation surfaces when logic is shared.
- Follow existing telemetry sanitation patterns: include actionable structured metadata while protecting sensitive raw text by default.
- Continue narrow, high-signal runtime changes with matching strict-gate tests.

## Git Intelligence
- Recent MVP-01 work favored incremental hardening of shared runtime contracts with explicit parity tests.
- Security/runtime stories should keep policy checks centralized and observable rather than scattered across ad-hoc call sites.

## Dependencies
- Existing routing and dispatch flow in `src/endi/routing.py`.
- Conversational path orchestration in `src/endi/conversation.py`.
- Workflow lifecycle boundaries in `src/endi/workflow.py`.
- Existing structured telemetry/event envelope conventions in runtime modules.
- Follow-on stories `MVP-02.2`, `MVP-02.3`, and `MVP-02.4`.

## References
- [Source: `_bmad-output/implementation-artifacts/mvp-02-kickoff-checklist.md`#First Story Selection]
- [Source: `_bmad-output/implementation-artifacts/epic-mvp-01-retro-2026-03-18.md`#Carry-Forward Guardrails]
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-02.1 — Capability authorization enforcement layer]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-005 Permission and Confirmation Controls]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-010 Human-in-the-Loop Safeguard]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-006 Context Resolution and Safety]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#7. Permission, Confirmation, and Sandboxing]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#10. Observability Architecture]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `project-context.md`]
- [Source: `docs/quality-gates.md`]

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
- Added centralized capability authorization decision model in `src/endi/authorization.py` with deterministic normalization, allow/deny evaluation, and stable metadata envelope fields.
- Enforced pre-execution command/workflow authorization checks in `src/endi/routing.py` with explicit `authorization_denied` runtime error mapping and side-effect short-circuiting.
- Extended workflow failure envelopes in `src/endi/workflow.py` to preserve structured failure details and deterministic custom failure types for security denials.
- Added tool-invocation capability gating in `src/endi/tools.py` with explicit `permission_denied` status code and deterministic denial metadata.
- Added/updated strict-gate tests for capability matrix, side-effect blocking, and command/conversation parity in `tests/test_authorization.py`, `tests/test_tool_contract.py`, and `tests/test_dual_mode_routing.py`.

### File List
- `src/endi/authorization.py`
- `src/endi/routing.py`
- `src/endi/tools.py`
- `src/endi/workflow.py`
- `tests/test_authorization.py`
- `tests/test_dual_mode_routing.py`
- `tests/test_tool_contract.py`
