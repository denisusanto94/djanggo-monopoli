"""Definisi 32 petak papan (9+7+9+7).

Urutan permainan: petak 0 (Mulai / tile_01) di pojok kiri bawah grid (9,1),
lalu naik sisi kiri, baris atas kiri→kanan, sisi kanan turun, baris bawah
kanan→kiri sampai kembali ke Mulai (berlawanan arah jarum jam di grid).

Empat sisi jalur (path_line 1–4), searah putaran papan:
  Line 1 — bawah ke tengah kiri: baris 9, kolom 1..8 (Mulai … ke kiri dari pojok kanan bawah).
  Line 2 — tengah kiri ke atas: kolom 1, baris 1..8 (naik, termasuk Pulau Terpencil).
  Line 3 — atas ke tengah kanan: baris 1, kolom 2..9 (kanan sepanjang atas).
  Line 4 — tengah kanan ke bawah: kolom 9, baris 2..9 (turun, termasuk Keliling Dunia).

Sudut rotasi kartu per sisi (CSS, setelah lawan-putar grid): line 1 = -45°, line 2 = 45°,
line 3 = -45°, line 4 = 45°.

Sudut: 8 Pulau Terpencil (1,1), 16 Piala Dunia Marmer (1,9), 24 Keliling Dunia (9,9).

Kota (properti) di 16 slot jalur diurut harga naik dari termurah ke termahal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PathLine = Literal[1, 2, 3, 4]

TileKind = Literal[
    "start",
    "property",
    "chance",
    "tax",
    "travel",
    "jail",
    "parking",
    "festival",
    "airport",
]


@dataclass(frozen=True)
class Tile:
    index: int
    code: str
    name: str
    kind: TileKind
    price: int | None
    color: str | None
    asset_file: str
    grid_row: int
    grid_col: int
    path_line: PathLine
    card_turn_deg: float


def _asset(n: int) -> str:
    return f"aset_monopoli/tile_{n:02d}.svg"


# Jalur dari (9,1): kiri naik 1..7, pojok (1,1), atas 9..16, kanan turun 17..24, bawah 25..31.
_RAW: list[tuple[str, str, TileKind, int | None, str | None]] = [
    ("start", "Mulai", "start", None, "#3498db"),
    ("banjarmasin", "Banjarmasin", "property", 280, "#1abc9c"),
    ("chance_1", "Kesempatan", "chance", None, "#9b59b6"),
    ("pontianak", "Pontianak", "property", 300, "#1abc9c"),
    ("tax_income", "Pajak Penghasilan", "tax", 200, None),
    ("padang", "Padang", "property", 320, "#1abc9c"),
    ("festival_1", "Festival", "festival", None, "#e91e63"),
    ("balikpapan", "Balikpapan", "property", 340, "#f39c12"),
    ("corner_jail", "Pulau Terpencil", "jail", None, "#7f8c8d"),
    ("malang", "Malang", "property", 360, "#f39c12"),
    ("chance_2", "Kejutan", "chance", None, "#9b59b6"),
    ("semarang", "Semarang", "property", 380, "#f39c12"),
    ("airport_1", "Bandara A", "airport", 400, "#34495e"),
    ("denpasar", "Denpasar", "property", 400, "#f39c12"),
    ("tax_luxury", "Pajak Mewah", "tax", 150, None),
    ("manado", "Manado", "property", 420, "#2ecc71"),
    ("marble_cup", "Piala Dunia Marmer", "festival", None, "#8e44ad"),
    ("palembang", "Palembang", "property", 440, "#2ecc71"),
    ("chance_3", "Lucky Card", "chance", None, "#9b59b6"),
    ("makassar", "Makassar", "property", 460, "#2ecc71"),
    ("parking", "Parkir Gratis", "parking", None, "#95a5a6"),
    ("tarakan", "Tarakan", "property", 470, "#3498db"),
    ("festival_2", "Konser", "festival", None, "#e91e63"),
    ("yogyakarta", "Yogyakarta", "property", 480, "#3498db"),
    ("world_tour", "Keliling Dunia", "travel", None, "#16a085"),
    ("bandung", "Bandung", "property", 500, "#3498db"),
    ("chance_4", "Misteri", "chance", None, "#9b59b6"),
    ("medan", "Medan", "property", 520, "#2ecc71"),
    ("airport_2", "Bandara B", "airport", 350, "#34495e"),
    ("surabaya", "Surabaya", "property", 560, "#3498db"),
    ("corner_go_bonus", "Bonus Roda", "chance", None, "#9b59b6"),
    ("jakarta", "Jakarta", "property", 600, "#e74c3c"),
]


def _path_line_for_cell(grid_row: int, grid_col: int) -> PathLine:
    """Sisi jalur 1..4; (9,9) di line 4 (ujung kanan bawah), bawah baris 9 selain itu line 1."""
    gr, gc = grid_row, grid_col
    if gr == 9 and gc != 9:
        return 1
    if gr == 9 and gc == 9:
        return 4
    if gc == 1 and gr < 9:
        return 2
    if gr == 1 and gc > 1:
        return 3
    if gc == 9 and gr > 1:
        return 4
    raise ValueError(f"Koordinat ({gr}, {gc}) bukan petak pinggir jalur")


def _card_turn_for_path_line(line: PathLine) -> float:
    """Sudut rotate kedua pada .tile-frame (setelah lawan-putar grid), per path_line."""
    return {1: -45.0, 2: 45.0, 3: -45.0, 4: 45.0}[line]


def _grid_for_index(i: int) -> tuple[int, int]:
    """Baris/kolom 1-based pada grid 9x9 (baris 1 = atas).

    Mulai (9,1); berlawanan arah jarum jam: kiri naik, atas, kanan turun,
    bawah kanan→kiri kembali ke (9,1).
    """
    if i == 0:
        return (9, 1)
    if 1 <= i <= 7:
        return (9 - i, 1)
    if i == 8:
        return (1, 1)
    if 9 <= i <= 16:
        return (1, i - 7)
    if 17 <= i <= 24:
        return (i - 15, 9)
    return (9, 33 - i)


def get_tiles() -> list[Tile]:
    out: list[Tile] = []
    for i, (code, name, kind, price, color) in enumerate(_RAW):
        gr, gc = _grid_for_index(i)
        pl = _path_line_for_cell(gr, gc)
        out.append(
            Tile(
                index=i,
                code=code,
                name=name,
                kind=kind,
                price=price,
                color=color,
                asset_file=_asset(i + 1),
                grid_row=gr,
                grid_col=gc,
                path_line=pl,
                card_turn_deg=_card_turn_for_path_line(pl),
            )
        )
    return out


TILES: list[Tile] = get_tiles()
