"""Serialisasi petak dari model Board → format template & JSON permainan."""

from __future__ import annotations

from types import SimpleNamespace

from django.http import HttpRequest

from .models import Board
from .tiles import _card_turn_for_path_line, _grid_for_index, _path_line_for_cell


def tile_type_to_kind(tile_type: str) -> str:
    return {
        'GO': 'start',
        'PROPERTY': 'property',
        'CHANCE': 'chance',
        'TAX': 'tax',
        'TRAVEL': 'travel',
        'JAIL': 'jail',
        'FREE_PARKING': 'parking',
        'FESTIVAL': 'festival',
        'AIRPORT': 'airport',
        'RAILROAD': 'airport',
        'UTILITY': 'chance',
        'COMMUNITY_CHEST': 'chance',
        'GO_TO_JAIL': 'jail',
    }.get(tile_type, 'property')


def board_to_play_payload(request: HttpRequest, board: Board) -> tuple[list[SimpleNamespace], list[dict]]:
    """Return (tiles_for_template, tiles_js_list)."""
    display: list[SimpleNamespace] = []
    js: list[dict] = []
    for tile in board.tiles.order_by('position'):
        gr, gc = _grid_for_index(tile.position)
        pl = int(tile.path_line) if tile.path_line else int(_path_line_for_cell(gr, gc))
        card_turn = float(_card_turn_for_path_line(pl))
        kind = tile_type_to_kind(tile.tile_type)
        code = (tile.code or '').strip() or f'tile_{tile.position}'
        use_custom = tile.display_mode == 'customize' and tile.image
        custom_url = request.build_absolute_uri(tile.image.url) if use_custom else None
        static_asset = f'aset_monopoli/tile_{tile.position + 1:02d}.svg'
        price = tile.price if tile.price else None
        display.append(
            SimpleNamespace(
                index=tile.position,
                code=code,
                name=tile.name,
                kind=kind,
                price=price,
                color=tile.group_color,
                asset_file=static_asset,
                custom_image_url=custom_url,
                grid_row=gr,
                grid_col=gc,
                path_line=pl,
                card_turn_deg=card_turn,
            )
        )
        js.append(
            {
                'index': tile.position,
                'code': code,
                'name': tile.name,
                'kind': kind,
                'price': price,
                'color': tile.group_color,
                'asset': custom_url or static_asset,
                'path_line': pl,
                'card_turn_deg': card_turn,
                'grid_row': gr,
                'grid_col': gc,
                'rent': tile.rent_base or None,
                'rent_1house': tile.rent_1house or None,
                'rent_2house': tile.rent_2house or None,
                'rent_3house': tile.rent_3house or None,
                'rent_4house': tile.rent_4house or None,
                'rent_hotel': tile.rent_hotel or None,
                'house_cost': tile.house_price or None,
                'description': tile.description or '',
            }
        )
    return display, js
