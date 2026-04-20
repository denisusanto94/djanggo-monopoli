from __future__ import annotations

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .tiles import TILES


def board(request):
    tiles_js = [
        {
            "index": t.index,
            "code": t.code,
            "name": t.name,
            "kind": t.kind,
            "price": t.price,
            "color": t.color,
            "asset": t.asset_file,
            "path_line": t.path_line,
            "card_turn_deg": t.card_turn_deg,
        }
        for t in TILES
    ]
    return render(
        request,
        "board/index.html",
        {
            "tiles": TILES,
            "tiles_json": json.dumps(tiles_js, ensure_ascii=False),
        },
    )


@require_GET
def tile_detail(request, index: int):
    if index < 0 or index >= len(TILES):
        return JsonResponse({"error": "not_found"}, status=404)
    t = TILES[index]
    return JsonResponse(
        {
            "index": t.index,
            "code": t.code,
            "name": t.name,
            "kind": t.kind,
            "price": t.price,
            "color": t.color,
            "asset": t.asset_file,
            "path_line": t.path_line,
            "card_turn_deg": t.card_turn_deg,
        }
    )


@require_POST
def roll(request):
    """Placeholder untuk logika server-side nanti."""
    return JsonResponse({"ok": True, "message": "Gunakan dadu di klien untuk demo."})
