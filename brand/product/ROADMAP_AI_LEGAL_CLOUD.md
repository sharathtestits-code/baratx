# Roadmap — AI, legal, cloud, onboarding

**Status:** Plan only for LLM. Do **not** wire a model until this is approved.  
Date: 2026-08-09

---

## 1. Where LLM helps (and where it shouldn’t)

### Ship later — high value

| Surface | Job | Why it competes in an “AI era” without becoming AI slop |
|---------|-----|--------------------------------------------------------|
| **Arena / Square suggestions** | Top 15–20 real questions/problems per tab | Users still post freely; LLM/RSS curates prompts so empty rooms feel alive |
| **Compose rewrite** | Polish user’s own draft (sharp / civic / short) | Assist, don’t auto-post; label “AI-assisted” if needed |
| **Argue my side** | 1-line For/Against for open debate | Matches sided-debate product |
| **Moderation assist** | Flag likely spam/abuse for human review | Scale ops; human still decides |
| **Digest headlines → debate titles** | Better than template-only RSS | Already have credible RSS allowlist |

### Do not lead with

| Anti-pattern | Why |
|--------------|-----|
| Auto-generated feeds of fake “takes” as users | Trust killer for Gen Z (your GTM doc) |
| Unlabeled AI replies as @baratx/@sharath | Breaks “human takes only” |
| Chatbot as the homepage | Competes with ChatGPT; you’re a square, not an oracle |

### Suggested phased build (when approved)

1. **No LLM:** curated + RSS top 15–20 prompts per arena (fast, free)  
2. **LLM rank/rewrite prompts only** from RSS + user questions (Gemini/OpenAI behind `AI_ASSIST_*`)  
3. **Optional compose rewrite** toggle  
4. Kill switch: `AI_ASSIST_PROVIDER=none`

Env (future): see `brand/social/ai-assist-notes.md`.

---

## 2. Legal / “register on our name” / secure the site

Not legal advice — checklist for counsel / CA / company secretary in India.

### Entity & brand

- [ ] Incorporate (Pvt Ltd / LLP) in **founders’ names** if not done  
- [ ] Trademark “BarathX” / logo (India — Class relevant to software/social)  
- [ ] Domain `barathx.com` already on Porkbun/Cloudflare — keep WHOIS/registrant = company or founder  
- [ ] Google / Apple developer accounts under company when you ship stores  

### Policies on-site (strengthen current `/terms` `/privacy` `/guidelines`)

- [ ] **DPDP Act 2023** privacy notice (purpose, retention, grievance officer, cross-border)  
- [ ] Intermediary / safe-harbour style terms (UGC, notice-and-takedown)  
- [ ] Age 18+ (already stated) + parental language if under-18 ever allowed  
- [ ] Cookie / analytics disclosure if you add trackers  
- [ ] Founding ₹150 / Race — clear “not a lottery; discretionary reward; T&Cs”  
- [ ] Contact: `hello@barathx.com` + physical address when incorporated  

### Security hygiene

- [ ] `JWT_SECRET`, `ADMIN_SECRET`, DB passwords only in Railway secrets  
- [ ] Resend domain auth (SPF/DKIM) for `hello@barathx.com`  
- [ ] Rate limits on auth, admin, post APIs  
- [ ] HTTPS only (Cloudflare + Railway — done)  
- [ ] Backup Postgres; plan R2 for media  
- [ ] Admin 2FA later; never commit `.env`  
- [ ] Bug/report path already in Guidelines — keep it visible  

---

## 3. Cloud — what’s best for BarathX now

**You’re already on a solid early stack:**

| Layer | Current | Recommendation |
|-------|---------|----------------|
| API + Postgres | **Railway** | Keep — simplest DX for this monorepo |
| Frontend | **Cloudflare Pages** (+ Railway can serve SPA) | Keep Pages for CDN edge |
| DNS / TLS | **Cloudflare** | Keep |
| Email send | **Resend** | Keep |
| Media later | Cloudflare **R2** | When images outgrow DB blobs |
| India latency later | Optional **AWS Mumbai** or **GCP asia-south1** | Only if Railway latency/cost hurts |

**Don’t move to AWS/GCP “because enterprise” yet** — cost and ops overhead rise before you have traffic. Revisit when you need SOC2, multi-region, or dedicated VPC.

**If you outgrow Railway:** Fly.io or Render are closer ports than raw AWS. Full AWS (ECS/EKS + RDS) only with a dedicated ops budget.

---

## 4. Onboarding (shipping now)

- First session: arena → take → city, with **Skip for now** (existing)  
- After that: **3-step nav tour** (Square / Alerts / Arenas) with **Skip tour**  
- Theme stays in Settings (no forced modal)

---

## 5. What shipped

1. Menu **Alerts** with unread badge  
2. Clearer **activity emails** (reply + posted) with login/post CTA  
3. **Follower** Alerts when someone you follow posts  
4. **QA org** docs for an automation agent  
5. **X/FB-style coach marks** (spotlight on real UI — Next/Got it, no Skip tour)  
6. **Top 15–20 suggestions** on Square + each Arena (`GET /suggestions`; optional LLM rank via `AI_ASSIST_*`)

**Optional next:** set `AI_ASSIST_PROVIDER=openai` + API key on Railway to rank/rewrite suggestion lists.
