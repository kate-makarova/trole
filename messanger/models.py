from django.contrib.auth.models import User
from django.db import models
from django.db.models import DO_NOTHING, CASCADE
from trole_game.models import Game


class Chat(models.Model):
    class Meta:
        abstract = True
    name = models.CharField(max_length=300)
    participants = models.ManyToManyField(User)
    last_post = models.ForeignKey('ChatPost', on_delete=models.CASCADE)
    channel = models.CharField(max_length=100)

class ChatPost(models.Model):
    author = models.ForeignKey(User, on_delete=DO_NOTHING)
    chat = models.ForeignKey(Chat, on_delete=CASCADE)
    date_created = models.DateTimeField()
    content_bb = models.TextField()
    content_html = models.TextField()

class PrivateChat(Chat):
    admin = models.ForeignKey(User, on_delete=models.DO_NOTHING)

class GameChat(Chat):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    access_level = models.IntegerField(default=1)

