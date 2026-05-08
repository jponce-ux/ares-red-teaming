# Story MVP-02.4: Capability-to-backend Mapping and Isolation Resolver

Status: done

## Metadata
- **Story ID:** `MVP-02.4`
- **Story Key:** `mvp-02-4-capability-to-backend-mapping-and-isolation-resolver`
- **Epic:** `EPIC-MVP-02` Safety, Permissions, and Human-in-the-Loop Controls
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 2`
- **Type:** `Runtime Policy`

## Story
As a runtime maintainer, I want explicit capability backend routing, so that high-risk actions use stronger isolation.

## Traceability
- **Functional Requirements:** `FR-005`
- **Architecture Constraints:** `ADR-017`, `ADR-012`, `ADR-004`, `ADR-006`, `ADR-011`

## Acceptance Criteria
1. Runtime uses an explicit capability-to-backend mapping table for backend selection.
2. When multiple capabilities are requested, the highest isolation requirement wins deterministically.
3. v1 ships with `LocalBackend` implementation and interface contracts for `WorkerBackend`, `ContainerBackend`, and `RemoteBackend`.

## Scope

### In Scope
- Policy-driven capability-to-backend mapping resolver aligned to locked runtime policy defaults.
- Deterministic precedence logic where stricter isolation wins for mixed-capability requests.
- `LocalBackend` concrete execution path for v1 and explicit backend interface contracts for worker/container/remote.
- Integration of backend selection outputs into runtime dispatch and policy/confirmation summaries.
- Structured telemetry/audit emission for backend selection rationale and selected backend.

### Out of Scope
- Full worker/container/remote backend runtime implementations.
- Remote dynamic policy fetch, centralized policy service, or distributed orchestration redesign.
- Changes to provider routing defaults (`chat/tools/embeddings`) or plugin architecture work.

## Tasks / Subtasks
- [x] Define backend policy contract and deterministic resolver (AC: 1, 2)
  - [x] Implement normalized capability mapping model based on locked v1 defaults from architecture.
  - [x] Define stable isolation ranking and deterministic tie/merge behavior for multi-capability inputs.
- [x] Implement backend interface boundary (AC: 3)
  - [x] Keep `LocalBackend` executable in v1.
  - [x] Define explicit interfaces/contracts for `WorkerBackend`, `ContainerBackend`, and `RemoteBackend` without implementing full runtimes.
- [x] Integrate resolver into shared runtime dispatch path (AC: 1, 2, 3)
  - [x] Resolve backend before side-effecting execution and make result available to confirmation/authorization telemetry payloads.
  - [x] Ensure command and conversation shared runtime behavior remains consistent at externally observable boundaries.
- [x] Add strict-gate tests for mapping/isolation behavior (AC: 1, 2, 3)
  - [x] Capability-to-backend matrix tests (single capability + mixed capability combinations).
  - [x] Determinism tests for stable backend result under repeated identical inputs.
  - [x] Contract tests confirming non-local backend interfaces are present and type-safe.
  - [x] Regression tests ensuring existing authorization + confirmation flows continue to behave safely.

## Dev Notes

### Technical Requirements
- Preserve deterministic behavior: identical resolved capabilities/context must produce the same selected backend and telemetry shape.
- Preserve safety-by-default behavior: stricter isolation wins; no downgrade to weaker backend when higher-risk capability is present.
- Maintain command/conversation parity for shared policy outcomes exposed through runtime envelopes and telemetry.
- Treat raw request/response/conversation text as sensitive-by-default in persistence and telemetry artifacts.
- Keep backend policy logic centralized in shared runtime/routing policy surfaces; avoid duplicating resolver logic across call sites.

### Architecture Compliance
- Align with architecture `5.5 Execution Backends` for v1 local backend + future backend interfaces.
- Implement explicit capability mapping per architecture `4.1 Key Separation Rules` and locked `ADR-017` decision.
- Preserve local-first runtime topology from architecture `12. Runtime Topology and Deployment` while enabling pluggable backends.
- Keep permission/confirmation contracts from architecture `7. Permission, Confirmation, and Sandboxing` intact.
- Keep strict quality-gate expectations aligned with architecture `11. Testing and CI Quality Model`.

### Library / Framework Requirements
- Runtime target remains Python `>=3.11` per project baseline.
- Continue with existing runtime stack and dependencies; do not add new dependencies unless a blocker is identified and justified.
- Keep implementations consistent with existing dataclass/enum/type-hinted patterns in `src/endi/`.

### File Structure Requirements
- Prefer extending existing runtime policy integration in `src/endi/routing.py` for dispatch wiring.
- Add focused backend policy/runtime abstraction module(s) under `src/endi/` only if separation improves clarity (for example, resolver + interface contracts).
- Preserve existing authorization/context integration points in `src/endi/authorization.py` and `src/endi/context.py` semantics.
- Add regression coverage in `tests/test_dual_mode_routing.py` and adjacent focused test modules only as needed.

### Testing Requirements (ADR-011)
- **Gate Level:** `Strict` (runtime/security boundary)
- Run quality gates in WSL project `.venv`:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`
- Required coverage:
  - Capability mapping matrix and strongest-isolation precedence.
  - Deterministic backend selection under repeated identical context.
  - LocalBackend execution path continuity in command dispatch.
  - Interface/contract presence for non-local backend types.
  - No regressions in authorization, per-action confirmation, and approve-plan policy behavior.

