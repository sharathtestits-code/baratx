# Daily peak digest + welcome replies

## New-user auto-replies (first Home post only)
Two replies — official engagement, **never counts toward Founding rewards**:

1. **@baratx** — Welcome to BaratX… what’s your city…
2. **@sharath** — Hey @{user} — Sharath here. Drop one real take…

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
- Markers: `#BaratXDaily` + `#BXMorning` / `#BXMidday` / `#BXEvening`

## Rewards exclusion
Likes/replies from `@baratx`, `@sharath`, other seeded officials, and any `blue` / `is_official` account are **ignored** for Founding payable + race like counts.

## Manual
Admin → **Run peak digest now** (`POST /admin/daily-digest?force=true&slot=morning|midday|evening`).

## Infra note
Scheduler runs in the API process. For multi-instance Railway deploys, move to a single worker / cron later.
