# BarathX — WhatsApp / Instagram marketing teaser

## Why this cut
- **9:16 Instagram Reel template** (1080×1920) with safe zones so logo + captions aren’t covered by IG UI
- Same story still works in **WhatsApp** groups / Status / Channel
- **~24 seconds**, **MP4 H.264**, burned-in captions (muted viewing)
- **One CTA** at the end: https://barathx.com

## Safe zones (Reel)
- Top ~320px reserved (username / audio)
- Bottom ~440px reserved (captions / buttons)
- Logo, plates, and CTA stay in the middle band

## Files
| File | Use |
|------|-----|
| `barathx-whatsapp-teaser.mp4` | **Primary** — IG Reels / Stories / WhatsApp Status |
| `barathx-whatsapp-teaser-square.mp4` | Feed / LinkedIn square (composed, not center-cropped) |
| `barathx-whatsapp-teaser-poster.jpg` | Thumbnail |
| `render_whatsapp_teaser.py` | Re-render |

## Beats (website page in background)
1. Hook — landing · WhatsApp takes disappear…  
2. Brand — India’s public square  
3. Square — real Square UI  
4. Arenas — real Arenas UI  
5. Live — real Live UI  
6. Promise — Human takes only  
7. CTA — https://barathx.com  

Screens live in `screens/` (`bx-site-*.png|jpg`).

## Paste message

```
WhatsApp takes disappear by Monday.

BarathX is India’s public square —
drop a take, pick a side, argue it live.
Human takes only. No AI slop.

Soft launch live in your browser (phone or desktop).
Apps coming soon.

→ https://barathx.com
```

Re-render: `python3 brand/social/whatsapp/render_whatsapp_teaser.py`
