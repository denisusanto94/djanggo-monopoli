from __future__ import annotations

import json
from types import SimpleNamespace

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .boardplay import board_to_play_payload
from .models import Board, Character
from .tiles import TILES


def board(request):
    """Papan permainan: default dari `tiles.py` (Papan Jakarta), atau Board DB jika ?board=<id>."""
    tiles_display = [
        SimpleNamespace(
            index=t.index,
            code=t.code,
            name=t.name,
            kind=t.kind,
            price=t.price,
            color=t.color,
            asset_file=t.asset_file,
            custom_image_url=None,
            grid_row=t.grid_row,
            grid_col=t.grid_col,
            path_line=t.path_line,
            card_turn_deg=t.card_turn_deg,
        )
        for t in TILES
    ]
    tiles_js = [
        {
            'index': t.index,
            'code': t.code,
            'name': t.name,
            'kind': t.kind,
            'price': t.price,
            'color': t.color,
            'asset': t.asset_file,
            'path_line': t.path_line,
            'card_turn_deg': t.card_turn_deg,
            'grid_row': t.grid_row,
            'grid_col': t.grid_col,
            'rent': t.rent,
            'rent_1house': t.rent_1house,
            'rent_2house': t.rent_2house,
            'rent_3house': t.rent_3house,
            'rent_4house': t.rent_4house,
            'rent_hotel': t.rent_hotel,
            'house_cost': t.house_cost,
            'description': t.description,
        }
        for t in TILES
    ]
    selected_board_id = None
    selected_board_name = None
    setup_skip_board_pick = False

    raw_board = request.GET.get('board')
    if raw_board:
        try:
            bid = int(raw_board)
        except (TypeError, ValueError):
            bid = None
        if bid is None or bid <= 0:
            return redirect('board')
        b = (
            Board.objects.filter(pk=bid, is_active=True)
            .prefetch_related('tiles')
            .first()
        )
        if b is not None and b.tiles.exists():
            tiles_display, tiles_js = board_to_play_payload(request, b)
            selected_board_id = b.id
            selected_board_name = b.name
            setup_skip_board_pick = True
        else:
            return redirect('board')
    else:
        builtin = (
            Board.objects.filter(is_builtin=True, is_active=True)
            .prefetch_related('tiles')
            .first()
        )
        if builtin is not None and builtin.tiles.exists():
            tiles_display, tiles_js = board_to_play_payload(request, builtin)

    characters = Character.objects.filter(is_active=True)
    characters_js = [
        {
            'id': c.id,
            'name': c.name,
            'shape': c.shape,
            'color': c.color,
            'image': c.image.url if c.image else None,
            'model_3d': c.model_3d.url if c.model_3d else None,
        }
        for c in characters
    ]

    boards_qs = (
        Board.objects.filter(is_active=True)
        .order_by('-is_builtin', 'name')
        .prefetch_related('tiles')
    )
    boards_js = [
        {
            'id': b.id,
            'name': b.name,
            'description': (b.description or '')[:200],
            'tile_count': b.tiles.count(),
            'is_builtin': b.is_builtin,
        }
        for b in boards_qs
        if b.tiles.exists()
    ]

    return render(
        request,
        'board/index.html',
        {
            'tiles': tiles_display,
            'tiles_json': json.dumps(tiles_js, ensure_ascii=False),
            'characters_json': json.dumps(characters_js, ensure_ascii=False),
            'boards_json': json.dumps(boards_js, ensure_ascii=False),
            'setup_skip_board_pick': setup_skip_board_pick,
            'selected_board_id': selected_board_id,
            'selected_board_name': selected_board_name,
        },
    )


@require_GET
def api_boards(request):
    data = []
    for b in (
        Board.objects.filter(is_active=True)
        .order_by('-is_builtin', 'name')
        .prefetch_related('tiles')
    ):
        n = b.tiles.count()
        if n == 0:
            continue
        data.append(
            {
                'id': b.id,
                'name': b.name,
                'description': (b.description or '')[:300],
                'tile_count': n,
                'is_builtin': b.is_builtin,
            }
        )
    return JsonResponse({'boards': data})


@require_GET
def tile_detail(request, index: int):
    if index < 0 or index >= len(TILES):
        return JsonResponse({'error': 'not_found'}, status=404)
    t = TILES[index]
    return JsonResponse(
        {
            'index': t.index,
            'code': t.code,
            'name': t.name,
            'kind': t.kind,
            'price': t.price,
            'color': t.color,
            'asset': t.asset_file,
            'path_line': t.path_line,
            'card_turn_deg': t.card_turn_deg,
        }
    )


@require_POST
def roll(request):
    return JsonResponse({'ok': True, 'message': 'Gunakan dadu di klien untuk demo.'})
