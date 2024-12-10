from django.contrib.auth.models import User
from django.db import models
from django.db.models import DO_NOTHING


class Genre(models.Model):
    name = models.CharField(max_length=200)

class Rating(models.Model):
    name = models.CharField(max_length=5)
    description=models.TextField()

class Fandom(models.Model):
    name = models.CharField(max_length=200)
    genre = models.ForeignKey(Genre, on_delete=models.DO_NOTHING)

class Game(models.Model):
    name = models.CharField(max_length=300)
    fandom = models.ForeignKey(Fandom, on_delete=models.DO_NOTHING)
    genre = models.ForeignKey(Genre, on_delete=models.DO_NOTHING)
    rating = models.ForeignKey(Rating, on_delete=models.DO_NOTHING)
    image = models.CharField(max_length=300)
    description = models.TextField()
    date_created = models.DateTimeField()
    user_created = models.ForeignKey(User, on_delete=DO_NOTHING)

class Character(models.Model):
    name = models.CharField(max_length=300)
    game = models.ForeignKey(Game, on_delete=models.DO_NOTHING)
    avatar = models.CharField(max_length=300)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField()

class Episode(models.Model):
    name = models.CharField(max_length=300)
    image = models.CharField(max_length=300)
    description = models.TextField()
    rating = models.ForeignKey(Rating, on_delete=models.DO_NOTHING)
    characters = models.ManyToManyField(Character, on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField()
    number_of_posts = models.IntegerField()
    last_post_date = models.DateTimeField()
    last_post_author = models.ForeignKey(Character, on_delete=models.DO_NOTHING)

class Post(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.DO_NOTHING)
    post_author = models.ForeignKey(Character, on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField()
    content = models.TextField()
    order = models.IntegerField()