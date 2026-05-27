# Feature Specification: Ollama Local Provider for ENDI CLI

**Feature Branch**: `[002-ollama-local-provider]`

**Created**: 2026-05-26

**Status**: Completed - historical artifact

**Input**: User description: "Add Ollama Local Model Connection to Endi CLI"

**Project Scope**: ENDI auxiliary Python project

**Implementation Boundary**: Implementation files, tests, docs, package metadata, virtual environments, caches, and generated artifacts for this feature stay under `endi/`. Spec Kit artifacts stay under root `.specify/specs/`.

**TDD Status Decision**: Historical completed spec. All tasks in `tasks.md` are checked off, including tests and validation, so this artifact is not retrofitted into the active TDD workflow. Future changes to Ollama provider behavior MUST be created as a new active TDD spec or an explicit amendment with failing tests first.

## Clarifications

### Session 2026-05-26

- Q: What should happen after a user selects an Ollama provider/model with `endi chat` and later runs `endi submit` without provider flags? -> A: ENDI remembers the last explicitly selected chat provider settings and reuses them for later chat/submit invocations until the user changes them.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chat With Local Ollama Model (Priority: P1)

An ENDI user can choose Ollama as the chat provider, select a local model, send a prompt, and see the local model response in the CLI without using a cloud AI provider.

**Why this priority**: This is the baseline value: ENDI must be usable with locally hosted models for red-team and stress-test workflows.

**Independent Test**: Run one CLI command with provider `ollama`, a model name such as `llama3.2`, and a prompt while the Ollama server is reachable; verify ENDI prints the model response.

**Acceptance Scenarios**:

1. **Given** a local Ollama server is reachable and the selected model is available, **When** the user submits a prompt with provider `ollama` and model `llama3.2`, **Then** ENDI sends the prompt to the local server and prints the model response.
2. **Given** no base URL is supplied, **When** the user selects provider `ollama`, **Then** ENDI uses `http://localhost:11434` as the default Ollama base URL.
3. **Given** the user supplies an alternate local base URL, **When** the user submits a prompt, **Then** ENDI sends the request to the configured base URL.
4. **Given** the user previously selected provider `ollama` and model `granite4.1:3b`, **When** the user later runs `endi submit "test"` without provider flags, **Then** ENDI uses the remembered Ollama provider/model instead of falling back to OpenAI.

---

### User Story 2 - Safe Ollama Failure Handling (Priority: P2)

An ENDI user receives clear, non-crashing CLI feedback when Ollama is unreachable, the selected model is missing, the request times out, or the response is malformed.

**Why this priority**: Red-team and stress-test workflows need predictable failure behavior so provider issues are visible and do not corrupt run output.

**Independent Test**: Run ENDI against simulated Ollama failures and verify each failure produces a clear error result without a traceback or unhandled exception.

**Acceptance Scenarios**:

1. **Given** no Ollama server is listening at the configured base URL, **When** the user sends a prompt, **Then** ENDI reports a connection failure with provider context and exits or returns an error result safely.
2. **Given** Ollama reports that the selected model is unavailable, **When** the user sends a prompt, **Then** ENDI reports a missing model error that names the requested model.
3. **Given** the request exceeds the configured timeout, **When** the timeout is reached, **Then** ENDI reports a timeout error and does not wait indefinitely.
4. **Given** Ollama returns malformed or incomplete data, **When** ENDI parses the response, **Then** ENDI reports a malformed response error instead of printing misleading output.

---

### User Story 3 - Red-Team Ready Ollama CLI Contract (Priority: P3)

An ENDI user can rely on stable CLI flags and structured output for future red-team and stress-test orchestration against local Ollama models.

**Why this priority**: The ARES red-team workflow will need repeatable local model execution with predictable input, output, and error shapes.

**Independent Test**: Invoke ENDI with documented provider, model, base URL, timeout, and JSON-output options and verify the CLI contract is stable for success and failure paths.

**Acceptance Scenarios**:

