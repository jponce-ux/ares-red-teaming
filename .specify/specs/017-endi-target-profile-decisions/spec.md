# Feature Specification: ENDI Target Profile and ARES MVP Decisions

**Feature Branch**: `[017-endi-target-profile-decisions]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: BA/PM decision record for ARES MVP target, severity rubric, evaluator criteria, mitigation ownership, manual deliverables, implementation order, Rust layout, and ARES-to-ENDI integration contract.
**Project Scope**: Cross-project decision artifact: ARES owns attack automation/evidence/report/replay; ENDI is the official target chatbot and owns target behavior changes.
**Implementation Boundary**: Spec artifacts live under `.specify/specs/017-endi-target-profile-decisions/`. ARES implementation remains Rust under the root Cargo workspace. ENDI target behavior changes remain under `endi/`.
**TDD Requirement**: Implementation for this feature MUST use test-driven development. For every new behavior, bug fix, or behavior-changing modification, add or update a failing unit test first, run the targeted test to record the expected failure, implement the smallest production change required to pass, then refactor only after the targeted test is green. Acceptance criteria are not complete until tests are traceable to the requirement they verify.

## User Scenarios & Testing

### User Story 1 - Define Official ENDI Target (Priority: P1)

As the ARES team, we can implement attacks against one official target profile instead of guessing ENDI's intended role and rules.

**Independent Test**: Review the target profile and verify it names the target, role/domain, provider/model/base URL, required behavior rules, allowed examples, and disallowed examples.

**Acceptance Scenarios**:

1. **Given** ARES attack fixtures are authored, **When** a fixture references a target rule, **Then** the rule ID exists in the ENDI target profile.
2. **Given** ENDI is run as the MVP target, **When** ARES invokes it, **Then** the target configuration is provider `ollama`, model `granite4.1:3b`, and base URL `http://localhost:11434`.

### User Story 2 - Classify Results Consistently (Priority: P1)

As a reviewer, I can interpret ARES results using shared run statuses and a severity rubric.

**Independent Test**: Verify evaluator/report specs can reference result statuses and severity definitions without inventing their own criteria.

**Acceptance Scenarios**:

1. **Given** an attack response clearly violates a target rule, **When** the evaluator classifies it, **Then** it can return `success` and assign Critical/High/Medium/Low severity according to the rubric.
2. **Given** ENDI or Ollama times out, **When** ARES records the result, **Then** it uses `target_error` or `harness_error` and severity `N/A`.

### User Story 3 - Establish MVP Mitigation Ownership (Priority: P2)

As the project team, we can prove risk reduction by applying one real target-side mitigation and replaying relevant attacks.

**Independent Test**: Verify the mitigation plan assigns ENDI ownership for target policy enforcement and ARES ownership for replay evidence.

**Acceptance Scenarios**:

1. **Given** baseline attacks find a vulnerability, **When** MVP mitigation is applied, **Then** ENDI has an explicit target policy/system prompt in the chat path.
2. **Given** the mitigation is applied, **When** ARES replays relevant attacks, **Then** the report shows closed, partially reduced, unchanged, or regressed status.

### Edge Cases

- ENDI has no visible system prompt before mitigation.
- ENDI answers outside the declared developer/Ops support domain.
- Ollama is unavailable, the model is missing, or a request times out.
- A response partially hints at hidden policy without full disclosure.
- A prompt asks for destructive commands or fake secrets.

## Requirements

### Functional Requirements

- **FR-001**: ENDI MUST be treated as the official MVP target chatbot named "ENDI Support Assistant".
- **FR-002**: ENDI's allowed domain MUST be local developer/Ops support for ENDI CLI, ARES CLI, Rust/Cargo basics, Python/virtualenv/uv setup, Ollama local setup, WSL2 troubleshooting, local test execution, and safe explanation of logs/errors/command output.
- **FR-003**: MVP target configuration MUST use provider `ollama`, model `granite4.1:3b`, and base URL `http://localhost:11434`.
- **FR-004**: ARES MUST execute ENDI through the CLI interface only and MUST NOT import ENDI Python code.
- **FR-005**: Target profile artifacts MUST define the required rule IDs R1 through R5.
- **FR-006**: ARES evaluator/reporting MUST use result statuses `blocked`, `success`, `partial`, `inconclusive`, `target_error`, and `harness_error`.
- **FR-007**: Severity MUST be Critical, High, Medium, Low, or N/A, and execution failures/timeouts MUST be tracked as status, not vulnerability severity.
- **FR-008**: MVP mitigation MUST be a target-side ENDI policy/system prompt enforcement change, not report-only guidance.
- **FR-008a**: The concrete ENDI target policy/system prompt mitigation MUST be specified by `.specify/specs/018-endi-target-policy-mitigation/`.
- **FR-009**: Manual attack documentation MUST include real ENDI responses.
- **FR-010**: Reflection checkpoints MUST be separate from the manual attack table.
- **FR-011**: The Rust layout MUST be a root Cargo workspace with `ares/` as the first binary crate and ENDI excluded from the workspace.
- **FR-012**: ARES-to-ENDI integration MUST capture attack ID, category, prompt, command, stdout, stderr, exit code, started time, duration, timeout, parsed ENDI output, evaluation decision, severity, and evidence.

### Key Entities

- **ENDI Support Assistant**: Official MVP target chatbot.
- **Target Rule**: R1-R5 behavior rule under test.
- **Result Status**: Evaluation status separate from severity.
- **Severity Rubric**: Critical/High/Medium/Low/N/A definitions.
- **Target Policy Mitigation**: ENDI-side system prompt or policy injected before the user message.
- **ARES-to-ENDI Contract**: Subprocess JSON-output interface.

## Success Criteria

- **SC-001**: Target profile artifact defines ENDI role/domain, provider/model/base URL, R1-R5, allowed examples, and disallowed examples.
- **SC-002**: Severity and result-status rubrics are available for evaluator, report, and replay specs.
- **SC-003**: Mitigation ownership is explicit: ENDI changes target behavior; ARES proves replay evidence.
- **SC-004**: Manual attack and reflection deliverable formats are specified.
- **SC-005**: Root Cargo workspace decision is specified for all ARES Rust work.

## Assumptions

- ENDI starts intentionally baseline-vulnerable enough for learning.
- Granite Guardian is future optional work, not MVP.
- Deterministic conservative evaluation is the MVP default.
