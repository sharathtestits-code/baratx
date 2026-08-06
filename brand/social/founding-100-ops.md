# Traction ops — rewards evaluation

Arenas: Sports · Politics · Entertainment · News · Spirituality

## How we evaluate (not AI, not self-claim alone)

| Step | Signal | What it means |
|------|--------|----------------|
| 1. Floor | Problem post ≥50 chars + flag, OR open any arena debate | They did a real action |
| 2. Community rating | Likes / replies (problems) or stances / debate posts | India cared — this is the rating |
| 3. Admin payout | You send UPI + Mark paid | Human veto for spam / self-like rings |

**Founding 100 (₹150, first 100 people, once):**
- Status `eligible` = floor cleared
- Status `payable` = rating bar met (≥25 likes **or** ≥5 replies from someone else; debates: ≥2 stances **or** ≥3 posts)
- Pay when `payable` (or after manual review if you intentionally override)

**Square Race (every 14 days, ₹150–₹500):**
- Ranking = highest likes on a Home post in the fortnight
- Prize scales with likes (min 25 likes to win; caps at ₹500)
- Admin → Lock current leader → Mark paid after UPI

## Who sees what

| Who | Where | What they see |
|-----|--------|----------------|
| Logged-out | — | Nothing (no reward strips) |
| Logged-in user | Home strips + **/rewards** | Own Founding steps + race rank / scoreboard |
| Blue account | **/rewards** → Blue ops view | Read-only founding queue + race top (no Mark paid) |
| Admin (ADMIN_SECRET) | **/admin** | Full tables, Mark paid, Lock race winner |

Users **don’t rate themselves**. Progress = likes/replies India gives them. They watch the meter on `/rewards`.

> Post a real city problem or open any arena debate. First 100 get ₹150 after people engage. Every 2 weeks the highest-liked Home post wins up to ₹500. barathx.com

## Don’t
- Pay for bare signup
- Promise “we verify your problem with officials”
- Ignore admin Mark paid — that’s the anti-fraud step
