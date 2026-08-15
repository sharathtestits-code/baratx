# BarathX — Business Requirements Document (BRD)
## Production features already shipped

| Field | Value |
|-------|--------|
| **Document** | BRD — Production Feature Baseline |
| **Product** | BarathX (India’s public square) |
| **Audience** | QA / Manual testers / Automation agents |
| **Version** | 1.0 |
| **Date** | 9 August 2026 |
| **Code baseline** | `main` (shipped) |
| **Status** | **Baseline — what is live today** |

---

## 1. Purpose

This BRD describes **all product features already pushed to production** so testers can:

1. Know what to test (in scope)  
2. Know what **not** to fail on (out of scope / not shipped)  
3. Use correct **prod vs QA** URLs  
4. Apply the same pass/fail rules ops use  

It is a **feature baseline**, not a wishlist. Future LLM / legal / cloud work is listed only under Out of Scope.

---

## 2. Environments

| | **Production (live users)** | **QA (for testers / automation)** |
|---|---|---|
| **App** | https://barathx.com | https://qa.barathx.com *(provision if not live yet)* |
| **API** | https://baratx-production.up.railway.app | https://baratx-qa.up.railway.app |
| **Ops console** | https://barathx.com/bx-ops | https://qa.barathx.com/bx-ops |
| **Docs map** | `DEPLOY.md` | `brand/qa/ENVIRONMENTS.md` |

**Rule for automation:** use `QA_*` URLs only. Do not run destructive admin actions on production.

Same **feature set** when QA is deployed from the **`qa`** branch and prod from **`main`**; data and secrets differ. Branch ladder: [BRANCHING.md](../qa/BRANCHING.md).

---

## 3. Product summary

**BarathX** is a text-and-live public square for India: short takes, real replies, sided debates (Arenas), and live rooms — not a Reels feed.

**Positioning (live landing):** Pick a side. Argue it live. · Human takes only. No AI slop.

**Primary logged-in IA (bottom nav):** Square · Live · Arenas · Alerts · You  

---

## 4. Global rules (apply everywhere)

| ID | Rule | Tester note |
|----|------|-------------|
| G1 | Users must be **18+** (signup / Google age confirm) | Reject under-age flows |
| G2 | English-first UI | Preference picker for en/hi/te; full hi/te chrome later — see I18N_HINDI_TELUGU.md |
| G3 | Post text max **500** chars; reply max **220** | |
| G4 | Images: JPEG/PNG/GIF/WebP, **≤ 5MB** | |
| G5 | Official accounts `@baratx`, `@sharath`, `@bharatvoices`, `@indiatech` — likes/replies **do not count** toward Founding / Race | |
| G6 | Blue founders `@baratx` / `@sharath` cannot be deleted or demoted | Admin must block those actions |
| G7 | Arenas ≠ Communities | Communities are member-run groups |
| G8 | Square **For you** shows people you don’t follow | Following tab is follow-gated |

---

## 5. In-scope features (production)

### 5.1 Public & legal

| ID | Feature | Path | Requirement / expected behavior |
|----|---------|------|--------------------------------|
| P1 | Landing | `/` (logged out) | Brand hero, Square/Arenas/Live story, Join / Sign in / Google, Founding CTA, FAQ, social links |
| P2 | Terms | `/terms` | 18+, content rules, liability — page must render (not blank) |
| P3 | Privacy | `/privacy` | Privacy copy — page must render |
| P4 | Guidelines | `/guidelines` | House rules, badges, reporting, Founding blurb |

### 5.2 Authentication

| ID | Feature | Path | Requirement / expected behavior |
|----|---------|------|--------------------------------|
| A1 | Email signup | `/signup` | Email, password, username, display name, **age 18+** confirm → Square / first session |
| A2 | Email login | `/login` | Email or username + password → Square |
| A3 | Google sign-in | `/login`, `/signup` | Opens Square; new Google users need age confirm |
| A4 | Phone OTP signup/login | `/signup`, `/login` | India phone flow; if SMS not configured, **dev OTP** may appear (document env) |
| A5 | Forgot / reset password | `/forgot-password`, `/reset-password` | Reset email when Resend/SMTP configured |
| A6 | Verify email | `/verify-email` + in-app banner | Token confirm; resend available |
| A7 | Logout | Settings | Session cleared → landing/login |
| A8 | Bootstrap follows | After signup | New users follow official BarathX accounts |

### 5.3 Square (Home)

