# ENDI Terminal UX Mini-Spec (MVP)

## Purpose
Define a terminal-native UX baseline for ENDI MVP so story implementation is consistent, testable, and operator-safe.

## Scope
- In scope: CLI and interactive shell output rendered in terminal using `Rich`.
- Out of scope: GUI, web dashboard, desktop app, mobile app.

## Design Principles
1. Safety-first clarity for high-impact actions.
2. Fast scanning under pressure (incident/debug contexts).
3. Consistent output grammar across command, workflow, and agent paths.
4. Accessibility in color and low-color terminals.

## Output Pattern Baseline
### 1) Result Panel
Required fields:
- `status` (success|partial|failed)
- `operation`
- `summary`
- `next_step` (optional)

### 2) Warning Panel
Required fields:
- `warning_code`
- `impact`
- `recommended_action`

### 3) Error Panel
Required fields:
- `error_code`
- `component` (command|workflow|step|agent|tool)
- `message`
- `correlation_id`

### 4) Confirmation Summary Panel (sensitive operations)
Required fields:
- `intent`
- `targets`
- `capabilities`
- `backend`
- `risk_level`
- `execution_id`

Behavior:
- Render before any sensitive action executes.
- Require explicit user confirmation in per-action mode.
- Persist a stable summary hash/identifier in audit linkage.

## Visual Conventions
- Success, warning, error, and confirmation states must use distinct icons/labels plus color.
- Distinguishability cannot depend on color alone.
- Keep headline line length concise to reduce wrapping in 80-120 column terminals.

## Terminal Compatibility Matrix (MVP)
Implementation and tests must cover at least:
1. Dark theme, 256-color terminal profile
2. Light theme profile
3. Low-color profile

For each profile verify:
- warning/error/confirmation states are distinguishable without color
- confirmation summary fields are complete and consistently ordered
- severe errors include correlation ID and component

## Story Linkage
- `MVP-05.1`: readability/theming baseline and snapshot matrix
- `MVP-05.2`: help/introspection output consistency
- `MVP-05.3`: confirmation summary normalization and audit linkage

## CI Guidance
- Treat presentation/readability checks as moderate-gate UX checks.
- Treat confirmation UX contract checks as strict-gate safety checks.
