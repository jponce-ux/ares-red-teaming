# ENDI Quality Gates Baseline

This document defines the baseline CI quality gates for ENDI and the local command parity required for contributors.

## Gate Tiering (ADR-011)

ENDI uses hybrid gate strictness by module tier. For MVP core stories, the gate level is **Strict**.

- **Strict (core/runtime/security/contract-critical modules):** merge requests must pass lint, type-check, and tests.
- **Moderate (adapters):** May allow reduced strictness in future stories when explicitly approved.
- **Light (plugins/experiments):** May prioritize iteration speed in future stories when explicitly approved.

Current story `MVP-00.1` establishes the strict baseline for all core MVP delivery foundation work.

## Merge Request Gate Policy

The GitLab CI pipeline in `.gitlab-ci.yml` enforces sequential stages:

1. **Lint stage:** `ruff check src tests`
2. **Type-check stage:** `mypy src`
3. **Test stage:** `pytest`

Stage-specific diagnostics are provided by independent GitLab jobs:

- `lint`
- `typecheck`
- `test`

A failure in any stage fails the pipeline and blocks merge when protected-branch checks require successful jobs.

## Deterministic Execution Baseline

To keep local and CI behavior reproducible:

- Python runtime is pinned to patch version `3.11.9` in CI.
- Dependencies are installed using `python -m pip install -e .[dev]`.
- CI quality tools are pinned for deterministic gates:
  - `ruff==0.4.10`
  - `mypy==1.10.0`
  - `pytest==8.2.2`
- CI and local commands are identical.

## Local Command Parity

Run the same commands used by CI before opening a merge request:

```bash
python -m pip install -e .[dev]
ruff check src tests
mypy src
pytest
```

## Stage-Failure Smoke Validation

You can quickly confirm each stage fails independently with clear diagnostics:

- Lint failure smoke: introduce an unused import in `src/` and run `ruff check src tests`.
- Type-check failure smoke: introduce an incompatible type assignment and run `mypy src`.
- Test failure smoke: force an assertion failure in `tests/test_smoke.py` and run `pytest`.

Revert smoke changes after validation.
