# BarathX — daily WhatsApp + X Cursor Automation

Paste into a new [Cursor Automation](https://cursor.com/automations). Agents cannot create automations via API — create once in the dashboard.

**Companion:** [README.md](./README.md) · [../ig/CONTENT-RULES.md](../../ig/CONTENT-RULES.md) · [../FOUNDING-PUBLIC-COPY.md](../FOUNDING-PUBLIC-COPY.md)

---

## Suggested schedule

| Cadence | Goal |
|---------|------|
| **Daily 09:00 IST** | 1 WhatsApp community post + 1 X post (copy + images) |

Trigger: **Scheduled** · Repo: `sharathtestits-code/baratx` · Branch: `main`  
Cron: `0 9 * * *` with timezone **Asia/Kolkata** (or UTC `30 3 * * *`)

---

## Automation prompt (copy/paste)

```
You prepare BarathX’s daily social pack (WhatsApp community + X). Draft only — do not post anywhere.

Read first:
- brand/social/daily/README.md
- brand/social/daily/AUTOMATION.md
- brand/ig/CONTENT-RULES.md
- brand/social/FOUNDING-PUBLIC-COPY.md
- Recent folders under brand/social/daily/ so today’s pack is not a repeat

Rules:
- Brand spelling: BarathX only (never BaratX / BharathX)
- Cadence: 1 WhatsApp community post + 1 X post for today (use IST date)
- Structure: pain → BarathX fix → signup CTA; include https://barathx.com
- Never mention Founding ₹ / ₹150 / UPI / cash. If Founding is mentioned, use exactly: “100 Founding spots, earned by opening a debate that gets real engagement, not by signing up.”
- Short, paste-ready copy; match tone of brand/social/daily/2026-08-14/PACK.md
- Prefer timely hooks (festivals, soft launch, India debate culture) without inventing fake traction

Create brand/social/daily/YYYY-MM-DD/ (today’s IST date) with:
1) PACK.md — WhatsApp community + X sections; each with Image filename + Post body in a fenced code block
2) Image assets for WA + X, referenced from PACK.md

Commit and open a PR titled “Daily social pack YYYY-MM-DD” if allowed; otherwise write files and stop.

In the run summary for Sharath: paste both posts in full + say where the images are.
```

---

## Manual create steps (Sharath)

1. Open https://cursor.com/automations → **New automation** (or https://cursor.com/automations/new)
2. Name: `BarathX daily WhatsApp + X pack`
3. Trigger: **Scheduled** → every day **09:00** · timezone **Asia/Kolkata** (cron `0 9 * * *`)
4. Repository: **`sharathtestits-code/baratx`** · branch **`main`** (required — cron defaults to no repo)
5. Tools: allow **Pull requests** / repo write so packs land as PRs
6. Paste the prompt above → **Save** → **Activate**
7. Run once manually → confirm `brand/social/daily/YYYY-MM-DD/PACK.md` looks right
8. Each morning: open the agent run → copy WA + X into WhatsApp / X yourself (never auto-blast)

---

## Plan note

Automations need Cursor **Pro+** (or Teams) with Cloud Agents. Each run bills as a Cloud Agent.