| ID | Feature | Path | Requirement / expected behavior |
|----|---------|------|--------------------------------|
| S1 | Square home | `/feed` | Header, compose, takes list |
| S2 | For you | Tab | Community takes visible without following; official digest ranked after community |
| S3 | Following | Tab | Only followed users + self |
| S4 | Compose take | Studio | Post text (± image, civic-problem checkbox, @mentions) |
| S5 | Hot take starters | Compose | Local starter lines fill compose — **not** full LLM drafts unless env says so |
| S6 | Top questions (suggestions) | Strip on Square | **15–20** suggested questions; tap fills compose; Hide works; never auto-posts |
| S7 | Today’s Square | Strip | Daily shared question → Answer fills compose; Later hides for the day |
| S8 | Founding chip | Header | Shows First 100 status; links to `/rewards` |
| S9 | First session | Gate on Square | Pick arena → take → city → Post & enter; **Skip for now** allowed |
| S10 | Coach marks | Overlay after first session | Spotlight: compose → Square → Live → Arenas → Alerts → You (why each tab); **Next / Got it**; × closes; **no “Skip tour”** |
| S11 | Like / unlike | Post | Count updates; author gets Alert (+ email if configured) |
| S12 | Reply | Post card / `/posts/:id` | Thread replies; author Alert |
| S13 | Repost | Post | Shows in Following as repost |
| S14 | Quote | `/feed?quote=:id` | Quote compose |
| S15 | Bookmark | Post → `/bookmarks` | Saved list |
| S16 | Hashtag | `/hashtag/:tag` | Tag timeline |
| S17 | Post detail | `/posts/:postId` | Full post + replies |
| S18 | New post Alerts | System | Followers + `@baratx`/`@sharath` get “posted in the Square” |
| S19 | Auto official replies | System | `@baratx` + `@sharath` welcome on **first** post + content replies on **all** community posts (human-style); excluded from rewards |

### 5.4 Alerts & email

| ID | Feature | Path | Requirement / expected behavior |
|----|---------|------|--------------------------------|
| N1 | Alerts inbox | `/notifications` | List interactions; mark read clears badge |
| N2 | Unread badge | Bottom nav + ☰ menu Alerts | Shows count |
| N3 | Alert types | — | follow, like, reply, repost, mention, post, message, badge |
| N4 | Activity email | Outbound | When Resend/SMTP set: reply / post / etc. with CTA to open app/login |

### 5.5 Arenas & topics

| ID | Feature | Path | Requirement / expected behavior |
|----|---------|------|--------------------------------|
| R1 | Arenas list | `/arenas` | Six arenas + live debates strip; join/leave |
| R2 | Arena detail | `/arenas/:key` | Join, topics, open debate, posts, suggestions strip |
| R3 | Arena keys | — | `startups`, `sports`, `politics`, `entertainment`, `news`, `spirituality` |
| R4 | Side labels | Debate rooms | Default For/Against; Startups **Fund it / Pass**; Spirituality **Resonates / Skeptical** |
| R5 | Topics | Arena chips + `/onboarding/topics` | Follow topics; use in debate |
| R6 | Arena suggestions | Arena detail | Top ~15–20 problems/questions for that arena |

### 5.6 Live, debates, Live Talk

| ID | Feature | Path | Requirement / expected behavior |
|----|---------|------|--------------------------------|
| L1 | Live list | `/spaces` | Rooms; Start a live; Jump in |
| L2 | Live / debate room | `/spaces/:id` | Posts in room |
| L3 | Pick a side | Debate rooms | Must choose side before posting; filter by side |
| L4 | Live Talk | In room panel | Join talk; mute/video primary; reactions; chat; pin; host remove; max **15** seats |
| L5 | Live Talk moderation | System | Filters / strikes / kick; repeated reports can remove account |

### 5.7 Communities

| ID | Feature | Path | Requirement / expected behavior |
|----|---------|------|--------------------------------|
| C1 | Communities | `/communities` | Member-run groups — **not** Arenas |
| C2 | Community detail | `/communities/:slug` | Join/leave, feed, post |

### 5.8 Profile & social

| ID | Feature | Path | Requirement / expected behavior |
|----|---------|------|--------------------------------|
| U1 | Profile | `/u/:username` | Avatar/cover, bio, stats, Follow, Message, Mute/Block |
| U2 | Followers / Following | `/u/:username/followers`, `.../following` | Lists + follow |
| U3 | Edit own profile | Profile | Name, username, bio, photos |
| U4 | Search / Explore | `/search` | People + posts |
| U5 | Messages | `/messages`, `/messages/:username` | DM inbox + thread |
| U6 | Bookmarks | `/bookmarks` | Saved posts |
| U7 | Lists | `/lists`, `/lists/:listId` | Custom lists (available by URL) |
| U8 | Settings | `/settings` | Theme (midnight / saffron / monsoon / ink), mutes, blocks, logout, links |

### 5.9 Rewards

| ID | Feature | Path | Requirement / expected behavior |
|----|---------|------|--------------------------------|
| W1 | Rewards page | `/rewards` | Founding 100 + Square Race explained + status |
| W2 | Founding 100 | — | **100** spots earned by debate/civic + engagement (not signup). **Public copy: no ₹.** Private surprise thank-you **₹150** after `payable`. Floor → rating → admin UPI paid |
| W3 | Founding rating bar | — | Problem: ≥**25** likes **or** ≥**5** human replies; Debate: ≥**2** stances **or** ≥**3** posts |
| W4 | Square Race | — | Every **14** days; highest-liked Home post; min **25** likes; prize **₹150–₹500**; admin locks winner + marks paid |
| W5 | Official exclusion | — | Official / blue engagement never counts toward W3/W4 |

### 5.10 Badges & moderation

