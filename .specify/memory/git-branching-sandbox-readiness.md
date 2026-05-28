# Git Branching Sandbox Readiness

## Problem Observed

During the batch Spec Kit implementation on 2026-05-27, `speckit-git-feature`
was invoked with an exact branch name:

```bash
GIT_BRANCH_NAME=001-endi-runtime-completion \
  .specify/extensions/git/scripts/bash/create-new-feature.sh \
  --json \
  --allow-existing-branch \
  --short-name endi-runtime \
  "Implement ENDI runtime completion"
```

It failed with:

```text
fatal: Unable to create '/home/jponce/ai_labs_mvd/ares-red-teaming/.git/index.lock': Read-only file system
```

This means the Codex session could edit workspace files but could not write Git
metadata under `.git/`. With approval policy set to `never`, Codex cannot
request escalation, so branch creation cannot be fixed from inside that
session.

## Required Behavior

If the user requests one branch per feature, Codex must stop before
implementation when Git metadata is read-only. Continuing in the working tree
does not satisfy the requested workflow.

## Preflight Check

Before a multi-feature Spec Kit implementation, run:

```bash
git rev-parse --is-inside-work-tree
git status --short --branch
GIT_BRANCH_NAME=sandbox-git-write-check \
  .specify/extensions/git/scripts/bash/create-new-feature.sh \
  --json \
  --allow-existing-branch \
  --short-name git-write-check \
  "Check git write access"
```

If this succeeds, switch back to the intended base branch and delete the
temporary branch before starting:

```bash
git switch main
git branch -D sandbox-git-write-check
```

If it fails with `.git/index.lock` or read-only filesystem errors, restart
Codex with repository Git metadata write access before implementation.

## Feature Branch Naming

For existing Spec Kit folders, use the folder name as the exact branch name:

```bash
GIT_BRANCH_NAME=010-attack-runner-concurrency \
  .specify/extensions/git/scripts/bash/create-new-feature.sh \
  --json \
  --allow-existing-branch \
  --short-name attack-runner \
  "Implement attack runner concurrency"
```

This avoids generating new `019+` branch numbers for already-created specs.
