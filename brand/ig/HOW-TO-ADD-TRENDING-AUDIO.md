# Instagram audio — how we pick it (BarathX)

## Hard limit (read this first)

| Post type | Can we attach trending IG music? |
| --- | --- |
| **Feed carousel / single image** (what Graph API auto-posts) | **No.** Meta Graph API cannot search or attach Instagram’s music library to feed posts. |
| **Reel** | **Yes — only inside the Instagram app** (or Creator Studio). We pick audio manually at publish. |

So: today’s auto IG slots (carousels) ship **without** a trending sound sticker. Trending music applies when we post a **Reel**.

## How we pick audio for Reels (the rubric)

We don’t chase whatever is #1 globally if it fights the brand. Order of checks:

1. **India / Gen Z discovery** — open IG Reel composer → **Trending** (region follows the account’s audience; `@getbarathx` ≈ India). Prefer tracks already on Reels in India that week.
2. **Mood fit for BarathX** — energetic / street / argumentative / “prove it” energy. Skip soft luxury, wedding, baby, ASMR, or anything that reads corporate.
3. **Length** — 15–45s Reel; pick a track with a clear hook in the first 1–2s (or trim to the drop).
4. **Lyric / vibe check** — no lyrics that undercut “human takes / no AI slop / pick a side.” If lyrics dominate, use an instrumental trending bed.
5. **Reuse rule** — same sound max **2× / week** so we don’t look like a spam page; rotate.
6. **Mute-first design** — text on screen still carries the message if audio is off (most scroll muted first).

### Quick picker (when you’re in the IG app)

1. Create Reel → upload clip  
2. Tap **Audio** → **Trending** (or search a sound you already saw on India Gen Z Reels)  
3. Apply → trim to the hook  
4. Paste caption (includes X + WhatsApp footers)  
5. Share  

Tip: upload muted / weak bed first, then replace with trending audio so the **sound sticker** shows (better discovery).

## What “I” (the agent) will do

| Situation | Action |
| --- | --- |
| Auto carousel schedule | Post visuals + caption via API — **no music** (impossible via API) |
| You send a real Live/face-cam clip | I’ll cut a Reel-ready file + caption; **you or I (computer-use / you in app) attach trending audio in IG** before share |
| Drive `Social Draft` asks for a Reel | Same — draft copy sacred; audio attached in-app at publish |

## Recommended sounds this week (refresh weekly)

Open IG on the posting phone → Reels → Audio → **Trending** and pick the first that passes the mood fit above.  
I can’t list Meta’s live trending catalog from the API — it only appears in-app.

When we have a Reel to ship, I’ll note in the run log:  
`audio: [track name / artist] · source: IG Trending · trim: 0:xx–0:yy`

## Cross-links reminder
Captions still include app + the other platforms (IG↔X↔WhatsApp) per `brand/social/LINKS.md`.
