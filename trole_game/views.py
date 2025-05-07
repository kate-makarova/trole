import datetime
import math

import django.utils.crypto
import pytz
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from trole.settings import DEFAULT_LANGUAGE
from trole_game.access_level import AccessLevelPermission
from trole_game.authentication import JWTOrGuestAuthentication
from trole_game.misc.rating import Rating
from trole_game.misc.status import GameStatus, EpisodeStatus
from trole_game.misc.participation import Participation
from trole_game.misc.permissions import GamePermissions
from trole_game.models import Character, Game, UserGameParticipation, Episode, Post, Genre, \
    UserGameDisplay, CharacterEpisodeNotification, Article, Fandom, CharacterSheetTemplate, \
    CharacterSheetTemplateField, CharacterSheetField, Page, UserSetting, Language, Draft, NewsArticle, Invitation
from trole_game.util.bb_translator import form_html, translate_bb
import operator
from django.db.models import CharField
from django.db.models.functions import Lower

from trole_game.util.mail_client import MailClient

CharField.register_lookup(Lower)
limit = 10

def index(request):
    return JsonResponse({
        'status': 'ok'
    })


class UserHome(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        data = []
        participations = UserGameParticipation.objects.filter(user_id=user_id).exclude(status=0)
        for participation in participations:
            game = {
                "id": participation.game.id,
                "name": participation.game.name,
                "rating": {
                    "id": participation.game.rating_id,
                    "name": Rating.get_ratings()[participation.game.rating_id]['name']
                },
                "description": participation.game.description,
                "image": participation.game.image,
                "total_episodes": participation.game.total_episodes,
                "total_posts": participation.game.total_posts,
                "total_characters": participation.game.total_characters,
                "total_users": participation.game.total_users,
                "my_characters": [],
                "fandoms": [],
                "genres": [],
            }

            for fandom in participation.game.fandoms.all():
                game["fandoms"].append({
                    "id": fandom.id,
                    "name": fandom.name
                })
            characters = Character.objects.filter(game_id=participation.game.id, user_id=user_id)
            for character in characters:
                new_episodes = 0
                unread_posts = 0

                notifications = CharacterEpisodeNotification.objects.filter(character_id=character.id, is_read=False)
                for notification in notifications:
                    if notification.notification_type == 1:
                        new_episodes += 1
                    if notification.notification_type == 2:
                        unread_posts += 1

                game['my_characters'].append({
                    "id": character.id,
                    "name": character.name,
                    "avatar": character.avatar,
                    "unread_posts": unread_posts,
                    "new_episodes": new_episodes,
                })
            data.append(game)
        return Response({
            'data': data
        })


class GameList(APIView):
    authentication_classes = [JWTOrGuestAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        if request.user.is_authenticated:
            games = Game.objects.filter(status_id=1).order_by('-last_post_published')[:10]
        else:
            games = Game.objects.filter(permission_level=0).order_by('-last_post_published')[:10]

        data = []

        for game in games:
            game_data = {
                "id": game.id,
                "name": game.name,
                "rating": {
                    "id": game.rating_id,
                   "name": Rating.get_ratings()[game.rating_id]['name']
                },
                "description": game.description,
                "image": game.image,
                "total_episodes": game.total_episodes,
                "total_posts": game.total_posts,
                "total_characters": game.total_characters,
                "total_users": game.total_users,
                "my_characters": [],
                "fandoms": [],
                "genres": [],
            }

            for fandom in game.fandoms.all():
                game_data["fandoms"].append({
                    "id": fandom.id,
                    "name": fandom.name
                })

            if request.user.is_authenticated:
                characters = Character.objects.filter(game_id=game.id, user_id=request.user.id)
                for character in characters:
                    new_episodes = 0
                    unread_posts = 0

                    notifications = CharacterEpisodeNotification.objects.filter(character_id=character.id, is_read=False)
                    for notification in notifications:
                        if notification.notification_type == 1:
                            new_episodes += 1
                        if notification.notification_type == 2:
                            unread_posts += 1

                    game_data['my_characters'].append({
                        "id": character.id,
                        "name": character.name,
                        "avatar": character.avatar,
                        "unread_posts": unread_posts,
                        "new_episodes": new_episodes,
                    })
            data.append(game_data)
        return Response({
            'data': data
        })


class UserGetByUsername(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        user = User.objects.get(username=username)
        settings = UserSetting.objects.filter(user_id=user.id)[0]
        data = {
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_staff,
            "avatar": "",
            "characters": [],
            "theme": settings.theme,
            "language": settings.ui_language
        }
        characters = Character.objects.filter(user_id=user.id)
        for character in characters:
            data['characters'].append({
                "id": character.id,
                "name": character.name,
                "avatar": character.avatar,
                "is_mine": True
            })
        return Response({"data": data})


class GetGameById(APIView):
    authentication_classes = [JWTOrGuestAuthentication]
    permission_classes = [AccessLevelPermission]

    def get(self, request, id):
        try:
            game = Game.objects.get(pk=id)
        except:
            return Response({"data": None}, 404)
        data = {
            "id": game.id,
            "status": {
                'id': game.status_id,
                'name': GameStatus.get_game_status()[game.status_id]
            },
            "access_level": {
                'id': game.permission_level,
                'name': GamePermissions.get_levels()[game.permission_level]
            },
            "name": game.name,
            "image": game.image,
            "total_characters": game.total_characters,
            "total_posts": game.total_posts,
            "total_users": game.total_users,
            "total_episodes": game.total_episodes,
            "rating": {
                "id": game.rating_id,
                "name": Rating.get_ratings()[game.rating_id]['name']
            },
            "description": game.description,
            "fandoms": game.fandoms.all().values('id', 'name'),
            "genres": game.genres.all().values('id', 'name'),
            "languages": game.languages.all().values('id', 'name'),
            "my_characters": [],
        }

        if game.user_created.id == request.user.id:
            data["can_admin"] = True
        else:
            data["can_admin"] = False

        participation = UserGameParticipation.objects.filter(
            game_id=game.id,
            user_id=request.user.id
        ).exclude(status=0)
        if len(participation):
            data["is_mine"] = True

            data['my_characters'] = Character.objects.filter(game_id=game.id, user_id=request.user.id).values("id",
                                                                                                              "name")
        else:
            data["is_mine"] = False

        return Response({"data": data})


class GetEpisodeById(APIView):
    authentication_classes = [JWTOrGuestAuthentication]
    permission_classes = [AccessLevelPermission]

    def get(self, request, id):
        try:
            episode = Episode.objects.get(pk=id)
        except:
            return Response({"data": None}, 404)
        participations = UserGameParticipation.objects.filter(user_id=request.user.id).exclude(status=0)
        data = {
            "id": episode.id,
            "game_id": episode.game.id,
            "name": episode.name,
            "image": episode.image,
            "status": EpisodeStatus.get_episode_status()[episode.status_id],
            "total_posts": episode.number_of_posts,
            "language": None,
            "description": episode.description,
            "characters": []
        }

        if episode.language is not None:
            data["language"] = {
                "id": episode.language.id,
                "name": episode.language.name
            }

        is_mine = False
        for character in episode.characters.all():
            data['characters'].append({
                "id": character.id,
                "name": character.name,
                "status": character.status,
                "avatar": character.avatar,
                "is_mine": (character.user.id == request.user.id)
            })
            if character.user.id == request.user.id and not character.status == 0:
                is_mine = True
        data["is_mine"] = is_mine

        can_edit = False
        if episode.user_created.id == request.user.id and len(participations):
            can_edit = True
        data["can_edit"] = can_edit

        notification = CharacterEpisodeNotification.objects.filter(
            episode_id=episode.id,
            user_id=request.user.id,
            notification_type=1,
            is_read=False
        )
        if len(notification):
            data["is_new"] = True
        else:
            data["is_new"] = False

        return Response({"data": data})


class GetEpisodeList(APIView):
    authentication_classes = [JWTOrGuestAuthentication]
    permission_classes = [AccessLevelPermission]

    def get(self, request, game_id):
        episodes = Episode.objects.filter(game_id=game_id).order_by('-last_post_date')
        data = []

        for episode in episodes:
            is_mine = False
            for character in episode.characters.all().exclude(status=0):
                if character.user.id == request.user.id:
                    is_mine = True
                    break
            if episode.category is None:
                category = ''
            else:
                category = episode.category.name

            if episode.last_post_author is None:
                last_post_author = None
            else:
                last_post_author = {
                    "id": episode.last_post_author.id,
                    "name": episode.last_post_author.name
                }

            data.append({
                "id": episode.id,
                "name": episode.name,
                "image": episode.image,
                "category": category,
                "status": EpisodeStatus.get_episode_status()[episode.status_id],
                "last_post_date": episode.last_post_date,
                "last_post_author": last_post_author,
                "description": episode.description,
                "characters": episode.characters.all().values('id', 'name', 'avatar'),
                "is_mine": is_mine
            })
        return Response({"data": data})


class GetCharacterList(APIView):
    authentication_classes = [JWTOrGuestAuthentication]
    permission_classes = [AccessLevelPermission]

    def get(self, request, game_id):
        characters = Character.objects.filter(game_id=game_id).order_by('name')
        data = []

        for character in characters:
            data.append({
                "id": character.id,
                "name": character.name,
                "status": character.status,
                "avatar": character.avatar,
                "user": {
                    "id": character.user.id,
                    "name": character.user.username
                },
                "is_mine": (character.user.id == request.user.id)
            })
        return Response({"data": data})


class GetPostsByEpisode(APIView):
    authentication_classes = [JWTOrGuestAuthentication]
    permission_classes = [AccessLevelPermission]

    def get(self, request, episode_id, page=1):
        if page == -1:
            episode = Episode.objects.get(pk=episode_id)
            page = math.ceil(episode.number_of_posts / limit)
        offset = (page-1)*limit
        posts = Post.objects.filter(episode_id=episode_id, is_deleted=False).order_by('order')[offset:offset+limit]
        data = []

        unread_post_ids = CharacterEpisodeNotification.objects.filter(
            episode_id=episode_id,
            user_id=request.user.id,
            is_read=False
        ).order_by('post_id').values_list('post_id', flat=True)

        for post in posts:
            if post.post_author.user.id == request.user.id:
                content_bb = post.content_bb
            else:
                content_bb = None
            data.append({
                "id": post.id,
                "is_read": post.id not in unread_post_ids,
                "content": post.content_html,
                "content_bb": content_bb,
                "post_date": post.date_created,
                "character": {
                    "id": post.post_author.id,
                    "name": post.post_author.name,
                    "avatar": post.post_author.avatar,
                    "status": post.post_author.status,
                    "is_mine": (post.post_author.user.id == request.user.id)
                },
                "is_mine": (post.post_author.user.id == request.user.id)
            })
        return Response({"data": data})


class Autocomplete(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    allowed_entities = ['Fandom', 'User']

    def get(self, request, class_name, search):
        data = []
        if class_name in self.allowed_entities:
            cls = globals()[class_name]
            results = getattr(cls, "objects").filter(name__lower__contains=search.lower()).order_by('name')[:10]

            for result in results:
                data.append({
                    "id": result.id,
                    "name": result.name
                })

        return Response({"data": data})


class CharacterAutocomplete(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, game_id, search):
        data = []
        results = Character.objects.filter(game_id=game_id, status=1, name__lower__contains=search.lower()).order_by('name')[:10]

        for result in results:
            data.append({
                "id": result.id,
                "name": result.name
            })

        return Response({"data": data})


class StaticList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    allowed_entities = ['Genre']
    static_names = ['GamePermissions',
                    'ParticipationStatus',
                    'ParticipationRole',
                    'GameStatus',
                    'Rating']

    def get(self, request, class_name):
        data = []
        if class_name in self.allowed_entities:
            cls = globals()[class_name]
            results = getattr(cls, "objects").all().order_by('name')[:10]

            for result in results:
                data.append({
                    "id": result.id,
                    "name": result.name
                })

        if class_name in self.static_names:
            if class_name == 'GamePermissions':
                for key, val in GamePermissions.get_levels().items():
                    data.append({
                        "id": key,
                        "name": val
                    })
            if class_name == 'ParticipationRole':
                for key, val in Participation.get_participation_role().items():
                    data.append({
                        "id": key,
                        "name": val
                    })
            if class_name == 'ParticipationStatus':
                for key, val in Participation.get_participation_status().items():
                    data.append({
                        "id": key,
                        "name": val
                    })

            if class_name == 'GameStatus':
                for key, val in GameStatus.get_game_status().items():
                    data.append({
                        "id": key,
                        "name": val
                    })

            if class_name == 'Rating':
                for key, val in Rating.get_ratings().items():
                    data.append({
                        "id": key,
                        "name": val['name']
                    })

        return Response({"data": data})


class EpisodeCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print(request.data)

        language = None
        if request.data['language']:
            language = int(request.data['language'])

        episode = Episode.objects.create(
            name=request.data['name'],
            image=request.data['image'],
            description=request.data['description'],
            status_id=1,
            rating_id=3,
            game_id=request.data['game'],
            user_created_id=request.user.id,
            date_created=datetime.datetime.now(),
            number_of_posts=0,
            language_id = language
        )

        for entity in request.data['characters']:
            episode.characters.add(entity['id'])

            character = Character.objects.get(pk=entity['id'])
            character.participating_episodes += 1
            character.save()

            if request.user.id != character.user.id:
                CharacterEpisodeNotification.objects.create(
                    user_id=character.user.id,
                    character_id=character.id,
                    episode_id=episode.id,
                    date_created=datetime.datetime.now(),
                    is_read=False,
                    notification_type=1
                )

        game = Game.objects.get(pk=request.data['game'])
        game.total_episodes += 1
        game.save()

        return Response({"data": episode.id})

class EpisodeUpdate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):

        print(request.data)

        language = None
        if request.data['language']:
            language = int(request.data['language'])

        episode = Episode.objects.get(pk=id)

        if episode.user_created.id != request.user.id:
            return Response({"data": "Access denied"})


        episode.name=request.data['name']
        episode.image=request.data['image']
        episode.description=request.data['description']
        episode.status_id=1
        episode.rating_id=3
        episode.language_id = language

        old_characters = list(episode.characters.all().values_list('id', flat=True))

        for entity in request.data['characters']:
            if entity == '':
                continue
            if entity['id'] in old_characters:
                old_characters.remove(entity['id'])
            else:
                episode.characters.add(entity['id'])
                character = Character.objects.get(pk=entity['id'])
                character.participating_episodes += 1
                character.save()

                if request.user.id != character.user.id:
                    CharacterEpisodeNotification.objects.create(
                        user_id=character.user.id,
                        character_id=character.id,
                        episode_id=episode.id,
                        date_created=datetime.datetime.now(),
                        is_read=False,
                        notification_type=1
                    )

        for removed_character in old_characters:
            character = Character.objects.get(pk=removed_character)
            episode.characters.remove(character)
            character.participating_episodes -= 1
            character.save()

            if request.user.id != character.user.id:
                CharacterEpisodeNotification.objects.create(
                    user_id=character.user.id,
                    character_id=character.id,
                    episode_id=episode.id,
                    date_created=datetime.datetime.now(),
                    is_read=False,
                    notification_type=0
                )

        episode.save()

        return Response({"data": episode.id})


class GameJoin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)

        game = Game.objects.get(pk=request.data['game'])
        game.total_users += 1
        game.save()

        UserGameParticipation.objects.create(
            user_id=request.user.id,
            game_id=request.data['game'],
            status=2,
            role=4
        )

        return Response({"data": 'success'})

class GameLeave(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)

        participation = UserGameParticipation.objects.filter(
            user_id=request.user.id,
            game_id=request.data['game']
        )

        if not len(participation):
            return Response({"data": 'error'})

        participation = participation[0]
        participation.status = 0
        participation.save()

        characters = Character.objects.filter(
            user_id=request.user.id,
            game_id=request.data['game']
        )
        for character in characters:
            character.status = 0
            character.save()

        game = Game.objects.get(pk=request.data['game'])
        game.total_users -= 1
        game.total_characters -= len(characters)

        if game.total_users == 0:
            game.status_id = 2

        game.save()

        return Response({"data": 'success'})


class CharacterCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print(request.data)
        characterSheetTemplate = CharacterSheetTemplate.objects.filter(game_id=request.data['game'])[0]

        character = Character.objects.create(
            name=request.data['name'],
            status=1,
            game_id=request.data['game'],
            avatar=request.data['avatar'],
            description=request.data['description'],
            character_sheet_template=characterSheetTemplate,
            user_id=request.user.id,
            date_created=datetime.datetime.now(),
            participating_episodes=0,
            posts_written=0,
        )

        for key, value in request.data.items():
            if key not in ['name', 'game', 'avatar', 'description']:
                CharacterSheetField.objects.create(
                    character=character,
                    character_sheet_template_field_id=key,
                    value=value
                )

        participations = UserGameParticipation.objects.filter(user_id=request.user.id, game_id=request.data['game']).exclude(status=0)
        if len(participations):
            participation = participations[0]
            if participation.status == 2:
                participation.status = 1
                participation.save()

        game = Game.objects.get(pk=request.data['game'])
        game.total_characters += 1
        game.save()

        return Response({"data": character.id})


class GameCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print(request.data)

        game = Game.objects.create(
            name=request.data['name'],
            image=request.data['image'],
            status_id=request.data['status'],
            description=request.data['description'],
            user_created_id=request.user.id,
            date_created=datetime.datetime.now(),
            total_posts=0,
            total_episodes=0,
            total_characters=0,
            total_users=1,
            total_articles=1,
            permission_level=request.data['access_level'],
            was_online_in_24=1,
            rating_id=request.data['rating'],
        )
        is_original = False
        fandom_ids = []

        for language_id in request.data['languages']:
            game.languages.add(language_id)

        for entity in request.data['fandoms']:
            if entity['id'] == 1:
                is_original = True
            fandom_ids.append(entity['id'])
            game.fandoms.add(entity['id'])

        if is_original:
            for genre in request.data['genres']:
                game.fandoms.add(genre)

        genres = Genre.objects.filter(id__in=fandom_ids)
        for genre in genres:
            game.genres.add(genre)

        UserGameParticipation.objects.create(
            user_id=request.user.id,
            game_id=game.id,
            status=1,
            role=1
        )

        UserGameDisplay.objects.create(
            user_id=request.user.id,
            game_id=game.id,
            display_category=1,
            is_on_main_page=True,
            order=None
        )

        Article.objects.create(
            name=game.name + ' - Index',
            content_bb='Write your articles',
            content_html='<p>Write your articles</p>',
            game_id=game.id,
            user_created_id=request.user.id,
            date_created=datetime.datetime.now(),
            is_index=True
        )

        CharacterSheetTemplate.objects.create(
            game=game,
            name_field_name=None,
            avatar_field_name=None,
            description_field_name=None,
            name_description=None,
            avatar_description=None,
            description_description=None,
            name_order=1,
            avatar_order=2,
            description_order=3,
            is_active=True
        )

        return Response({"data": game.id})

class GameUpdate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):

        print(request.data)

        game = Game.objects.get(pk=id)

        game.name=request.data['name']
        game.image=request.data['image']
        game.status_id=request.data['status']
        game.description=request.data['description']
        game.permission_level=request.data['access_level']
        game.rating_id=request.data['rating']

        old_languages = list(game.languages.all().values_list('id', flat=True))

        for lang_id in request.data['languages']:
            if id == '':
                continue
            lang_id = int(lang_id)
            if id in old_languages:
                old_languages.remove(lang_id)
            else:
                game.languages.add(lang_id)

        for removed_language in old_languages:
            language = Language.objects.get(pk=removed_language)
            game.languages.remove(language)

        is_original = False
        fandom_ids = []

        old_fandoms = list(game.fandoms.all().values_list('id', flat=True))

        for entity in request.data['fandoms']:
            if entity == '' or entity['id'] == 0:
                continue
            if entity['id'] == 1:
                is_original = True
            if entity['id'] in old_fandoms:
                old_fandoms.remove(entity['id'])
            else:
                game.fandoms.add(entity['id'])

        for removed_fandom in old_fandoms:
            fandom = Fandom.objects.get(pk=removed_fandom)
            game.fandoms.remove(fandom)

        if not is_original:
            game.genres.clear()

        if is_original:
            old_genres = list(game.genres.all().values_list('id', flat=True))

            for genre_id in request.data['genres']:
                if genre_id == '':
                    continue
                if genre_id in old_genres:
                    old_genres.remove(genre_id)
                else:
                    game.genres.add(genre_id)

            for removed_genre in old_genres:
                genre = Genre.objects.get(pk=removed_genre)
                game.genre.remove(genre)

        genres = Genre.objects.filter(id__in=fandom_ids)
        for genre in genres:
            if not len(game.genres.filter(pk=genre.id)):
                game.genres.add(genre)

        game.save()

        return Response({"data": game.id})

class PostCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)

        order = Post.objects.filter(episode_id=request.data['episode']).count() + 1
        post = Post.objects.create(
            content_bb=request.data['content'],
            content_html=form_html(request.data['content']),
            episode_id=request.data['episode'],
            order=order,
            post_author_id=request.data['character'],
            date_created=datetime.datetime.now(),
        )

        post.post_author.posts_written += 1
        post.post_author.last_post_date = post.date_created
        post.post_author.save()

        episode = Episode.objects.get(pk=request.data['episode'])
        episode.number_of_posts += 1
        episode.last_post_date = post.date_created
        episode.last_post_author = post.post_author
        episode.save()

        for character in episode.characters.exclude(user_id=request.user.id):
            CharacterEpisodeNotification.objects.create(
                user_id=character.user.id,
                character_id=character.id,
                episode_id=episode.id,
                post_id=post.id,
                date_created=datetime.datetime.now(),
                is_read=False,
                notification_type=2
            )

        game = Game.objects.get(pk=episode.game.id)
        game.total_posts += 1
        game.last_post_published = post.date_created
        game.save()

        return Response({"data": post.id})


