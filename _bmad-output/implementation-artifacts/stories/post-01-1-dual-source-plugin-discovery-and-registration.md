# Story POST-01.1: Dual-source Plugin Discovery and Registration

## Metadata


- **Story ID:** `POST-01.1`

- **Epic:** `EPIC-POST-01` Plugin Ecosystem and Compatibility Controls

- **Priority:** `P2`

- **Suggested Sprint:** `Sprint 5`

- **Type:** `Plugin Extension`

## User Story

As a platform extender, I want local manifest and package entry-point plugin discovery, so that I can add capabilities without core edits.

## Traceability


- **Functional Requirements:** `FR-008`

- **Architecture Constraints:** `ADR-005`, `ADR-013`

## Scope

### In Scope


- Discovery from `~/.endi/plugins` local manifest source.

- Discovery from package entry points (`endi.plugins`).

- Unified plugin registration contract for commands/workflows/agents/tools.

- Explicit diagnostics for invalid plugin manifests/registrations.

### Out of Scope


- Signed plugin trust model.

- Hot-reload of plugins during active runtime.

## Acceptance Criteria

1. Startup loader discovers plugins from local manifest path and package entry points.
2. Valid plugins register commands/workflows/agents/tools through unified contract only.
3. Invalid plugin definitions are rejected with explicit structured diagnostics.
4. New plugin capabilities are loaded without core runtime module edits.

## Implementation Notes


- Keep discovery and validation stages separated for clearer diagnostics.

- Normalize plugin metadata before registration to avoid source-specific behavior drift.

- Preserve clear startup summary of loaded/rejected plugins.

## Tasks


- [ ] Implement local manifest plugin discovery adapter.

- [ ] Implement package entry-point discovery adapter.

- [ ] Implement unified plugin normalization and registration flow.

- [ ] Implement explicit rejection diagnostics.

- [ ] Add startup integration tests for mixed plugin sets.

## Testing Notes (ADR-011)


- **Gate Level:** `Light` (plugin path), with targeted strict checks on core registration interfaces.

- Plugin smoke tests for local and package sources.

- Negative tests for malformed manifests and contract violations.

- Startup tests ensuring no core edits required for net-new plugin command.

## Dependencies


- Core registries and contract validators.

- Capability/version metadata model.

## Definition of Done


- All acceptance criteria pass.

- Light plugin gate checks pass plus core contract checks.

- Discovery behavior is deterministic and clearly diagnosable.
