# Story MVP-00.1: Repository Scaffold and CI Quality Baseline

## Metadata
- **Story ID:** `MVP-00.1`

- **Epic:** `EPIC-MVP-00` Delivery Foundation and Greenfield Bootstrap

- **Priority:** `P1`

- **Suggested Sprint:** `Sprint 1`

- **Type:** `Delivery Foundation`

## User Story
As a maintainer, I want a greenfield scaffold and CI baseline, so that feature stories build on a stable, testable delivery foundation.

## Traceability
- **Functional Requirements:** `FR-002`, `FR-007`

- **Architecture Constraints:** `ADR-001`, `ADR-002`, `ADR-011`

## Scope

### In Scope
- Create baseline Python repository structure for ENDI runtime development (source and tests layout, packaging/config skeleton).

- Add CI pipeline for pull requests that runs `ruff`, `mypy`, and `pytest`.

- Configure CI to fail fast with stage-specific reporting for lint, type-check, and test stages.

- Document baseline quality-gate policy and strict-gate applicability for core MVP stories.

### Out of Scope
- Implementation of feature runtime components (router, workflows, agent loop, providers).

- Advanced release/deployment automation beyond baseline PR validation.

## Acceptance Criteria
1. Project skeleton is created with source/tests layout and baseline Python project configuration for ENDI runtime development.
2. CI pipeline runs lint (`ruff`), type-check (`mypy`), and tests (`pytest`) on pull requests.
3. CI reports stage-specific failures clearly (lint, type-check, test) and blocks merge on failed strict-gate checks.
4. Baseline quality-gate configuration is documented and aligned to ADR-011 tiering for core MVP stories.

## Implementation Notes
- Keep CLI stack choices aligned with architecture baseline (`Typer`, `Rich`, `Prompt Toolkit`) even if full runtime wiring is deferred.

- Preserve deterministic and observable development workflow standards from day one by enforcing quality gates in CI.

- Ensure CI jobs are deterministic and reproducible in local and CI environments (consistent Python version and dependency install path).

## Tasks
- [x] Create baseline repository scaffold (`src/`, `tests/`, baseline package metadata, and developer tooling config).

- [x] Add lint configuration for `ruff` and include baseline rule set appropriate for core modules.

- [x] Add static type-check configuration for `mypy` with strictness suitable for core runtime foundation.

- [x] Add baseline `pytest` configuration and smoke tests to validate scaffold integrity.

- [x] Implement PR CI workflow with separate lint, type-check, and test stages and clear failure signaling.

- [x] Document quality-gate policy and stage expectations in project docs.

## Testing Notes (ADR-011)
- **Gate Level:** `Strict`

- Add CI smoke validation proving each stage can fail independently with clear diagnostics.

- Add local command parity checks so the same quality commands used in CI run identically for contributors.

- Ensure strict-gate criteria are explicit for core/runtime stories to avoid gate ambiguity in follow-on implementation.

## Dependencies
- Python runtime baseline decision (`ADR-001`).

- CLI stack baseline (`ADR-002`) for dependency planning.

- CI/testing gate model (`ADR-011`) for strict core quality enforcement.

## Definition of Done
- All acceptance criteria pass.

- PR CI executes lint, type-check, and tests with stage-specific outcomes.

- Quality-gate policy is documented and traceable to ADR-011 and story FR coverage.

- Story status remains `ready-for-dev` until implementation begins.

## Dev Agent Record

### Debug Log
- Initial direct checks failed in host shell because `ruff`, `mypy`, and `pytest` were unavailable.
- Host `python` alias was not usable; switched to WSL Python runtime.
- System Python was externally managed (PEP 668), so a project-local virtual environment was created at `.venv`.
- CLI smoke test failed initially (`SystemExit(2)`) due to Typer single-command parsing behavior; resolved by adding `@app.callback()`.
- CI target was corrected from GitHub Actions to GitLab CI after repository hosting clarification.

### Completion Notes
- Implemented baseline Python scaffold (`src/endi`, `tests`) with package metadata and CLI entrypoint.
- Added strict quality tooling configuration (`ruff`, `mypy`, `pytest`) in `pyproject.toml`.
- Added merge-request quality workflow with explicit lint → type-check → test stages in GitLab CI.
- Added quality gate policy documentation aligned with ADR-011 strict tiering for core MVP scope.
- Validation executed in WSL virtual environment:
  - `ruff check src tests` ✅
  - `mypy src` ✅
  - `pytest` ✅ (2 passed)

## File List
- `pyproject.toml`
- `src/endi/__init__.py`
- `src/endi/cli.py`
- `tests/test_smoke.py`
- `.gitlab-ci.yml`
- `docs/quality-gates.md`

## Change Log
- 2026-03-17: Implemented repository scaffold and CI quality baseline for story `MVP-00.1`.
- 2026-03-17: Replaced GitHub Actions workflow with GitLab CI pipeline and updated documentation references.

## Status
done
