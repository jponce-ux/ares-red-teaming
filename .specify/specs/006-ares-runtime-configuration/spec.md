# Feature Specification: ARES Configuration and Runtime Settings

**Feature Branch**: `[006-ares-runtime-configuration]`
**Created**: 2026-05-27
**Status**: Draft
**Input**: `tickets/ares_tickets/04_add_ares_configuration_and_runtime_settings.md`
**Project Scope**: ARES root Rust project
**Implementation Boundary**: Rust configuration code and safe examples in ARES paths only.

## User Scenarios & Testing

### User Story 1 - Load Repeatable Runtime Config (Priority: P1)

As a red-team operator, I can load ARES runtime settings from a config file so attack runs are repeatable.

**Independent Test**: Load a safe example config and verify ENDI command, working directory, fixture path, report path, timeout, concurrency, and evidence settings are resolved.

**Acceptance Scenarios**:

1. **Given** a valid config file, **When** ARES starts a run, **Then** ARES loads typed runtime settings.
2. **Given** no explicit config is passed, **When** a documented default config exists, **Then** ARES can load it predictably.

### User Story 2 - Override Config From CLI (Priority: P2)

As a red-team operator, I can override config values from CLI flags for one run.

**Independent Test**: Load config plus CLI override inputs and verify override precedence.

**Acceptance Scenarios**:

1. **Given** config defines timeout and concurrency, **When** CLI flags override them, **Then** the effective runtime settings use CLI values.
2. **Given** invalid timeout or concurrency is supplied, **When** ARES validates settings, **Then** ARES fails before execution with a clear error.

### Edge Cases

- Missing config file.
- Malformed config file.
- Invalid paths.
- Zero timeout or zero concurrency.
- Evidence retention disabled.
- Example config accidentally includes secrets.

## Requirements

### Functional Requirements

- **FR-001**: ARES MUST support a config file for runtime settings.
- **FR-002**: ARES MUST support CLI flags overriding config values.
- **FR-003**: Config MUST include ENDI command/path settings.
- **FR-004**: Config MUST include ENDI working directory settings.
- **FR-005**: Config MUST include attack fixture path.
- **FR-006**: Config MUST include report output path.
- **FR-007**: Config MUST include per-attack timeout.
- **FR-008**: Config MUST include max concurrency.
- **FR-009**: Config MUST include evidence retention behavior.
- **FR-010**: ARES MUST validate config before execution.
- **FR-011**: Safe example config MUST NOT include credentials or secrets.

### Key Entities

- **AresConfig**: Full runtime configuration.
- **EndiCommandConfig**: ENDI executable/path and working directory.
- **RuntimeLimits**: Timeout and max concurrency.
- **EvidenceConfig**: Evidence retention behavior.
- **EffectiveConfig**: Config after CLI override resolution.

## Success Criteria

- **SC-001**: ARES loads a documented safe config file.
- **SC-002**: CLI overrides take precedence over file config in tests.
- **SC-003**: Invalid config fails before attack execution with clear errors.
- **SC-004**: Safe example config contains no secrets.

## Assumptions

- TOML is preferred for human-editable local config unless implementation chooses another serde-supported format.