| ID | Feature | Path | Requirement / expected behavior |
|----|---------|------|--------------------------------|
| B1 | Blue official | Profile / Guidelines | Staff/platform |
| B2 | Gold | Profile | Brand/topic voices — not personal “verified celebrity” |
| B3 | Badge change | Admin / blue user tools | Optional notify user |
| B4 | Report post | Post menu | Reasons; auto-mod after repeated reports |
| B5 | Mute / Block | Profile + Settings | Hide from feed/DMs as designed |
| B6 | Ops delete | `/bx-ops` Users / Engage | Delete misleading user/post (not protected blues) |

### 5.11 Admin console

| ID | Feature | Path | Requirement / expected behavior |
|----|---------|------|--------------------------------|
| AD1 | Unlock | `/bx-ops` | Requires `ADMIN_SECRET`; `/admin` is a public 404 |
| AD2 | Overview | Tab | Stats, needs-attention cards, quick jumps, newest signups |
| AD3 | Users | Tab | Search; expand details; badge actions; delete |
| AD4 | Engage | Tab | Comment on posts as official; delete post; auto-engage note |
| AD5 | Post | Tab | Post as official account |
| AD6 | Payouts | Tab | Founding Mark paid; Race lock winner / Mark paid |
| AD7 | Tools | Tab | Refresh debate prompts; Run peak digest; Post IG carousel |

### 5.12 Background / ops (verify via effects, not UI alone)

| ID | Feature | Requirement / expected behavior |
|----|---------|--------------------------------|
| O1 | Peak digest | ~**09:00 / 13:30 / 20:00 IST** multi-arena posts from credible RSS as @baratx + @sharath (Admin can force) |
| O2 | Instagram carousel | Scheduled / Admin force to **@getbaratx** when `INSTAGRAM_*` configured |
| O3 | Official engage poller | Backfills missed @baratx/@sharath replies (~45s) |

### 5.13 Mobile / PWA

| ID | Feature | Requirement / expected behavior |
|----|---------|--------------------------------|
| M1 | PWA / installable web | Manifest + theme; usable in mobile browser |
| M2 | Capacitor shells | Android/iOS projects exist; store push/Google native OAuth may be incomplete |

---

## 6. Out of scope (do **not** fail builds for these)

| Item | Status |
|------|--------|
| Separate QA host live | Deploy from **`qa`** branch; prod from **`main`** — see `brand/qa/BRANCHING.md` |
| Real MSG91 SMS always on | UI exists; SMS depends on env |
| Automated UPI payouts | Admin marks paid manually |
| Full LLM rewrite / “argue my side” | Roadmap; suggestions may optionally LLM-rank if `AI_ASSIST_*` set |
| Video / Reels product feed | Not built |
| Hindi / Telugu full UI | P1 plaza chrome live (Square / Arenas / Live / Settings / nav); content rails still English |
| Native push (FCM/APNs) | Not shipped |
| RaceStrip / FoundingStrip on Square | Code may exist; not required in current Square shell |

---

## 7. Suggested test priority (for human tester)

### P0 — must pass before release sign-off

1. Signup / login (email) + age gate  
2. Square For you shows community posts without follow  
3. Compose + reply + Alert for author  
4. First session + coach marks (Next/Got it)  
5. Arenas list → open one arena → suggestions visible  
6. Live list → enter a room  
7. Admin unlock → Users search → Overview stats  
8. Rewards page loads with Founding + Race copy  

### P1 — important

- Following tab, bookmarks, search, profile follow/message  
- Debate pick-a-side posting  
- Founding chip → Rewards  
- Alerts badge + menu Alerts  
- Password reset (if email configured)  

### P2 — ops / env-dependent

- Google login, phone OTP, activity emails, IG carousel, peak digest  

---

## 8. Acceptance criteria (BRD-level)

The build is accepted for tester baseline when:

1. All **P0** flows work on the target environment (Prod smoke or QA when available).  
2. Square **For you** is not empty solely because the tester follows nobody.  
3. Official auto-replies appear on new community posts without counting toward Founding.  
4. Ops can open `/bx-ops`, view users, and reach Engage / Payouts / Tools.  
5. Legal pages `/terms`, `/privacy`, `/guidelines` render content (not blank).  
6. No requirement to test unshipped items in §6.

---

## 9. Related docs for testers

| Doc | Use |
|-----|-----|
| `brand/qa/FEATURE_MATRIX.md` | Case IDs for automation |
| `brand/qa/ENVIRONMENTS.md` | QA vs Prod URLs |
| `brand/qa/AUTOMATION_AGENT.md` | How an agent should log in |
| `brand/qa/E2E_BOOTSTRAP.md` | Playwright starter |
| `brand/social/founding-100-ops.md` | Rewards ops detail |
| `brand/social/daily-digest-ops.md` | Digest + welcome rules |
| `DEPLOY.md` | Hosting / secrets |

---

## 10. Document control

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 1.0 | 2026-08-09 | Product / engineering baseline | First BRD of shipped prod features for tester handoff |

**Owner:** Product (TestITS) · **Implementation:** BaratX `main`  

When new features ship, update this BRD version and the QA feature matrix in the same PR.
