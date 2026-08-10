# Traction ops — rewards evaluation

Arenas: Sports · Politics · Entertainment · News · Spirituality · Startups

## How we evaluate (not AI, not self-claim alone)

| Step | Signal | What it means |
|------|--------|----------------|
| 1. Floor | Problem post ≥50 chars + flag, OR open any arena debate | They did a real action |
| 2. Community rating | Likes / replies (problems) or stances / debate posts | India cared — this is the rating |
| 3. Admin payout | You send UPI + Mark paid | Human veto for spam / self-like rings |

**Founding 100 (membership; private ₹150 thank-you once):**

- **Public pitch (only):** `100 Founding spots, earned by opening a debate that gets real engagement, not by signing up.` — **no ₹ in any public/surface copy**
- **Private (after `payable`):** `You're in. Small thank-you on the way — ₹150, no strings.`
- Status `eligible` = floor cleared (still no amount shown in product API/UI)
- Status `payable` = rating bar met (≥25 likes **or** ≥5 replies from someone else; debates: ≥2 stances **or** ≥3 posts) → reveal thank-you amount
- Pay when `payable` (or after manual review if you intentionally override)
- Brief: `brand/gtm/SALES-GROWTH-BRIEF.md`

**Square Race (every 14 days, ₹150–₹500):**
- Ranking = highest likes on a Home post in the fortnight
- Prize scales with likes (min 25 likes to win; caps at ₹500)
- Admin → Lock current leader → Mark paid after UPI
- Keep Race prize talk separate from Founding public pitch

## Who sees what

| Who | Where | What they see |
|-----|--------|----------------|
| Logged-out | Landing / marketing | Public Founding line only — no ₹ |
| Logged-in (not yet payable) | Home strips + **/rewards** | Spots + progress — no ₹ |
| Logged-in (`payable` / `paid`) | Strip + **/rewards** | Surprise thank-you with ₹150 |
| Blue account | **/rewards** → Blue ops view | Read-only founding queue + race top (no Mark paid) |
| Ops (ADMIN_SECRET) | **/bx-ops** | Full tables + amounts, Mark paid, Lock race winner |

Users **don’t rate themselves**. Progress = likes/replies India gives them. They watch the meter on `/rewards`.

> 100 Founding spots, earned by opening a debate that gets real engagement, not by signing up. barathx.com

## Don’t
- Advertise Founding ₹150 (or any amount) in bios, outreach, posts, or pre-earn UI
- Pay for bare signup
- Promise “we verify your problem with officials”
- Ignore admin Mark paid — that’s the anti-fraud step
