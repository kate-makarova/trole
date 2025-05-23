import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import DO_NOTHING, CASCADE
from trole_game.models import Game


class Chat(models.Model):
    class Meta:
        abstract = True
    name = models.CharField(max_length=300)

class ChatPost(models.Model):
    class Meta:
        abstract = True
    author = models.ForeignKey(User, on_delete=DO_NOTHING)
    chat = models.ForeignKey(Chat, on_delete=CASCADE)
    date_created = models.DateTimeField()
    content_bb = models.TextField()
    content_html = models.TextField()

class PrivateChat(Chat):
    chat_admin = models.ForeignKey(User, on_delete=models.DO_NOTHING)

class GameChat(Chat):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    access_level = models.IntegerField(default=1)

class PrivateChatPost(ChatPost):
    chat = models.ForeignKey(PrivateChat, on_delete=CASCADE)

class GameChatPost(ChatPost):
    chat = models.ForeignKey(GameChat, on_delete=CASCADE)

    # 1 for private chars, 2 for game chats
class ChatParticipation(models.Model):
    chat_type = models.IntegerField(default=1)
    private_chat = models.ForeignKey(PrivateChat, null=True, on_delete=models.CASCADE)
    game_chat = models.ForeignKey(GameChat, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_read_message_date = models.DateTimeField(default=datetime.datetime.now)
    last_open_private_chat = models.BooleanField(default=False)

