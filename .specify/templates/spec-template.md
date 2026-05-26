# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`

**Created**: [DATE]

**Status**: Draft

**Input**: User description: "$ARGUMENTS"

**Project Scope**: [ARES root Rust project / ENDI auxiliary Python project / cross-project integration or NEEDS CLARIFICATION]

**Implementation Boundary**: [For ARES, use root Rust workspace paths. For ENDI, use only paths under `endi/`. Spec artifacts remain under root `.specify/specs/`.]

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?
- How does the chatbot respond to attempts to reveal or transform its system prompt?
- How does the evaluator handle ambiguous responses or partial policy violations?
- How are simulated malicious-code or exfiltration scenarios constrained safely?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]
- **FR-RT-001**: Chatbot target MUST define a system prompt, a support role or documented alternate domain, guardrails where available, and at least three verifiable behavior rules.
- **FR-RT-002**: Red teaming artifacts MUST document at least five manual attacks across distinct categories before automation is considered complete.
- **FR-RT-003**: Redteam CLI MUST execute attack definitions from a machine-readable file and preserve prompt, response, category, target rule, and result evidence.
- **FR-RT-004**: Attack suite MUST include at least three categories with three to five variants each for MVP scope: prompt injection, jailbreak or role manipulation, and system prompt extraction.
- **FR-RT-005**: System MUST evaluate attack success using a documented LLM-as-judge method, deterministic heuristics, or both.
- **FR-RT-006**: System MUST generate a Markdown or HTML vulnerability report with summary, category findings, severity, successful prompts, and mitigation suggestions.
- **FR-RT-007**: Team MUST apply at least one mitigation and re-run relevant attacks to verify closed, reduced, or open status.
- **FR-RT-008**: Team MUST record reflection checkpoints for manual and automated phases, including how AI tools helped or caused problems.
- **FR-RS-001**: First-party executable code MUST be implemented in Rust using Cargo workspace conventions.
- **FR-RS-002**: Async or concurrent attack execution MUST use Tokio with bounded concurrency, timeouts, cancellation, and retry behavior.
- **FR-RS-003**: Rust modules MUST use strong domain types for attacks, target rules, evaluator decisions, severities, and mitigation replay status.
- **FR-RS-004**: Error handling MUST use `Result`, `thiserror` for library/domain errors, and `anyhow` at CLI or application boundaries.
- **FR-RS-005**: Execution evidence, provider calls, evaluator decisions, and report generation MUST use `tracing` spans/events with secret redaction.
- **FR-RS-006**: Code changes MUST be compatible with `cargo fmt`, `cargo clippy`, and `cargo test` quality gates.
- **FR-BD-001**: Feature scope MUST explicitly identify whether implementation targets ARES, ENDI, or cross-project integration.
- **FR-BD-002**: ENDI-targeted implementation MUST keep source, tests, docs, environment files, package metadata, and generated Python artifacts under `endi/`.
- **FR-BD-003**: Spec Kit artifacts MUST remain under root `.specify/specs/` regardless of whether the implementation target is ARES or ENDI.
- **FR-BD-004**: ARES-targeted implementation MUST default to Rust/Cargo/Tokio conventions unless the specification explicitly declares a bounded non-Rust artifact.

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]
- **Target Rule**: Verifiable chatbot behavior constraint, including rule text, refusal criteria, and examples of allowed and disallowed responses.
- **Attack Case**: Reproducible attack prompt or template with category, variants, expected violation, and target rule under test.
- **Attack Result**: Execution record containing attack prompt, chatbot response, evaluator decision, severity, evidence, and rationale.
- **Mitigation**: Prompt, guardrail, routing, filtering, or evaluator change linked to observed vulnerability evidence and replay result.
- **Rust Crate**: Cargo workspace member with a single clear responsibility, public API boundary, dependency set, and test strategy.
- **Async Attack Run**: Bounded Tokio execution unit that captures concurrency limits, timeouts, retry policy, cancellation path, and correlation identifier.
- **Project Scope**: The ownership boundary for a feature: ARES root Rust project, ENDI auxiliary Python project, or explicit cross-project integration.
- **ENDI Artifact**: Any implementation file, Python package file, local environment file, documentation, test, or generated artifact owned by the auxiliary ENDI project under `endi/`.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]
- **SC-RT-001**: At least five manual attacks are documented with category, prompt, response, success/failure, and severity.
- **SC-RT-002**: Automated suite runs at least three attack categories with three to five variants per category from repeatable fixtures.
- **SC-RT-003**: Every successful automated attack includes retained evidence and a severity assignment in the generated report.
- **SC-RT-004**: At least one mitigation is replayed against the relevant attack set and reported as closed, reduced, or still open.
- **SC-RT-005**: Show-and-tell can demonstrate the chatbot target, a successful attack, the generated report, and one mitigation replay.
- **SC-RS-001**: Rust quality gates pass for changed crates: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features`, and `cargo test --workspace`.
- **SC-RS-002**: Concurrent red teaming features include stress or async validation that demonstrates bounded resource use and predictable failure handling.
- **SC-BD-001**: No ENDI-targeted implementation files are created outside `endi/`.
- **SC-BD-002**: Root `.specify/specs/` contains the spec artifacts for the feature, including ENDI-targeted features.

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- [Assumption about target users, e.g., "Users have stable internet connectivity"]
- [Assumption about scope boundaries, e.g., "Mobile support is out of scope for v1"]
- [Assumption about data/environment, e.g., "Existing authentication system will be reused"]
- [Dependency on existing system/service, e.g., "Requires access to the existing user profile API"]
