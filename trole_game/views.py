import datetime

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from trole_game.misc.participation import Participation
from trole_game.misc.permissions import GamePermissions
from trole_game.models import Character, Game, UserGameParticipation, Episode, Post, Fandom, Rating, Genre, GameStatus, \
    UserGameDisplay, CharacterEpisodeNotification, Article


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

class UserGetByUsername(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        user = User.objects.get(username=username)
        data = {
            "id": user.id,
            "username": user.username,
            "avatar": "",
            "characters": []
        }
        characters = Character.objects.filter(user_id = user.id)
        for character in characters:
            data['characters'].append({
                "id": character.id,
                "name": character.name,
                "avatar": character.avatar,
                "is_mine": True
            })
        return Response({"data": data})

class GetGameById(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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
            "rating": game.rating.name,
            "description": game.description,
            "fandoms": game.fandoms.all().values('id', 'name'),
            "genres": game.genres.all().values('id', 'name')
        }
        return Response({"data": data})

class GetEpisodeById(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        episode = Episode.objects.get(pk=id)
        data = {
            "id": episode.id,
            "name": episode.name,
            "image": episode.image,
            "status": episode.status.name,
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
        return Response({"data": data})

class GetEpisodeList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, game_id):
        episodes = Episode.objects.filter(game_id=game_id).order_by('-last_post_date')
        data = []

        for episode in episodes:
            is_mine = False
            for character in episode.characters.all():
                if character.user.id == request.user.id:
                    is_mine = True
                    break
            if episode.category == None:
                category = ''
            else:
                category = episode.category.name

            if episode.last_post_author == None:
                last_post_author = None
            else:
                last_post_author = {
                    "id": episode.last_post_author.id,
                    "name": episode.last_post_author.name
                },
            data.append({
                "id": episode.id,
                "name": episode.name,
                "image": episode.image,
                "category": category,
                "status": episode.status.name,
                "last_post_date": episode.last_post_date,
                "last_post_autor": last_post_author,
                "description": episode.description,
                "is_mine": is_mine
            })
        return Response({"data": data})

class GetCharacterList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, episode_id):
        posts = Post.objects.filter(episode_id=episode_id).order_by('order')
        data = []

        for post in posts:
            data.append({
                "id": post.id,
                "is_read": True,
                "content": post.content,
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
    allowed_entities = ['Rating', 'Genre', 'GameStatus']
    static_names = ['GamePermissions', 'ParticipationStatus', 'ParticipationRole']

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

        return Response({"data": data})

class EpisodeCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print(request.data)

        episode = Episode.objects.create(
        name = request.data['name'],
        image = request.data['image'],
        description = request.data['description'],
        status_id = 1,
        category = None,
        rating_id = 3,
        game_id = request.data['game'],
        user_created_id = request.user.id,
        date_created = datetime.datetime.now(),
        number_of_posts = 0,
        last_post_date = None,
        last_post_author = None,
        in_category_order = None
        )

        for entity in request.data['characters']:
            episode.characters.add(entity['id'])
            if request.user.id != entity['id']:

                character = Character.objects.get(pk=entity['id'])
                character.participating_episodes += 1;
                character.save()

                CharacterEpisodeNotification.objects.create(
                    character_id = entity['id'],
                    episode_id = episode.id,
                    date_created = datetime.datetime.now(),
                    is_read = False,
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

        UserGameParticipation.create(
            user_id = request.user.id,
            game_id = request.data['game'],
            status = 2,
            role = 4
        )

        return Response({"data": 'success'})

class CharacterCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print(request.data)

        character = Character.objects.create(
            name=request.data['name'],
            game_id = request.data['game'],
            avatar = request.data['avatar'],
            description = request.data['description'],
            user_id = request.user.id,
            date_created = datetime.datetime.now(),
            posts_written = 0,
        )

        participation = UserGameParticipation.objects.filter(user_id=request.user.id, game_id=request.data['game'])
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
            image = request.data['image'],
            status_id = request.data['status'],
            description = request.data['description'],
            user_created_id = request.user.id,
            date_created = datetime.datetime.now(),
            total_posts= 0,
            total_episodes = 0,
            total_characters = 0,
            total_users = 1,
            permission_level = request.data['access_level'],
            was_online_in_24 = 1,
            rating_id = request.data['rating'],
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
            user_id = request.user.id,
            game_id = game.id,
            status = 1,
            role = 1
        )

        UserGameDisplay.objects.create(
            user_id = request.user.id,
            game_id = game.id,
            display_category = 1,
            is_on_main_page = True,
            order = None
        )

        return Response({"data": game.id})

class PostCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print(request.data)

        order = Post.objects.filter(episode_id=request.data['episode']).count() + 1
        post = Post.objects.create(
            content=request.data['content'],
            episode_id = request.data['episode'],
            order=order,
            post_author_id = request.data['character'],
            date_created = datetime.datetime.now(),
        )

        post.post_author.posts_written += 1
        post.post_author.last_post_date = post.date_created
        post.post_author.save()

        episode = Episode.objects.get(pk=request.data['episode'])
        episode.number_of_posts += 1
        episode.last_post_date = post.date_created
        episode.last_post_author = post.post_author
        episode.save()

        for character in episode.characters.exclude(user_id=request.user.id) :
            # if character.user.id != post.post_author.id:

            CharacterEpisodeNotification.objects.create(
                character_id = character.id,
                episode_id = episode.id,
                post_id = post.id,
                date_created = datetime.datetime.now(),
                is_read = False,
                notification_type=2
            )

        game = Game.objects.get(pk=episode.game.id)
        game.total_posts += 1
        game.last_post_published = post.date_created
        game.save()


        return Response({"data": post.id})

class GetArticleById(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, game_id, id):
        article = Article.objects.get(game_id=game_id, pk=id)
        data = {
            "id": article.id,
            "name": article.name,
            "content": article.content,
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, game_id):
        article = Article.objects.get(game_id=game_id, is_index=True)
        data = {
            "id": article.id,
            "name": article.name,
            "content": article.content,
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

class Breadcrumbs(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, path):
        breadcrumbs = []

        if path == 'game':
            game = Game.objects.get(pk=request.GET.get('0'))
            participates = UserGameParticipation.objects.filter(game_id=game.id, user_id=request.user.id).count()
            if participates:
                breadcrumbs = [
                    {"name": "My Games", "path": "/home"},
                    {"name": game.name, "path": "/game/" + str(game.id)},
                ]
            else:
                breadcrumbs = [
                    {"name": "Games", "path": "/games"},
                    {"name": game.name, "path": "/game/" + str(game.id)},
                ]

        if path == 'episode':
            episode = Episode.objects.get(pk=request.GET.get('0'))
            if episode.user_participates(request.user.id):
                breadcrumbs = [
                    {"name": "My Games", "path": "/home"},
                    {"name": episode.game.name, "path": "/game/"+str(episode.game.id)},
                    {"name": episode.name, "path": "/episode"+str(episode.id)}
                ]
            else:
                breadcrumbs = [
                    {"name": "Games", "path": "/games"},
                    {"name": episode.game.name, "path": "/game/" + str(episode.game.id)},
                    {"name": episode.name, "path": "/episode/" + str(episode.id)}
                ]

        if path == 'article':
            if len(request.GET) > 1:
                article = Article.objects.get(game_id=request.GET.get('0'), pk=request.GET.get('1'))
                index_article = Article.objects.get(game_id=int(request.GET.get('0')), is_index=True)
                article_breadcrumbs = [
                    {
                        "name": index_article.name,
                        "path": '/article/' + str(request.GET.get('0'))
                    },
                    {
                        "name": article.name,
                        "path": '/article/'+str(request.GET.get('0'))+'/'+str(request.GET.get('1'))
                    }
                ]

            else:
                index_article = Article.objects.get(game_id=int(request.GET.get('0')), is_index=True)
                article_breadcrumbs = [
                    {
                        "name": index_article.name,
                        "path": '/article/' + str(request.GET.get('0'))
                    }
                ]

            participates = UserGameParticipation.objects.filter(game_id=index_article.game.id, user_id=request.user.id).count()
            if participates:
                breadcrumbs = [
                    {"name": "My Games", "path": "/home"},
                    {"name": index_article.game.name, "path": "/game/"+str(index_article.game.id)},
                ]
            else:
                breadcrumbs = [
                    {"name": "Games", "path": "/games"},
                    {"name": index_article.game.name, "path": "/game/" + str(index_article.game.id)},
                ]
            breadcrumbs += article_breadcrumbs


        return Response({"data": breadcrumbs})

