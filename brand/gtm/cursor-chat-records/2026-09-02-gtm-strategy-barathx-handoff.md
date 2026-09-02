# BarathX GTM strategy — durable handoff

**Date:** 2026-09-02  
**Source agent:** [GTM strategy for BarathX](https://cursor.com/agents/bc-5eab029b-6e35-45dc-8a75-0abfc16b2af5)  
**Founder:** Sharath (TestITS)  
**Repo:** https://github.com/sharathtestits-code/baratx  
**Site:** https://barathx.com · Social: [@getbaratx](https://x.com/getbaratx) / [IG](https://www.instagram.com/getbaratx/)

**Brand spelling:** always **BarathX** (never BaratX / BharathX). Handle stays `@getbaratx`.

---

## Product north star / emotional positioning

**One-line north star (use everywhere):**  
*I want people to feel: this is India’s moment to build its own digital public square — and BarathX is that home.*

**What people should feel when they hear “BarathX”:**
- **Pride** — India’s own digital public square; by Indians, for Indians, owned by Indians
- **Relief** — done shouting into vanishing WhatsApp groups and empty-like feeds
- **Courage** — safe to take a side; answered by humans, not bots / AI slop / ads machine
- **Belonging** — city, campus, builders, debates — a home for people with a POV
- **Momentum** — soft launch = early; join India’s conversation at the start

**Do not make them feel:** another startup, another social clone, a feature dump, “Indian Instagram.”

**Positioning lines in active use:**
- “India has opinions. Now it has a home.”
- “Human takes only. No AI slop.”
- “One question. Your take. No Reels required.”

**Product (for creatives):** Square · Arenas · Live — conversation network, not a Reels/ads feed. Soft launch live in browser (+ app path).

**Policy notes locked in outreach:** no adult content encouraged; country-based restrictions next; **18+ gate deferred** on prod to reduce signup friction (do not claim 18+ in cold creatives). Themes: midnight + saffron accent; guest shell stays dark; appearance/themes live under Settings after signup.

---

## Work completed this thread (high-signal)

Long GTM + product + social thread (Aug–Sep 2026). Highlights with concrete artifacts:

### Daily discovery series (video)
| Part | Status | Branch / PR | Paths & downloads |
|------|--------|-------------|-------------------|
| **Part 1 — Square** | Built (25.0s), open PR | `cursor/daily-part1-25s-2af5` · [#107](https://github.com/sharathtestits-code/baratx/pull/107) | `brand/social/daily/2026-08-25/barathx-part1-25s.mp4` · also `brand/social/instagram/demo-series/PART-01-square-v5/` · [raw download](https://raw.githubusercontent.com/sharathtestits-code/baratx/cursor/daily-part1-25s-2af5/brand/social/daily/2026-08-25/barathx-part1-25s.mp4) · script `…/RECORDING-SCRIPT.md` · captions `…/PACK.md` · live stills `brand/social/whatsapp/screens/live-2026-08-25/` |
| **Part 2 — Arenas** | Built (25.0s), HeyGen 35% placeholder zone, open PR | `cursor/arenas-part2-25s-2af5` · [#109](https://github.com/sharathtestits-code/baratx/pull/109) | `brand/social/daily/2026-08-28/barathx-PART2-arenas-25s.mp4` · [raw download](https://raw.githubusercontent.com/sharathtestits-code/baratx/cursor/arenas-part2-25s-2af5/brand/social/daily/2026-08-28/barathx-PART2-arenas-25s.mp4) · caption `brand/social/instagram/demo-series/PART-02-arenas/CAPTION.txt` |
| Parts 3–7 | Planned only | See series plan below | Do **not** regenerate Part 1 |

**Part 1 hook (approved):** “Would you rather get 1,000 likes… or 10 real opinions?”  
**Part 2 hook (approved script):** “Why argue in a WhatsApp group?” → Agree/Disagree/It depends → “Not another group chat” → end **PART 2 — ARENAS ✓ · NEXT → YOU**.

Series map file: `brand/social/instagram/demo-series/SERIES.md`

### Creator / GTM outreach packs
| Pack | PR | Paths |
|------|-----|-------|
| Creator collab emails + one-pager (feeling-first, latest screens) | [#108](https://github.com/sharathtestits-code/baratx/pull/108) · `cursor/creator-collab-emails-2af5` | `brand/gtm/outreach/emails-2026-08-27/EMAILS.md` · `…/BarathX-Creator-Collab-One-Pager.pdf` · [PDF raw](https://raw.githubusercontent.com/sharathtestits-code/baratx/cursor/creator-collab-emails-2af5/brand/gtm/outreach/emails-2026-08-27/BarathX-Creator-Collab-One-Pager.pdf) |
| Earlier IG-bio outreach emails | [#102](https://github.com/sharathtestits-code/baratx/pull/102) | `brand/gtm/outreach/emails-2026-08-18/` (one-pager, PPT, Nikhil follow-up) |
| Creator collab deck / terms / hooks | [#93](https://github.com/sharathtestits-code/baratx/pull/93) | GTM deck docs |

### Infra / product (thread context, much already on `main`)
- Domain **barathx.com** (Porkbun → Cloudflare), API on **Railway** + Postgres
- Soft launch live; Google/email auth work; phone OTP code path exists but **MSG91 not live** (see below)
- IG photo carousels via Meta Graph API; Reels music must be added **manually in IG app**
- Social links for captions: X https://x.com/getbaratx · IG https://www.instagram.com/getbaratx/ · WA channel https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o · Community https://chat.whatsapp.com/EV3Uj35EXrHImZ6MZxGAtU
- Drive playbook / automation docs: [#58](https://github.com/sharathtestits-code/baratx/pull/58)
- Open-source MIT intent: [#45](https://github.com/sharathtestits-code/baratx/pull/45)

**Diff-metadata note for this agent’s primary PR:** [#6](https://github.com/sharathtestits-code/baratx/pull/6) `cursor/phone-signup-username-2af5` (phone OTP username dead-end + awareness posts) — still listed open/draft in GitHub UI; treat merge state carefully vs `main`.

---

## Open PR merge checklist (prioritize recent content)

Merge **content / series** first so creatives are on `main`, then product/docs.

### Priority A — merge soon (recent GTM / reels)
1. [#109](https://github.com/sharathtestits-code/baratx/pull/109) — Part 2 Arenas 25s + HeyGen layout  
2. [#108](https://github.com/sharathtestits-code/baratx/pull/108) — Creator collab emails + PDF  
3. [#107](https://github.com/sharathtestits-code/baratx/pull/107) — Part 1 Square 25s + discovery series  

### Priority B — useful content / app store
4. [#104](https://github.com/sharathtestits-code/baratx/pull/104) — “Why India needs BarathX” reel  
5. [#102](https://github.com/sharathtestits-code/baratx/pull/102) — Creator outreach emails  
6. [#93](https://github.com/sharathtestits-code/baratx/pull/93) — Creator collab deck  
7. [#92](https://github.com/sharathtestits-code/baratx/pull/92) — WA teaser IG reel safe-zone  
8. [#80](https://github.com/sharathtestits-code/baratx/pull/80) — In-app soft-launch demos  
9. [#58](https://github.com/sharathtestits-code/baratx/pull/58) — Drive Social Draft playbook  

### Priority C — product / mobile / ops (review before merge; may be stale vs `main`)
- [#105](https://github.com/sharathtestits-code/baratx/pull/105) biometric unlock  
- [#100](https://github.com/sharathtestits-code/baratx/pull/100) iOS App Store checklist  
- [#99](https://github.com/sharathtestits-code/baratx/pull/99) Play Console next steps  
- [#95](https://github.com/sharathtestits-code/baratx/pull/95) WhatsApp Early Circle pack  
- [#90](https://github.com/sharathtestits-code/baratx/pull/90) mobile UI align  
- [#85](https://github.com/sharathtestits-code/baratx/pull/85) topic next-step + demo scripts  
- [#69](https://github.com/sharathtestits-code/baratx/pull/69) private ops route docs  
- [#56](https://github.com/sharathtestits-code/baratx/pull/56) grunge IG publisher  
- [#45](https://github.com/sharathtestits-code/baratx/pull/45) MIT license  
- [#44](https://github.com/sharathtestits-code/baratx/pull/44) QA provision  
- Older drafts (#39–#29, #6, #4): many UI/caption drafts — **diff against current `main` before merging**; large plaza/theme work may already be deployed

**Account switch:** code lives in GitHub — new Cursor Pro account only needs repo access. Chat UI does **not** move; use this folder.

---

## MSG91 / phone OTP status

**Status (as of end of thread):** Production phone OTP is **not** delivering SMS. Users see “Phone OTP is not available…” on India numbers. **Not** an India-block bug.

| Env | Behavior |
|-----|----------|
| Local / non-prod | Demo OTP can show in UI |
| Production (`ENVIRONMENT=production`) | Needs real MSG91; no demo leak → looks “unavailable” |

**Required Railway vars (API service only — never commit):**
- `MSG91_AUTH_KEY`
- `MSG91_TEMPLATE_ID`
- `MSG91_SENDER_ID` (6-char approved sender; default in code often `BARATX`)

**Founder progress in-thread:** creating MSG91 account (Transactional + OTP auth); instructed to finish KYC, create Authkey + DLT OTP template + Sender ID, add wallet ₹200–500, paste 3 vars on Railway → redeploy → test `+91` on https://barathx.com.

**Workaround until live:** Google or email login.

See also `DEPLOY.md` (MSG91 still listed as pending).

---

## HeyGen + Cursor pipeline decision (user-approved path)

**Question:** Can HeyGen connect to Cursor for automatic Reels posting?

**Answer locked in chat:**
1. **No** one-click HeyGen↔Cursor integration.
2. **Yes** to a scripted pipeline: Cursor/Cloud Agent calls **HeyGen API** → ffmpeg composites avatar into BarathX UI reel (Part 2’s ~35/65 layout) → commit/notify download.
3. **IG Reels post stays mostly manual** — Meta Graph cannot attach trending Reels music; founder posts in IG app (~30s) and adds audio.
4. Photo carousels to `@getbaratx` already auto via Graph API; WhatsApp/X packs stay paste/manual by design.

**Practical recommendation (approved direction):**  
`Cursor + HeyGen API` auto-generate daily files → notify “Part N ready — download” → founder posts in IG with trending audio.

Scaffold work was started on branch `cursor/heygen-composite-chat-2af5` (HeyGen composite + this chat-records handoff). Finish wiring needs HeyGen API key in env (not in git).

---

## Series plan Parts 1–7

**Format:** ~25s · 9:16 · scroll-stop hook first (not “Features · Part N”) · product answers hook · cliffhanger + Follow `@getbaratx` · brand **BarathX** only · no ₹/fee spam in cold creatives.

| Part | Focus | Status | End cliffhanger |
|------|--------|--------|-----------------|
| **1** | **Square** — today’s question, Drop a take, replies, Live strip | **Shipped** (PR #107) | Part 2 Arenas |
| **2** | **Arenas** — topics, Agree/Disagree/It depends, not a group chat | **Shipped video** (PR #109); HeyGen avatar overlay still TBD | Part 3 You |
| **3** | **You / Profile** — identity on the record | Script next | Part 4 Look & Explore |
| **4** | **Look & Explore** — themes, search | Planned | Part 5 Live |
| **5** | **Live rooms** — Jump in, Talk (mute/video/seats) | Planned | Part 6 Founding & civic |
| **6** | **Founding & civic** — earned Founding 100, civic/city takes | Planned | Part 7 Pro tips |
| **7** | **Pro tips** — bookmarks, mute/block, notifications, Settings | Planned | Series wrap · barathx.com |

Optional later remixes: Circles (Campus/City/Builders), Home hub tabs, human-vs-AI ranking.

ChatGPT brief for Parts 2–7 was produced in-thread (reuse from agent transcript / SERIES.md). **Do not regenerate Part 1.**

---

## Ops notes for next agent

### Live UI capture (hard rule)
- Founder repeatedly rejected **old screens**. Always capture from **live** https://barathx.com first.
- Store stills under dated folders, e.g. `brand/social/whatsapp/screens/live-YYYY-MM-DD/`.
- Renderer must **refuse** older folders; capture → then render.
- Part 1 used `live-2026-08-25`; Part 2 must stay on latest Arenas UI.

### Railway
- Production API + Postgres on Railway; frontend on Cloudflare Pages (barathx.com).
- Secrets stay on Railway (MSG91, Google, Resend, Turnstile, IG tokens, etc.) — **never** commit.
- QA org / `baratx-qa` was a recurring ops thread; confirm health before tester handoff (`DEPLOY.md`, PR #44).
- Redeploy after env var changes.

### Guest routes / shell
- Guest / logged-out shell stays **dark** (theme switch after signup → Settings).
- Do not hijack static/config routes as SPA routes (past bug: `/public/config`).
- Logout must remain visible after UI updates (fixed once; regression-watch).

### Social posting
- IG: 3 posts/day target historically for carousels; **1 elaborated demo Reel/day** for discovery series.
- Always spell **BarathX**; include X + IG + WhatsApp links in captions.
- Trending India audio attached **in IG app**; Graph API cannot set Reels music.
- Automations: Drive “Social Draft — …” playbook (PR #58); prefer drafts + notify over silent bad posts.

### Brand / product truth for copy
- Built by Indians, for Indians, owned by Indians.
- Soft launch live — invite people to **try the site**, not just an idea.
- Human-first ranking; no adult content; DPDP/privacy posture (privacy@barathx.com / hello@barathx.com).

### Account continuity
- Sync = GitHub `baratx` repo + open PRs. Document durable decisions here under `brand/gtm/cursor-chat-records/`.

---

## Remaining work

1. **Finish MSG91** — Authkey + DLT template + Sender ID → Railway vars → redeploy → verify India OTP SMS.  
2. **Merge Priority A PRs** (#109, #108, #107).  
3. **HeyGen overlay** — drop founder clone into Part 2 35% zone; finish `heygen` composite script + API key.  
4. **Post Part 1 & 2** on IG/X/WA (manual Reels + trending audio); log insights in `brand/social/instagram/demo-series/INSIGHTS_LOG.md`.  
5. **Produce Parts 3–7** in sequence (25s, live captures only, discovery cliffhangers).  
6. **Creator outreach** — send #108 emails + PDF; track replies/rates (no ₹ in cold email unless founder asks).  
7. **Triage older open PRs** vs current `main` (close stale or rebase).  
8. **App store path** — Play/iOS checklist PRs (#99/#100) when mobile push resumes.  
9. Keep **this handoff folder** updated after major strategy decisions.

---

*Generated from Cloud Agent transcript `bc-5eab029b-6e35-45dc-8a75-0abfc16b2af5` (selective extract: user messages + assistant conclusions). No secrets included.*
