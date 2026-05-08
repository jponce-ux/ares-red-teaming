# Story POST-01.3: Plugin Command Discoverability Parity

## Metadata


- **Story ID:** `POST-01.3`

- **Epic:** `EPIC-POST-01` Plugin Ecosystem and Compatibility Controls

- **Priority:** `P2`

- **Suggested Sprint:** `Sprint 5`

- **Type:** `Plugin UX`

## User Story

As an operator, I want plugin commands to appear in standard help/introspection output, so that extension features remain discoverable.

## Traceability


- **Functional Requirements:** `FR-008`, `FR-009`

- **Architecture Constraints:** `ADR-005`, `ADR-002`

## Scope

### In Scope


- Plugin command entries in standard help output.

- Plugin command entries in introspection output with examples and execution target.

- Consistent validation error schema for plugin and core commands.

- Clean startup-boundary removal when plugin is absent/disabled.

### Out of Scope


- Dynamic runtime plugin enable/disable without restart.

- External docs generation pipeline.

## Acceptance Criteria

1. Plugin commands are listed in help/introspection outputs with examples.
2. Plugin command validation errors follow same schema and UX quality as core commands.
3. Disabling/removing a plugin removes its commands at startup boundary.
4. Discoverability outputs clearly indicate plugin source/ownership metadata.

## Implementation Notes


- Keep command metadata shape identical for core and plugin commands.

- Prevent help/introspection drift by rendering from unified command registry.

- Include plugin provenance field for operator transparency.

## Tasks


- [ ] Extend command registry metadata to include plugin provenance.

- [ ] Ensure help/introspection renderers include plugin commands uniformly.

- [ ] Reuse core command validation/error formatting for plugin commands.

- [ ] Implement startup reconciliation for removed/disabled plugins.

- [ ] Add UX parity tests for help, introspection, and error flows.

## Testing Notes (ADR-011)


- **Gate Level:** `Light`

- Integration tests for plugin command visibility in help/introspection.

- Regression tests for validation error parity.

- Startup tests for plugin disable/remove reconciliation.

## Dependencies


- Plugin registration pipeline.

- Shared command metadata and help/introspection renderers.

## Definition of Done


- All acceptance criteria pass.

- Light plugin gate checks pass.

- Plugin commands are discoverable and behaviorally consistent with core commands.
