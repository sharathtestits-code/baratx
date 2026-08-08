# BharatX Instagram carousel (real app screens)

Replaces the fake AI “in-app” slide (garbled “Kollrata” / “fioillato” text) with **actual screenshots** from https://barathx.com.

## Slides (`export/slide-01.png` … `slide-10.png`)

| # | Content |
|---|---|
| 01 | Every social app you use… |
| 02 | …was built for someone else. |
| 03 | Someone else’s culture / language / rules |
| 04 | India’s own public square + BharatX mark |
| 05 | **Real** landing / signup screen |
| 06 | **Real** mobile feed in a phone frame (this replaces the broken mock) |
| 07 | **Real** post detail + replies |
| 08 | **Real** Explore (desktop + mobile) |
| 09 | **Real** compose welcome + desktop feed |
| 10 | CTA — comment BX |

## Source screenshots

Raw captures live in `screens/` (desktop + mobile). Taken from the production app, including authenticated feed with real posts.

## Regenerate exports

From repo root (Chrome required):

```bash
cd brand/carousel
python3 render_slides.py
```

Or open `index.html` locally and screenshot each `.slide` at 1080×1080.

## Posting note

Upload `export/slide-01.png` through `slide-10.png` in order as an IG carousel. Do **not** reuse the old AI-generated in-app mock.
