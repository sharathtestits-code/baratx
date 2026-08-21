# BarathX — daily WhatsApp + X + LinkedIn (2×/day)

**Draft + email only.** Never auto-post to WhatsApp, X, or LinkedIn. You paste after the ready email.

**Companion:** [README.md](./README.md) · [../../ig/CONTENT-RULES.md](../../ig/CONTENT-RULES.md) · [../FOUNDING-PUBLIC-COPY.md](../FOUNDING-PUBLIC-COPY.md)

---

## Schedule (IST)

| Time | Slot | Channels |
|------|------|----------|
| **09:00** | Morning | WhatsApp + X + LinkedIn |
| **20:00** | Evening | WhatsApp + X + LinkedIn |

### Preferred: GitHub Action (already in repo)

Workflow: `.github/workflows/daily-social-pack.yml`

- Cron: `30 3 * * *` (09:00 IST) and `30 14 * * *` (20:00 IST)
- Builds: rotating **feature** + **trending** stills + **~20s reel** + `PACK.md`
- Emails: **Your BarathX post is ready** (Resend / SMTP secrets, or Railway `/admin/social-pack-notify`)
- Commits: `brand/social/daily/YYYY-MM-DD/`

**Repo secrets to set (GitHub → Settings → Secrets):**

| Secret | Purpose |
|--------|---------|
| `RESEND_API_KEY` | Send ready email |
| `RESEND_FROM` | optional From address |
| `SOCIAL_PACK_EMAIL` | defaults toward owner Gmail if unset on Railway |
| `ADMIN_SECRET` | fallback: call prod notify endpoint when Resend isn’t in Actions |

Manual run: Actions → **Daily social pack** → Run workflow.

### Optional: Cursor Automation

Paste into [Cursor Automation](https://cursor.com/automations) if you want an agent review pass. Agents cannot create automations via API.

Suggested crons (Asia/Kolkata): `0 9 * * *` and `0 20 * * *`  
Repo: `sharathtestits-code/baratx` · Branch: `main`

---

## Automation prompt (copy/paste)

```
You prepare BarathX’s daily social pack (WhatsApp + X + LinkedIn). Draft only — do not post anywhere (especially not WhatsApp).

Read first:
- brand/social/daily/README.md
- brand/social/daily/AUTOMATION.md
- brand/social/daily/features.py
- brand/ig/CONTENT-RULES.md
- brand/social/FOUNDING-PUBLIC-COPY.md
- Recent folders under brand/social/daily/ so today’s pack is not a repeat

Rules:
- Brand spelling: BarathX only (never BaratX / BharathX)
- Cadence: TWO posts today (morning + evening IST) × WhatsApp + X + LinkedIn
- Each day covers a DIFFERENT product feature (rotation in features.py) + India trending hook + different still template
- Include ~20s 9:16 reel (barathx-daily-reel-20s.mp4)
- Structure each post: trend → feature highlight → signup CTA + https://barathx.com
- Never mention Founding ₹ / ₹150 / UPI / cash. If Founding is mentioned, use exactly: “100 Founding spots, earned by opening a debate that gets real engagement, not by signing up.”
- Prefer timely India hooks without partisan campaigning or fake traction
- Short, paste-ready copy

Preferred one-shot:
  python3 brand/social/daily/build_daily_pack.py --approve --notify

Or step-by-step:
1) python3 brand/social/daily/build_daily_pack.py --date YYYY-MM-DD --approve --notify
2) Confirm brand/social/daily/YYYY-MM-DD/ has PACK.md, stills, reel, NOTIFY-PREVIEW-*.md (or email sent)

Commit and open a PR titled “Daily social pack YYYY-MM-DD” if allowed.

In the run summary: feature of the day, trend hook, both slots’ WA + X + LinkedIn copy, image paths, reel path. Say “awaiting approve” if MOCKUP ribbon is on.
```

---

## Manual create steps (Sharath) — Cursor Automation

1. Open https://cursor.com/automations → **New automation**
2. Name: `BarathX daily AM pack` (repeat for PM)
3. Trigger: **Scheduled** → **09:00** (and second automation **20:00**) · timezone **Asia/Kolkata**
4. Repository: **`sharathtestits-code/baratx`** · branch **`main`**
5. Paste the prompt → **Save** → **Activate**
6. When email says **Your BarathX post is ready** → open pack → paste to WhatsApp / X / LinkedIn yourself

---

## Approval loop

1. Agent/Action ships mockups with **MOCKUP · APPROVE** ribbon (or `--approve` for finals)
2. You reply `approve all` (or AM/PM / tweaks) if mockups
3. Re-run with `--approve` and re-send ready email
4. You post manually — never auto-blast WhatsApp
