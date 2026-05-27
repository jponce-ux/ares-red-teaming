# Research: Ollama Local Provider for ENDI CLI

## Decision: Support Unqualified Ollama Provider Selection

Users may select `--provider ollama --model llama3.2` instead of requiring a vendor-qualified identifier such as `ollama:llama3.2`.

**Rationale**: The ticket's example uses `--provider ollama --model gemma4:e2b`. ENDI already has a model flag, so accepting an unqualified provider name makes the CLI predictable and avoids forcing the model into the provider identifier.

**Alternatives considered**:

- Require `--provider ollama:llama3.2`: already partly supported, but contradicts the requested example.
- Add only environment-based provider config: less explicit and weaker for reproducible red-team runs.

## Decision: Use Ollama `/api/chat` With `stream: false`

ENDI sends one non-streaming chat request to `/api/chat` for each prompt.

**Rationale**: The existing ENDI chat provider contract returns one complete response object. Non-streaming mode keeps output deterministic and simplifies CLI JSON results for future stress-test orchestration.

**Alternatives considered**:

- Streaming responses: useful later, but it changes output semantics and needs separate cancellation/progress behavior.
- `/api/generate`: less aligned with chat-style message history.

## Decision: Map Ollama Failures to Explicit Provider Codes

Connection failures, missing models, timeouts, and malformed responses use explicit `ProviderAdapterError.code` values.

**Rationale**: Future red-team and stress-test runners need stable categories to distinguish local infrastructure issues from model behavior.

**Alternatives considered**:

- Collapse all failures into `provider_failure`: simpler but loses the missing-model and timeout distinctions required by the ticket.

## Decision: Add `chat` as a CLI Alias

ENDI will expose `endi chat` with the same provider/model/base URL/timeout/output options as single-prompt submit behavior.

**Rationale**: The requested usage says `endi chat --provider ollama --model gemma4:e2b`. ENDI already has `submit`; the alias preserves existing behavior while supporting the requested command shape.

**Alternatives considered**:

- Rename `submit` to `chat`: breaking change for existing tests and users.
- Document `submit` only: fails the requested usage pattern.
