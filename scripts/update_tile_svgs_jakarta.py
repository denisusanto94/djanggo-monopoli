"""Sekali pakai: label teks di static/aset_monopoli/tile_*.svg untuk papan Jakarta."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "static" / "aset_monopoli"

LABELS: list[tuple[str, str]] = [
    ("Mulai", "start"),
    ("Museum Sumpah Pemuda", "property"),
    ("Kesempatan", "chance"),
    ("Taman Prasasti", "property"),
    ("Pajak Penghasilan", "tax"),
    ("Setu Babakan Betawi", "property"),
    ("Festival", "festival"),
    ("Lapangan Banteng", "property"),
    ("Pulau Terpencil", "jail"),
    ("Pasar Tanah Abang", "property"),
    ("Kejutan", "chance"),
    ("Glodok Chinatown", "property"),
    ("Bandara Halim", "airport"),
    ("Museum Nasional", "property"),
    ("Pajak Mewah", "tax"),
    ("Museum Wayang", "property"),
    ("Piala Dunia Marmer", "festival"),
    ("Museum Sejarah Jakarta", "property"),
    ("Lucky Card", "chance"),
    ("Kebun Binatang Ragunan", "property"),
    ("Parkir Gratis", "parking"),
    ("Wisata Muara Angke", "property"),
    ("Konser", "festival"),
    ("Gelora Bung Karno", "property"),
    ("Keliling Jabodetabek", "travel"),
    ("GI & Bundaran HI", "property"),
    ("Misteri", "chance"),
    ("TMII", "property"),
    ("Soekarno-Hatta", "airport"),
    ("Taman Impian Ancol", "property"),
    ("Bonus Roda", "chance"),
    ("Monas", "property"),
]


def patch_svg(content: str, title: str, kind: str) -> str:
    def sub_y110(m: re.Match[str]) -> str:
        return f"{m.group(1)}{title}{m.group(3)}"

    def sub_y135(m: re.Match[str]) -> str:
        return f"{m.group(1)}{kind}{m.group(3)}"

    content = re.sub(
        r'(<text x="100" y="110"[^>]*>)([^<]+)(</text>)',
        sub_y110,
        content,
        count=1,
    )
    content = re.sub(
        r'(<text x="100" y="135"[^>]*>)([^<]+)(</text>)',
        sub_y135,
        content,
        count=1,
    )
    return content


def main() -> int:
    if len(LABELS) != 32:
        print("LABELS harus 32 item", file=sys.stderr)
        return 1
    for i, (title, kind) in enumerate(LABELS):
        path = SVG_DIR / f"tile_{i + 1:02d}.svg"
        if not path.is_file():
            print("Missing", path, file=sys.stderr)
            return 1
        old = path.read_text(encoding="utf-8")
        new = patch_svg(old, title, kind)
        path.write_text(new, encoding="utf-8")
    print("Updated", len(LABELS), "SVG files in", SVG_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
