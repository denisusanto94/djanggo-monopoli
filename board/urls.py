from django.urls import path
from . import views, admin_views

urlpatterns = [
    path("", views.board, name="board"),
    path("api/tile/<int:index>/", views.tile_detail, name="tile_detail"),
    path("api/roll/", views.roll, name="roll"),
    
    # Admin Routes
    path("admin/", admin_views.admin_login, name="admin_login"),
    path("admin/logout/", admin_views.admin_logout, name="admin_logout"),
    path("admin/dashboard/", admin_views.admin_dashboard, name="admin_dashboard"),
    path("admin/users/", admin_views.admin_users, name="admin_users"),
    path("admin/boards/", admin_views.admin_board_list, name="admin_boards"),
    path("admin/boards/<int:board_id>/tiles/", admin_views.admin_tile_setup, name="admin_tiles"),
    path("admin/characters/", admin_views.admin_characters, name="admin_characters"),
    path("admin/characters/delete/<int:char_id>/", admin_views.admin_character_delete, name="admin_character_delete"),
    path("admin/abilities/", admin_views.admin_abilities, name="admin_abilities"),
]
