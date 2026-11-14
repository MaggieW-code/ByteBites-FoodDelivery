---
name: lint
description: Run the ByteBites linters and formatters (ruff for Python; frontend linters and type checks once configured) and report only new violations in the files the current branch changes, with an explanation of each rule. Use when asked to lint, check formatting, or see whether code is ready for review. Fixes only when asked.
argument-hint: "[--fix]"
---

# Lint the current change

Arguments: `$ARGUMENTS`

The repo has existing violations. Report and fix only what this branch touches (`AGENTS.md`
CHECKS). Config: `ruff.toml`.

Don't read source files to lint them; the tools do that. Open a file only to explain or fix
a reported line.

## 1. Find the files this change touches

- Parent branch per `AGENTS.md` STARTUP (default `origin/main`).
- Changed files: `git diff --name-only <parent>...HEAD` plus uncommitted ones from
  `git status --short`. Skip deleted files.

## 2. Run the tools on those files only

Use the virtual environment's executables: `.venv/bin/` on Linux and macOS,
`.venv\Scripts\` on Windows.

- Python (`*.py`): `ruff check <files>` and `ruff format --check <files>`.
- Frontend: run `npm run lint` and `npm run typecheck` in `frontend/` only if `package.json`
  defines them. If it doesn't, say "frontend lint and type checks are not configured yet".

## 3. Report

For each file: rule code, `line`, message. Then explain each distinct rule once, in one or
two lines: what it catches and why it matters. `ruff rule <CODE>` prints the official
explanation. Separate:
- **New:** lines this branch added or changed (`git diff <parent>...HEAD -- <file>`).
- **Existing:** already on the parent. Mention the count only; don't fix them.

## 4. Fix (only with `--fix` or the developer's yes)

- `ruff check --fix <files>` and `ruff format <files>`, on the changed files only.
- Never use `--unsafe-fixes` without asking.
- Show `git diff --stat` afterwards and re-run step 2.
- Anything not auto-fixable: propose the edit and wait.
