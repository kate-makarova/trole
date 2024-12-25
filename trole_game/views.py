from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from trole_game.models import Character, Game, UserGameParticipation, Episode, Post


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

