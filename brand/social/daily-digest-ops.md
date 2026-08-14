# Daily peak digest + welcome replies

## New-user first post
1. **One official voice** (`@baratx` or `@sharath`) — welcome that nods to their take
2. Support/bugs → always `@baratx`

## Every later community post
**One** official reply that reacts to the post topic (not twin bots).
Official digest posts are skipped.

Runs on `POST /posts` and a background poller (~45s) for anything missed.
Disable: `DISABLE_OFFICIAL_ENGAGE=1`

Official likes/replies **never** count toward Founding / Race.

## Peak auto-posts (3×/day IST — not all day)
Slots: **09:00 · 13:30 · 20:00 IST**

Per slot (2 arenas, rotated so every floor including **Startups** gets coverage):

1. **@baratx** — Daily glimpse (headline + named publisher only)
2. **@sharath** — Response take on the same story
3. **@sharath** replies on the admin post
4. **@baratx** replies on Sharath’s post
5. **Mutual likes** on both posts and both replies

### Credibility rules
- Google News RSS, **credible publishers only** (PIB / PTI / ANI / Reuters / The Hindu / Indian Express / ET / LiveMint / Inc42 / etc.)
- Soft-penalize horoscope, listicles, rumours, clickbait
- **No invented facts** — copy is headline + source + debate CTA only
- Markers: `#BarathXDaily` + `#BXMorning` / `#BXMidday` / `#BXEvening`

## Rewards exclusion
Likes/replies from `@baratx`, `@sharath`, other seeded officials, and any `blue` / `is_official` account are **ignored** for Founding payable + race like counts.

## Manual
Admin → Engage tab still works for extra human comments.
Ops → **Run peak digest now** (`POST /admin/daily-digest?force=true&slot=morning|midday|evening`).

## Infra note
Scheduler runs in the API process. For multi-instance Railway deploys, move to a single worker / cron later.
