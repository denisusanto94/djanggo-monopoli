"""Isi petak papan dari definisi standar `board.tiles.TILES`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def kind_to_tile_type(kind: str) -> str:
    return {
        'start': 'GO',
        'property': 'PROPERTY',
        'chance': 'CHANCE',
        'tax': 'TAX',
        'travel': 'TRAVEL',
        'jail': 'JAIL',
        'parking': 'FREE_PARKING',
        'festival': 'FESTIVAL',
        'airport': 'AIRPORT',
    }.get(kind, 'PROPERTY')


def seed_tiles_for_board(board, TileModel=None) -> int:
    """
    Hapus semua petak papan ini lalu buat ulang dari TILES.
    TileModel: kelas Tile (models.Tile atau historical dari migrasi).
    """
    from board.models import Tile as RealTile
    from board.tiles import TILES as default_tiles

    TileCls = TileModel or RealTile
    TileCls.objects.filter(board=board).delete()
    n = 0
    for t in default_tiles:
        TileCls.objects.create(
            board=board,
            name=t.name,
            code=(t.code or '')[:64],
            position=t.index,
            tile_type=kind_to_tile_type(t.kind),
            display_mode='static',
            path_line=int(t.path_line),
            group_color=(t.color or '')[:32] if t.color else '',
            price=t.price or 0,
            rent_base=t.rent or 0,
            rent_1house=t.rent_1house or 0,
            rent_2house=t.rent_2house or 0,
            rent_3house=t.rent_3house or 0,
            rent_4house=t.rent_4house or 0,
            rent_hotel=t.rent_hotel or 0,
            house_price=t.house_cost or 0,
            hotel_price=t.house_cost or 0,
            description=t.description or '',
        )
        n += 1
    return n
