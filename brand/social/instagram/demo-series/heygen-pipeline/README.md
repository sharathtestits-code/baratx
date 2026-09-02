# HeyGen → BarathX reel composite

Drop a HeyGen talking-head into the left **~35%** avatar zone of demo reels (Part 2 Arenas first). Runs inside Cursor / any machine with `ffmpeg` + Python 3.

**Brand:** BarathX · https://barathx.com · [@getbaratx](https://www.instagram.com/getbaratx/)

## What this does

1. **Optional:** call HeyGen API (`POST /v3/videos`) with the Part VO script → download transparent `.webm`
2. **ffmpeg** overlays that clip onto the existing 9:16 product reel (UI stays on the right)
3. Avatar runs **0–21s**; end card (**21–25s**) stays full-bleed brand
4. Audio prefers HeyGen VO (base reel is silent)

IG Reels **trending music** is still added manually in the Instagram app (Graph API limitation).

## Setup

```bash
# 1) HeyGen dashboard → API key
export HEYGEN_API_KEY="…"

# 2) Discover your Digital Twin + voice
python3 brand/social/instagram/demo-series/heygen-pipeline/heygen_client.py list-avatars
python3 brand/social/instagram/demo-series/heygen-pipeline/heygen_client.py list-voices

export HEYGEN_AVATAR_ID="your_look_id"
export HEYGEN_VOICE_ID="your_voice_id"
```

Copy `env.example` → keep secrets out of git.

## Part 2 — Arenas (25s)

VO script: `PART02_VO.txt` (matches `PART-02-arenas/SCRIPT.md`).

### A) You exported from HeyGen UI (no API)

```bash
cd brand/social/instagram/demo-series/heygen-pipeline
python3 run_part02_composite.py --avatar /path/to/your-clone.webm
```

### B) Generate via API + composite

```bash
python3 run_part02_composite.py --generate
```

### C) Smoke test (no HeyGen key)

```bash
python3 run_part02_composite.py --smoke
```

Outputs:
- `cache/barathx-PART2-arenas-25s-HEYGEN.mp4`
- `brand/social/daily/2026-08-28/barathx-PART2-arenas-25s-HEYGEN.mp4` (after run)

Base reel is auto-downloaded from PR branch `cursor/arenas-part2-25s-2af5` if missing locally.

## Low-level tools

```bash
# Generate only
python3 heygen_client.py generate \
  --script PART02_VO.txt \
  --out cache/part02-avatar.webm \
  --format webm

# Composite only
python3 composite_avatar.py \
  --base ../PART-02-arenas/barathx-PART2-arenas-25s.mp4 \
  --avatar cache/part02-avatar.webm \
  --out cache/barathx-PART2-arenas-25s-HEYGEN.mp4
```

## Layout constants (must match Part 2 renderer)

| Constant | Value |
|----------|-------|
| Canvas | 1080×1920 |
| Avatar width ratio | 0.35 |
| Panel top | 130px |
| Bottom bar | 110px |
| Avatar on-screen | 0–21.0s |

## Next parts

Reuse `composite_avatar.py` with a new `--base` + VO file. Keep the same left-zone layout for Parts 3–7 when the avatar hosts the series.