## Previous Story Intelligence (MVP-02.3)
- Reuse centralized policy enforcement in `routing.py` and avoid introducing side-channel policy decisions.
- Preserve deterministic normalization/fingerprinting discipline for policy artifacts where backend resolution metadata is emitted.
- Keep non-interactive and out-of-plan safety guarantees untouched when adding backend resolution behavior.
- Maintain telemetry/audit linkage quality and correlation continuity.
- Continue sensitive-by-default sanitization for raw text fields in session snapshots and telemetry payloads.

## Dependencies
- Capability authorization baseline from `MVP-02.1`.
- Confirmation and approve-plan policy paths from `MVP-02.2` and `MVP-02.3`.
- Existing deterministic dispatch/runtime lifecycle in `src/endi/routing.py` and `src/endi/workflow.py`.
- Architecture-locked v1 capability-to-backend defaults in `_bmad-output/planning-artifacts/endi-architecture-final.md`.

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-02.4 — Capability-to-backend mapping and isolation resolver]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-005 Permission and Confirmation Controls]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#5.5 Execution Backends]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#7. Permission, Confirmation, and Sandboxing]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#14. Locked v1 Default Configuration Profile]
- [Source: `_bmad-output/implementation-artifacts/stories/mvp-02-1-capability-authorization-enforcement-layer.md`]
- [Source: `_bmad-output/implementation-artifacts/stories/mvp-02-2-per-action-confirmation-for-sensitive-capabilities.md`]
- [Source: `_bmad-output/implementation-artifacts/stories/mvp-02-3-approve-plan-execution-mode-for-trusted-automation.md`]
- [Source: `project-context.md`]

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used
- Cascade (GPT-5)