1. **Given** a caller uses machine-readable output, **When** an Ollama prompt succeeds, **Then** ENDI returns a structured success result containing the response text and route information.
2. **Given** a caller uses machine-readable output, **When** an Ollama prompt fails, **Then** ENDI returns a structured error result that identifies the failure category.
3. **Given** a red-team runner will execute multiple prompts later, **When** ENDI handles one prompt, **Then** provider selection, model selection, timeout, and base URL inputs are explicit and repeatable.

### Edge Cases

- Ollama base URL is empty, malformed, or lacks a scheme.
- Model name includes a tag, such as `gemma4:e2b`, `llama3.2`, or `mistral`.
- Ollama is reachable but returns an HTTP error for a missing model.
- Ollama returns a response without message content.
- Ollama returns invalid JSON or a non-object response.
- Prompt text is long enough to exercise request construction without logging secrets or dumping excessive content.
- Request timeout is configured to a low value and must terminate predictably.
- A remembered provider/model exists and the user omits provider flags on a later invocation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: ENDI MUST allow users to select Ollama as the chat model provider.
- **FR-002**: ENDI MUST allow users to select a local Ollama model by name, including tagged names such as `gemma4:e2b`.
- **FR-003**: ENDI MUST default the Ollama base URL to `http://localhost:11434` when no base URL is provided.
- **FR-004**: ENDI MUST allow users to override the Ollama base URL per invocation.
- **FR-005**: ENDI MUST send user prompts to the selected local Ollama model and print the response text.
- **FR-006**: ENDI MUST handle Ollama connection failures without an unhandled exception or traceback.
- **FR-007**: ENDI MUST identify missing model failures separately from generic provider failures when Ollama returns enough information to do so.
- **FR-008**: ENDI MUST enforce configurable request timeout behavior for Ollama calls.
- **FR-009**: ENDI MUST handle malformed Ollama responses as explicit provider errors.
- **FR-010**: ENDI MUST support structured machine-readable output for Ollama success and failure results.
- **FR-011**: ENDI MUST keep provider configuration explicit and avoid tracked credentials or secrets for local Ollama use.
- **FR-012**: ENDI-targeted implementation MUST keep all source and test changes under `endi/`.
- **FR-013**: Spec Kit artifacts for this feature MUST remain under root `.specify/specs/`.
- **FR-014**: ENDI MUST remember the last explicitly selected chat provider, model, base URL, API key environment variable, and timeout settings for later `chat`, `submit`, and `shell` invocations that omit those options.
- **FR-015**: Explicit provider options on a new invocation MUST override remembered provider defaults and update the remembered defaults.

### Key Entities

- **Ollama Provider Selection**: User-facing provider choice that routes chat prompts to a local Ollama-compatible server.
- **Ollama Model Name**: Local model identifier, optionally including a tag, used to select the model for a prompt.
- **Ollama Base URL**: Local HTTP endpoint for the Ollama server; defaults to `http://localhost:11434` and can be overridden.
- **Remembered Chat Defaults**: Local ENDI runtime settings storing the last explicit chat provider selection for later invocations.
- **Prompt Request**: User prompt plus provider, model, base URL, and timeout configuration.
- **Provider Response**: Successful response text or structured provider error category with safe details.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can run one ENDI prompt against a reachable local Ollama model and see a model response in the CLI.
- **SC-002**: The default local Ollama URL is used automatically in 100% of Ollama invocations where no base URL is supplied.
- **SC-003**: Connection failure, missing model, timeout, and malformed response scenarios are each covered by automated tests.
- **SC-004**: Machine-readable output distinguishes success from provider error paths for Ollama invocations.
- **SC-005**: No implementation or test file for this ENDI feature is created outside `endi/`.
- **SC-006**: After running `endi chat --provider ollama --model granite4.1:3b "Hello"`, a later `endi submit "test"` uses the remembered Ollama model without requiring repeated provider flags.

## Assumptions

- The user's machine may or may not have Ollama running during automated tests, so tests use simulated HTTP responses rather than requiring a live model.
- ENDI already owns the Python CLI surface and provider adapter boundary under `endi/`.
- `endi chat --provider ollama --model <model>` may be implemented as a documented alias or equivalent CLI path if ENDI's existing command structure uses a different command name.
- Local Ollama does not require API credentials by default.
