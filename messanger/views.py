# chat/views.py
from django.shortcuts import render

from messanger.models import PrivateChat, ChatParticipation


def test(request, id):
    #chat = PrivateChat.oblects.get(pk=id)
   # user_id = 1
   # participation = ChatParticipation.objects.select_related('user_setting').filter(chat_type=1, private_chat_id=id, user_setting__user_id=user_id)[0]

    return render(request, "messanger/test.html", {"room_name": 'uuu'})