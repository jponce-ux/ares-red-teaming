# MVP-03 Sensitive-Data Sanitization Regression Template

Source:
- `_bmad-output/implementation-artifacts/epic-mvp-02-retro-2026-03-19.md`
- `_bmad-output/implementation-artifacts/mvp-03-kickoff-checklist.md`

Purpose: Provide reusable regression scenarios to validate sensitive-by-default handling for raw text across externally observable boundaries.

## Policy Baseline
- Raw/free-form text is sensitive by default.
- Do not persist or emit raw request/response/conversation text unless explicit opt-in policy exists.
- Prefer structured, sanitized metadata for diagnostics/auditability.

## Sensitive Field Set (baseline)
Use this as the minimum denylist in regressions:
- `request_text`
- `response_text`
- `conversation_text`
- `raw_input`
- `raw_output`
- `prompt`
- `completion`
- Nested equivalents with similar semantics

## Regression Case Template

### Case ID
`SAN-<story>-<nn>`

### Boundary
`cli_output | telemetry_event | session_snapshot | persistence_record | runtime_error`

### Given
- A flow that processes sensitive raw text in input or intermediate runtime context.

### When
- The flow reaches the target boundary and emits output/telemetry/persistence artifact.

### Then
- No raw sensitive field from the baseline set appears in emitted/persisted data.
- Any nested structures are recursively sanitized.
- Remaining payload preserves deterministic structured fields required for diagnostics.

### Assertions
- [ ] Raw text keys absent at top level.
- [ ] Raw text keys absent in nested objects/arrays.
- [ ] Correlation fields remain present and valid.
- [ ] Structured runtime status/error envelope remains valid.
- [ ] Command/conversation parity preserved where applicable.

### Evidence
- Test name:
- Fixture/input summary:
- Expected sanitized payload excerpt:
- Actual payload excerpt:
- Result: `pass | fail`

## Required Regression Set for MVP-03

### 1) CLI Output Sanitization
- Validate that user-facing command output does not include raw request/response/conversation text by default.
- Include success and runtime-error paths.

### 2) Telemetry Payload Sanitization
- Validate structured events exclude raw text fields at all applicable boundaries.
- Include conversational path telemetry with nested summaries.

### 3) Session Snapshot Sanitization
- Validate session snapshot/context artifacts exclude raw text fields before persistence/emission.
- Include nested context objects and mixed-type collections.

### 4) Persistence Record Sanitization
- Validate persisted execution history records contain required structured metadata but not sensitive raw text.
- Cover command/workflow and conversational extensions as implemented.

### 5) Runtime Error Envelope Sanitization
- Validate runtime error payload remains structured and correlation-complete without leaking raw text.
- Cover both command and conversation boundary errors.

## Suggested Test Naming Pattern
- `test_<module>_sanitizes_raw_text_<boundary>_<scenario>()`
- `test_<module>_sanitization_recursive_<scenario>()`
- `test_<module>_sanitization_parity_command_conversation_<scenario>()`

## Review Gate (Must pass before story close)
- [ ] All required regression categories implemented for touched boundaries.
- [ ] At least one recursive sanitization test included.
- [ ] At least one parity test included when command/conversation overlap exists.
- [ ] Failing regression proves leakage would be caught.
