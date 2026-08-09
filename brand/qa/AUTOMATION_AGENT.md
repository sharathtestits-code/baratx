# Automation agent — how to QA BarathX

Companion to `FEATURE_MATRIX.md`. Goal: an agent (Cursor cloud / Playwright / similar) can **log in and exercise the product** without guessing.

## Recommended stack

1. **Playwright** (or Cursor computer-use agent) against `QA_BASE_URL`
2. Secrets from env — never hardcode in repo
3. One run = smoke order in the feature matrix; nightly = full matrix

## Suggested repo layout (when you add E2E)

```
e2e/
  playwright.config.ts
  tests/
    auth.spec.ts
    square.spec.ts
    alerts.spec.ts
    arenas.spec.ts
  fixtures/auth.ts
```

Not present yet — matrix is the contract until specs land.

## Login helpers (API-first is faster)

```
POST {QA_API_BASE}/auth/login/email
{ "email": "<QA_USER_A_EMAIL or username>", "password": "..." }
→ access_token

Authorization: Bearer <token>
GET /posts?feed=global
GET /notifications
POST /posts  (multipart or form as app does)
```

UI path: `/login` → fill email/password → submit → wait for `/feed`.

Official: username `sharath` + `QA_OFFICIAL_PASSWORD`.  
Admin: open `/admin`, type `QA_ADMIN_SECRET`, Open.

## Selectors (stable-ish)

Prefer role/label over CSS hash classes:

- Login: `textbox` email/password, button “Sign in”
- Square compose: textarea placeholder “What's your take?” / studio compose
- Bottom nav: “Alerts”, “Square”, “Live”, “Arenas”
- Menu: button that opens plaza side menu → “Alerts”
- First session: “Skip for now”
- Nav tour: “Skip tour”

## Pass/fail reporting

Write a short markdown run log under `brand/qa/runs/YYYY-MM-DD.md`:

```
# QA run 2026-08-09
Agent: …
Base: https://barathx.com
- A2 PASS
- S1 PASS
- S3 PASS (post id …)
- N4 FAIL — reason
```

## Safety

- Do not delete protected blues (`baratx`, `sharath`) from admin  
- Prefer unique `qa-` prefixed posts so cleanup is obvious  
- Do not post to Instagram / force digests on production unless ops ask  
- Rate-limit: ≤1 post/sec in automation
