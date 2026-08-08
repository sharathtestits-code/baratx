# Audit Week 1 — product fixes (Aug 8, 2026)

Shipped on `cursor/audit-week1-prod-2af5` → **merged to `main`** and live.

## Production

- **Frontend:** https://barathx.com (debate-first landing + Square home)
- **API + SPA mirror:** https://baratx-production.up.railway.app
- **E2E recording:** `/opt/cursor/artifacts/baratx-audit-e2e-signup-to-features-demo.mp4`

## Done (code)

1. **Mobile FAB overlap** — Compose FAB hidden on Square `/feed`, live rooms, rewards/settings.
2. **Arenas ≠ Communities** — Communities API filters `is_arena=False`; copy on Arenas/Communities/landing/menu.
3. **Founding ₹150** — landing hero, first-session footnote, Arenas featured strip, menu, Settings.
4. **Debate-first landing** — “Pick a side. Argue it live.” + Answer today's question / Watch a live debate + FAQ + Startups-first.
5. **Today's Square** remounted on returning home.
6. **Guidelines** page + badges legend (Settings + Guidelines).
7. **Less botty seeding** — varied debate titles; Startups = Fund it/Pass; digest densified to 1 arena/slot with Startups weight.
8. **Railway serves SPA** — Docker multi-stage builds frontend into the API image (same-origin fallback).

## Ops still needed (not code)

- Recruit 20–30 builders into Startups Arena; open 3–5 Fund it/Pass rooms.
- Add `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` GitHub secrets so `.github/workflows/deploy-pages.yml` can redeploy Pages on every main push.
- Pay out Founding rewards when rooms qualify.