### Debug Log References
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && git log -n 5 --pretty=format:'%h %s'"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest tests/test_dual_mode_routing.py -q"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`

### Completion Notes List
- Implemented `src/endi/backends.py` with explicit v1 capability-to-backend policy defaults, deterministic highest-isolation-wins resolver, and stable metadata payload shape for audit/telemetry use.
- Added backend execution boundary contracts (`ExecutionBackend`, `WorkerBackend`, `ContainerBackend`, `RemoteBackend`) and retained concrete `LocalBackend` execution path for v1.
- Integrated backend resolution into shared command dispatch in `src/endi/routing.py` before execution, including context exposure (`execution_backend`, `backend_selection`) and policy payload linkage for authorization/confirmation.
- Extended command and conversation telemetry to emit structured backend selection rationale while preserving sensitive-by-default sanitization behavior.
- Added strict-gate regression coverage in `tests/test_dual_mode_routing.py` for mapping matrix, deterministic selection, interface contracts, command telemetry embedding, and conversation runtime-error parity extraction.
- Updated approve-plan action fixtures to match locked v1 backend mapping for `system.modify` (`worker`) so existing confirmation/authorization protections remain covered with the new resolver.
- Quality gates passed in WSL project `.venv`: `ruff check src tests`, `mypy src`, `pytest` (72 passed).

### Code Review (2026-03-20)

#### Findings (ordered by severity)
- **High — Selected backend is not used for command execution (safety/parity regression risk)**
  - Evidence: backend selection resolves and is propagated (`execution_backend`, `backend_selection`) in `src/endi/routing.py` at lines 859-867, but execution always instantiates `LocalBackend` at lines 985-986.
  - Impact: externally observable metadata can report `worker`/higher isolation while execution still runs through local backend, creating a downgrade gap against the story intent (high-risk actions use stronger isolation) and a command boundary parity risk between reported and actual execution backend.
  - AC/constraint impact: risks AC2 intent in practice (strongest isolation winning does not govern actual execution path) and safety-by-default guardrail.

#### Acceptance Criteria Coverage Check
- **AC1 (explicit mapping table):** Covered by `src/endi/backends.py` mapping constants and resolver (`_DEFAULT_CAPABILITY_BACKENDS`, `resolve_backend_selection`) with tests at `tests/test_dual_mode_routing.py` lines 1343-1362.
- **AC2 (highest isolation wins deterministically):** Resolver logic uses stable isolation ordering and deterministic normalization (`src/endi/backends.py` lines 20-27, 116-130, 186-209); determinism and mixed-capability behavior covered at `tests/test_dual_mode_routing.py` lines 1364-1392.
- **AC3 (Local backend + non-local contracts):** Local implementation and protocol contracts present in `src/endi/backends.py` lines 62-113; contract coverage at `tests/test_dual_mode_routing.py` lines 1394-1412.

#### Coverage Gaps / Residual Risks
- Missing regression test asserting that resolved non-local backend selection is either enforced in dispatch execution or explicitly blocked/fails-safe (current tests validate selection metadata and contracts, but not execution-path alignment).
- No direct test proving that runtime overrides cannot weaken locked v1 capability mappings for sensitive capabilities; current tests focus on defaults/determinism rather than anti-downgrade constraints under override input.

#### Quality Gate Evidence (WSL `.venv`)
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"` → `All checks passed!`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"` → `Success: no issues found in 9 source files`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"` → `72 passed in 0.21s`

#### Post-Review Fix Applied (2026-03-20)
- Implemented execution-path alignment so command dispatch uses the resolved backend selection rather than always executing through local backend; added fail-safe `backend_unavailable` blocking when selected non-local backend is not configured.
- Added anti-downgrade guard for locked capability mappings so runtime overrides cannot reduce isolation below locked defaults for known capabilities.
- Added focused regressions for (1) backend-unavailable blocking and (2) locked-capability downgrade override protection.
- Re-ran strict gates in WSL project `.venv`:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"` → `All checks passed!`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"` → `Success: no issues found in 9 source files`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"` → `74 passed in 0.46s`

### File List
- `src/endi/backends.py`
- `src/endi/routing.py`
- `tests/test_dual_mode_routing.py`
- `_bmad-output/implementation-artifacts/stories/mvp-02-4-capability-to-backend-mapping-and-isolation-resolver.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log
- 2026-03-19: Implemented deterministic capability-to-backend resolver and backend interface contracts; integrated resolver metadata into shared routing telemetry/policy payloads; added strict regression coverage and passed WSL `.venv` quality gates.
- 2026-03-20: Applied post-review hardening to align command execution with resolved backend selection, added fail-safe `backend_unavailable` blocking for unconfigured non-local backends, and enforced locked-capability anti-downgrade override protection with added regressions.
