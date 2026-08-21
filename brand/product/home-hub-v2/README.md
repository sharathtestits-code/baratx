# Home hub v2 — Overview / Tagged / Following / My posts

**Status:** Approved and shipped in product code (`Home.jsx` + `feed=mine`).  
**Problem:** Home stacked Tagged + Following (+ more) as one long feed. Fine with few users; noisy at scale.

## Shipped design

**Segmented Home:** `Overview` · `Tagged` · `Following` · `My posts`

| Tab | What it shows |
|-----|----------------|
| **Overview** | Compact previews only — max **2–3** items per block + **See all** (jumps to that tab) |
| **Tagged** | Full mentions inbox (`feed=mentions`) |
| **Following** | People you follow (`feed=following`) |
| **My posts** | Your posts (`feed=mine`) |

Same pattern on **desktop web**, **mobile web**, and **native app** (one React Home; Capacitor inherits it).

### Why this
- Mentions feel like an **inbox**, not mixed into following noise  
- Overview stays a **dashboard**, not an endless stream (Square stays the stream)  
- Counts on chips (`Tagged 12`) scale as volume grows  

### Mockups
- `home-hub-desktop-tabs-mockup.png` — desktop Overview  
- `home-hub-mobile-overview-mockup.png` — mobile Overview  
- `home-hub-mobile-tagged-tab-mockup.png` — mobile Tagged tab  
