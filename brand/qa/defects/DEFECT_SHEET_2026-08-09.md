# BarathX QA — Defect sheet

**Environment:** QA only (`https://qa.barathx.com` → API proxy / `https://baratx-qa.up.railway.app`)  
**Date:** 2026-08-09  
**Tester:** Cursor QA agent (11y-style exploratory + catalog API/UI)  
**Accounts:** `@testits_a` / `@testits_b` · Admin secret from `.env.qa`  
**Evidence:** `brand/qa/runs/`, `e2e/runs/`, `brand/qa/scripts/run_qa_human_explore.py`

---

## Summary

| Severity | Count |
|----------|------:|
| P0 | 1 |
| P1 | 2 |
| P2 | 4 |
| P3 | 1 |

**Catalog:** 118 documented cases · **Executed this pass:** API deep explore (~40) + UI first-time Playwright + Admin UI/API  
**Core member flows (login, Square post/like/reply, follow Alerts, arenas, live list, DMs, admin ops):** working on QA after account setup.

---

## Fix status (engineering — 2026-08-09)

| ID | Sev | Status | Notes |
|----|-----|--------|-------|
| **DEF-001** | P0 | **Code harden + ops** | `email.py` never mails Railway hosts; QA detected via `ENVIRONMENT=qa` / CORS / Railway service name. **Ops:** set Railway QA `FRONTEND_URL=https://qa.barathx.com` and prefer `ENVIRONMENT=qa`. |
| **DEF-002** | P1 | **Follows DEF-001** | Same link host fix; re-test Resend / `dev_verify_url` after QA redeploy. |
| **DEF-003** | P2 | **Fixed (build)** | Vite injects `VITE_PUBLIC_URL` into OG tags. Set Pages QA `VITE_PUBLIC_URL=https://qa.barathx.com`. |
| **DEF-004** | P2 | **Fixed** | First-session take starts empty; prompts are chips + placeholder only. |
| **DEF-005** | P2 | **Fixed** | Admin Users shows email + `(unverified)` / verified status. |
| **DEF-006** | P2 | **Fixed** | `users.has_posted_once` lifetime flag; welcome no longer re-fires after delete-all. |
| **DEF-007** | P3 | **Fixed** | Removed blue-ops hint from non-blue member profile views. |

---

## Retest — 2026-08-09 (live QA)

**Verdict: NOT CLEAR — fixes not on live QA yet.**

| Gate | Status |
|------|--------|
| PR #21 merged to `main` | **No** (`670cff5` not ancestor of `origin/main`) |
| Railway `baratx-qa` redeploy with fix | **No** (API still mails `baratx-production-f8ce.up.railway.app`) |
| Cloudflare `qa.barathx.com` rebuild with fix + `VITE_PUBLIC_URL` | **No** (live bundle still `useState(Uu[0])`; OG still `barathx.com`) |

| ID | Live QA (`qa.barathx.com` / `baratx-qa`) | Evidence |
|----|------------------------------------------|----------|
| **DEF-001** | **FAIL** | Signup/`forgot-password` `dev_*_url` → `https://baratx-production-f8ce.up.railway.app/...` |
| **DEF-002** | **FAIL** | Resend verify same bad host |
| **DEF-003** | **FAIL** | `og:url` / `og:image` still `https://barathx.com/...` |
| **DEF-004** | **FAIL** | Live JS still `useState(Uu[0])` (prompt prefilled) |
| **DEF-005** | **FAIL** *(code not live)* | Live JS lacks `(unverified)` admin label |
| **DEF-006** | **FAIL** | Delete-all → new post still got **4** official replies (2 welcome) for `@qaretest1786308208` |
| **DEF-007** | **FAIL** | Live JS still contains “Badge grant/demote is only available…” |

