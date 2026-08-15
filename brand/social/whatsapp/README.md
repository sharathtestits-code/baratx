# BarathX — WhatsApp group marketing teaser

## Why this cut
Research for WhatsApp groups / Status / Channel (2026):
- **9:16 vertical**, **~24 seconds**, **MP4 H.264**, target **under 16MB**
- **Burned-in captions** — most people watch muted in groups
- **One CTA** at the end: https://barathx.com
- Hook first (WhatsApp pain), then product, then link

## Files
| File | Use |
|------|-----|
| `barathx-whatsapp-teaser.mp4` | **Primary** — send in WhatsApp groups / Channel / Status |
| `barathx-whatsapp-teaser-square.mp4` | Optional 1:1 if a group compresses vertical oddly |
| `barathx-whatsapp-teaser-poster.jpg` | Thumbnail / preview still |
| `render_whatsapp_teaser.py` | Re-render |

## Beats (website page in background)
1. Hook — landing page behind “WhatsApp takes disappear…”  
2. Brand — landing · India’s public square  
3. Square — real Square UI still  
4. Arenas — real Arenas UI still  
5. Live — real Live/Spaces UI still  
6. Promise — Home hub still · Human takes only  
7. CTA — signup page · https://barathx.com  

Screens live in `screens/` (`bx-site-*.png|jpg`).

## Paste message (send with the video)

```
WhatsApp takes disappear by Monday.

BarathX is India’s public square —
drop a take, pick a side, argue it live.
Human takes only. No AI slop.

Soft launch live in your browser (phone or desktop).
Apps coming soon.

→ https://barathx.com
```

### Shorter alt
```
Tired of debates dying in the group chat?

BarathX — India’s public square.
Square · Arenas · Live
Human takes only.

→ https://barathx.com
```

Re-render: `python3 brand/social/whatsapp/render_whatsapp_teaser.py`
