# Story MVP-01.5: Tool Contract Standardization Baseline

Status: done

## Metadata
- **Story ID:** `MVP-01.5`
- **Story Key:** `mvp-01-5-tool-contract-standardization-baseline`
- **Epic:** `EPIC-MVP-01` Core CLI, Routing, and Deterministic Runtime
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 1`
- **Type:** `Core Runtime Contract`

## Story
As a runtime engineer, I want all tools to follow a single validated contract, so that invocation behavior is deterministic and safe across command and agent paths.

## Traceability
- **Functional Requirements:** `FR-004`
- **Architecture Constraints:** `ADR-003`, `ADR-004`, `ADR-011`, `ADR-012`, `ADR-013`

## Acceptance Criteria
1. Tool registry rejects tool registration when required metadata or contract fields are missing or malformed; invalid tools never enter active registry state.
2. Tool invocation validates input against declared schema before execution and blocks handler side effects when validation fails.
3. Tool execution returns structured success/error responses with deterministic status codes for success, invalid contract, invalid input, not found, and execution error outcomes.
4. Command and conversational runtime surfaces preserve the same tool contract semantics at externally observable boundaries: identical validation behavior, deterministic status mapping, and structured tool error code/component details when tool invocation fails (conversation may also include loop-level termination reason).

## Scope

### In Scope
- Establish a canonical tool contract shape for metadata, input schema, execution interface, and output envelope.
- Enforce registration-time validation for required tool contract fields.
- Enforce invocation-time input validation before executing tool handlers.
- Standardize structured success/error response envelopes and deterministic status code mapping.
- Cover both command and conversational/agent call paths where tool invocation is shared.

### Out of Scope
- New tool categories beyond current baseline (`filesystem`, `shell`) unless required by contract abstraction.
- Provider-adapter capability contracts (`MVP-04.1`) and plugin discovery/versioning (`POST-01.*`).
- Policy-level authorization/confirmation flows (`MVP-02.*`) except where contract errors must remain structured.

## Tasks / Subtasks
- [x] Define canonical tool contract model (AC: 1, 2, 3)
  - [x] Specify required registration fields (identifier, description, capability metadata, input schema, callable handler).
  - [x] Define typed success/error response envelope with deterministic status code set.
  - [x] Establish normalization rules for optional metadata and defaults.
- [x] Enforce registration validation in registry path (AC: 1)
  - [x] Add fail-fast checks that reject tools missing required contract fields.
  - [x] Return structured, non-throwing validation errors where possible to preserve deterministic behavior.
  - [x] Ensure invalid tools never appear in active registry state.
- [x] Enforce invocation schema validation (AC: 2)
  - [x] Validate invocation payload against declared input schema before handler execution.
  - [x] Return structured validation failures with deterministic status codes.
  - [x] Block execution side effects when validation fails.
- [x] Standardize execution output contract (AC: 3)
  - [x] Normalize success payload shape and metadata fields.
  - [x] Normalize error payload shape including stable error codes/categories.
  - [x] Ensure status codes are deterministic across repeated runs and across command/agent paths.
- [x] Integrate contract usage in routing/runtime surfaces (AC: 1, 2, 3)
  - [x] Verify command-dispatch tool calls use the same contract validation and response envelopes.
  - [x] Verify conversational/agent tool calls use the same contract validation and response envelopes.
  - [x] Ensure conversation failure surfaces preserve structured tool error semantics (error code/component/status mapping) in addition to loop termination metadata.
- [x] Add strict-gate tests for contract behavior (AC: 1, 2, 3)
  - [x] Registry tests for required-field rejection and accepted valid registrations.
  - [x] Invocation tests for schema pass/fail and execution blocking on invalid input.
  - [x] Response-shape and deterministic status-code tests on success and error paths.
  - [x] Cross-path runtime tests asserting command dispatch and conversational runtime expose equivalent tool contract outcomes for shared invocations.

## Dev Notes

### Technical Requirements
- Preserve deterministic runtime behavior already established in `MVP-01.1` through `MVP-01.4`.
- Prefer single-source contract validation utilities used by both command and agent tool invocation paths.
- Keep contract enforcement fail-fast and explicit; avoid implicit coercion that can mask malformed inputs.
- Ensure contract errors are structured and safe for telemetry/logging envelopes.

### Architecture Compliance
- Align with deterministic orchestration guarantees (architecture `5.3 Workflow Engine`).
- Respect bounded and policy-controlled agent runtime behavior (architecture `5.4 Agent Runtime`).
- Keep registry and validation hooks in core runtime boundaries (architecture `6.3 Registry Boundaries`).
- Maintain strict compatibility posture for core contracts (architecture `13.1 Core Versioning`, `13.2 Capability Versioning`).

### Library / Framework Requirements
- Runtime implementation in Python `>=3.11`.
- Continue project dependency baselines from `pyproject.toml`:
  - `typer>=0.12,<1`
  - `rich>=13,<14`
  - `prompt-toolkit>=3.0,<4`
- Quality tooling expectations:
  - `pytest>=8,<9`
  - `mypy>=1.10,<2`
  - `ruff>=0.4,<1`

### File Structure Requirements
- Keep runtime contract/registry changes under `src/endi/` and extend existing module boundaries before introducing new modules.
- If creating a dedicated tool contract module, keep naming and typing patterns consistent with current runtime files.
- Place tests in `tests/` using existing `test_*.py` conventions with focused contract-level coverage.

### Testing Requirements (ADR-011)
- **Gate Level:** `Strict`
- Add registration validation tests for missing required fields and malformed schemas.
- Add invocation validation tests proving handler execution is blocked for invalid payloads.
- Add deterministic response contract tests validating stable status codes and envelope structure.
- Add cross-path tests to assert parity between command-triggered and conversational tool invocation contracts at externally observable runtime surfaces (not only registry utility calls).
- Validate that conversation path failures preserve loop termination reason and structured tool failure details (`error_code`, `component`, deterministic status mapping) for UX/telemetry consistency.
- Run `ruff`, `mypy`, and `pytest` in WSL project `.venv`.

## Previous Story Intelligence (MVP-01.4)
- Keep deterministic and structured patterns used in `src/endi/routing.py` and related runtime modules.
- Reuse centralized policy and sanitization style where shared runtime artifacts are produced.
- Preserve parity between command and conversational execution paths when behavior is intended to be common.
- Avoid alternate bypass paths around centralized dispatch/runtime logic.

## Git Intelligence
- Recent commits show incremental hardening of the deterministic core (`MVP-01.1` to `MVP-01.4`).
- Continue the pattern of narrow runtime changes paired with strict contract-focused tests.
- Keep implementation scoped to core runtime contract boundaries without architectural churn.

## Latest Tech Information
- No additional external libraries are required for this story; use current project dependency set.
- Avoid version upgrades in this story unless a blocker is discovered during implementation.

## Dependencies
- Existing routing/dispatch behavior in `src/endi/routing.py` for command and conversation parity.
- Deterministic workflow contract conventions in `src/endi/workflow.py`.
- Conversational bounded-loop integration points in `src/endi/conversation.py`.
- Follow-on contract consumers in provider/plugin stories (`MVP-04.1`, `POST-01.*`).

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-01.5 — Tool contract standardization baseline]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-004 Tool Contract Standardization]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#7) Non-Functional Requirements]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#5.3 Workflow Engine (Deterministic Core)]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#5.4 Agent Runtime]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#6.3 Registry Boundaries]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#13. Versioning and Compatibility]
- [Source: `_bmad-output/planning-artifacts/endi-adr-rationales.md`#ADR-011 — Testing Strategy and CI Quality Gates]
- [Source: `_bmad-output/planning-artifacts/endi-adr-rationales.md`#ADR-013 — Versioning and Compatibility Policy]
- [Source: `_bmad-output/implementation-artifacts/stories/mvp-01-4-safe-context-precedence-and-sensitive-state-handling.md`]
- [Source: `project-context.md`]
- [Source: `pyproject.toml`]

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used
- Cascade (GPT-5)

### Debug Log References
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest -q tests/test_tool_contract.py tests/test_conversational_loop.py tests/test_dual_mode_routing.py"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check ."`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest -q"`

