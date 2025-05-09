# chat/views.py
from datetime import datetime

from django.db import connection
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from messanger.models import PrivateChat, ChatParticipation, PrivateChatPost, ChatPost, GameChat, GameChatPost


class ActiveChats(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        participation = ChatParticipation.objects.filter(user_id=request.user.id)
        data = []
        for p in participation:
            if p.chat_type == 1:
                chat = p.private_chat
                unread = PrivateChatPost.objects.filter(chat_id=chat.id,
                                                 date_created__gt=p.last_read_message_date).count()

                users = []
                participants = ChatParticipation.objects.filter(private_chat_id=chat.id)
                for p1 in participants:
                    users.append({
                        "id": p1.user.id,
                        "name": p1.user.username,
                        "avatar": ""
                    })
            else:
                chat = p.game_chat
                unread = GameChatPost.objects.filter(chat_id=chat.id,
                                                    date_created__gt=p.last_read_message_date).count()
                users = []
                participants = ChatParticipation.objects.filter(private_chat_id=chat.id)
                for p1 in participants:
                    users.append({
                        "id": p1.user.id,
                        "name": p1.user.username,
                        "avatar": ""
                    })

            data.append({
                "id": chat.id,
                "type": p.chat_type,
                "title": chat.name,
                "users": users,
                "unread": unread
            })
        return Response({"data": data})

class UpdateLastReadMessageDate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.data['chat_type'] == 1:
            participation = ChatParticipation.objects.filter(user_id=request.user.id, private_chat_id=request.data['chat_id'])
        else:
            participation = ChatParticipation.objects.filter(user_id=request.user.id,
                                                             game_chat_id=request.data['chat_id'])
        if participation.exists():
            participation = participation[0]
            participation.last_read_message_date = datetime.datetime.now()
            participation.save()


class GetPrivateChat(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        participation = ChatParticipation.objects.filter(user_id=request.user.id, private_chat_id=id)
        if len(participation) == 0:
            return Response({'data': 'Not found'}, status=404)

        chat = PrivateChat.objects.get(pk=id)
        participants = ChatParticipation.objects.filter(private_chat_id=id)

        data = {
            "id": chat.id,
            "title": chat.name,
            "users": []
        }

        for participant in participants:
            data['users'].append({
                "id": participant.user.id,
                "name": participant.user.username,
                "avatar": "--"
            })

        return Response({"data": data})

class PrivateChatGetMessages(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id, page=1):
        limit = 20
        offset = (page - 1) * limit
        participation = ChatParticipation.objects.filter(user_id=request.user.id, private_chat_id=id)
        if len(participation) == 0:
            return Response({'data': 'Not found'}, status=404)

        data = []
        posts = PrivateChatPost.objects.filter(chat_id=id).order_by('-date_created')[offset:offset+limit]
        for post in reversed(posts):
            data.append({
                "id": post.id,
                "text": post.content_html,
                "user": {
                    "id": post.author.id,
                    "name": post.author.username,
                    "avatar": "--"
                    },
                "time": post.date_created
            })

        return Response({"data": data})

class AddPrivateChat(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat = PrivateChat.objects.create(
            name = request.data['name'],
            chat_admin=request.user
        )

        for user_data in request.data['participants']:
            ChatParticipation.objects.create(
                chat_type=1,
                private_chat=chat,
                user_id=user_data['id']
            )

        return Response({'data': 'ok'})


class RenamePrivateChat(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat = PrivateChat.objects.get(pk=request.data['id'])
        chat.name = request.data['name']
        chat.save()

        return Response({'data': 'ok'})

class PrivateChatAddParticipant(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat = PrivateChat.objects.get(pk=request.data['id'])
        if chat.admin.id != request.user.id:
            return Response({'data': 'Not allowed'}, status=403)

        participation = ChatParticipation.objects.filter(private_chat=chat, user_id=request.data['user_id'])
        if len(participation):
            return Response({'data': 'Already participating'}, status=400)

        ChatParticipation.objects.create(
            chat_type=1,
            private_chat=chat,
            user_id=request.data['user_id'],
        )

        return Response({'data': 'ok'})


class PrivateChatRemoveParticipant(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat = PrivateChat.objects.get(pk=request.data['id'])
        if chat.admin.id != request.user.id:
            return Response({'data': 'Not allowed'}, status=403)

        participation = ChatParticipation.objects.filter(private_chat=chat, user_id=request.data['user_id'])
        if len(participation) == 0:
            return Response({'data': 'Not participating'}, status=400)

        participation.delete()

        return Response({'data': 'ok'})


class LastOpenChat(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        participations = ChatParticipation.objects.filter(user_id=request.user.id, last_open_private_chat=True)
        if len(participations) == 0:
            return Response({'data': 0})
        participation = participations[0]
        return Response({'data': participation.private_chat.id})

class LastOpenChatUpdate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_participation = ChatParticipation.objects.filter(user_id=request.user.id, last_open_private_chat=True)
        if len(old_participation) != 0:
            old_participation = old_participation[0]
            old_participation.last_open_private_chat = False
            old_participation.save()

        participation = ChatParticipation.objects.filter(user_id=request.user.id, private_chat_id=request.data['chat_id'])
        if len(participation) == 0:
            return Response({'data': 'Not found'}, status=404)
        participation = participation[0]
        participation.last_open_private_chat = True
        participation.save()

        return Response({'data': 'ok'})


class TotalPrivateUnread:
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT COUNT(*) AS total_unread_messages
                           FROM messanger_privatechatpost m
                                    LEFT JOIN messanger_chatparticipation r
                                              ON m.chat_id = r.private_chat_id AND r.user_id = %s
                           WHERE m.date_created > r.last_read_message_date;
                           """, [request.user.id])
            row = cursor.fetchone()
        return Response({'data': row[0]})