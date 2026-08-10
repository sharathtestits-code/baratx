# BarathX — Prod MVP versioning

Production releases on **`main`** are labeled **MVP1**, **MVP2**, **MVP3**, … (never resets).

| Item | Detail |
|------|--------|
| File | [`VERSION`](../../VERSION) — integer only (`1` → display `MVP1`) |
| Bump | Auto on every push to `main` via `.github/workflows/bump-mvp.yml` |
| Skip | Commits starting with `chore(mvp):` (the bump bot) do not re-bump |
| UI | Settings → “BarathX MVP{n}” |
| API | `GET /health` → `{ "mvp": "MVP1", "version": "1", ... }` |

## Flow

```
PR merges into main
  → deploy may build current VERSION (e.g. MVP1)
  → bump workflow commits VERSION+1 (chore(mvp): bump to MVP2)
  → Pages / Railway rebuild with the new label
```

## Manual bump (rare)

```bash
./scripts/bump-mvp.sh   # prints new label, updates VERSION
git add VERSION && git commit -m "chore(mvp): bump to MVP$(tr -d '[:space:]' < VERSION)"
```

`dev` / `qa` keep whatever VERSION was last merged; only **`main`** auto-increments.
