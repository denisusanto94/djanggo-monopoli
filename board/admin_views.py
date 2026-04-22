from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User, Role, Permission, Board, Tile, Character, AbilityCard

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
                return redirect('admin_dashboard')
            else:
                error = "Anda tidak memiliki akses ke halaman ini."
        else:
            error = "Email atau password salah."
    
    return render(request, 'admin/login.html', {'error': error})

@login_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@login_required(login_url='admin_login')
def admin_dashboard(request):
    stats = {
        'users': User.objects.count(),
        'boards': Board.objects.count(),
        'characters': Character.objects.count(),
        'abilities': AbilityCard.objects.count(),
    }
    return render(request, 'admin/dashboard.html', {'stats': stats})

@login_required(login_url='admin_login')
def admin_users(request):
    users = User.objects.all()
    roles = Role.objects.all()
    return render(request, 'admin/users.html', {'users': users, 'roles': roles})

@login_required(login_url='admin_login')
def admin_board_list(request):
    boards = Board.objects.all()
    return render(request, 'admin/board_list.html', {'boards': boards})

@login_required(login_url='admin_login')
def admin_tile_setup(request, board_id):
    board = Board.objects.get(id=board_id)
    tiles = Tile.objects.filter(board=board).order_by('position')
    return render(request, 'admin/tiles.html', {'board': board, 'tiles': tiles})

@login_required(login_url='admin_login')
def admin_characters(request):
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
                is_active=is_active
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
    Character.objects.get(id=char_id).delete()
    return redirect('admin_characters')

@login_required(login_url='admin_login')
def admin_abilities(request):
    abilities = AbilityCard.objects.all()
    return render(request, 'admin/abilities.html', {'abilities': abilities})
