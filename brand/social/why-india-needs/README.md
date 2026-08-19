# Why India needs BarathX — 20s follow-up reel

Append this **after** the “built for someone else” deck (repo root `slide-01.png` … `slide-04.png`) or your screen recording.

## Files

| File | Use |
|------|-----|
| `barathx-why-india-needs-20s.mp4` | **1080×1080** — matches slide deck; append to square export |
| `barathx-why-india-needs-20s-reel.mp4` | **1080×1920** — IG Reels / Stories |
| `barathx-why-india-needs-poster.jpg` | Thumbnail / cover still |
| `screens/` | Latest product stills used in the render |

## Regenerate

```bash
bash brand/social/why-india-needs/capture_screens.sh
/tmp/pilvenv/bin/python brand/social/why-india-needs/render_why_india_needs.py
```

Requires Pillow + ffmpeg. Copy outputs to `/opt/cursor/artifacts/` for upload.

## Append to your `.mov` (Mac)

Your file: `ScreenRecording_08-18-2026 17-08-23_1.mov`

```bash
# 1) Export your recording as MP4 if needed (same resolution as slides = 1080 square ideal)
# 2) Concat part A + this 20s part
ffmpeg -i "ScreenRecording_08-18-2026 17-08-23_1.mov" \
  -i barathx-why-india-needs-20s.mp4 \
  -filter_complex "[0:v]scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2[v0];[1:v]scale=1080:1080[v1];[v0][v1]concat=n=2:v=1:a=0[outv]" \
  -map "[outv]" -c:v libx264 -crf 20 -movflags +faststart \
  barathx-why-india-full.mp4
```

For vertical Reels, use `barathx-why-india-needs-20s-reel.mp4` and scale part A to 1080×1920 instead.

## Caption (IG / WhatsApp)

```
Why India needs BarathX 🇮🇳

Not another Reels feed.
Square · Arenas · Live — pick a side, argue it on the record.

Human takes only. No AI slop.
→ barathx.com

#BarathX #India #PublicSquare #Debate #BuildInPublic
```

## Beats (20s)

1. Why India needs BarathX — live landing
2. Not another Reels feed — Square
3. One question. Your take. — compose
4. Arenas — pick a side
5. Live — argue now
6. Built for India — home / civic feed
7. Human takes only
8. Join free → barathx.com