class GetArticleById(APIView):
    authentication_classes = [JWTOrGuestAuthentication]
    permission_classes = [AccessLevelPermission]

    def get(self, request, game_id, id):
        article = Article.objects.get(game_id=game_id, pk=id)
        data = {
            "id": article.id,
            "name": article.name,
            "content": article.content_html,
            "content_bb": article.content_bb,
            "game": {
                "id": article.game_id,
                "name": article.game.name
            },
            "author": {
                "id": article.user_created.id,
                "name": article.user_created.username
            },
            "date_created": article.date_created,
        }
        return Response({"data": data})


class GetIndexArticle(APIView):
    authentication_classes = [JWTOrGuestAuthentication]
    permission_classes = [AccessLevelPermission]

    def get(self, request, game_id):
        article = Article.objects.get(game_id=game_id, is_index=True)
        data = {
            "id": article.id,
            "name": article.name,
            "content": article.content_html,
            "content_bb": article.content_bb,
            "game": {
                "id": article.game_id,
                "name": article.game.name
            },
            "author": {
                "id": article.user_created.id,
                "name": article.user_created.username
            },
            "date_created": article.date_created,
        }
        return Response({"data": data})


class SetPostsRead(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, episode_id):
        notifications = CharacterEpisodeNotification.objects.filter(
            episode_id=episode_id,
            notification_type__in=[1, 2],
            user_id=request.user.id,
            is_read=False
        )
        for notification in notifications:
            notification.is_read = True
            notification.date_read = datetime.datetime.now()
            notification.save()

        return Response({"data": "ok"})


class ArticleCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)

        article = Article.objects.create(
            name=request.data['name'],
            game_id=request.data['game'],
            user_created_id=request.user.id,
            date_created=datetime.datetime.now(),
            content_bb=request.data['content'],
            content_html=form_html(request.data['content']),
            is_index=False
        )

        game = Game.objects.get(pk=request.data['game'])
        game.total_articles += 1
        game.save()

        return Response({"data": article.id})


class ArticleUpdate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):

        article = Article.objects.get(pk=id)
        if article.user_created_id != request.user.id:
            return Response({"data": "You are not the author of this article"})
        else:
            article.name = request.data['name']
            article.content_bb = request.data['content']
            article.content_html = form_html(request.data['content'])
            article.save()

        return Response({"data": article})

class PostUpdate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):

        post = Post.objects.get(pk=id)
        if post.post_author.user.id != request.user.id:
            return Response({"data": "You are not the author of this post"})
        else:
            post.content_bb = request.data['content']
            post.content_html = form_html(request.data['content'])
            post.save()

        return Response({"data": {
            "id": post.id,
            "content": post.content_html,
            "content_bb": post.content_bb
        }})

class PostDelete(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):

        post = Post.objects.get(pk=id)
        if post.post_author.user.id != request.user.id:
            return Response({"data": "You are not the author of this post"})
        else:
            post.is_deleted = True
            post.save()

            episode = post.episode
            episode.number_of_posts -= 1
            episode.save()

            game = episode.game
            game.total_posts -= 1
            game.save()

            character = post.post_author
            character.posts_written -= 1
            character.save()


        return Response({"data": {
            "id": post.id,
            "is_deleted": True
        }})

