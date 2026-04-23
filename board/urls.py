from django.urls import path

from . import admin_views, views

urlpatterns = [
    path('', views.board, name='board'),
    path('api/tile/<int:index>/', views.tile_detail, name='tile_detail'),
    path('api/boards/', views.api_boards, name='api_boards'),
    path('api/roll/', views.roll, name='roll'),
    path('admin/login/', admin_views.admin_login, name='admin_login'),
    path('admin/logout/', admin_views.admin_logout, name='admin_logout'),
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.admin_users, name='admin_users'),
    path('admin/boards/', admin_views.admin_board_list, name='admin_boards'),
    path('admin/boards/new/', admin_views.admin_board_new, name='admin_board_new'),
    path(
        'admin/boards/<int:board_id>/toggle-active/',
        admin_views.admin_board_toggle_active,
        name='admin_board_toggle',
    ),
    path(
        'admin/boards/<int:board_id>/delete/',
        admin_views.admin_board_delete,
        name='admin_board_delete',
    ),
    path(
        'admin/boards/<int:board_id>/tiles/<int:tile_id>/edit/',
        admin_views.admin_tile_edit,
        name='admin_tile_edit',
    ),
    path(
        'admin/boards/<int:board_id>/tiles/<int:tile_id>/delete/',
        admin_views.admin_tile_delete,
        name='admin_tile_delete',
    ),
    path('admin/boards/<int:board_id>/tiles/', admin_views.admin_tile_setup, name='admin_tiles'),
    path('admin/characters/', admin_views.admin_characters, name='admin_characters'),
    path(
        'admin/characters/delete/<int:char_id>/',
        admin_views.admin_character_delete,
        name='admin_character_delete',
    ),
    path('admin/abilities/', admin_views.admin_abilities, name='admin_abilities'),
    path('admin/', admin_views.admin_root_redirect),
]
