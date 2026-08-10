# BarathX — Git branches (PROD / QA / DEV)

| Branch | Role | Deploys to |
|--------|------|------------|
| **`main`** | **PROD** — live users only | `https://barathx.com` + Railway `baratx-production` |
| **`qa`** | **QA / staging** — test before prod | `https://qa.barathx.com` + Railway `baratx-qa` |
| **`dev`** | **Development** — integration / WIP | Local + optional preview; not prod |

Feature work uses short-lived branches (`cursor/…`) and merges **up** the ladder — never commit straight to `main` for day-to-day work.

```
feature / cursor/*  →  PR into `dev`
`dev`               →  PR into `qa`     (QA validates here)
`qa`                →  PR into `main`   (prod release)
```

Hotfix for prod: branch from `main` → PR into `main` → immediately cherry-pick or merge back into `qa` and `dev` so they don’t drift.

## Hosting wiring (ops checklist)

Do this once in each dashboard so branches match environments:

### Cloudflare Pages

| Project | Production branch | Site |
|---------|-------------------|------|
| `baratx` (prod) | **`main`** | barathx.com |
| `baratx-qa` | **`qa`** (not `main`) | qa.barathx.com |

### Railway

| Service | Watch / deploy branch | API |
|---------|----------------------|-----|
| Production API | **`main`** | baratx-production.up.railway.app |
| QA API | **`qa`** | baratx-qa.up.railway.app |

`dev` does not auto-deploy to prod or QA. Use local Docker / optional preview builds.

## Rules

1. **`main` = PROD.** Only promote from `qa` after QA sign-off.
2. Automation / Playwright / Cursor QA agents use **QA URLs** and preferably the **`qa`** branch — never point destructive tests at prod.
3. Keep secrets separate (QA `ADMIN_SECRET` ≠ prod).
4. After merging to `main`, confirm prod deploy; then ensure `dev` / `qa` are updated (merge `main` back or continue the ladder so tips don’t diverge for long).

See also: [ENVIRONMENTS.md](./ENVIRONMENTS.md) · [DEPLOY.md](../../DEPLOY.md) · [MVP.md](./MVP.md)

## Prod MVP version

`main` (PROD) carries an incrementing label: **MVP1**, **MVP2**, **MVP3**, …

- Source of truth: repo-root [`VERSION`](../../VERSION) (integer)
- Each push to `main` (except the bump commit itself) runs [`.github/workflows/bump-mvp.yml`](../../.github/workflows/bump-mvp.yml) and bumps the number
- Shown in Settings and API `/health`
- Full notes: [MVP.md](./MVP.md)
