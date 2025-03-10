# chat/views.py
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from messanger.models import PrivateChat, ChatParticipation


def test(request, id):
    #chat = PrivateChat.oblects.get(pk=id)
   # user_id = 1
   # participation = ChatParticipation.objects.select_related('user_setting').filter(chat_type=1, private_chat_id=id, user_setting__user_id=user_id)[0]

    return render(request, "messanger/test.html", {"room_name": 'uuu'})

class ActiveChats(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        participation = ChatParticipation.objects.filter(user_id=user_id)
        data = []
        for p in participation:
            if p.chat_type == 1:
                chat = p.private_chat
            else:
                chat = p.game_chat
            data.append({
                "id": chat.id,
                "type": p.chat_type,
                "title": chat.name,
                "users": [],
                "unread": 0
            })
        return Response({"data": data})
