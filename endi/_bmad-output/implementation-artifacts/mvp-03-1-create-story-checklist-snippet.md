# MVP-03.1 Create-Story Checklist Snippet

Purpose: Copy/paste-ready checklist for `create-story` on `mvp-03-1-sqlite-execution-history-schema-and-write-path`.

Source artifacts:
- `_bmad-output/implementation-artifacts/mvp-03-fr-007-compliance-matrix.md`
- `_bmad-output/implementation-artifacts/mvp-03-sensitive-data-sanitization-regression-template.md`

## Story Add-On (Paste into story Dev Notes / Testing Requirements)

### FR-007 Boundary Coverage (Required Matrix Rows)
- [ ] `session` boundary implemented with deterministic envelope fields and root correlation semantics.
- [ ] `command` boundary implemented with valid `session_id -> command_id` parent linkage.
- [ ] `workflow` boundary implemented with valid `command_id -> workflow_id` parent linkage.
- [ ] `step` boundary implemented with valid `workflow_id -> step_id` parent linkage.
- [ ] `runtime_error` envelope implemented with structured error fields and boundary correlation continuity.

### Determinism Requirements
- [ ] Repeated identical logical inputs produce stable envelope keys/status mapping.
- [ ] Missing parent-linkage fails as deterministic structured contract violation.

### Sensitive-by-Default Regression Cases (Minimum Set)
Use case IDs with the sanitization template format `SAN-<story>-<nn>`:
- [ ] `SAN-mvp-03-1-01` — CLI output sanitization (success + runtime_error path)
- [ ] `SAN-mvp-03-1-02` — telemetry payload sanitization for command/workflow/step events
- [ ] `SAN-mvp-03-1-03` — session snapshot sanitization with recursive nested-field checks
- [ ] `SAN-mvp-03-1-04` — persistence record sanitization for execution history rows
- [ ] `SAN-mvp-03-1-05` — runtime_error envelope sanitization (no raw text leakage)

### Test Evidence Requirements
- [ ] At least one recursive sanitization test included.
- [ ] Correlation continuity assertions included for `session -> command -> workflow -> step`.
- [ ] Structured runtime_error assertions include `error.type`, `error.code`, `error.component`.
- [ ] Strict WSL `.venv` quality gates recorded: `ruff check src tests`, `mypy src`, `pytest`.

### Review-Ready Exit Conditions
- [ ] Matrix row coverage for `mvp-03-1` is demonstrably satisfied.
- [ ] Sanitization regressions are green and would fail on raw-text leakage.
- [ ] No command/conversation parity regressions introduced at shared externally observable boundaries.
