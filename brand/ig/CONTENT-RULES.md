# BarathX IG content rules

## Brand spelling (non-negotiable)
**BarathX** — never BaratX, never BharathX. Captions, slides, hashtags, CTAs.

## Primary job of every post
Make a stranger understand **why they should sign up** at barathx.com.

Not: “here is a feature.”
Yes: “here is the pain → BarathX fix → create an account.”

## Visuals (product-first — no blank type slides)
Auto IG carousels must show **real BarathX UI** (Square / Arenas / Live / signup / Home) in phone frames, crisp dark + saffron type — never empty gradient text cards.

| IST slot | Pack folder | Energy |
|----------|-------------|--------|
| Morning 09:00 | `brand/ig/carousel/signup-excite/` | pain → signup |
| Midday 13:30 | `brand/ig/carousel/how-it-works/` | product proof |
| Evening 20:00 | `brand/ig/carousel/launch-pain/` | debate CTA |

Regenerate all packs (6 slides each, 1080×1080 JPG):

```bash
python3 brand/ig/render_product_carousels.py
```

Optional single-frame daily aliases:

```bash
python3 brand/ig/render_daily_ig.py --date YYYY-MM-DD --all-slots
```

Do **not** reuse one pack for all three slots. Do **not** ship slides without product screens.

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
