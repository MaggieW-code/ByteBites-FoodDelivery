---
name: audit-security
description: Audit ByteBites for security leaks - committed secrets and API keys, vulnerable or unused dependencies, API endpoints that expose too much or lack protection, and risky automation (git hooks, Claude Code settings and skills, GitHub Actions). Use when asked for a security check, before a milestone or release, or when adding a dependency, endpoint, or workflow. For React hooks and webhooks, use audit-hooks. Read-only; reports findings, never changes code.
argument-hint: "[secrets|deps|api|automation] (default: all)"
---

# Security audit

Scope: `$ARGUMENTS` (empty means all four parts). Read-only: report, don't fix.
Load context README-first (`AGENTS.md` AGENT RULES).

**Never print a secret.** Show the file, line, and kind of secret, masked
(`sk_live_****9f2a`).

## 1. Secrets and keys

- Industry standard: **gitleaks** (`gitleaks detect --no-banner --redact` scans the whole
  history; `gitleaks protect --staged` checks staged files). Use it if installed; if not,
  say so and ask before installing.
- Fallback: search tracked files (`git grep -nIE`) for private keys (`-----BEGIN .*PRIVATE KEY`),
  cloud and API key shapes (`AKIA[0-9A-Z]{16}`, `sk_(live|test)_`, `ghp_`, `xox[bp]-`),
  assignments like `(api_key|secret|password|token)\s*[:=]\s*['"][^'"]{8,}`, and `.env`
  files. Also check history: `git log --all -p -S '<pattern>'` for anything found.
- Check `.gitignore` covers `.env*`, local settings, and key files.
- If a real secret was ever committed: it is leaked even after deletion. The fix order is
  **rotate the key first**, then remove it from the code; rewriting history is the
  developer's call (`AGENTS.md` forbids agents changing history).

## 2. Dependencies

- Python: **pip-audit** (`pip-audit -r requirements.txt`) for known vulnerabilities. If not
  installed, say so and ask before installing.
- Frontend: `npm audit --omit=dev` in `frontend/` (built in), then `npm audit` for dev tools.
- Unused dependencies: a package in `requirements.txt` or `package.json` that nothing
  imports (`git grep`). Unused code is still attack surface.
- Unpinned or very loose versions, and packages with install scripts added in this change.

## 3. API endpoints (OWASP API Security Top 10)

Read `backend/app/routes/README.md`, then each route file and `main.py`. For every endpoint:
- **Exposure:** does the response return more fields than the client needs? Do error
  responses leak internals (stack traces, file paths, raw validation dumps shown to users)?
- **Authorization:** do write endpoints (`POST`, `PATCH`, `DELETE`) and any per-user data
  check who is calling? List the unprotected ones (expected until the Auth epic lands, but
  report them).
- **Object access:** can a caller read or change another user's record by changing an ID?
- **Input:** path parameters and bodies validated; sizes bounded (`max_length`).
- **CORS:** `allow_origins` is an explicit list, never `*` with credentials.
- **Docs and debug:** `/docs` and `/openapi.json` exposure is a deliberate choice; no debug
  or test routes registered in `main.py`.
- Frontend: no keys or secrets in `frontend/src` (everything there ships to the browser).

## 4. Automation (git hooks, Claude Code, CI)

- **Git hooks** (`.githooks/`): run only local, readable commands; no network calls or
  downloads.
- **Claude Code** (`.claude/`): skills' `allowed-tools` grant only what they need;
  `settings.json` permissions aren't broader than needed; no hooks that run downloaded code.
  `settings.local.json` is ignored by git.
- **GitHub Actions** (`.github/workflows/`): least-privilege `permissions:`; no secrets
  echoed to logs; no `pull_request_target` checking out PR code; third-party actions
  pinned to a version (ideally a commit SHA).

## Report

```
## Security audit (<scope>)

| Severity | Area | Where | Finding | Fix (fix or proposal) |
|---|---|---|---|---|
| critical / high / medium / low | secrets / deps / api / automation | path:line | ... | ... |

Tools run: gitleaks yes/no, pip-audit yes/no, npm audit yes/no. Not checked: ...
```

Critical means a live secret or a remotely exploitable hole: tell the developer at the top,
before anything else.
