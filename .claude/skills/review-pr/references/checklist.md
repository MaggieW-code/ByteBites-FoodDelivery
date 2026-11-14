# PR review checklist

Based on `AGENTS.md` and Google's code review guide: approve a change that improves the
codebase, even if it isn't perfect. Block on correctness, rules, and missing tests, not taste.

## PR hygiene
- Title, PR type, and `closes #<issue>` follow `.github/pull_request_template.md`.
- What Changed, How to Test, and Expected Outputs are filled in.
- One concern per PR. Unrelated changes are a `suggestion:` to split.
- Base branch matches GIT FLOW (task → epic, epic → main). Branch is up to date with its parent
  (`git rev-list --count HEAD..<parent>` is 0).
- No `Co-Authored-By` trailers, "Generated with" lines, or agent names in commits or the body.
- AI use is disclosed: a matching `docs/PROVENANCE.md` entry exists.
- Each change is labelled a **fix** (with evidence) or a **proposal** (with team agreement).

## Architecture (`AGENTS.md` ARCHITECTURE)
- Routes: HTTP only, call one service, translate domain errors, no file access.
- Services: business rules, raise named domain errors, never `HTTPException`, no files.
- Repositories: the only code touching `data/`; no business rules.
- Models: imported by every layer, import none of them.
- Frontend: only `api/` calls `fetch`; components render; `types/` changes in the same PR as
  the backend model it mirrors.
- Cross-feature access goes through the other feature's service.
- Any rule broken: name the rule and the compliant option.

## Correctness
- Errors: caught as narrowly as possible (`except ValueError` around Pydantic is a bug).
  "Not found" raises, it doesn't return `None`.
- Status codes: 201 on create, 404 not found, 422 validation, no client blame for server faults.
- Input validated on the backend, whatever the frontend does.
- Path parameters validated on every route that takes them.
- Edge cases: empty lists, missing records, blank strings, duplicate IDs.

## Tests
- Every behaviour change has tests (pytest in `backend/tests/`, Vitest in the frontend).
- A bug fix has a test that fails without the fix.
- Tests use `tmp_path` and `monkeypatch`; nothing reads or writes `backend/app/data/`.
- Tests check behaviour (status, body, raised error), not implementation details.

## Readability
- Semantic names; booleans read as questions (`is_active`, `has_items`).
- No dead code, unused parameters, or commented-out blocks.
- Comments explain why, not what.

## Vertical stack and docs
- Every affected layer is changed, or the PR lists the follow-up tasks.
- A folder whose files were added, removed, or repurposed has its README updated, including
  removing "Not yet true" bullets the PR fixes.
- `docs/architecture.md` changes when layer rules or feature files change.