class CharacterSheetTemplateGet(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, game_id):
        character_sheet = CharacterSheetTemplate.objects.get(game_id=game_id)

        field_data = [
            {
                "id": "name",
                "type": 1,
                "field_name": "Character Name",
                "description": "Character name",
                "is_required": True,
                "order": character_sheet.name_order,
                "is_active":character_sheet.is_active
            },
            {
                "id": "avatar",
                "type": 1,
                "field_name": "Character Avatar",
                "description": "Character avatar",
                "is_required": True,
                "order": character_sheet.avatar_order,
                "is_active": character_sheet.is_active
            },
            {
                "id": "description",
                "type": 2,
                "field_name": "Character Description",
                "description": "Character description",
                "is_required": True,
                "order": character_sheet.description_order,
                "is_active": character_sheet.is_active
            }
        ]
        fields = CharacterSheetTemplateField.objects.filter(
            character_sheet_template=character_sheet.id
        )
        for field in fields:
            field_data.append({
                "id": field.id,
                "type": field.type,
                "field_name": field.field_name,
                "description": field.description,
                "is_required": field.is_required,
                "order": field.order,
                "is_active": field.is_active
            })

        print(field_data)
        field_data = sorted(field_data, key=operator.itemgetter('order'))

        return Response({
            "data": {
                "id": character_sheet.id,
                "game_id": character_sheet.game_id,
                "fields": field_data
            }
        })

