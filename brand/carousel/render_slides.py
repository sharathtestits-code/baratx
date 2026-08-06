#!/usr/bin/env python3
"""Render brand/carousel/index.html slides to 1080x1080 PNGs via Chrome."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPORT = ROOT / "export"
CHROME = "/usr/local/bin/google-chrome"
PORT = 8765


def main() -> None:
    EXPORT.mkdir(parents=True, exist_ok=True)

    pkg = ROOT / "package.json"
    if not pkg.exists():
        pkg.write_text(
            '{"name":"baratx-carousel","private":true,"type":"module","dependencies":{"puppeteer-core":"^24.2.0"}}\n',
            encoding="utf-8",
        )
    subprocess.check_call(["npm", "install", "--silent"], cwd=str(ROOT))

    server = subprocess.Popen(
        ["python3", "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(0.5)

    node_script = ROOT / "_render_cdp.mjs"
    node_script.write_text(
        f"""
import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';

const outDir = {json.dumps(str(EXPORT))};
fs.mkdirSync(outDir, {{ recursive: true }});

const browser = await puppeteer.launch({{
  executablePath: {json.dumps(CHROME)},
  headless: true,
  defaultViewport: {{ width: 1200, height: 1400, deviceScaleFactor: 1 }},
  args: ['--hide-scrollbars', '--font-render-hinting=none'],
}});

const page = await browser.newPage();
await page.goto('http://127.0.0.1:{PORT}/index.html', {{ waitUntil: 'networkidle0', timeout: 90000 }});
await page.evaluate(() => document.fonts.ready);
await new Promise((r) => setTimeout(r, 800));

const slides = await page.$$('.slide');
if (!slides.length) throw new Error('No .slide elements found');

for (let i = 0; i < slides.length; i++) {{
  const n = String(i + 1).padStart(2, '0');
  const file = path.join(outDir, `slide-${{n}}.png`);
  const box = await slides[i].boundingBox();
  if (!box) throw new Error(`No bounding box for slide ${{n}}`);
  await page.screenshot({{
    path: file,
    type: 'png',
    clip: {{
      x: Math.round(box.x),
      y: Math.round(box.y),
      width: 1080,
      height: 1080,
    }},
  }});
  console.log('wrote', file, `${{Math.round(box.width)}}x${{Math.round(box.height)}}`);
}}

await browser.close();
""",
        encoding="utf-8",
    )

    try:
        subprocess.check_call(["node", str(node_script)], cwd=str(ROOT))
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    slides = sorted(EXPORT.glob("slide-*.png"))
    print(f"Exported {len(slides)} slides → {EXPORT}")
    for p in slides:
        print(f"  {p.name}: {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()
