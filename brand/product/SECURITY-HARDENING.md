# BarathX — anti-hack / security hardening checklist

**Not a guarantee of “unhackable.”** No website is. Goal: remove easy attack paths and make abuse expensive.  
Last updated: 2026-08-27 · Site: https://barathx.com

---

## Already protecting the site

| Layer | What it blocks |
|-------|----------------|
| HTTPS + HSTS | Downgrade / cookie theft on cleartext |
| Security headers (nosniff, frame DENY, CSP on Pages) | Clickjacking, some XSS, MIME tricks |
| bcrypt passwords + hashed OTPs | Stolen DB password/OTP reuse |
| JWT with token version + “Sign out everywhere” | Stolen session after reset/revoke |
| Rate limits on login / signup / forgot / OTP / admin | Brute force, SMS spam |
| Cloudflare Turnstile on email/Google signup | Bot account farms |
| Phone OTP preferred (no bot check needed for humans) | Bots without SIMs |
| CORS allowlist (prod) + Bearer tokens (no cookies) | Cross-site credential abuse |
| Text sanitisation (no HTML posts) | Stored XSS via posts |
| Image upload MIME + magic-byte checks | Malicious uploads |
| Admin secret + ops owner path (not public `/admin`) | Random admin probing |
| Anti-scrape UA / bulk-read throttles | Mass scrapers |
| OpenAPI docs off in production | API map for attackers |
| Strong `JWT_SECRET` required in production | Trivial token forging |

---

## What we harden in this pass

- HSTS on API + Pages; CSP allows Turnstile; Railway SPA gets CSP/HSTS
- Rate limits on password reset, email verify/resend, OTP verify (+ OTP by IP)
- Login / Google redirects use allowlisted `safeNextPath` only
- CORS methods/headers tightened
- Legacy plaintext OTP compare removed

---

## Still recommended (ops / later)

1. **Cloudflare** — WAF, bot fight, DDoS (already in front of Pages; keep API behind CF too if possible)
2. **Shared rate store (Redis)** when Railway runs multiple replicas (in-memory resets per instance)
3. **Hash email-verify / password-reset tokens at rest** (DB leak → less useful)
4. **Short JWT TTL** + refresh (already ~2 days; can go shorter)
5. **Dependency updates** + Dependabot / CI security scan
6. **Secrets rotation** playbook (`JWT_SECRET`, `ADMIN_SECRET`, MSG91, Resend)
7. **Counsel / pen-test** before serious US/ad spend
8. Never put secrets in the frontend repo; keep `ADMIN_SECRET` only for owners

---

## User-facing truth

We can make hacking **hard and noisy**. We cannot promise “zero option for hacking.” Honest Settings copy: rate limits, hashed passwords, session revoke, private email/phone/DOB.
