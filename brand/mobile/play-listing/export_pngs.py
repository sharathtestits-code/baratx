#!/usr/bin/env python3
"""Export Play Console listing PNGs from SVGs in this folder."""

from pathlib import Path

try:
    import cairosvg
except ImportError as exc:
    raise SystemExit(
        "Install cairosvg first: python3 -m pip install cairosvg"
    ) from exc

HERE = Path(__file__).resolve().parent


def export(svg_name: str, png_name: str, width: int, height: int) -> None:
    src = HERE / svg_name
    dest = HERE / png_name
    cairosvg.svg2png(
        url=str(src),
        write_to=str(dest),
        output_width=width,
        output_height=height,
    )
    print(f"wrote {dest.name} ({width}x{height})")


if __name__ == "__main__":
    export("icon-512.svg", "icon-512.png", 512, 512)
    export("feature-1024x500.svg", "feature-1024x500.png", 1024, 500)
