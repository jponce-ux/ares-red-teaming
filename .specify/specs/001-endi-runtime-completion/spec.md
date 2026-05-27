# Feature Specification: ENDI Runtime Completion

**Feature Branch**: `001-endi-runtime-completion`

**Created**: 2026-05-26

**Status**: Active - TDD required before implementation resumes

**Input**: User description: "create the spec-driven artifacts in root .specify/specs folder then implement them, you'll find all the information of the missing work here endi/MISSING_IMPLEMENTATION.md"

**Project Scope**: ENDI auxiliary Python project

**Implementation Boundary**: Implementation MUST stay under `endi/`. Spec artifacts remain under root `.specify/specs/`.

**TDD Requirement**: Implementation for this active ENDI feature MUST use test-driven development. For every new behavior, bug fix, or behavior-changing modification, add or update a failing pytest unit test first, run the targeted test to record the expected failure, implement the smallest production change required to pass, then refactor only after the targeted test is green. Acceptance criteria are not complete until tests are traceable to the requirement they verify.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Provider-Backed Chat (Priority: P1)

As an ENDI CLI user, I want free-text input to call a configured chat provider,
so that ENDI behaves like an AI assistant instead of echoing placeholder text.

**Why this priority**: This closes the largest product gap: free-text chat is
currently not connected to an AI provider.

**Independent Test**: Run `endi submit "hello"` with a fake configured provider
and verify the response comes from the provider adapter, not from a placeholder.

**Acceptance Scenarios**:

1. **Given** an OpenAI-compatible chat configuration and credentials, **When** a
   user submits free text, **Then** ENDI sends ordered chat messages to the
   provider and prints the provider response.
2. **Given** explicit local fallback is enabled and the primary provider fails
   for an allowed reason, **When** a chat request is submitted, **Then** ENDI
   calls the Ollama fallback provider and records fallback metadata.
3. **Given** no provider credentials or local fallback are available, **When** a
   user submits free text, **Then** ENDI returns a structured error without
   leaking secrets.

---

### User Story 2 - Safe Tool Execution (Priority: P1)

As an ENDI operator, I want filesystem and shell tools to be registered with
capability checks, so that bounded conversations and commands can use local
tools safely.

**Why this priority**: BMAD marks tool contracts complete, but no real shell or
filesystem tool category exists.

**Independent Test**: Invoke registered filesystem and shell tools through the
tool registry with allow/deny capability sets and verify side effects occur
only when authorized.

**Acceptance Scenarios**:

1. **Given** `filesystem.read` is granted, **When** ENDI reads an allowed file,
   **Then** the tool returns file content with structured metadata.
2. **Given** `filesystem.write` is missing, **When** ENDI attempts to write a
   file, **Then** the write is denied before side effects.
3. **Given** `shell.exec` is granted and timeout is configured, **When** ENDI
   runs a command, **Then** stdout, stderr, exit code, and timeout status are
   returned in a structured payload.

---

### User Story 3 - Operator CLI Controls (Priority: P2)

As an ENDI CLI user, I want interactive shell mode, JSON output, approve-plan,
and non-interactive flags, so that ENDI can be used interactively and by
automation.

**Why this priority**: Existing routing supports much of this internally, but
the CLI does not expose the controls.

**Independent Test**: Exercise CLI commands with `--output json`,
`--approve-plan`, `--non-interactive`, and interactive shell quit behavior.

**Acceptance Scenarios**:

1. **Given** `--output json`, **When** a command or conversation completes,
   **Then** ENDI emits machine-readable JSON instead of Rich panels.
2. **Given** approve-plan context flags, **When** a sensitive command is
   submitted non-interactively, **Then** ENDI passes the approval context into
   dispatch.
3. **Given** interactive shell mode, **When** the user enters `/help` then
   `/exit`, **Then** ENDI processes help and exits cleanly.

---

### User Story 4 - Extensibility and Diagnostics Baseline (Priority: P3)

As an ENDI maintainer, I want plugin discovery and JSON logs, so that ENDI can
grow through extensions and runtime behavior can be audited.

**Why this priority**: These are planned BMAD gaps needed before ENDI can be
treated as a complete CLI assistant foundation.

**Independent Test**: Load a fixture plugin manifest and verify valid commands
appear in discovery, invalid manifests produce diagnostics, and execution logs
are written as JSON lines.

