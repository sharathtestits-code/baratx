# Home hub v2 — organize Tagged / Following / My posts

**Status:** Mockups only — awaiting Sharath approval before code.  
**Problem:** Home stacks Tagged you + Following activity (+ more) as one long feed. Fine with few users; noisy at scale.

## Proposal (recommended)

**Segmented Home:** `Overview` · `Tagged` · `Following` · `My posts`

| Tab | What it shows |
|-----|----------------|
| **Overview** | Compact previews only — max **2–3** items per block + **See all** (jumps to that tab) |
| **Tagged** | Full mentions inbox (`feed=mentions`) |
| **Following** | People you follow (`feed=following`) |
| **My posts** | Your posts (`feed=mine` — wire if missing) |

Same pattern on **desktop web**, **mobile web**, and **native app** (one React Home; Capacitor inherits it).

### Why this
- Mentions feel like an **inbox**, not mixed into following noise  
- Overview stays a **dashboard**, not an endless stream (Square stays the stream)  
- Counts on chips (`Tagged 12`) scale as volume grows  

### Mockups
- `home-hub-desktop-tabs-mockup.png` — desktop Overview  
- `home-hub-mobile-overview-mockup.png` — mobile Overview  
- `home-hub-mobile-tagged-tab-mockup.png` — mobile Tagged tab  

## Alternatives (if you prefer)

**A. Collapsible sections only** — keep one page, default collapse Following after 2, expand on tap. Less clear than tabs.

**B. Move Tagged → Notifications only** — Home becomes Following + Continue only. Mentions leave Home.

## Out of scope until approved
No Home.jsx / CSS changes until you pick a direction (recommend **tabs** as above).
