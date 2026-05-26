# Project Context

## Execution Environment

- This project lives in the WSL filesystem and development commands must run in WSL, not in the Windows PowerShell Python environment.
- For Python tooling (`pytest`, `ruff`, `mypy`, CLI checks), always use the project's virtual environment located in this project folder inside WSL.
- Git commands related to this project should also be executed inside WSL to ensure repository path and ownership handling remain consistent.
- Never run Python tooling with system Python in PowerShell.
- Never run Python tooling with non-venv Python in WSL.

## Agent Command Rules

- For BMAD workflows (including `dev-story`, `code-review`, and similar agents), testing/tooling commands are mandatory in WSL + project venv.
- Agent command execution policy: if the venv is not active, activate it first; do not run the command outside the venv.
- File-editing policy for agents: do not create new files with `apply_patch` using `*** Add File:` in this repo/tooling setup, because the patch parser may reject add-file headers.
- For new files, use the dedicated file creation tool (`write_to_file`) and reserve `apply_patch` for edits to existing files.
- If command execution fails due to missing modules, treat that as a venv activation/context error first.
- When invoking WSL from IDE automation, prefer a Windows-local working directory (for example, `C:\`) and execute commands through:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && <command>"`
- Avoid UNC-style IDE working directories for automated command execution (for example, `\\wsl.localhost\...`) because they can trigger shell/editor misparsing, long-running hangs, or malformed temporary filenames.
- Prefer sequential command execution for review/tooling steps over parallel shell invocations in this repo.
- For code review workflows, prefer direct file reads for scoped files first; use `git diff` only when explicit patch-level context is required.
- `git diff` is optional for review context and should be run only when a reviewer needs patch-level comparison; if file paths and current contents are already known, reviewers may skip it.
- When running Git inspection commands in IDE/agent automation (`git diff`, `git log`, `git show`, and similar), disable paging to avoid non-interactive terminal blocking.
- Preferred patterns for this repo: `git --no-pager <command>` or `GIT_PAGER=cat git <command>`.

## Verification Expectations

- Test/lint/type/tooling commands must run in WSL + project venv only.
- Environment errors must be treated as setup-context issues before code issues.
