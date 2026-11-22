---
name: audit-hooks
description: Audit React hooks for leaks and stale data (effects without cleanup, race conditions, missing dependencies, state updates after unmount, secrets in client code) and webhooks for unsafe handling (missing signature checks, replays, duplicate deliveries, leaked secrets). Use when asked to check hooks or webhooks, when adding a useEffect or custom hook, or when adding an endpoint that receives webhooks. Read-only; reports findings, never changes code.
argument-hint: "[react|webhooks] (default: both)"
---

# Audit React hooks and webhooks

Scope: `$ARGUMENTS` (empty means both). Read-only: report, don't fix.
Load context README-first (`AGENTS.md` AGENT RULES): `frontend/src/hooks/README.md` and
`frontend/src/pages/README.md` for React, `backend/app/routes/README.md` for webhooks.

## 1. React hooks

Find every `useEffect`, `useLayoutEffect`, custom `use*` hook, `setInterval`, `setTimeout`,
`addEventListener`, and `fetch` in `frontend/src` (`git grep -n`). For each, check:

- **Cleanup (leaks):** every timer, interval, listener, subscription, and request is undone
  in the effect's return function (`clearTimeout`, `removeEventListener`,
  `controller.abort()`). Without it, work keeps running after the component unmounts.
- **Race conditions:** an effect that fetches must ignore or cancel a stale response when
  its inputs change (prefer `AbortController`; an `active` flag also works). Otherwise a
  slow response for item A overwrites item B.
- **Dependencies:** every value from the component used inside the effect is in its
  dependency array (the `react-hooks/exhaustive-deps` rule). Missing ones cause stale data;
  objects or functions created during render cause the effect to run every render.
- **Rules of Hooks:** hooks are called at the top level of a component or custom hook,
  never inside conditions, loops, or callbacks.
- **Unneeded effects:** state derived from props or other state should be computed during
  render, not copied with an effect ("You Might Not Need an Effect", react.dev).
- **Secrets:** no API keys, tokens, or private URLs in hooks or anywhere in `frontend/src`;
  all of it ships to the browser.
- **Dev safety net:** `<StrictMode>` in `index.tsx` runs every effect twice in development,
  which exposes missing cleanup early. Note whether it's on.
- **Tooling:** `eslint-plugin-react-hooks` catches the dependency and Rules of Hooks
  problems automatically. Note whether it's configured (`frontend/package.json`).

## 2. Webhooks

A webhook is an HTTP request another service sends to us (e.g. a payment or delivery
provider). Find receiving endpoints (`git grep -niE "webhook|signature|callback"` in
`backend/`). If there are none, say "no webhooks yet" and list the checklist below as
requirements for when one is added.

For each receiving endpoint, check:
- **Signature verification:** the raw request body is verified with the provider's HMAC
  signature and a shared secret, compared in constant time (`hmac.compare_digest`), before
  anything is parsed or trusted. Unsigned requests are rejected with 401.
- **Replay protection:** the signed timestamp is checked and old requests (e.g. over 5
  minutes) are rejected.
- **Idempotency:** providers retry, so the same event can arrive more than once. Store
  processed event IDs and skip duplicates.
- **Secret handling:** the signing secret comes from config/environment, never the code.
- **Fast response:** reply 2xx quickly and do slow work afterwards; slow replies trigger
  retries.
- **No leaks:** don't log full payloads or headers containing personal data or secrets;
  error responses don't reveal internals.
- **Sending webhooks (if we do):** sign what we send, use HTTPS only, and block requests to
  internal addresses (server-side request forgery).
- Industry reference: the Standard Webhooks specification, and the provider's own guide
  (Stripe, GitHub).

## Report

```
## Hooks audit (<scope>)

| Severity | Kind | Where | Finding | Fix (fix or proposal) |
|---|---|---|---|---|
| high / medium / low | react / webhook | path:line | ... | ... |

Checked: <n> effects, <n> custom hooks, <n> webhook endpoints. Not checked: ...
```

Then list what is already done well (e.g. "`useDebounce` clears its timer").
