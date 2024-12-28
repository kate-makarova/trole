import datetime

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from trole_game.misc.participation import Participation
from trole_game.misc.permissions import GamePermissions
from trole_game.models import Character, Game, UserGameParticipation, Episode, Post, Fandom, Rating, Genre


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
                "my_characters": [],
                "fandoms": [],
                "genres": []
            }
            for fandom in participation.game.fandoms.all():
                game["fandoms"].append({
                    "id": fandom.id,
                    "name": fandom.name
                })
            characters = Character.objects.filter(game_id=participation.game.id, user_id=user_id)
            for character in characters:
                game['my_characters'].append({
                    "id": character.id,
                    "name": character.name,
                    "avatar": character.avatar
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
            "description": game.description
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
    allowed_entities = [Character, Fandom]

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

class StaticList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    allowed_entities = [Rating, Genre]
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

        return Response({"data": episode.id})

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
        )

        return Response({"data": character.id})

class GameCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print(request.data)

        game = Game.objects.create(
            name=request.data['name'],
            image = request.data['avatar'],
            status = 1,
            description = request.data['description'],
            user_created_id = request.user.id,
            date_created = datetime.datetime.now(),
            total_posts= 0,
            total_episodes = 0,
            total_characters = 0,
            total_users = 1,
            permission_level = 1,
            was_online_in_24 = 1,
            rating_id = 3,
        )
        for entity in request.data['fandoms']:
            game.fandoms.add(entity['id'])

        UserGameParticipation.objects.create(
            user_id = request.user.id,
            game_id = game.id,
            status = 1,
            role = 1
        )

        return Response({"data": game.id})

class PostCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        print(request.data)

        post = Post.objects.create(
            content=request.data['name'],
            episode_id = request.data['episode'],
            order=request.data['order'],
            post_author_id = request.user.id,
            date_created = datetime.datetime.now(),
        )

        return Response({"data": post.id})

