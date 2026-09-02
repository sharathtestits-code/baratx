#!/usr/bin/env python3
"""Minimal HeyGen v3 client for BarathX reel composites.

Env:
  HEYGEN_API_KEY   required for API calls
  HEYGEN_AVATAR_ID Digital Twin / avatar look id
  HEYGEN_VOICE_ID  voice id

Docs: https://developers.heygen.com/generate-avatar-video
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

BASE = "https://api.heygen.com"


def _api_key() -> str:
    key = os.environ.get("HEYGEN_API_KEY", "").strip()
    if not key:
        raise SystemExit("Set HEYGEN_API_KEY (HeyGen dashboard → API).")
    return key


def _request(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    url = f"{BASE}{path}"
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "x-api-key": _api_key(),
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HeyGen {method} {path} → HTTP {e.code}: {detail}") from e
    return json.loads(raw) if raw else {}


def list_avatars(*, avatar_type: str | None = "digital_twin", ownership: str = "private") -> list[dict]:
    q = f"?ownership={ownership}"
    if avatar_type:
        q += f"&avatar_type={avatar_type}"
    data = _request("GET", f"/v3/avatars/looks{q}")
    return data.get("data") or data.get("looks") or []


def list_voices() -> list[dict]:
    data = _request("GET", "/v3/voices")
    return data.get("data") or data.get("voices") or []


def create_avatar_video(
    *,
    script: str,
    avatar_id: str,
    voice_id: str,
    title: str = "BarathX reel VO",
    aspect_ratio: str = "9:16",
    resolution: str = "1080p",
    remove_background: bool = True,
    output_format: str = "webm",
    engine: str | None = None,
) -> str:
    """Create avatar video; returns video_id."""
    payload: dict[str, Any] = {
        "type": "avatar",
        "avatar_id": avatar_id,
        "script": script,
        "voice_id": voice_id,
        "title": title,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "remove_background": remove_background,
        "output_format": output_format,
    }
    if engine:
        payload["engine"] = {"type": engine}
    data = _request("POST", "/v3/videos", body=payload)
    video_id = (data.get("data") or {}).get("video_id") or data.get("video_id")
    if not video_id:
        raise SystemExit(f"No video_id in response: {json.dumps(data)[:500]}")
    return str(video_id)


def get_video(video_id: str) -> dict[str, Any]:
    data = _request("GET", f"/v3/videos/{video_id}")
    return data.get("data") or data


def wait_for_video(video_id: str, *, poll_s: float = 8.0, timeout_s: float = 900.0) -> dict[str, Any]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        info = get_video(video_id)
        status = info.get("status")
        print(f"  status={status}", flush=True)
        if status == "completed":
            return info
        if status == "failed":
            raise SystemExit(
                f"HeyGen failed: {info.get('failure_message') or info.get('failure_code') or info}"
            )
        time.sleep(poll_s)
    raise SystemExit(f"Timed out waiting for HeyGen video {video_id}")


def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "BarathX-HeyGen-Pipeline/1.0"})
    with urllib.request.urlopen(req, timeout=180) as resp, dest.open("wb") as f:
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            f.write(chunk)
    return dest


def cmd_list_avatars(_: argparse.Namespace) -> None:
    looks = list_avatars()
    if not looks:
        looks = list_avatars(avatar_type=None)
    for look in looks[:50]:
        lid = look.get("id") or look.get("avatar_id")
        name = look.get("name") or look.get("avatar_name") or ""
        engines = look.get("supported_api_engines") or []
        print(f"{lid}\t{name}\tengines={engines}")


def cmd_list_voices(_: argparse.Namespace) -> None:
    for v in list_voices()[:80]:
        vid = v.get("voice_id") or v.get("id")
        name = v.get("name") or ""
        lang = v.get("language") or v.get("locale") or ""
        print(f"{vid}\t{name}\t{lang}")


def cmd_generate(args: argparse.Namespace) -> None:
    avatar_id = args.avatar_id or os.environ.get("HEYGEN_AVATAR_ID", "").strip()
    voice_id = args.voice_id or os.environ.get("HEYGEN_VOICE_ID", "").strip()
    if not avatar_id or not voice_id:
        raise SystemExit("Need --avatar-id / HEYGEN_AVATAR_ID and --voice-id / HEYGEN_VOICE_ID")

    script = Path(args.script).read_text(encoding="utf-8").strip() if args.script else args.text
    if not script:
        raise SystemExit("Provide --script FILE or --text '…'")

    out = Path(args.out)
    print(f"Creating HeyGen video → {out}", flush=True)
    video_id = create_avatar_video(
        script=script,
        avatar_id=avatar_id,
        voice_id=voice_id,
        title=args.title,
        aspect_ratio=args.aspect_ratio,
        remove_background=not args.keep_background,
        output_format=args.format,
        engine=args.engine,
    )
    print(f"video_id={video_id}", flush=True)
    info = wait_for_video(video_id)
    url = info.get("video_url")
    if not url:
        raise SystemExit(f"completed but no video_url: {info}")
    download(url, out)
    meta = out.with_suffix(out.suffix + ".json")
    meta.write_text(json.dumps({"video_id": video_id, **info}, indent=2), encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size} bytes)")
    print(f"Meta  {meta}")


def main() -> None:
    p = argparse.ArgumentParser(description="BarathX HeyGen v3 helper")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list-avatars", help="List Digital Twin / avatar looks")
    s.set_defaults(func=cmd_list_avatars)

    s = sub.add_parser("list-voices", help="List voices")
    s.set_defaults(func=cmd_list_voices)

    s = sub.add_parser("generate", help="Generate + download avatar video")
    s.add_argument("--script", help="Path to VO script text file")
    s.add_argument("--text", help="Inline VO script")
    s.add_argument("--out", required=True, help="Output path (.webm or .mp4)")
    s.add_argument("--avatar-id", default="")
    s.add_argument("--voice-id", default="")
    s.add_argument("--title", default="BarathX Part VO")
    s.add_argument("--aspect-ratio", default="9:16")
    s.add_argument("--format", default="webm", choices=("webm", "mp4"))
    s.add_argument("--engine", default=None, help="avatar_iv | avatar_v | avatar_iii")
    s.add_argument("--keep-background", action="store_true")
    s.set_defaults(func=cmd_generate)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
