#!/usr/bin/env python3
"""Composite a HeyGen (or any) talking-head clip into a BarathX 9:16 reel.

Default layout matches Part 2 Arenas:
  - left ~35% = avatar zone
  - right ~65% = product UI (already in base reel)
  - avatar active for first `avatar_end_s` seconds (default 21.0)
  - end card stays full-bleed brand

Works with:
  - transparent .webm (preferred — HeyGen output_format=webm + remove_background)
  - opaque .mp4/.mov (cropped + scaled into the left panel)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

W, H = 1080, 1920
DEFAULT_AVATAR_RATIO = 0.35
DEFAULT_TOP = 130
DEFAULT_BOTTOM_BAR = 110


def probe(path: Path) -> dict:
    raw = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=width,height,codec_type,codec_name,pix_fmt",
            "-of",
            "json",
            str(path),
        ],
        text=True,
    )
    return json.loads(raw)


def has_alpha(path: Path) -> bool:
    info = probe(path)
    for s in info.get("streams") or []:
        if s.get("codec_type") != "video":
            continue
        pix = (s.get("pix_fmt") or "").lower()
        if any(tok in pix for tok in ("a", "rgba", "argb", "bgra", "gbrap", "yuva")):
            return True
    return path.suffix.lower() == ".webm"


def has_audio(path: Path) -> bool:
    info = probe(path)
    return any(s.get("codec_type") == "audio" for s in info.get("streams") or [])


def composite(
    *,
    base: Path,
    avatar: Path,
    out: Path,
    avatar_ratio: float = DEFAULT_AVATAR_RATIO,
    top: int = DEFAULT_TOP,
    bottom_bar: int = DEFAULT_BOTTOM_BAR,
    avatar_end_s: float = 21.0,
    keep_avatar_audio: bool = True,
) -> Path:
    if not base.exists():
        raise SystemExit(f"Missing base reel: {base}")
    if not avatar.exists():
        raise SystemExit(f"Missing avatar clip: {avatar}")

    left_w = int(W * avatar_ratio)
    panel_h = H - top - bottom_bar
    ax, ay = 8, top + 8
    aw, ah = left_w - 16, panel_h - 16
    duration = float(probe(base)["format"]["duration"])
    alpha = has_alpha(avatar)
    out.parent.mkdir(parents=True, exist_ok=True)

    vfmt = "rgba" if alpha else "yuv420p"
    avatar_chain = (
        f"[1:v]scale={aw}:{ah}:force_original_aspect_ratio=increase,"
        f"crop={aw}:{ah},format={vfmt},setpts=PTS-STARTPTS[av]"
    )
    enable = f"between(t\\,0\\,{avatar_end_s:.3f})"
    overlay = f"[0:v][av]overlay={ax}:{ay}:enable='{enable}'[vout]"

    fc_parts = [avatar_chain, overlay]
    maps = ["-map", "[vout]"]
    audio_args: list[str]

    if keep_avatar_audio and has_audio(avatar):
        fc_parts.append(
            f"[1:a]aresample=44100,apad,atrim=0:{duration:.3f},asetpts=PTS-STARTPTS[aout]"
        )
        maps += ["-map", "[aout]"]
        audio_args = ["-c:a", "aac", "-b:a", "192k"]
    else:
        audio_args = ["-an"]

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(base),
        "-i",
        str(avatar),
        "-filter_complex",
        ";".join(fc_parts),
        *maps,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        *audio_args,
        "-movflags",
        "+faststart",
        "-t",
        f"{duration:.3f}",
        str(out),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"ffmpeg failed:\n{proc.stderr[-2500:]}")
    return out


def make_smoke_avatar(path: Path, duration: float = 21.0) -> Path:
    """Synthetic avatar clip for pipeline smoke tests (no HeyGen key needed)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    vf = (
        f"color=c=0x101016:s=540x960:d={duration:.2f},"
        f"drawbox=x=170:y=280:w=200:h=200:color=0xff9933@1:t=fill,"
        f"drawtext=text='HEYGEN':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=520"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            vf,
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=44100",
            "-t",
            f"{duration:.2f}",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(path),
        ],
        check=True,
        capture_output=True,
    )
    return path


def main() -> None:
    p = argparse.ArgumentParser(description="Overlay HeyGen avatar onto BarathX reel")
    p.add_argument("--base", required=True, type=Path, help="Base 9:16 reel mp4")
    p.add_argument("--avatar", type=Path, help="HeyGen export (webm/mp4)")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--avatar-ratio", type=float, default=DEFAULT_AVATAR_RATIO)
    p.add_argument("--top", type=int, default=DEFAULT_TOP)
    p.add_argument("--bottom-bar", type=int, default=DEFAULT_BOTTOM_BAR)
    p.add_argument("--avatar-end", type=float, default=21.0, help="Seconds avatar stays on")
    p.add_argument("--no-avatar-audio", action="store_true")
    p.add_argument("--smoke-avatar", action="store_true", help="Generate synthetic avatar for test")
    args = p.parse_args()

    avatar = args.avatar
    if args.smoke_avatar:
        avatar = Path(tempfile.gettempdir()) / "bx-smoke-avatar.mp4"
        make_smoke_avatar(avatar, duration=max(args.avatar_end, 1.0))
        print(f"Smoke avatar → {avatar}")
    if not avatar:
        raise SystemExit("Provide --avatar or --smoke-avatar")

    out = composite(
        base=args.base,
        avatar=avatar,
        out=args.out,
        avatar_ratio=args.avatar_ratio,
        top=args.top,
        bottom_bar=args.bottom_bar,
        avatar_end_s=args.avatar_end,
        keep_avatar_audio=not args.no_avatar_audio,
    )
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
