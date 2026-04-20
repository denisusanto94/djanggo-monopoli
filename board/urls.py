from django.urls import path

from . import views

urlpatterns = [
    path("", views.board, name="board"),
    path("api/tile/<int:index>/", views.tile_detail, name="tile_detail"),
    path("api/roll/", views.roll, name="roll"),
]
