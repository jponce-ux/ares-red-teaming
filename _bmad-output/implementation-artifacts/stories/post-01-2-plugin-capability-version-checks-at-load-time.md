# Story POST-01.2: Plugin Capability Version Checks at Load Time

## Metadata


- **Story ID:** `POST-01.2`

- **Epic:** `EPIC-POST-01` Plugin Ecosystem and Compatibility Controls

- **Priority:** `P2`

- **Suggested Sprint:** `Sprint 5`

- **Type:** `Compatibility Enforcement`

## User Story

As a maintainer, I want compatibility checks before plugin activation, so that incompatible extensions fail safely.

## Traceability


- **Functional Requirements:** `FR-008`

- **Architecture Constraints:** `ADR-013`, `ADR-005`

## Scope

### In Scope


- Load-time checks for core SemVer compatibility.

- Capability contract version checks for plugin-provided features.

- Hard-fail behavior for incompatible plugins.

- Deprecation warning output with removal target version.

### Out of Scope


- Automatic plugin migration/refactoring.

- Online compatibility service checks.

## Acceptance Criteria

1. Plugin activation validates core SemVer and capability-version compatibility at load time.
2. Incompatible plugins fail fast before runtime activation.
3. Failure messages include actionable remediation guidance.
4. Deprecation warnings include replacement/removal target version metadata.

## Implementation Notes


- Keep compatibility evaluation deterministic and fully auditable in startup logs.

- Ensure capability version checks are decoupled from provider-specific logic.

- Emit explicit decision outputs for loaded vs rejected plugins.

## Tasks


- [ ] Implement compatibility evaluator for core and capability contracts.

- [ ] Implement hard-fail path and structured startup diagnostics.

- [ ] Implement deprecation-warning emission path.

- [ ] Add compatibility fixtures covering valid/invalid version matrices.

- [ ] Add tests for fail-fast and warning behavior.

## Testing Notes (ADR-011)


- **Gate Levels:** `Light` for plugin suite, with targeted `Strict` checks at core loader contract boundaries.

- Version matrix unit tests.

- Startup integration tests for mixed compatible/incompatible plugin sets.

- Regression tests for warning and hard-fail semantics.

## Dependencies


- Version metadata in plugin manifests/entry-point descriptors.

- Core loader registration pipeline.

## Definition of Done


- All acceptance criteria pass.

- Light+targeted strict gates pass for touched modules.

- Compatibility failures are deterministic and actionable.
