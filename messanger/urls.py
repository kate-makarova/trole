from django.urls import path

from . import views

urlpatterns = [
    path("chat/<int:id>", views.room, name="private_chat"),
    path("game_chat/<int:game_id>", views.room, name="default_game_chat"),
    path("game_chat/<int:game_id>/<int:id>", views.room, name="custom_game_chat"),
]