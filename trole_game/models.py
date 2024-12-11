from django.contrib.auth.models import User
from django.db import models
from django.db.models import DO_NOTHING

class GameStatus(models.Model):
    name = models.CharField(max_length=50)

class EpisodeStatus(models.Model):
    name = models.CharField(max_length=50)

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
    status = models.ForeignKey(GameStatus, on_delete=models.DO_NOTHING)
    description = models.TextField()
    date_created = models.DateTimeField()
    user_created = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    total_posts = models.IntegerField()
    total_episodes = models.IntegerField()
    total_characters = models.IntegerField()
    last_post_published = models.DateTimeField()
    permission_level = models.IntegerField()

class UserGameParticipation(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField()

class GameEpisodeCategory(models.Model):
    name = models.CharField(max_length=50)
    order = models.IntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

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
    status = models.ForeignKey(EpisodeStatus, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(GameEpisodeCategory, on_delete=DO_NOTHING)
    rating = models.ForeignKey(Rating, on_delete=models.DO_NOTHING)
    characters = models.ManyToManyField(Character, on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField()
    number_of_posts = models.IntegerField()
    last_post_date = models.DateTimeField()
    last_post_author = models.ForeignKey(Character, on_delete=models.DO_NOTHING)
    in_category_order = order = models.IntegerField()

class Post(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.DO_NOTHING)
    post_author = models.ForeignKey(Character, on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField()
    content = models.TextField()
    order = models.IntegerField()

class CharacterCounter(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    participating_episodes = models.IntegerField()
    posts_written = models.IntegerField()
    unread_posts = models.IntegerField()
    last_post_date = models.DateTimeField()

