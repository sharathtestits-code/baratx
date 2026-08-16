# BarathX — daily WhatsApp + X + LinkedIn (2×/day)

Paste into [Cursor Automation](https://cursor.com/automations). Agents cannot create automations via API — create once in the dashboard.

**Companion:** [README.md](./README.md) · [../../ig/CONTENT-RULES.md](../../ig/CONTENT-RULES.md) · [../FOUNDING-PUBLIC-COPY.md](../FOUNDING-PUBLIC-COPY.md)

---

## Schedule (IST)

| Time | Slot | Channels |
|------|------|----------|
| **09:00** | Morning | WhatsApp + X + LinkedIn |
| **20:00** | Evening | WhatsApp + X + LinkedIn |

Create **two** automations (or one cron with slot detection from clock hour).

Suggested crons (Asia/Kolkata):
- Morning: `0 9 * * *`
- Evening: `0 20 * * *`

Repo: `sharathtestits-code/baratx` · Branch: `main`  
**You post manually** after the “post is ready” email — never auto-blast.

---

## Automation prompt (copy/paste)

```
You prepare BarathX’s daily social pack (WhatsApp + X + LinkedIn). Draft only — do not post anywhere.

Read first:
- brand/social/daily/README.md
- brand/social/daily/AUTOMATION.md
- brand/ig/CONTENT-RULES.md
- brand/social/FOUNDING-PUBLIC-COPY.md
- Recent folders under brand/social/daily/ so today’s pack is not a repeat

Rules:
- Brand spelling: BarathX only (never BaratX / BharathX)
- Cadence: TWO posts today (morning + evening IST) × WhatsApp + X + LinkedIn
- Structure each post: pain/trend → BarathX fix/highlight → signup CTA + https://barathx.com
- Cover product highlights across the day: Square · Arenas · Live · human-first / AI demotion · soft launch · Founding public line (no ₹)
- Never mention Founding ₹ / ₹150 / UPI / cash. If Founding is mentioned, use exactly: “100 Founding spots, earned by opening a debate that gets real engagement, not by signing up.”
- Prefer timely India hooks (culture, campus, soft launch, AI-in-feeds) without partisan campaigning or fake traction
- Short, paste-ready copy

Create brand/social/daily/YYYY-MM-DD/ (today’s IST date) with:
1) PACK.md — Post 1 Morning + Post 2 Evening; each channel has Image filename + Post body in a fenced code block
2) APPROVAL.md — list images awaiting Sharath approval
3) Images via: python3 brand/social/daily/render_daily_crosspost.py --date YYYY-MM-DD
4) After writing pack, run: python3 brand/social/daily/notify_pack_ready.py --date YYYY-MM-DD --slot all
   (emails “Your BarathX post is ready”; if email env missing, NOTIFY-PREVIEW-*.md is enough)

Commit and open a PR titled “Daily social pack YYYY-MM-DD” if allowed.

In the run summary: paste both slots’ WA + X + LinkedIn copy + image paths + say “awaiting approve” if MOCKUP ribbon is on.
```

---

## Manual create steps (Sharath)

1. Open https://cursor.com/automations → **New automation**
2. Name: `BarathX daily AM pack` (repeat for PM)
3. Trigger: **Scheduled** → **09:00** (and second automation **20:00**) · timezone **Asia/Kolkata**
4. Repository: **`sharathtestits-code/baratx`** · branch **`main`**
5. Paste the prompt → **Save** → **Activate**
6. When email says **Your BarathX post is ready** → open pack → paste to WhatsApp / X / LinkedIn yourself

---

## Approval loop

1. Agent ships mockups with **MOCKUP · APPROVE** ribbon  
2. You reply `approve all` (or AM/PM / tweaks)  
3. Agent re-renders with `--approve` and re-sends ready email  
4. You post  
