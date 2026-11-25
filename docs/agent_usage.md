# Using AI agents in ByteBites

How to get good, safe results from AI coding agents (Claude Code, Codex, Copilot, Cursor)
in this repo. The rules agents follow live in [`AGENTS.md`](../AGENTS.md); this page is for
people.

## What's set up

| Piece | Where | What it does |
|---|---|---|
| Rules | `AGENTS.md` (Claude Code reads it through `CLAUDE.md`) | Architecture, checks, git flow, what agents may and may not do |
| Folder READMEs | Every major folder | Purpose, contents, connections, conventions. Agents read these before code, so they need far less context |
| Skills | `.claude/skills/` | Step-by-step procedures you can call by name (below) |
| README hook | `.githooks/pre-commit` | Blocks a commit when a folder is missing its README. Enable once per clone: `git config core.hooksPath .githooks` |

**Agents never commit, push, or open PRs.** They hand you the exact commands with an
explanation, and you run them. That keeps you in control of the git history and means every
commit is yours.

## How agents load context (and why READMEs matter)

An agent reads, in order: `AGENTS.md` → the README of each folder the task touches → only
the source files it needs. A README costs a few hundred tokens; scanning a folder can cost
tens of thousands. Better READMEs mean faster, cheaper, more accurate agents, and they help
people the same way.

When you add, remove, or repurpose files, update that folder's README in the same PR.

## Skills

Type `/` in Claude Code to see them. Arguments in `[ ]` are optional.

| Skill | Use it to | Example |
|---|---|---|
| `/review-pr [number]` | Review a PR against `AGENTS.md` and run the checks | `/review-pr 131` |
| `/lint [--fix]` | Lint only what your branch changed and explain each rule | `/lint`, then `/lint --fix` |
| `/study <topic>` | Learn a concept bottom-up, with this repo's code as the example | `/study dependency injection` |
| `/fix-finding <issue>` | Fix one bug: failing test first, minimal fix, docs, PR summary | `/fix-finding #123` |
| `/audit-security [part]` | Check for leaked keys, vulnerable dependencies, leaky endpoints, risky CI and git hooks | `/audit-security api` |
| `/audit-hooks [react\|webhooks]` | Check React hooks for leaks and stale data, and webhooks for missing signature checks | `/audit-hooks react` |

Claude can also pick `review-pr`, `lint`, `study`, `audit-security`, and `audit-hooks` on its own when your
request matches. `fix-finding` only runs when you type it.

## Working effectively

1. **Start each session by answering the startup question.** The agent asks whether your
   branch is an epic or a task, then checks how far behind it is. Answer it; it prevents
   painful rebases later.
2. **One task per request, with a clear finish line.** "Fix #123 so `POST
   /restaurants/x/menu` returns 404" beats "clean up the menu code".
3. **Point at files and issues.** Paths, issue numbers, and error messages save the agent
   from searching.
4. **Ask for a plan first on anything big.** "Plan how to add customer registration across
   the stack; don't edit yet." Review the plan, then let it build.
5. **Read every diff before you accept it.** You must be able to explain every line you
   submit (course AI policy). If you can't, ask `/study` or reject the change.
6. **Let the checks decide.** The agent runs lint and tests before every summary. A
   summary without check results isn't done.
7. **Fix or proposal?** Agents label each change. A fix has evidence (a failing test, a
   broken rule, dead code). A proposal is a choice and needs team agreement first.
8. **Disclose AI use.** Add an entry to `docs/PROVENANCE.md` and mention it in the PR
   description. Never put agent names or `Co-Authored-By` lines in commits.

## What you can ask for (examples)

**Understand code**
- "Explain how a menu request flows from the frontend to `menus.json`."
- "What does `backend/app/services/README.md` say I need to change to add a field?"
- `/study why we raise domain errors instead of HTTPException`

**Build a feature (vertical slice)**
- "Plan the Customer Accounts register story through every layer: model, repository,
  service, route, tests, API client, types, page. List the files first."
- "Write the pytest tests for `CustomerService.register` before the implementation."

**Fix and test**
- `/fix-finding #123`
- "This test fails only on Windows: <paste output>. Find the cause."
- "Add tests for the empty and error states of the Discover page."

**Review and ship**
- `/lint`, then `/review-pr` on your own branch before asking a teammate.
- "Draft the PR description from the template for this branch."
- "My rebase hit a conflict in `menu_service.py`: <paste>. Walk me through it."

**Security**
- `/audit-security` before each milestone, and `/audit-security deps` after adding a package.
- `/audit-hooks react` after adding a `useEffect` or custom hook; `/audit-hooks webhooks`
  when adding an endpoint that receives webhooks.

## Things to avoid

- Pasting secrets, API keys, or `.env` contents into a prompt.
- Accepting changes outside the task ("while I was there I also refactored…"). Ask the
  agent to split them out.
- Installing community skills or tools without reading them first. A skill can run
  commands; treat it like a new dependency.
- Long sessions that drift across many tasks. Start a fresh session per task; the READMEs
  and `AGENTS.md` give the new session its context.

## Windows notes

- Virtual environment executables are in `.venv\Scripts\` (not `.venv/bin/`).
- Git hooks run through Git for Windows' bundled shell, so `.githooks/pre-commit` works in
  Git Bash, PowerShell, and VS Code.
- Skills live in `.claude/skills/` as plain files (no symlinks), so they work on every clone.

## Other agents

Skills are an open format (`SKILL.md`, see agentskills.io), but each tool reads its own
folder. Claude Code reads `.claude/skills/`. Codex reads `.agents/skills/`. If a teammate
uses another tool, they can still follow `AGENTS.md` and the READMEs, and can open a skill
file and paste its steps into a prompt.
