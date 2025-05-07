from django.urls import path

from . import views

urlpatterns = [
    path("test/<int:id>", views.test, name="test"),
    path("api/active-chats", views.ActiveChats.as_view(), name="active_chats"),
    path("api/private-chat/<int:id>", views.GetPrivateChat.as_view(), name="get_private_chat"),
    path("api/private-chat-messages/<int:id>", views.PrivateChatGetMessages.as_view(), name="private_chat_get_messages"),
    path("api/private-chat-messages/<int:id>/<int:page>", views.PrivateChatGetMessages.as_view(),
         name="private_chat_get_messages_full"),
    path("api/private-chat-add", views.AddPrivateChat.as_view(), name="add_private_chat"),
    path("api/private-chat-add-participant", views.PrivateChatAddParticipant.as_view(), name="add_private_chat_participant"),
    path("api/last-open-chat", views.LastOpenChat.as_view(), name="last_open_chat"),
    path("api/last-open-chat/update", views.LastOpenChatUpdate.as_view(), name="last_open_chat_update"),
]