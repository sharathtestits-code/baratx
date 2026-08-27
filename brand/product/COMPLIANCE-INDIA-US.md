# BarathX — India + US compliance map (product checklist)

**Not legal advice.** Have counsel review before scaling ads / US users / paid features.  
Last updated: 2026-08-27 · Brand: **BarathX** · Site: https://barathx.com

---

## What we already have

| Area | Status |
|------|--------|
| India DPDP privacy notice + consent at signup | Live (`Privacy` / `Terms`, `privacy_accepted_at`) — notice states we **save** account data and **do not sell** personal information |
| **18+ DOB + age consent** | Live — `/age-consent`, DOB on email/phone/Google new accounts |
| Account data export / delete | Settings → Download my data / Delete account |
| Grievance contact | privacy@barathx.com |
| Activity email opt-out | Settings toggle + `/unsubscribe?token=` footer + `List-Unsubscribe` headers |
| Bot gate (Turnstile) + phone OTP preferred | Live |
| HTTPS, rate limits, hashed passwords/OTPs | Live |

---

## India (must-haves)

### 1. Digital Personal Data Protection Act, 2023 (+ Rules)
- Clear notice + **affirmative consent** before processing personal data (signup checkbox).
- **Purpose limitation** — only collect what you need (DOB = age gate only, never public).
- **Children**: DPDP treats under-**18** as children → verifiable parental consent or **do not onboard under-18**. BarathX product rule: **18+ only**, DOB + attestation.
- Rights: access, correction, erasure, withdraw consent (Settings + privacy@).
- Security safeguards + breach readiness.
- Cross-border transfer: disclose hosting; use contracted processors.

### 2. IT Act, 2000 / Intermediary Guidelines (safe harbour)
- Terms + Guidelines; notice-and-takedown path for unlawful content.
- Grievance / report flows (in-app report + email).
- Do not host CSAM; expedited remove + report.

### 3. SMS / OTP (TRAI / telecom practice)
- OTP SMS is **transactional** (account security) — no marketing SMS without separate consent.
- Rate-limit OTP; never sell phone numbers.

### 4. Consumer / advertising (if you run India ads later)
- ASCI / local ad rules; no misleading “guaranteed cash for signup” (already banned in Founding public copy).

---

## United States (must-haves if you have US users or market there)

### 1. COPPA (under 13)
- Do not knowingly collect data from under-13 without parental consent.
- Safer for BarathX: **block under-18** (same as India) so COPPA under-13 never arises.

### 2. State privacy (CCPA/CPRA California, and growing list)
- Privacy policy disclosures; “Do Not Sell/Share” if you ever sell/share for ads (we claim we don’t sell).
- Access / delete rights (already partly covered).

### 3. CAN-SPAM (email)
- **Transactional** (verify, reset): no unsubscribe required, but keep content transactional only.
- **Commercial / activity / marketing**: clear identification, **working unsubscribe**, honour promptly.
- Headers: `List-Unsubscribe` + `List-Unsubscribe-Post` on activity emails (API one-click URL).
- **Subscribe**: activity emails default ON at signup (with notice in Privacy); user can opt out.  
  **Marketing newsletters** (if added later): need **separate opt-in**, never bundled only into Privacy checkbox.

### 4. TCPA (SMS marketing)
- Marketing texts need prior express consent. OTP login/signup ≠ marketing consent.

---

## DOB + age consent (product rule)

| Field | Purpose | Public? |
|-------|---------|---------|
| Date of birth | Prove 18+; child-protection compliance | **Never** |
| Age attestation checkbox | Record that user confirmed accuracy | Internal consent log |
| Privacy / Terms checkbox | DPDP / contract | Internal |

**Consent page** (`/age-consent`): explains why DOB is asked, India + US child rules, that DOB is private. Linked from signup before account create.

---

## Email: where subscribe / unsubscribe live

| Action | Where |
|--------|--------|
| **Subscribe (activity emails)** | Default ON when you have an email. Re-enable: **Settings → Email notifications** → check “Send me activity emails (subscribe)” |
| **Unsubscribe (activity emails)** | 1) **Unsubscribe** link in every activity email footer → `/unsubscribe?token=…` 2) **Settings → Email notifications** (uncheck) 3) Gmail/Yahoo one-click via `List-Unsubscribe` header → API `POST /auth/unsubscribe` |
| **Transactional** (verify email, password reset) | Always sent when needed — **no unsubscribe** (account security) |
| **Marketing / promo blasts** | **Not built yet.** If added: separate subscribe checkbox + separate unsubscribe |

---

## Ship checklist (this release)

- [x] DOB + 18+ attestation on signup (email / phone / Google new accounts)
- [x] `/age-consent` notice page
- [x] Privacy / Terms children section updated (18+, DOB private)
- [x] `List-Unsubscribe` headers on activity emails
- [x] Settings copy clarifies subscribe / unsubscribe / transactional
- [ ] Counsel review of Privacy + age flow before US paid ads
- [ ] If marketing email product ships: double opt-in + separate unsub list

---

## Contacts

- Privacy / DPDP grievance: **privacy@barathx.com**
- Product ops: **hello@barathx.com**
