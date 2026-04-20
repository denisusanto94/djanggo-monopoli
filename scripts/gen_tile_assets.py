"""Generate placeholder SVGs into static/aset_monopoli/. Run: python scripts/gen_tile_assets.py"""
import os
import sys
from pathlib import Path

import django

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monopoli_game.settings")
django.setup()

from board.tiles import TILES  # noqa: E402

PALETTE = [
    "#e74c3c",
    "#3498db",
    "#2ecc71",
    "#f39c12",
    "#9b59b6",
    "#1abc9c",
    "#e91e63",
    "#34495e",
    "#f4d03f",
    "#16a085",
    "#95a5a6",
    "#7f8c8d",
]


def main() -> None:
    out = ROOT / "static" / "aset_monopoli"
    out.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(TILES, start=1):
        name = t.name.replace("&", "dan")
        c = t.color or PALETTE[i % len(PALETTE)]
        label = name[:18]
        svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <defs>
    <linearGradient id="g{i}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="{c}" stop-opacity="0.55"/>
    </linearGradient>
  </defs>
  <rect width="200" height="200" fill="url(#g{i})"/>
  <rect x="10" y="10" width="180" height="36" rx="10" fill="{c}" opacity="0.9"/>
  <text x="100" y="35" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif"
    font-size="16" font-weight="700" fill="#0b1f4d">{i:02d}</text>
  <text x="100" y="110" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif"
    font-size="14" font-weight="600" fill="#0b1f4d">{label}</text>
  <text x="100" y="135" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif"
    font-size="11" fill="#1a3d8a" opacity="0.85">{t.kind}</text>
</svg>
"""
        (out / f"tile_{i:02d}.svg").write_text(svg, encoding="utf-8")
    print(f"Wrote {len(TILES)} files to {out}")


if __name__ == "__main__":
    main()