class CharacterSheetTemplateUpdate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        template = CharacterSheetTemplate.objects.get(pk=id)
        if template.game.user_created.id != request.user.id:
            return Response({"data": "You are not the admin of this game"})

        new_field_data = {}
        old_field_data = {}

        for key, value in request.data.items():
            key_parts = key.split('-')

            if len(key_parts) == 2 and key_parts[1] in ['name', 'description', 'avatar']:
                setattr(template, key_parts[1]+'-'+key_parts[0], value)

            if len(key_parts) == 3:
                if key_parts[2] not in new_field_data:
                    new_field_data[key_parts[2]] = {}
                new_field_data[key_parts[2]][key_parts[0]] = value

            if len(key_parts) == 2 and key_parts[1] not in ['name', 'description', 'avatar']:
                if key_parts[1] not in old_field_data:
                    old_field_data[key_parts[1]] = {}
                old_field_data[key_parts[1]][key_parts[0]] = value

        for key, data in old_field_data.items():
            field = CharacterSheetTemplateField.objects.get(pk=int(key))
            for field_name, field_value in data.items():
                setattr(field, field_name, field_value)
            field.save()

        for key, data in new_field_data.items():
            new_field = CharacterSheetTemplateField()
            new_field.character_sheet_template = template
            new_field.is_required = False
            for field_name, field_value in data.items():
                setattr(new_field, field_name, field_value)
            new_field.save()

        template.save()

        return Response({"data": template.id})