**Branch preview static check** (`https://c824aa30.baratx.pages.dev`, commit `670cff5`): DEF-004 empty `useState("")` + `placeholder:Uu[0]` **present**; DEF-007 ops hint **removed**; DEF-005 `(unverified)` **present**. Preview still points API at **production** (`baratx-production.up.railway.app`) and OG still prod (no `VITE_PUBLIC_URL` on that Pages build) — interactive preview signup **CORS-blocked**.

### Unblock checklist (then re-run this section)

1. Merge PR #21 → `main` (or deploy this branch to Railway QA).  
2. Railway QA vars: `FRONTEND_URL=https://qa.barathx.com`, prefer `ENVIRONMENT=qa`. Redeploy API.  
3. Cloudflare Pages QA: set `VITE_PUBLIC_URL=https://qa.barathx.com`, rebuild `qa.barathx.com`.  
4. Re-hit: forgot-password host, OG source, first-take `0/500`, admin email row, delete-all welcome, `/u/baratx` as member.

---


## Failed scenarios

| Case ID | Scenario | Result | Linked defect |
|---------|----------|--------|---------------|
| **TC-CFG-01** | QA `FRONTEND_URL` / reset & verify link host is `qa.barathx.com` | **FAIL** | DEF-001 (P0) |
| **TC-A5-01** | Forgot password → usable reset link on QA | **FAIL** | DEF-001 (link goes to production Railway host) |
| **TC-A5-02** | Reset password via email/dev link on QA | **FAIL** (blocked by bad host) | DEF-001 |
| **TC-A6-01** | Verify email (banner / verify link) | **FAIL** | DEF-001 + DEF-002 |
| **TC-A6-02** *(implied)* | Resend verification from Square banner | **FAIL** | DEF-002 (Resend uses same wrong host) |
| **TC-P1-01** *(meta)* | QA landing share / OG tags represent QA | **FAIL** | DEF-003 (OG → `barathx.com`) |
| **TC-S9-01** | First session — drop first take UX | **FAIL** (UX) | DEF-004 (prompt counted as real text, e.g. 51/500) |
| **TC-AD1-01** *(Users list)* | Admin Users shows member email correctly | **FAIL** | DEF-005 (`email —` for `@testits_a` / `@testits_b`) |
| **TC-S19-01** *(edge)* | Official welcome only once per account | **FAIL** (after delete-all-posts) | DEF-006 |
| **TC-U1-01** *(copy)* | Official profile does not show blue-only ops text to members | **FAIL** | DEF-007 |

### Also failed earlier, then fixed / re-run

| Case ID | Scenario | Notes |
|---------|----------|--------|
| TC-A2-01 | Email login Member A | Failed once when account missing on QA; **PASS** after signup + password reset to `.env.qa` |
| TC-A1-03 | Signup duplicate email | Failed once (email not yet registered); **PASS** on re-run |
| TC-AD1-01 | Admin unlock (UI automation) | Failed when shell had empty `QA_ADMIN_SECRET`; **PASS** with correct secret |

### Not failed — expected / blocked / skipped

| Case ID | Scenario | Notes |
|---------|----------|--------|
| TC-W* ops | `GET /rewards/ops` as Member A | **403 by design** (blue only) — not a defect |
| TC-A3-01 / TC-A4-* happy | Google / Phone OTP full path | **Not executed** (P2 / external) |
| TC-U1-05 | Mobile Follow contrast | **PASS** (Follow/Following visible on Midnight) |

---

## Defects

