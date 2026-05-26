# MVP-02 Kickoff Checklist

Source: `_bmad-output/implementation-artifacts/epic-mvp-01-retro-2026-03-18.md`
Purpose: Convert retrospective action items into immediately executable prep work for `epic-mvp-02`.

## Execution Checklist

- [ ] **High** — Add epic closeout checklist to workflow
  - Owner: Scrum Master / Process Owner
  - First concrete task: Add a reusable closeout section to the retrospective/epic flow that requires updating `epic-*` and `epic-*-retrospective` statuses in `sprint-status.yaml`.
  - Done when: New epic closeout checklist exists and is used in next epic closure.

- [ ] **High** — Add contract parity checklist for shared runtime behavior
  - Owner: Architect + Lead Developer
  - First concrete task: Create a one-page parity checklist covering command/conversation behavior for validation, status mapping, and structured error fields.
  - Done when: Checklist is referenced in MVP-02 story implementation/review notes.

- [ ] **Medium** — Enforce WSL pre-flight execution guidance
  - Owner: Lead Developer
  - First concrete task: Add a pre-flight section to team working agreements describing required WSL `.venv` command pattern and sequential execution expectations.
  - Done when: Guidance is documented and used before starting MVP-02 story work.

- [ ] **Medium** — Add retrospective continuity review at epic start
  - Owner: Scrum Master
  - First concrete task: Add a kickoff ritual item to classify prior retro actions as `completed`, `in-progress`, or `not-addressed`.
  - Done when: MVP-02 kickoff notes include continuity status for prior epic actions.

- [ ] **High** — Add status consistency verification before reporting snapshots
  - Owner: Project Lead
  - First concrete task: Define a pre-report check that compares each epic status with all child story statuses to catch mismatches.
  - Done when: Pre-report check is run before the next sprint/epic status update.

## MVP-02 Readiness Gate (Before first story starts)

- [ ] `epic-mvp-01` and `epic-mvp-01-retrospective` remain `done` in `_bmad-output/implementation-artifacts/sprint-status.yaml`
- [ ] Owners acknowledge checklist items and execution order
- [ ] First MVP-02 story is selected and moved according to normal workflow
- [ ] `epic-mvp-02` only transitions from `backlog` when actual story implementation begins

## Kickoff Continuity Record (2026-03-19)

### Owner Acknowledgment

- [ ] Scrum Master / Process Owner acknowledged kickoff continuity items and sequence
- [ ] Architect acknowledged kickoff continuity items and sequence
- [ ] Lead Developer acknowledged kickoff continuity items and sequence
- [ ] Project Lead acknowledged kickoff continuity items and sequence

### First Story Selection

- Selected first MVP-02 story: `mvp-02-1-capability-authorization-enforcement-layer`
- Rationale: foundational dependency for capability enforcement and confirmation flows (`FR-005`, `FR-010`)

### Go-Forward Sequence (Do not start implementation in step 1-2)

1. Kickoff continuity pass complete and owner acknowledgments captured.
2. Run `create-story` for `mvp-02-1-capability-authorization-enforcement-layer`.
3. Run `dev-story` to begin implementation; only then allow `epic-mvp-02` transition out of `backlog`.
