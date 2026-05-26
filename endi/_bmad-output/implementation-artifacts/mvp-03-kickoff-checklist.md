# MVP-03 Kickoff Checklist

Source: `_bmad-output/implementation-artifacts/epic-mvp-02-retro-2026-03-19.md`
Purpose: Convert retrospective action items into immediately executable prep work for `epic-mvp-03`.

## Supporting Artifacts (Risk-Reduction Prep)

- FR-007 compliance matrix: `_bmad-output/implementation-artifacts/mvp-03-fr-007-compliance-matrix.md`
- Sensitive-data sanitization regression template: `_bmad-output/implementation-artifacts/mvp-03-sensitive-data-sanitization-regression-template.md`
- Status consistency preflight checklist: `_bmad-output/implementation-artifacts/status-consistency-preflight-checklist.md`
- MVP-03.1 create-story checklist snippet: `_bmad-output/implementation-artifacts/mvp-03-1-create-story-checklist-snippet.md`

## Execution Checklist

- [ ] **High** — Add epic-closeout preflight consistency gate
  - Owner: Scrum Master / Project Lead
  - First concrete task: Add a required pre-closeout check that blocks epic closure when parent epic status does not match child story completion state in `sprint-status.yaml`.
  - Done when: Epic closeout cannot proceed unless epic/story status consistency passes.

- [ ] **High** — Enforce policy-to-execution alignment test requirement
  - Owner: Architect + Lead Developer
  - First concrete task: Add a story-template checklist item requiring at least one regression test that proves exposed policy metadata matches actual runtime behavior.
  - Done when: MVP-03 story implementation/review notes include explicit policy-to-execution alignment evidence.

- [ ] **High** — Add sensitive-data sanitization regression template
  - Owner: Lead Developer + QA
  - First concrete task: Define reusable regression cases for CLI output, telemetry payloads, and session snapshots validating raw-text exclusion and recursive sanitization.
  - Done when: MVP-03 stories touching observability/persistence include sanitization regressions at all externally observable boundaries.

- [ ] **Medium** — Add review checklist item for metadata vs execution parity
  - Owner: Code Review Lead
  - First concrete task: Extend review checklist with a mandatory verification that reported contract fields are consistent with actual execution-path behavior.
  - Done when: Every MVP-03 runtime/security review includes an explicit parity assertion outcome.

- [ ] **Medium** — Define FR-007 compliance matrix
  - Owner: Architect + QA
  - First concrete task: Create a compact matrix mapping each FR-007 boundary to expected deterministic envelope fields, correlation linkage, and redaction expectations.
  - Done when: Matrix is referenced by MVP-03 observability/persistence stories and used during review.

- [ ] **Medium** — Add pre-snapshot status consistency validation step
  - Owner: Project Lead
  - First concrete task: Introduce a short validation pass before sprint/epic status snapshots to catch parent/child drift.
  - Done when: Status snapshots include evidence that consistency validation was executed.

## MVP-03 Readiness Gate (Before first story starts)

- [ ] `epic-mvp-02` and `epic-mvp-02-retrospective` remain `done` in `_bmad-output/implementation-artifacts/sprint-status.yaml`
- [ ] Owners acknowledge checklist items and execution order
- [ ] FR-007 compliance matrix exists and is reviewable: `_bmad-output/implementation-artifacts/mvp-03-fr-007-compliance-matrix.md`
- [ ] Sanitization regression template is available for MVP-03 stories: `_bmad-output/implementation-artifacts/mvp-03-sensitive-data-sanitization-regression-template.md`
- [ ] Status consistency preflight checklist is available for status updates: `_bmad-output/implementation-artifacts/status-consistency-preflight-checklist.md`
- [ ] MVP-03.1 create-story checklist snippet is ready for handoff: `_bmad-output/implementation-artifacts/mvp-03-1-create-story-checklist-snippet.md`
- [ ] First MVP-03 story is selected and moved according to normal workflow
- [ ] `epic-mvp-03` only transitions from `backlog` when actual story implementation begins

## Kickoff Continuity Record (2026-03-19)

### Owner Acknowledgment

- [ ] Scrum Master / Project Lead acknowledged kickoff continuity items and sequence
- [ ] Architect acknowledged kickoff continuity items and sequence
- [ ] Lead Developer acknowledged kickoff continuity items and sequence
- [ ] QA acknowledged kickoff continuity items and sequence
- [ ] Code Review Lead acknowledged kickoff continuity items and sequence

### First Story Selection

- Selected first MVP-03 story: `mvp-03-1-sqlite-execution-history-schema-and-write-path`
- Rationale: establishes the persistence substrate required by subsequent observability/correlation/retention stories (`FR-007`, `FR-002`).

### Go-Forward Sequence (Do not start implementation in step 1-2)

1. Kickoff continuity pass complete and owner acknowledgments captured.
2. Confirm FR-007 compliance matrix, sanitization regression template, and `mvp-03-1` create-story snippet are ready for use.
3. Run `create-story` for `mvp-03-1-sqlite-execution-history-schema-and-write-path`.
4. Run `dev-story` to begin implementation; only then allow `epic-mvp-03` transition out of `backlog`.
