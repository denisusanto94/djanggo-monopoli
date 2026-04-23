"""Definisi 32 petak papan Jakarta (9+7+9+7).

Tema: objek wisata & landmark DKI Jakarta. Properti (16 petak) diurut dari yang relatif
kurang ramai wisatawan hingga ikon paling populer, mengikuti kenaikan harga/sewa.

Urutan permainan: petak 0 (Mulai / tile_01) di pojok kiri bawah grid (9,1),
lalu naik sisi kiri, baris atas kiri→kanan, sisi kanan turun, baris bawah
kanan→kiri sampai kembali ke Mulai (berlawanan arah jarum jam di grid).

Sudut: 8 Pulau Terpencil (1,1), 16 Piala Dunia Marmer (1,9), 24 Keliling Jabodetabek (9,9)."""

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
    # Harga sewa per level (None = bukan properti)
    rent: int | None = None
    rent_1house: int | None = None
    rent_2house: int | None = None
    rent_3house: int | None = None
    rent_4house: int | None = None
    rent_hotel: int | None = None
    house_cost: int | None = None
    # Deskripsi singkat untuk petak non-properti
    description: str | None = None


def _asset(n: int) -> str:
    return f"aset_monopoli/tile_{n:02d}.svg"


# fmt: off
# Petak jalur: (code, name, kind, price, color, rent, r1h, r2h, r3h, r4h, rhotel, house_cost, description)
_RAW: list[tuple] = [
    # code,               name,                kind,        price, color,      rent,  r1h,  r2h,  r3h,   r4h,  rhotel, hcost, desc
    ("start",            "Mulai",              "start",      None, "#3498db",  None, None, None, None,   None,  None,  None,  "Lewati petak Mulai dan kumpulkan Rp 200!"),
    ("sumpah_pemuda",    "Museum Sumpah Pemuda", "property",  280, "#1abc9c",    22,   60,  180,  500,    720,   900,    50,   None),
    ("chance_1",         "Kesempatan",         "chance",     None, "#9b59b6",  None, None, None, None,   None,  None,  None,  "Ambil kartu Kesempatan dan ikuti instruksinya!"),
    ("taman_prasasti",   "Taman Museum Prasasti", "property", 300, "#1abc9c",    24,   66,  200,  560,    800,  1000,    50,   None),
    ("tax_income",       "Pajak Penghasilan",  "tax",         200, None,        None, None, None, None,   None,  None,  None,  "Bayar pajak penghasilan sebesar Rp 200."),
    ("setu_babakan",     "Setu Babakan Betawi", "property",   320, "#1abc9c",    26,   72,  220,  600,    900,  1100,    50,   None),
    ("festival_1",       "Festival",           "festival",   None, "#e91e63",  None, None, None, None,   None,  None,  None,  "Selamat! Kamu berada di Festival. Nikmati hiburan!"),
    ("lap_banteng",      "Lapangan Banteng",   "property",    340, "#f39c12",    28,   84,  250,  700,   1000,  1200,   100,   None),
    ("corner_jail",      "Pulau Terpencil",    "jail",        None, "#7f8c8d",  None, None, None, None,   None,  None,  None,  "Hanya berkunjung — atau terkurung di Pulau Terpencil!"),
    ("tanah_abang",      "Pasar Tanah Abang",  "property",    360, "#f39c12",    30,   90,  270,  750,   1100,  1300,   100,   None),
    ("chance_2",         "Kejutan",            "chance",      None, "#9b59b6",  None, None, None, None,   None,  None,  None,  "Ambil kartu Kejutan — bisa beruntung atau sial!"),
    ("glodok",           "Glodok Chinatown",   "property",    380, "#f39c12",    32,   96,  300,  800,   1150,  1400,   100,   None),
    ("airport_halim",    "Bandara Halim",      "airport",     400, "#34495e",   25,  None, None, None,   None,  None,  None,  "Bandara: sewa Rp 25 per bandara yang kamu miliki × 25."),
    ("museum_nasional",  "Museum Nasional",    "property",    400, "#f39c12",    35,  100,  320,  850,   1200,  1500,   100,   None),
    ("tax_luxury",       "Pajak Mewah",        "tax",         150, None,        None, None, None, None,   None,  None,  None,  "Bayar pajak kemewahan sebesar Rp 150."),
    ("museum_wayang",    "Museum Wayang",      "property",    420, "#2ecc71",    40,  110,  340,  900,   1300,  1600,   150,   None),
    ("marble_cup",       "Piala Dunia Marmer", "festival",   None, "#8e44ad",  None, None, None, None,   None,  None,  None,  "Festival Piala Dunia Marmer! Pesta gratis untuk semua pemain."),
    ("museum_sejarah",   "Museum Sejarah Jakarta", "property", 440, "#2ecc71",    44,  120,  360,  950,   1400,  1700,   150,   None),
    ("chance_3",         "Lucky Card",         "chance",      None, "#9b59b6",  None, None, None, None,   None,  None,  None,  "Ambil kartu Lucky Card — semoga keberuntungan bersamamu!"),
    ("ragunan",          "Kebun Binatang Ragunan", "property", 460, "#2ecc71",    48,  130,  390, 1000,   1500,  1800,   150,   None),
    ("parking",          "Parkir Gratis",      "parking",    None, "#95a5a6",  None, None, None, None,   None,  None,  None,  "Istirahat sebentar! Parkir Gratis, tidak ada yang terjadi."),
    ("muara_angke",      "Wisata Muara Angke", "property",    470, "#3498db",    44,  100,  300,  750,   1100,  1300,   150,   None),
    ("festival_2",       "Konser",             "festival",   None, "#e91e63",  None, None, None, None,   None,  None,  None,  "Konser spektakuler! Bersenang-senanglah bersama teman."),
    ("gbk",              "Gelora Bung Karno",  "property",    480, "#3498db",    48,  110,  330,  800,   1200,  1400,   150,   None),
    ("world_tour",       "Keliling Jabodetabek", "travel",   None, "#16a085",  None, None, None, None,   None,  None,  None,  "Keliling Jabodetabek! Pilih petak tujuanmu di wilayah DKI & sekitarnya."),
    ("grand_hi",         "Grand Indonesia & Bundaran HI", "property", 500, "#3498db",    52,  120,  360,  850,   1300,  1550,   200,   None),
    ("chance_4",         "Misteri",            "chance",      None, "#9b59b6",  None, None, None, None,   None,  None,  None,  "Ambil kartu Misteri — isi kartu rahasia menanti!"),
    ("tmii",             "Taman Mini Indonesia Indah", "property", 520, "#2ecc71",    56,  130,  390,  900,   1400,  1700,   200,   None),
    ("airport_soetta",   "Bandara Soekarno-Hatta", "airport", 350, "#34495e",   25,  None, None, None,   None,  None,  None,  "Bandara: sewa Rp 25 per bandara yang kamu miliki × 25."),
    ("ancol",            "Taman Impian Jaya Ancol", "property", 560, "#3498db",    60,  150,  450, 1000,   1500,  2000,   200,   None),
    ("corner_go_bonus",  "Bonus Roda",         "chance",      None, "#9b59b6",  None, None, None, None,   None,  None,  None,  "Bonus Roda! Putar roda keberuntungan dan dapatkan hadiah."),
    ("monas",            "Monumen Nasional (Monas)", "property", 600, "#e74c3c",    70,  180,  540, 1200,   1800,  2500,   200,   None),
]
# fmt: on


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
    for i, row in enumerate(_RAW):
        code, name, kind, price, color, rent, r1h, r2h, r3h, r4h, rhotel, hcost, desc = row
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
                rent=rent,
                rent_1house=r1h,
                rent_2house=r2h,
                rent_3house=r3h,
                rent_4house=r4h,
                rent_hotel=rhotel,
                house_cost=hcost,
                description=desc,
            )
        )
    return out


TILES: list[Tile] = get_tiles()
