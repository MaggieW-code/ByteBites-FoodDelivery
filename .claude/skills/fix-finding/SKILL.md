---
name: fix-finding
description: Fix one bug or finding end to end the ByteBites way - confirm it's a fix (not a proposal), reproduce it with a failing test, make the minimal change, update READMEs, run CHECKS, and hand off the PR summary and git commands. Use when asked to fix a specific bug, issue, or finding.
argument-hint: "<issue-number or description>"
disable-model-invocation: true
---

# Fix one finding

Finding: `$ARGUMENTS`

Follow `AGENTS.md` throughout. One finding per PR.

## 1. Confirm it's a fix

- Restate the problem in one sentence with `path:line`.
- Apply the objectivity test (`AGENTS.md` AGENT RULES). If the only reason is taste or
  "industry standard", it's a **proposal**: stop and say it needs team agreement first.
- If it touches more than one feature, propose splitting it.

## 2. Branch (developer runs it)

- Run STARTUP if it hasn't run this session (parent branch, how far behind).
- Hand off the branch command per COMMAND HANDOFF, e.g.
  `git switch -c <name>/fix/<short-name> origin/<parent>`. Wait for the developer.

## 3. Reproduce first

- Read the README of every folder involved.
- Write the smallest test that shows the bug, in the right layer's test file.
- Run it and show that it **fails for the reason described**. A test that passes before the
  fix proves nothing; rewrite it.

## 4. Minimal fix

- Change only what the finding needs. No drive-by refactors; list anything else you notice
  as a separate follow-up.
- Re-run the new test (passes) and CHECKS (no new failures, no new lint violations).

## 5. Vertical stack and docs

- List every layer the change affects (UI, API, services, data, tests, docs) and either
  change it or give the developer the follow-up tasks.
- Remove the matching "Not yet true" bullet from the folder README; update
  `docs/architecture.md` if a layer rule changed.
- Provenance: if AI was used, add the skeleton entry per AGENT RULES.

## 6. Hand off

- Summary per SUMMARIES, using `.github/pull_request_template.md`: title with the issue or
  finding number, `closes #<issue>`, PR type, What Changed, How to Test (the failing-then-
  passing test), Expected Outputs, and the line "Fix: <objective evidence>".
- Suggest the reviewer: the person who knows this code best (`git log --format=%an -- <file>`),
  asked as the expert.
- Give the commit, push, and `gh pr create` commands per COMMAND HANDOFF, then wait.
