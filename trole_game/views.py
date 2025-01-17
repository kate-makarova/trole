import datetime
from importlib.resources import contents

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from trole_game.access_level import AccessLevelPermission
from trole_game.authentication import JWTOrGuestAuthentication
from trole_game.misc.rating import Rating
from trole_game.misc.status import GameStatus, EpisodeStatus
from trole_game.misc.participation import Participation
from trole_game.misc.permissions import GamePermissions
from trole_game.models import Character, Game, UserGameParticipation, Episode, Post, Genre, \
    UserGameDisplay, CharacterEpisodeNotification, Article, Fandom, MediaType, CharacterSheetTemplate, \
    CharacterSheetTemplateField, CharacterSheetField, Page
from trole_game.util.bb_translator import translate_bb
import operator


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
        participations = UserGameParticipation.objects.filter(user_id=user_id)
        for participation in participations:
            game = {
                "id": participation.game.id,
                "name": participation.game.name,
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
            games = Game.objects.all().order_by('-last_post_published')[:10]
        else:
            games = Game.objects.filter(permission_level=0).order_by('-last_post_published')[:10]

        data = []

        for game in games:
            game_data = {
                "id": game.id,
                "name": game.name,
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
        data = {
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_staff,
            "avatar": "",
            "characters": []
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
        game = Game.objects.get(pk=id)
        data = {
            "id": game.id,
            "name": game.name,
            "image": game.image,
            "total_characters": game.total_characters,
            "total_posts": game.total_posts,
            "total_users": game.total_users,
            "total_episodes": game.total_episodes,
            "rating": Rating.get_ratings()[game.rating_id]['name'],
            "description": game.description,
            "fandoms": game.fandoms.all().values('id', 'name'),
            "genres": game.genres.all().values('id', 'name'),
            "my_characters": [],
        }

        if game.user_created.id == request.user.id:
            data["can_admin"] = True
        else:
            data["can_admin"] = False

        participation = UserGameParticipation.objects.filter(game_id=game.id, user_id=request.user.id)
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
        episode = Episode.objects.get(pk=id)
        data = {
            "id": episode.id,
            "name": episode.name,
            "image": episode.image,
            "status": EpisodeStatus.get_episode_status()[episode.status_id],
            "total_posts": episode.number_of_posts,
            "description": episode.description,
            "characters": []
        }
        is_mine = False
        for character in episode.characters.all():
            data['characters'].append({
                "id": character.id,
                "name": character.name,
                "avatar": character.avatar,
                "is_mine": (character.user.id == request.user.id)
            })
            if character.user.id == request.user.id:
                is_mine = True
        data["is_mine"] = is_mine

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
            for character in episode.characters.all():
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

    def get(self, request, episode_id):
        posts = Post.objects.filter(episode_id=episode_id).order_by('order')
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
                    "is_mine": (post.post_author.user.id == request.user.id)
                },
                "is_mine": (post.post_author.user.id == request.user.id)
            })
        return Response({"data": data})


class Autocomplete(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    allowed_entities = ['Fandom']

    def get(self, request, class_name, search):
        data = []
        if class_name in self.allowed_entities:
            cls = globals()[class_name]
            results = getattr(cls, "objects").filter(name__contains=search).order_by('name')[:10]

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
        results = Character.objects.filter(game_id=game_id, name__contains=search).order_by('name')[:10]

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

        episode = Episode.objects.create(
            name=request.data['name'],
            image=request.data['image'],
            description=request.data['description'],
            status_id=1,
            category=None,
            rating_id=3,
            game_id=request.data['game'],
            user_created_id=request.user.id,
            date_created=datetime.datetime.now(),
            number_of_posts=0,
            last_post_date=None,
            last_post_author=None,
            in_category_order=None
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


class GameJoin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)

        UserGameParticipation.objects.create(
            user_id=request.user.id,
            game_id=request.data['game'],
            status=2,
            role=4
        )

        return Response({"data": 'success'})


class CharacterCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print(request.data)

        character = Character.objects.create(
            name=request.data['name'],
            game_id=request.data['game'],
            avatar=request.data['avatar'],
            description=request.data['description'],
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

        participations = UserGameParticipation.objects.filter(user_id=request.user.id, game_id=request.data['game'])
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

        CharacterSheetTemplate.create(
            game=game
        )

        return Response({"data": game.id})


class PostCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)

        order = Post.objects.filter(episode_id=request.data['episode']).count() + 1
        post = Post.objects.create(
            content_bb=request.data['content'],
            content_html=translate_bb(request.data['content']),
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
            content_html=translate_bb(request.data['content']),
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
            article.content_html = translate_bb(request.data['content'])
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
            post.content_html = translate_bb(request.data['content'])
            post.save()

        return Response({"data": {
            "id": post.id,
            "content": post.content_html,
            "content_bb": post.content_bb
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
                "order": character_sheet.name_order,
                "is_active": character_sheet.is_active
            },
            {
                "id": "description",
                "type": 2,
                "field_name": "Character Description",
                "description": "Character description",
                "is_required": True,
                "order": character_sheet.name_order,
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

        field_data = sorted(field_data, key=operator.itemgetter('order'))

        return Response({
            "data": {
                "id": character_sheet.id,
                "game_id": character_sheet.game_id,
                "fields": field_data
            }
        })

class GetNewsArticleById(APIView):
    authentication_classes = []
    permission_classes = []

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

class GetPageByPath(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, path):
        article = Page.objects.get(path=path)
        data = {
            "id": article.id,
            "name": article.name,
            "content": article.content_html,
            "content_bb": article.content_bb,
            "author": {
                "id": article.user_created.id,
                "name": article.user_created.username
            },
            "date_created": article.date_created,
        }
        return Response({"data": data})