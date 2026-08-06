# BaratX Instagram — 2×/day carousel

## Goal
Two carousel posts per day that show the **real BaratX app** and drive people to [barathx.com](https://barathx.com).

## How posting works (important)
We post through **Meta Graph API** (Instagram Professional / Business account linked to a Facebook Page).

We do **not** log in with Instagram username/password in a bot — that gets accounts restricted and breaks 2FA.

### What to share with the agent (once)
1. Instagram **Professional** account username (e.g. `@baratx`)
2. Facebook Page connected to that IG account
3. Meta app with `instagram_content_publish`, `pages_show_list`, `instagram_basic` (or newer equivalents)
4. Long-lived **Page access token** + **IG Business Account ID**

Save as Railway / local env (never commit):

```bash
INSTAGRAM_ACCESS_TOKEN=...
INSTAGRAM_BUSINESS_ACCOUNT_ID=...
# optional
INSTAGRAM_USERNAME=baratx
```

Then: `python3 brand/social/instagram/post_carousel.py --pack morning`

## Assets
Carousel slides (1080×1080), in order:

`brand/carousel/export/slide-01.png` … `slide-10.png`

Regenerate from real app screens:

```bash
cd brand/carousel && python3 render_slides.py
```

## Cadence (IST)
| Slot | Time | Pack |
|------|------|------|
| Morning | ~10:30 | `morning` — product story / “India’s public square” |
| Evening | ~19:30 | `evening` — debate / civic / Founding 100 angle |

Max **2 posts/day**. Marker in caption: `#BaratXApp` (for ops search).

## Captions (rotate — pick one per slot)

### Morning A — square
India doesn’t need another foreign firehose.
It needs a **public square**.

BaratX = short posts, real replies, arenas that matter —
Sports · Politics · Entertainment · News · Spirituality.

Open the app. Drop your city. Argue like you mean it.
→ barathx.com

#BaratX #BaratXApp #IndiaPublicSquare #MakeInIndia #IndianApp #SocialMediaIndia #Hyderabad #DesiTwitter #CivicIndia #PublicSquare

### Morning B — product
Stop scrolling. Start arguing.

Inside BaratX:
• Home feed that feels Indian
• Arenas for real fights
• Replies > empty likes

Built in India. For India.
→ barathx.com

#BaratX #BaratXApp #IndianStartup #ProductHuntIndia #TechIndia #SocialApp #Debate #BarathX

### Evening A — civic
Your city has a take. The feed should hear it.

Post one real problem from your street / ward / campus on BaratX.
Founding voices get seen — and rewarded for **real** civic posts.

→ barathx.com

#BaratX #BaratXApp #CivicTech #India2026 #LocalIssues #Hyd #Telangana #Democracy #PublicSquare #Founding100

### Evening B — FOMO
Every social app you use was built for someone else.

Culture. Language. Rules. Not ours.

BaratX is India’s own public square.
Comment **BX** if you want the link — or just go: barathx.com

#BaratX #BaratXApp #IndiaFirst #DesiApp #ViralIndia #InstagramIndia #StartupIndia #JoinBaratX

## Manual backup
If API token isn’t ready: upload `slide-01`→`slide-10` in Instagram app, paste a caption from above.
