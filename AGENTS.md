# AGENTS.md

AGENTS.md is the single source of truth for how work is done. Other agent files point to it.

## PRINCIPLES (earlier wins when they conflict)

1. YAGNI: only build what the current task needs.
2. Fail fast: validate inputs, raise clear errors, never fail silently.
3. Simple first: optimise only after measuring a real problem.
4. DRY: extract a pattern on the third copy, or on the second if the copies must change together.
5. Delete aggressively, within scope: remove dead code, unused params, and stale files the
   task touches. Outside the task's scope, flag them and ask before deleting.
6. Semantic naming: long, descriptive names. Booleans read as questions (is_x, has_y).
7. Tracer: every major directory has a README.md with Purpose, Contents, How it connects,
   and Conventions (only if any). Read the README instead of scanning the whole directory.
   `.githooks/pre-commit` blocks commits when a tracked, non-hidden directory up to three
   levels deep is missing one. Enable it once per clone: `git config core.hooksPath .githooks`.
   When a change adds, removes, or repurposes files, update that directory's README.
8. Vertical stack: for every implementation, follow the change through every layer of the
   stack (e.g. UI, API, services, data, infrastructure, tests, docs). Don't change every
   layer. Instead, list which layers are affected and give the developer the next tasks
   needed to finish the change through the whole stack.

## ARCHITECTURE

Full layer responsibilities live in `docs/architecture.md`; update that file, not this one,
when the architecture changes.

Layers (requests flow left to right, dependencies point the same way):

**Frontend → FastAPI Routes → Services → Repositories → JSON persistence**

Backend (`backend/app/`):
- `routes/`: HTTP only. Parse the request, call one service, return the response and status
  code. Translate domain errors into HTTP errors here. No business logic, no file access.
- `services/`: business rules, validation, calculations, state transitions. Raise domain
  errors (e.g. `MenuItemNotFoundError`), never `HTTPException`. Never touch files directly.
- `repositories/`: the only layer that reads or writes `data/`. Hides the file format from
  services.
- `models/`: Pydantic request, response, and domain models shared across layers.
- `data/`: JSON files. Paths are configurable (`config.py`, e.g. `RESTAURANT_TRIAL_PATH`)
  so tests use their own temporary files.
- `main.py` (repo root): app setup, middleware, and router registration only.

Frontend (`frontend/src/`):
- `api/`: the only place that calls `fetch` or the backend.
- `pages/`: top-level views. `components/`: reusable UI. `layouts/`: shared page layout.
- `hooks/`: React stateful logic. `lib/`: plain data-in, data-out functions.
- `routes/`: URL-to-page routing. `types/`: TypeScript types that mirror backend models.

Code rules:
- A layer calls only the layer directly below it. Routes never call repositories; components
  never call `fetch`.
- Known exception: `MenuService` uses `RestaurantRepository` to check a restaurant exists.
  New cross-feature access goes through the other feature's service, not its repository.
- Every behaviour change ships with tests in `backend/tests/` (pytest) or the frontend
  (vitest).
- Frontend `types/` change together with the backend models they mirror.

- Warn the developer explicitly when a change goes against this architecture or breaks
  a code rule, even if the change works. Say what rule it breaks and what the compliant
  option would be.

## CHECKS

Run these before every summary and report the results:
- Lint: `.venv/bin/ruff check .` and `.venv/bin/ruff format --check .` (config: `ruff.toml`).
  The repo has existing violations; report new ones in the files the change touches and
  don't fix unrelated files unless asked.
- Backend tests: `.venv/bin/pytest backend/tests`
- Frontend tests: `cd frontend && npm test`

## AGENT RULES

- Read the nearest README.md before editing.
- Stay scoped to the task.
- Ask before adding dependencies, top-level directories, or new patterns.
- Propose changes to AGENTS.md instead of silently breaking a rule.
- The agent never changes git history or remotes: no commit, branch, switch, merge, rebase,
  reset, stash, tag, delete, push, or opening/merging PRs. Read-only commands (`git fetch`,
  `status`, `log`, `diff`, `rev-list`, `merge-base`, `range-diff`, `gh pr view`,
  `gh pr list`) are fine.
- Every git and GitHub step in the flows below is run by the developer. See COMMAND HANDOFF.
- Agents are never contributors. Commit messages, squash messages, and PR descriptions the
  agent drafts contain no `Co-Authored-By` trailers, no "Generated with" lines, and no agent
  names or emails. Never set the git author or committer to an agent. AI use is disclosed
  in `docs/PROVENANCE.md` and the PR description instead, not in git metadata.
- Provenance: before handing off a PR, remind the developer to record AI use. If no entry
  covers this work yet, append a skeleton to `docs/PROVENANCE.md` with the next entry number
  and every value left blank for the developer to fill in:

  ```markdown
  ### Entry <next number>

  - Student(s):
  - Artifact:
  - Label: <!-- AI-GENERATED | AI-ASSISTED | AI-REVISED | NO-AI -->
  - AI tool:
  - Purpose:
  - Influence:
  - Validation:
  - PR:
  ```

## COMMAND HANDOFF

When a git or GitHub step is needed, the agent hands the developer the commands instead of
running them:
- Give the exact commands in order, in one copy-pasteable block per step, with real branch
  names and hashes filled in (no placeholders left).
