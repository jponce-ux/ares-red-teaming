# Status Consistency Preflight Checklist

Purpose: Prevent parent/child status drift before sprint snapshots and epic closeout updates in `_bmad-output/implementation-artifacts/sprint-status.yaml`.

Source:
- `_bmad-output/implementation-artifacts/epic-mvp-02-retro-2026-03-19.md`
- `_bmad-output/implementation-artifacts/mvp-03-kickoff-checklist.md`

## When to Run
- Before posting a sprint status snapshot.
- Before transitioning any `epic-*` status.
- Before marking any `epic-*-retrospective` status as `done`.

## Preflight Steps

### 1) Confirm target scope
- [ ] Target epic key identified (example: `epic-mvp-03`).
- [ ] All child story keys for the epic listed from `development_status`.
- [ ] Retrospective key identified (example: `epic-mvp-03-retrospective`).

### 2) Validate parent/child consistency
- [ ] If all child stories are `done`, parent epic is `done` (or is being transitioned in this same update).
- [ ] If any child story is not `done`, parent epic is not marked `done`.
- [ ] Parent status is never moved to a state that contradicts child story states.

### 3) Validate retrospective consistency
- [ ] Retrospective status is `done` only when retrospective artifact exists.
- [ ] Retrospective key update does not modify unrelated epic/story statuses.
- [ ] Retrospective completion aligns with workflow convention (`optional -> done` when completed).

### 4) Validate update integrity
- [ ] `last_updated` is refreshed once for the same edit.
- [ ] Unrelated statuses remain unchanged.
- [ ] Existing comments/header metadata are preserved.

### 5) Evidence capture
- [ ] Record updated keys and previous -> new values.
- [ ] Record artifact path(s) that justify status transitions.
- [ ] Include a short note if any deliberate exception was applied.

## Quick Decision Table

| Condition | Required status outcome |
|---|---|
| All stories in epic are `done` | Epic may be `done` |
| Any story in epic is not `done` | Epic must not be `done` |
| Retrospective artifact not present | `epic-*-retrospective` must not be `done` |
| Retrospective artifact present and approved | `epic-*-retrospective` may be `done` |

## Usage Note
Run this checklist as a mandatory preflight step in story/review/retro workflows that update `sprint-status.yaml`.
