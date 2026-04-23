from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .default_tiles_seed import seed_tiles_for_board
from .models import AbilityCard, Board, Character, Role, Tile, User


def _require_staff(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    if not getattr(request.user, 'is_staff', False):
        messages.error(request, 'Anda tidak memiliki izin mengakses halaman admin.')
        return redirect('admin_login')
    return None


def seed_board_tiles_from_default(board: Board) -> int:
    return seed_tiles_for_board(board, Tile)


def _parse_int(post, key, default=0):
    raw = post.get(key)
    if raw is None or raw == '':
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def admin_root_redirect(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('admin_login')


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                next_url = (request.POST.get('next') or request.GET.get('next') or '').strip()
                if next_url.startswith('/') and not next_url.startswith('//'):
                    return redirect(next_url)
                return redirect('admin_dashboard')
            error = 'Anda tidak memiliki akses ke halaman ini.'
        else:
            error = 'Email atau password salah.'

    return render(
        request,
        'admin/login.html',
        {'error': error, 'next': request.GET.get('next', '')},
    )


@login_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    return redirect('admin_login')


@login_required(login_url='admin_login')
def admin_dashboard(request):
    redir = _require_staff(request)
    if redir:
        return redir
    stats = {
        'users': User.objects.count(),
        'boards': Board.objects.count(),
        'characters': Character.objects.count(),
        'abilities': AbilityCard.objects.count(),
    }
    boards = Board.objects.all().order_by('-is_builtin', '-updated_at')
    return render(request, 'admin/dashboard.html', {'stats': stats, 'boards': boards})


@login_required(login_url='admin_login')
def admin_users(request):
    redir = _require_staff(request)
    if redir:
        return redir
    users = User.objects.all()
    roles = Role.objects.all()
    return render(request, 'admin/users.html', {'users': users, 'roles': roles})


def _redirect_after_board_quick_add_error(return_board_id):
    try:
        bid = int(return_board_id)
    except (TypeError, ValueError):
        return redirect('admin_boards')
    if bid > 0 and Board.objects.filter(pk=bid).exists():
        return redirect('admin_tiles', board_id=bid)
    return redirect('admin_boards')


@login_required(login_url='admin_login')
def admin_board_list(request):
    redir = _require_staff(request)
    if redir:
        return redir
    boards = Board.objects.all().order_by('-is_builtin', '-updated_at')
    return render(request, 'admin/board_list.html', {'boards': boards})


@login_required(login_url='admin_login')
@require_POST
def admin_board_quick_add(request):
    redir = _require_staff(request)
    if redir:
        return redir
    ret = request.POST.get('return_board_id')
    name = (request.POST.get('quick_name') or '').strip()
    if not name:
        messages.error(request, 'Nama papan wajib diisi.')
        return _redirect_after_board_quick_add_error(ret)
    desc = (request.POST.get('quick_description') or '').strip()
    board = Board.objects.create(
        name=name,
        description=desc or None,
        is_active=True,
        is_builtin=False,
    )
    messages.success(
        request,
        f'Papan "{board.name}" dibuat. Atur petak atau generate dari template.',
    )
    return redirect('admin_tiles', board_id=board.id)


@login_required(login_url='admin_login')
@require_POST
def admin_board_toggle_active(request, board_id):
    redir = _require_staff(request)
    if redir:
        return redir
    board = get_object_or_404(Board, pk=board_id)
    board.is_active = not board.is_active
    board.save(update_fields=['is_active', 'updated_at'])
    messages.success(
        request,
        f'Papan "{board.name}" sekarang {"aktif" if board.is_active else "nonaktif"}.',
    )
    return redirect('admin_boards')


@login_required(login_url='admin_login')
@require_POST
def admin_board_delete(request, board_id):
    redir = _require_staff(request)
    if redir:
        return redir
    board = get_object_or_404(Board, pk=board_id)
    if board.is_builtin:
        messages.error(
            request,
            'Papan bawaan tidak dapat dihapus. Nonaktifkan papan jika tidak ingin ditampilkan di permainan.',
        )
        return redirect('admin_boards')
    name = board.name
    board.delete()
    messages.success(request, f'Papan "{name}" dan semua petaknya telah dihapus.')
    return redirect('admin_boards')


@login_required(login_url='admin_login')
def admin_board_new(request):
    redir = _require_staff(request)
    if redir:
        return redir
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        if not name:
            messages.error(request, 'Nama papan wajib diisi.')
        else:
            desc = (request.POST.get('description') or '').strip()
            board = Board.objects.create(
                name=name,
                description=desc or None,
                is_active=True,
                is_builtin=False,
            )
            messages.success(
                request,
                f'Papan "{board.name}" dibuat. Atur petak atau generate dari template.',
            )
            return redirect('admin_tiles', board_id=board.id)
    return render(request, 'admin/board_form.html', {'board': None})


@login_required(login_url='admin_login')
def admin_tile_setup(request, board_id):
    redir = _require_staff(request)
    if redir:
        return redir
    board = get_object_or_404(Board, pk=board_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'generate_default':
            n = seed_board_tiles_from_default(board)
            messages.success(
                request,
                f'Berhasil membuat {n} petak dari template papan standar.',
            )
            return redirect('admin_tiles', board_id=board.id)
        messages.error(request, 'Aksi tidak dikenal.')
        return redirect('admin_tiles', board_id=board.id)
    tiles = Tile.objects.filter(board=board).order_by('position')
    return render(request, 'admin/tiles.html', {'board': board, 'tiles': tiles})


@login_required(login_url='admin_login')
def admin_tile_edit(request, board_id, tile_id):
    redir = _require_staff(request)
    if redir:
        return redir
    board = get_object_or_404(Board, pk=board_id)
    tile = get_object_or_404(Tile, pk=tile_id, board=board)
    if request.method == 'POST':
        allowed_tt = {c[0] for c in Tile.TILE_TYPES}
        tt = request.POST.get('tile_type')
        dm = request.POST.get('display_mode')
        tile.name = (request.POST.get('name') or '').strip() or tile.name
        tile.code = (request.POST.get('code') or '').strip()[:64]
        if tt in allowed_tt:
            tile.tile_type = tt
        if dm in ('static', 'customize'):
            tile.display_mode = dm
        tile.path_line = max(1, min(4, _parse_int(request.POST, 'path_line', tile.path_line or 1)))
        tile.group_color = (request.POST.get('group_color') or '').strip()[:32]
        tile.price = _parse_int(request.POST, 'price', tile.price)
        tile.rent_base = _parse_int(request.POST, 'rent_base', tile.rent_base)
        tile.rent_1house = _parse_int(request.POST, 'rent_1house', tile.rent_1house)
        tile.rent_2house = _parse_int(request.POST, 'rent_2house', tile.rent_2house)
        tile.rent_3house = _parse_int(request.POST, 'rent_3house', tile.rent_3house)
        tile.rent_4house = _parse_int(request.POST, 'rent_4house', tile.rent_4house)
        tile.rent_hotel = _parse_int(request.POST, 'rent_hotel', tile.rent_hotel)
        tile.house_price = _parse_int(request.POST, 'house_price', tile.house_price)
        tile.hotel_price = _parse_int(request.POST, 'hotel_price', tile.hotel_price)
        tile.description = (request.POST.get('description') or '').strip()
        if 'image' in request.FILES:
            if tile.image:
                tile.image.delete(save=False)
            tile.image = request.FILES['image']
        if request.POST.get('clear_image') == '1':
            if tile.image:
                tile.image.delete(save=False)
            tile.image = None
        tile.save()
        messages.success(request, f'Petak "{tile.name}" disimpan.')
        return redirect('admin_tiles', board_id=board.id)
    return render(
        request,
        'admin/tile_edit.html',
        {
            'board': board,
            'tile': tile,
            'tile_types': Tile.TILE_TYPES,
            'display_modes': Tile.DISPLAY_MODE,
        },
    )


@login_required(login_url='admin_login')
@require_POST
def admin_tile_delete(request, board_id, tile_id):
    redir = _require_staff(request)
    if redir:
        return redir
    board = get_object_or_404(Board, pk=board_id)
    tile = get_object_or_404(Tile, pk=tile_id, board=board)
    name = tile.name
    if tile.image:
        tile.image.delete(save=False)
    tile.delete()
    messages.success(request, f'Petak "{name}" dihapus.')
    return redirect('admin_tiles', board_id=board.id)


@login_required(login_url='admin_login')
def admin_characters(request):
    redir = _require_staff(request)
    if redir:
        return redir
    if request.method == 'POST':
        char_id = request.POST.get('id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        shape = request.POST.get('shape')
        color = request.POST.get('color')
        is_active = request.POST.get('is_active') == 'on'

        if char_id:
            character = Character.objects.get(id=char_id)
            character.name = name
            character.description = description
            character.shape = shape
            character.color = color
            character.is_active = is_active
        else:
            character = Character(
                name=name,
                description=description,
                shape=shape,
                color=color,
                is_active=is_active,
            )

        if 'image' in request.FILES:
            character.image = request.FILES['image']
        if 'model_3d' in request.FILES:
            character.model_3d = request.FILES['model_3d']

        character.save()
        return redirect('admin_characters')

    characters = Character.objects.all()
    return render(request, 'admin/characters.html', {'characters': characters})


@login_required(login_url='admin_login')
def admin_character_delete(request, char_id):
    redir = _require_staff(request)
    if redir:
        return redir
    Character.objects.get(id=char_id).delete()
    return redirect('admin_characters')


@login_required(login_url='admin_login')
def admin_abilities(request):
    redir = _require_staff(request)
    if redir:
        return redir
    abilities = AbilityCard.objects.all()
    return render(request, 'admin/abilities.html', {'abilities': abilities})