- Before each step, explain in plain words what it does and why it is needed at this point.
- Say what output to expect and what a bad result looks like (e.g. a conflict, a rejected push).
- Wait for the developer to report back before giving the next step. Check the result with
  read-only commands before moving on.
- If something goes wrong, give the recovery command (e.g. `git rebase --abort`,
  `git reset --hard <recorded-hash>`) and explain what it restores.

## STARTUP (at the start of every session)

1. Ask the developer whether the current branch is an epic or a task, and for a task, which
   epic branch it belongs to. Branch names don't encode this. Remember the answer for the
   session.
2. Run `git fetch --prune`. Always compare against the remote refs (`origin/...`), never the
   local copies of `main` or the epic, which may be stale.
3. The parent is `origin/<epic-branch>` for a task and `origin/main` for an epic.
4. Check how far behind the branch is: `git rev-list --count HEAD..<parent>`.
5. Check whether the parent was rewritten (e.g. the epic was rebased onto main):
   - `fork_point=$(git merge-base --fork-point <parent> HEAD)`
   - If `git merge-base --is-ancestor "$fork_point" <parent>` fails, the commits the branch
     was built on are gone from the parent. The branch needs
     `git rebase --onto <parent> "$fork_point"`, not a plain rebase.
   - `--fork-point` uses the remote-tracking reflog, so it only works if this clone fetched
     the parent before it was rewritten. If it returns nothing, say so and ask the developer
     for the old parent head.
6. Tell the developer the result if the branch is behind. Flag it as critical when:
   - the parent's new commits touch the same files this branch changes
     (compare `git diff --name-only HEAD...<parent>` with `git diff --name-only <parent>...HEAD`),
   - they change the architecture, shared interfaces, dependencies, or config, or
   - the branch is far enough behind that a later merge or rebase is likely to conflict.
7. If updating makes sense, recommend a rebase onto the parent's latest head and hand off the
   commands (COMMAND HANDOFF, rebase safety).
8. If the branch is only slightly behind and no files overlap, mention it in one line and carry on.

## GIT FLOW

Branches: `main` (stable), one epic branch per epic issue, and task branches off an epic.
Every merge happens on GitHub through a pull request, so peer review and CI run.
- Task → epic: PR into the epic, merged with **Squash and merge**.
- Epic → main: rebase the epic onto `origin/main` first, then PR into `main`, merged with
  **Rebase and merge**.
- Nobody pushes directly to main. main is never rebased and never force-pushed.
- CI (`.github/workflows/`) only runs on PRs into `main`. For task → epic PRs, run CHECKS
  locally and say so in the summary.

Rebase safety (applies to every rebase):
- Rebase only when the developer says yes.
- Before: git fetch, clean tree, and record both the old base (`git merge-base HEAD <parent>`)
  and the old head (`git rev-parse HEAD`). The old head is the recovery point:
  `git reset --hard <old-head>`.
- During: if a conflict is not obvious, stop and ask. git rebase --abort restores the branch.
- After: check `git range-diff <old-base>..<old-head> <new-base>..HEAD` to confirm the commits
  still contain the same changes, then run CHECKS.
- Push a rebased branch only with git push --force-with-lease --force-if-includes.
  Never use a plain --force.

Task → epic (squash merge on GitHub):
1. Bring the branch up to date: rebase it onto `origin/<epic>` (rebase safety above) and push.
2. Check: clean tree, CHECKS pass, `origin/<epic>` is an ancestor of the branch.
3. Remind the developer about provenance (AGENT RULES).
4. Give the summary (SUMMARIES) and wait for the developer's yes.
5. Hand off `gh pr create --base <epic> --head <branch>` with the drafted title and body.
   The developer merges it on GitHub with **Squash and merge** after review.
6. Delete the branch only when the developer allows it. Check first that the PR is merged
   (`gh pr view <number> --json state`).

Epic → main (rebase, then rebase-merge on GitHub):
1. Check: the architecture is intact (no violations of the ARCHITECTURE section) and CHECKS
   pass on the epic.
2. Check: no open task branches or PRs off the epic still hold work the developer needs
   (`gh pr list --base <epic>`).
3. Give the summary and wait for the developer's yes. List the open branches off this epic,
   because rebasing the epic rewrites their base.
4. Rebase the epic onto `origin/main` (rebase safety above), run CHECKS again, and push with
   --force-with-lease --force-if-includes.
5. Remind the developer about provenance, then hand off `gh pr create --base main --head <epic>`.
   The developer merges it on GitHub with **Rebase and merge** after review and CI pass.
   If GitHub reports the branch is out of date, main has moved: repeat step 4.
6. Rebase and merge gives the commits new hashes on main. Tell the developer how to move each
   remaining branch off the old epic: `git rebase --onto origin/main <old-epic-head> <branch>`.

If any check fails, stop and ask.

## SUMMARIES (before every PR and every rebase)

Follow `.github/pull_request_template.md` so the summary can be pasted as the PR body:
- Title, and `closes #<issue>` when the PR closes one.
- PR Type: Epic, User Story, Maintenance, or Refactor.
- What Changed: plain words, grouped by area, with the files changed.
- How to Test and Expected Outputs.

Then, for the developer (not part of the PR body unless they want it):
- The commits involved.
- Potential issues: architecture or code-rule violations, breaking changes, new dependencies,
  deleted files, migrations or config changes, untested layers of the vertical stack.
- CHECKS results.