class GetNewsArticleById(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, id):
        article = NewsArticle.objects.get(pk=id)
        data = {
            "id": article.id,
            "name": article.name,
            "image": article.image,
            "content": article.content_html,
            "content_bb": article.content_bb,
            "author": {
                "id": article.user_created.id,
                "name": article.user_created.username
            },
            "date_created": article.date_created,
        }
        return Response({"data": data})

class GetNewsArticleList(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, offset=0, limit=10):
        articles = NewsArticle.objects.order_by('-date_created').all()[offset:offset+limit]
        data = []
        for article in articles:
            data.append({
                "id": article.id,
                "name": article.name,
                "image": article.image,
                "content": article.content_html,
                "content_bb": article.content_bb,
                "author": {
                    "id": article.user_created.id,
                    "name": article.user_created.username
                },
                "date_created": article.date_created,
            })
        return Response({"data": data})

class GetPageByPath(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, path):
        try:
            user_setting = UserSetting.objects.filter(user_id=request.user.id)[:1][0]
            language = user_setting.language
        except:
            language = 'en'

        articles = Page.objects.filter(path=path)
        filtered = [article for article in articles if article.language == language]
        if len(filtered) == 0:
            filtered = [article for article in articles if article.language == DEFAULT_LANGUAGE]
        article = filtered[0]

        data = {
            "id": article.id,
            "name": article.name,
            "content": article.content_html,
            "language": article.language,
            "content_bb": article.content_bb,
            "author": {
                "id": article.user_created.id,
                "name": article.user_created.username
            },
            "date_created": article.date_created,
        }
        return Response({"data": data})