**Acceptance Scenarios**:

1. **Given** a local plugin manifest, **When** ENDI loads plugins, **Then** valid
   plugin command metadata is added to discoverability output.
2. **Given** an invalid plugin manifest, **When** ENDI loads plugins, **Then**
   the plugin is rejected with structured diagnostics.
3. **Given** a log path, **When** ENDI dispatches input, **Then** ENDI writes a
   JSON log event with route, status, and correlation fields.

### Edge Cases

- Provider credentials are absent, empty, or malformed.
- Provider returns malformed JSON or an unexpected schema.
- Ollama is unavailable while fallback is enabled.
- File paths escape the configured project root.
- Shell command times out or exits non-zero.
- Interactive input receives EOF or `/exit`.
- Plugin manifest contains duplicate command names.
- JSON output must not include provider secrets or sensitive context values.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-ENDI-001**: ENDI MUST replace placeholder free-text conversation behavior with provider-backed chat execution.
- **FR-ENDI-002**: ENDI MUST include concrete chat adapters for OpenAI-compatible APIs, Anthropic-compatible APIs, and Ollama local chat.
- **FR-ENDI-003**: ENDI MUST preserve explicit-only local fallback behavior for Ollama; fallback MUST only run when enabled by user/config and the failure reason is allowed.
- **FR-ENDI-004**: ENDI MUST expose safe filesystem read/write tools through the existing `ToolRegistry` contract.
- **FR-ENDI-005**: ENDI MUST expose a safe shell execution tool through the existing `ToolRegistry` contract with timeout handling.
- **FR-ENDI-006**: ENDI MUST enforce tool capability checks before filesystem or shell side effects.
- **FR-ENDI-007**: ENDI MUST expose CLI controls for JSON output, approve-plan context, non-interactive execution, provider selection, local fallback, and interactive shell mode.
- **FR-ENDI-008**: ENDI MUST produce structured JSON output when requested without Rich formatting.
- **FR-ENDI-009**: ENDI MUST write structured JSON log events when a log path is configured.
- **FR-ENDI-010**: ENDI MUST discover plugin manifests from a configured local directory and include valid plugin commands in help/introspection.
- **FR-ENDI-011**: ENDI MUST keep all implementation files, tests, docs, and generated Python artifacts under `endi/`.
- **FR-ENDI-012**: ENDI MUST keep Spec Kit artifacts for this feature under root `.specify/specs/001-endi-runtime-completion/`.

### Key Entities *(include if feature involves data)*

- **Chat Provider Config**: Provider identifier, model, base URL, environment
  variable for credentials, timeout, and fallback settings.
- **Chat Adapter Result**: Provider name, response text, metadata, and
  structured error details on failure.
- **Tool Contract**: Existing ENDI tool metadata, schema, capability, handler,
  and deterministic result envelope.
- **Plugin Manifest**: JSON manifest describing plugin name, version, commands,
  examples, argument schema, and execution target.
- **JSON Log Event**: Timestamp, route, status, input type, correlation fields,
  provider/fallback metadata when present, and sanitized error details.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-ENDI-001**: Free-text submit returns a fake provider response in tests and no longer returns `[conversation] ...`.
- **SC-ENDI-002**: Provider adapter tests cover OpenAI-compatible, Anthropic-compatible, Ollama, malformed response, and missing credential cases.
- **SC-ENDI-003**: Tool tests prove missing capabilities block filesystem write and shell execution before side effects.
- **SC-ENDI-004**: CLI tests prove JSON output parses as JSON and includes route/status/output fields.
- **SC-ENDI-005**: Plugin tests prove one valid manifest command appears in discoverability and one invalid manifest is rejected.
- **SC-ENDI-006**: ENDI validation gates pass from `endi/`: pytest, ruff, and mypy.

## Assumptions

- ENDI remains a Python project inside `endi/`.
- Network-backed provider tests use fakes/mocks and do not require real cloud
  credentials.
- Real provider credentials are read from environment variables only.
- Plugin command execution can remain metadata-only for this feature; command
  execution may still require a separately implemented plugin runtime.
- Post-MVP graph and multi-agent templates can be documented as backlog unless
  needed for provider-backed chat completion.
