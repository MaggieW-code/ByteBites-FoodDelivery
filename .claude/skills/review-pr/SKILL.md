---
name: review-pr
description: Review a ByteBites pull request against AGENTS.md (layer rules, tests, vertical stack, PR template, provenance, fix vs proposal) and run CHECKS on it. Use when asked to review a PR, check a PR before merging, or check whether a branch is ready for a PR. Takes a PR number; no argument means the current branch.
argument-hint: "[pr-number]"
---

# Review a PR

Target: `$ARGUMENTS` (empty means the current branch).

Rules come from `AGENTS.md`. Read its ARCHITECTURE, CHECKS, AGENT RULES, GIT FLOW, and
SUMMARIES sections before reviewing; this skill does not repeat them.

## 1. Gather (read-only)

- PR number given: `gh pr view <n> --json number,title,body,baseRefName,headRefName,author,files`
  and `gh pr diff <n>`. CI status: `gh pr checks <n>`.
- No number: `git fetch --prune`, find the parent (`AGENTS.md` STARTUP), then
  `git diff <parent>...HEAD` and `git log --oneline <parent>..HEAD`.
- Read the README of every folder the diff touches.

## 2. Run CHECKS on the PR's code

- Current branch: run CHECKS directly.
- Another PR: ask the developer first, then use a throwaway detached worktree (no branch is
  created): `git fetch origin pull/<n>/head`, `git worktree add --detach <temp-dir>/pr-<n> FETCH_HEAD`.
  Run CHECKS there, then always `git worktree remove --force <temp-dir>/pr-<n>`.
- A failure caused by a missing local dependency is an environment problem, not the PR's.
  Say which it is. Report only new lint violations in the files the PR touches.

## 3. Review

Work through [references/checklist.md](references/checklist.md). Every finding needs a
`file:line` and evidence. Prefer fewer, certain findings over many guesses.

## 4. Report

Use Conventional Comments labels so the author knows what blocks the merge:

```
## #<n> <title>  <head> → <base>

**Recommendation:** approve | approve with nits | changes requested   (the developer decides)

### Blocking
- **issue:** `path:line` What is wrong. Evidence. Suggested fix.

### Non-blocking
- **suggestion:** / **question:** / **nit:** `path:line` ...

### Praise
- **praise:** what the PR does well (at least one, when true).

### CHECKS
Lint (new violations only), backend tests, frontend tests, CI status.
```

- Talk about the code, never the person ("this route catches `ValueError`", not "you").
- A change labelled as a fix with no objective evidence is a `question:`, not an `issue:`.
- Don't post anything. If the developer wants it on GitHub, give them the comment text
  and the command (`gh pr review <n> --comment --body-file <file>`) per COMMAND HANDOFF.
  Never suggest `--approve` or `--request-changes`; the developer chooses.
