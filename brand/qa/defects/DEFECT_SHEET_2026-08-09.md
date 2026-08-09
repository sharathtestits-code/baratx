# BarathX QA — Defect sheet

**Environment:** QA only (`https://qa.barathx.com` → API proxy / `https://baratx-qa.up.railway.app`)  
**Date:** 2026-08-09  
**Tester:** Cursor QA agent (11y-style exploratory + catalog API/UI)  
**Accounts:** `@testits_a` / `@testits_b` · Admin secret from `.env.qa`  
**Evidence:** `brand/qa/runs/2026-08-09-full-execution.md`, `brand/qa/runs/`, `e2e/runs/`

---

## Summary (full pass — late 2026-08-09)

| Layer | Result |
|-------|--------|
| **API catalog** | **86 PASS · 0 FAIL · 59 SKIP** |
| **UI walkthrough** | Login, Square, post, arenas, communities, rewards, settings, profile, logout, admin **PASS** |
| **Prior DEF-001…007** | **CLOSED** |

SKIP = Google/Phone OTP, image upload, coach marks, Live Talk deep, IG/ops, Capacitor (vendors / interactive).

| Severity | Open |
|----------|-----:|
| P0 | 0 |
| P1–P3 | 0 new |

---

## Fix status

| ID | Sev | Status | Notes |
|----|-----|--------|-------|
| **DEF-001…007** | — | **CLOSED** | Live QA retest clear after merge/deploy |
| **DEF-008** | **P0** | **CLOSED** | Live QA: document nav → HTML; `fetch` → JSON. Verified 2026-08-09 after PR #49. |

---

## Defects

| ID | Sev | Area | Title | Steps | Expected | Actual | Recommendation |
|----|-----|------|-------|-------|----------|--------|----------------|
| **DEF-008** | **P0** | Routing / same-origin | Hard nav / refresh to app paths hits API JSON | Open `/notifications`, `/bookmarks`, `/messages`, `/lists`, `/arenas`, `/spaces` via refresh or new tab on QA | SPA shell loads | `{"detail":"Not authenticated"}` or raw JSON arrays | Prefer document-nav SPA shell (shipped); longer-term mount API under `/api` |

---

## UX backlog (not filed as bugs)

1. Stronger empty states on Alerts / Messages / Bookmarks.  
2. Don’t re-show full first-session modal after Skip every login.  
3. Paginate Live/Spaces (heavy load).  
4. Search empty state with examples (`@baratx`, `#politics`).  
5. Admin Users: show email + verified without expanding the row *(small UI tweak included with DEF-008).*  

---

## Retest — DEF-001…007 (post-deploy)

**CLEAR** on live QA — see prior section history / commit history.