### Completion Notes List
- Added `src/endi/tools.py` with canonical tool contract dataclasses, strict registration checks, input schema validation, and deterministic success/error envelopes.
- Updated conversational runtime in `src/endi/conversation.py` to consume structured `ToolResult` envelopes and treat tool error envelopes deterministically as tool-failure terminations.
- Added strict-gate contract tests in `tests/test_tool_contract.py` covering registration rejection, invocation schema enforcement, deterministic status codes, and command/conversation parity via shared registry invocation.
- Documented agent file-creation guardrail in `project-context.md` to avoid `apply_patch` new-file failures and use dedicated file creation tooling.
- Verified quality gates in WSL project `.venv`: `ruff`, `mypy`, focused `pytest`, and full `pytest` all passing.

### File List
- `src/endi/tools.py`
- `src/endi/conversation.py`
- `tests/test_tool_contract.py`
- `project-context.md`

### Change Log
- 2026-03-18: Implemented tool contract baseline (registry + invocation validation + deterministic envelopes), integrated conversational envelope handling, added strict-gate tests, and documented apply-patch new-file limitation guardrail.
- 2026-03-18: Normalized MVP-01.5 acceptance-criteria wording across story, backlog, and PRD to require externally observable command/conversation contract parity and deterministic structured tool-failure semantics.
- 2026-03-18: Added runtime-error surfacing follow-ups: CLI display for runtime_error context, conversation telemetry runtime_error emission, README discoverability link, and supporting regression tests.