class GetCharacter(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        character = Character.objects.get(pk=id)
        data = {
            "id": character.id,
            "name": character.name,
            "status": character.status,
            "avatar": character.avatar,
            "user": {
                "id": character.user.id,
                "name": character.user.username
            }
        }
        return Response({"data": data})

class UpdateCharacter(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        character = Character.objects.get(pk=id)
        print(request.data)
        if character.user.id == request.user.id or character.game.user_created.id == request.user.id:
            for key, value in request.data.items():
                if key.isnumeric():
                    try:
                        field = CharacterSheetField.objects.get(character=character, character_sheet_template_field_id=key)
                        field.value = value
                        field.save()
                    except:
                        CharacterSheetField.objects.create(
                            character=character,
                            character_sheet_template_field_id=key,
                            value=value
                        )
                    continue
                if key == 'game':
                    continue
                if key == 'status':
                    game = Game.objects.get(pk=character.game.id)
                    if int(value) == 1 and character.status != 1:
                        game.total_characters += 1
                        game.save()

                    if int(value) != 1 and character.status == 1:
                        game.total_characters -= 1
                        game.save()
                    continue
                setattr(character, key, value)
            character.save()

            return Response({"data": True})

        return Response({"data": False})


class GetCharacterSheetById(APIView):
    authentication_classes = [JWTOrGuestAuthentication]
    permission_classes = [AccessLevelPermission]

    def get(self, request, character_id):
        character = Character.objects.get(pk=character_id)
      #  template = CharacterSheetTemplate.objects.get(pk=character.character_sheet_template.id)
        fields = []
        fields.append({
            "id": "name",
            "field_name": "name",
            "value": character.name
        })
        fields.append({
            "id": "avatar",
            "field_name": "avatar",
            "value": character.avatar
        })
        fields.append({
            "id": "description",
            "field_name": "description",
            "value": character.description
        })
        additional_fields = CharacterSheetField.objects.filter(character_id=character.id)
        for additional_field in additional_fields:
            template = CharacterSheetTemplateField.objects.get(pk=additional_field.character_sheet_template_field_id)
            fields.append({
                "id": template.id,
                "field_name": template.field_name,
                "value": additional_field.value
            })

        data = {
            "character_id": character.id,
            "game_id": character.game.id,
            "can_moderate": character.game.user_created.id == request.user.id,
            "can_edit": character.user.id == request.user.id,
            "fields": fields,
            "user": {
                "id": character.user.id,
                "name": character.user.username
            }
        }

        return Response({"data": data})

class GetLanguageList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        languages = Language.objects.all()
        data = []
        for language in languages:
            data.append({
                "id": language.id,
                "name": language.name
            })
        return Response({"data": data})

class GetGameLanguageList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, game_id):
        game = Game.objects.get(pk=game_id)
        languages = game.languages.all()
        data = []
        for language in languages:
            data.append({
                "id": language.id,
                "name": language.name
            })
        return Response({"data": data})

class UpdateUserSettings(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        settings = UserSetting.objects.filter(user_id=user_id)[0]
        settings.theme = request.data['theme']
        settings.save()

        return Response({"data": True})

class DraftCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        draft = Draft.objects.create(
            episode_id=request.data['episode'],
            character_id =request.data['character'],
            user_id=request.user.id,
            date_draft_initiated=request.data['initiated'],
            autosave=request.data['autosave'],
            date_draft_created=datetime.datetime.now(),
            content_bb=request.data['content'],
            content_html=form_html(request.data['content']),
            published=False,
            publisher_post_id=None
        )

        if request.data['autosave']:
            stale = Draft.objects.filter(
                episode_id=request.data['episode'],
                character_id =request.data['character'],
                autosave=True).order_by('-date_draft_created').all()[5:]
            for stale_draft in stale:
                stale_draft.delete()

        return Response({"data": True})

class DraftList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, episode_id, page=-1):
        if page == -1:
            total = Draft.objects.filter(episode_id=episode_id, user_id =request.user.id).count()
            if total == 0:
                return Response({"data": []})
            page = math.ceil(total / limit)
            print(page)
        offset = (page-1)*limit
        drafts = Draft.objects.filter(
            episode_id=episode_id,
            user_id =request.user.id).order_by('-date_draft_created').all()[offset:offset+limit]

        data = []
        for draft in drafts:
            data.append({
                "id": draft.id,
                "character": {
                    "id": draft.character.id,
                    "name": draft.character.name
                },
                "init_date_time": draft.date_draft_initiated,
                "date_time": draft.date_draft_created,
                "auto": draft.autosave,
                "published": draft.published,
                "published_post_id": draft.publisher_post_id
            })

        return Response({"data": data})

class DraftGet(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        draft = Draft.objects.get(pk=id)
        data = {
            "id": draft.id,
            "character": draft.character.name,
            "date_time": draft.date_draft_initiated,
            "auto": draft.autosave,
            "published": draft.published,
            "published_post_id": draft.publisher_post_id,
            "content_bb": draft.content_bb,
            "content": draft.content_html
        }

        return Response({"data": data})

class InvitationSend(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender = request.user
        receiver_email = request.data['receiver_email']
        mail_client = MailClient()
        with open('./trole_game/emails/invitation.html', 'r') as file:
            body_html = file.read()
        with open('./trole_game/emails/invitation.txt', 'r') as file:
            body_text = file.read()

        send_date = datetime.datetime.now()
        expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)
        key = django.utils.crypto.get_random_string(100)

        Invitation.objects.create(
            key=key,
            sender = sender,
            receiver_email = receiver_email,
            send_date = send_date,
            expiration_date = expiration_date
        )

        replacements = {
            "{{username}}": sender.username,
            "{{expiration_date}}": expiration_date.isoformat(),
            "{{url}}": 'https://trole.online/invitation/' + key
        }

        for placeholder_name in replacements:
            body_html = body_html.replace(placeholder_name, replacements[placeholder_name])

        for placeholder_name in replacements:
            body_text = body_text.replace(placeholder_name, replacements[placeholder_name])

        result = mail_client.send(
            'You Are Invited to Trole Online',
            body_text,
            body_html,
            receiver_email
            )

        return Response({"data": "sent"})

class InvitationGet(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, key):
        invitation = Invitation.objects.get(key=key)
        if invitation is None:
            return None
        else:
            data = {
                "key": invitation.key,
                "receiverEmail": invitation.receiver_email,
                "sender": {
                    "id": invitation.sender.id,
                    "name": invitation.sender.username,
                },
                "expirationDate": invitation.expiration_date.isoformat(),
                "accepted": invitation.accepted
            }
            return Response({"data": data})

class Register(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        invitation = Invitation.objects.filter(key=request.data['invitation_key'])
        utc = pytz.UTC

        if len(invitation) == 0:
            return Response({"data": {
                "status": "error",
                "error": "Invitation not found"
            }})

        invitation = invitation[0]

        if invitation.accepted:
            return Response({"data": {
                "status": "error",
                "error": "Invitation already accepted"
            }})

        if invitation.expiration_date < utc.localize(datetime.datetime.now()):
            return Response({"data": {
                "status": "error",
                "error": "Invitation expired"
            }})

        existing_user = User.objects.filter(email=request.data['email'])
        if len(existing_user):
            return Response({"data": {
                "status": "error",
                "error": "Email already exists"
            }})

        user = User.objects.create_user(
            request.data['username'],
            request.data['email'],
            request.data['password']
        )

        invitation.accepted = True
        invitation.receiver = user
        invitation.save()

        refresh = RefreshToken.for_user(user)

        return Response({"data": {
            "status": "success",
            "user": {
                "id": user.id,
                "username": user.username,
            },
            "token": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }})