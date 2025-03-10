from django.urls import path

from . import views

urlpatterns = [
    path("test/<int:id>", views.test, name="test"),
    path("api/active-chats/<int:user_id>", views.ActiveChats.as_view(), name="active_chats"),
    # path("chat/<int:id>", views.room, name="private_chat"),
    # path("game_chat/<int:game_id>", views.room, name="default_game_chat"),
    # path("game_chat/<int:game_id>/<int:id>", views.room, name="custom_game_chat"),
]