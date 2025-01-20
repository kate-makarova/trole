from django.contrib.auth.models import User
from django.db import models
from django.db.models import DO_NOTHING

class Language(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=300)
    name_rus = models.CharField(max_length=300)

class UserSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ui_language = models.CharField(max_length=2)
    timezone = models.CharField(max_length=20)

class Genre(models.Model):
    name = models.CharField(max_length=200)
    name_rus = models.CharField(max_length=200, null=True)

class MediaType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    name_rus = models.CharField(max_length=50, null=True)
    description_rus = models.TextField(null=True)

class Fandom(models.Model):
    name = models.CharField(max_length=200)
    name_rus = models.CharField(max_length=200, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.DO_NOTHING)
    mediaType = models.ForeignKey(MediaType, on_delete=models.DO_NOTHING)

class Game(models.Model):
    name = models.CharField(max_length=300)
    fandoms = models.ManyToManyField(Fandom)
    genres = models.ManyToManyField(Genre)
    rating_id = models.IntegerField()
    image = models.CharField(max_length=300)
    status_id = models.IntegerField()
    description = models.TextField()
    date_created = models.DateTimeField()
    user_created = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    total_posts = models.IntegerField()
    total_episodes = models.IntegerField()
    total_characters = models.IntegerField()
    total_users = models.IntegerField()
    total_articles = models.IntegerField()
    last_post_published = models.DateTimeField(null=True)
    permission_level = models.IntegerField()
    was_online_in_24 = models.IntegerField()
    languages = models.ManyToManyField(Language)

class UserGameParticipation(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField()
    role = models.IntegerField()

class GameEpisodeCategory(models.Model):
    name = models.CharField(max_length=50)
    order = models.IntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

class CharacterSheetTemplate(models.Model):
    game = models.ForeignKey(Game, on_delete=models.DO_NOTHING)

    name_field_name = models.CharField(max_length=300, null=True)
    avatar_field_name = models.CharField(max_length=300, null=True)
    description_field_name = models.CharField(max_length=300, null=True)

    name_description = models.CharField(null=True)
    avatar_description = models.CharField(null=True)
    description_description = models.CharField(null=True)

    name_order = models.IntegerField(default=1, null=True)
    avatar_order = models.IntegerField(default=2, null=True)
    description_order = models.IntegerField(default=3, null=True)
    is_active = models.BooleanField()

class Character(models.Model):
    name = models.CharField(max_length=300)
    game = models.ForeignKey(Game, on_delete=models.DO_NOTHING)
    avatar = models.CharField(max_length=300)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField()
    participating_episodes = models.IntegerField()
    posts_written = models.IntegerField()
    last_post_date = models.DateTimeField(null=True)
    character_sheet_template = models.ForeignKey(CharacterSheetTemplate, on_delete=models.DO_NOTHING)

class Episode(models.Model):
    name = models.CharField(max_length=300)
    image = models.CharField(max_length=300)
    description = models.TextField()
    status_id = models.IntegerField()
    category = models.ForeignKey(GameEpisodeCategory, on_delete=DO_NOTHING, null=True)
    rating_id = models.IntegerField()
    game = models.ForeignKey(Game, on_delete=models.DO_NOTHING)
    characters = models.ManyToManyField(Character)
    user_created = models.ForeignKey(User, on_delete=DO_NOTHING)
    date_created = models.DateTimeField()
    number_of_posts = models.IntegerField()
    last_post_date = models.DateTimeField(null=True)
    last_post_author = models.ForeignKey(Character, related_name='last_post_author_id', on_delete=models.DO_NOTHING, null=True)
    in_category_order = models.IntegerField(null=True)

    def user_participates(self, user_id):
        for character in self.characters.all():
            if character.user.id == user_id:
                return True
        return False

class Post(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.DO_NOTHING)
    post_author = models.ForeignKey(Character, on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField()
    content_bb = models.TextField()
    content_html = models.TextField()
    order = models.IntegerField()

class CharacterEpisodeNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    is_read = models.BooleanField()
    date_created = models.DateTimeField()
    date_read = models.DateTimeField(null=True)
    notification_type = models.IntegerField()
    post_id = models.IntegerField(null=True)


class UserGameDisplay(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    display_category = models.IntegerField()
    is_on_main_page = models.BooleanField()
    order = models.IntegerField(null=True)

class SiteStatistics(models.Model):
    total_fandoms = models.IntegerField()
    total_games = models.IntegerField()
    total_posts = models.IntegerField()
    total_episodes = models.IntegerField()
    total_characters = models.IntegerField()
    total_users = models.IntegerField()
    permission_level = models.IntegerField()
    was_online_in_24 = models.IntegerField()

class Article(models.Model):
    name = models.CharField(max_length=300)
    content_bb = models.TextField()
    content_html = models.TextField()
    game = models.ForeignKey(Game, on_delete=models.DO_NOTHING)
    user_created = models.ForeignKey(User, on_delete=DO_NOTHING)
    date_created = models.DateTimeField()
    is_index = models.BooleanField()

class CharacterSheetTemplateField(models.Model):
    character_sheet_template = models.ForeignKey(CharacterSheetTemplate, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=300)
    type = models.IntegerField()
    options = models.TextField(null=True)
    description = models.TextField()
    is_required = models.BooleanField()
    order = models.IntegerField()
    is_active = models.BooleanField(default=True)

class CharacterSheetField(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    character_sheet_template_field = models.ForeignKey(CharacterSheetTemplateField, on_delete=models.DO_NOTHING)
    value = models.TextField()

class Page(models.Model):
    name = models.CharField(max_length=300)
    language = models.CharField(max_length=2)
    path = models.CharField()
    content_bb = models.TextField()
    content_html = models.TextField()
    user_created = models.ForeignKey(User, on_delete=DO_NOTHING)
    date_created = models.DateTimeField()