| ID | Sev | Area | Title | Steps to reproduce | Expected | Actual | Recommendation |
|----|-----|------|-------|--------------------|----------|--------|----------------|
| **DEF-001** | **P0** | Config / Auth email | QA `FRONTEND_URL` points at production Railway app | 1. Call `POST /auth/forgot-password` for a QA user 2. Read `dev_reset_url` | Link host is `qa.barathx.com` | Host is `baratx-production-f8ce.up.railway.app` | Set Railway **QA** `FRONTEND_URL=https://qa.barathx.com` (and rebuild/redeploy API). Re-test forgot + verify links. |
| **DEF-002** | **P1** | Auth / First-time UX | New members stuck unverified; verify banner always on | Sign up / use `@testits_a` → open Square | Can verify email on QA or banner is suppressible in QA | Banner: “Confirm your email…”; `is_email_verified=false`; Resend uses same bad link host as DEF-001 | Fix DEF-001; ensure Resend/SMTP or `dev_verify_url` opens QA; optionally auto-verify seeded QA test users. |
| **DEF-003** | **P2** | SEO / QA branding | QA HTML OG tags advertise production | View source on `qa.barathx.com` | `og:url` / images use QA host | `og:url` / `og:image` → `https://barathx.com/...` | Build QA frontend with QA public URL / meta, or inject per-environment meta. |
| **DEF-004** | **P2** | Onboarding UX | First-take prompt is real text, not placeholder | New user → first-session “Drop your first take” | Prompt is placeholder (0/500 until user types) | Prompt pre-filled; counter shows e.g. `51/500` | Use `placeholder` (or clear-on-focus) so users don’t have to delete starter text. |
| **DEF-005** | **P2** | Admin Users | Email shows as “—” for members who have emails | Admin → Users → `@testits_a` / `@testits_b` | Show email (and verified flag) | UI shows `email —` while API has emails (unverified) | Display email even when unverified; add Verified / Unverified badge. |
| **DEF-006** | **P2** | Engagement | Deleting all posts re-triggers “first post” welcome (4 official replies) | Delete all posts → post again | Welcome flood once per account lifetime (or once ever) | `prior_posts==0` after deletes → welcome + engage (4 replies) again | Persist `has_posted_once` flag (or similar) so welcome is lifetime-once. |
| **DEF-007** | **P3** | Profile / Ops leakage | Blue-only ops copy visible to normal members | Open `/u/baratx` as `@testits_a` | Ops/badge tools only for blues | Text like badge grant/demote / invite rules visible on official profile | Gate that copy behind blue/admin auth. |

---

## Not defects (by design / env)

| Item | Notes |
|------|--------|
| `GET /rewards/ops` → 403 for Member A | Expected: “Blue accounts only”. |
| Official 2 replies on later posts | Working; 4 replies only when treated as first post. |
| Empty `VITE_API_BASE` on QA build | OK — QA host proxies `/auth`, `/posts`, etc. (`qa.barathx.com/health` → ok). |
| Google / Phone OTP happy path | Not fully exercised (P2 / external deps). |
| Admin unlock UI | **PASS** once secret loaded (Overview/Users/Engage/Post/Payouts/Tools). |

---

## What worked (human + API)

- Landing, login (“Enter BarathX”), session → first-session / Square  
- Member B follow → Alert on A; A post → Alert on B; like/reply Alerts  
- Official `@baratx` / `@sharath` auto-replies  
- Arenas join, spaces list, communities join, DMs, block/unblock, report  
- Admin: stats, users, protected blue delete blocked, official post/reply, badge grant/revoke, founding/race queues, delete post  
- Follow control visible on Midnight (desktop + mobile screenshots)

---

## Product / UX notes (not filed as bugs)

1. First-session modal still blocks `@testits_a` until Post & enter / Skip — fine for true first-timers; QA accounts may want a “complete onboarding” admin tool.  
2. Email field on login is `type="text"` (supports username) — OK; keep accessible name/label.  
3. Rotate shared passwords if ever used outside private QA.

---

## Files

| Artifact | Path |
|----------|------|
| This sheet | `brand/qa/defects/DEFECT_SHEET_2026-08-09.md` |
| CSV | `brand/qa/defects/DEFECT_SHEET_2026-08-09.csv` |
| API explore JSON | `brand/qa/runs/2026-08-09-full-explore.json` |
| UI screenshots | `e2e/runs/ui-*.png` |
