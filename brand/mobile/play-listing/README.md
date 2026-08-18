# Play listing assets

Upload these in Play Console → **Main store listing**.

| File | Play field | Size |
|------|------------|------|
| `icon-512.png` | App icon | 512×512 PNG |
| `feature-1024x500.png` | Feature graphic | 1024×500 PNG, no alpha |
| Phone screenshots | Phone | Capture on device (not in this folder) |

Sources: `icon-512.svg` (from `brand/baratx-logo-mark.svg`), `feature-1024x500.svg`.

Regenerate PNGs:

```bash
python3 brand/mobile/play-listing/export_pngs.py
```
