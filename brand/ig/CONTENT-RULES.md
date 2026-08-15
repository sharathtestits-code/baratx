# BarathX IG content rules

## Brand spelling (non-negotiable)
**BarathX** — never BaratX, never BharathX. Captions, slides, hashtags, CTAs.

## Primary job of every post
Make a stranger understand **why they should sign up** at barathx.com.

Not: “here is a feature.”
Yes: “here is the pain → BarathX fix → create an account.”

## Visuals
Each daily slot uses a **different** pack **and** a **rotating template** (never the same look every day):
- morning → pain / signup-excite energy
- midday → how-it-works / product proof
- evening → launch-pain / debate prompt

Generate today’s three creatives (different templates via date hash):

```bash
python3 brand/ig/render_daily_ig.py --date YYYY-MM-DD --all-slots
```

Outputs in `brand/social/daily/YYYY-MM-DD/ig-{morning,midday,evening}.jpg` (plus a named template file).
Do **not** reuse yesterday’s identical frame for all three posts.

## Caption formula
1. **Hook pain** (1 line) — something they already feel
2. **Product proof** (1–2 lines) — one feature/mechanic
3. **Signup CTA** (1 line) — sign up / join / leave first take
4. **barathx.com**
5. **Hashtags**

## Visual rule
Headline on creative should sell the *outcome* (why join), not only the feature name.
Example: “Your takes die in group chats” > “220-char replies”

## Always include
- Clear reason to create an account
- One concrete next step (sign up / comment BX / pick a side)

## Founding 100 (surprise — don't advertise pay)
- Public line only: **100 Founding spots, earned by opening a debate that gets real engagement, not by signing up.**
- **Never** put ₹150 / any rupee amount in captions, bios, carousels, or Reels about Founding.
- Cash thank-you is private, in-app, only after someone has already earned the spot.
- Full rule: `brand/gtm/SALES-GROWTH-BRIEF.md` · `brand/social/FOUNDING-PUBLIC-COPY.md`
