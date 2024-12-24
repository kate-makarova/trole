from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse

from trole_game.models import Character, Game, UserGameParticipation


def index(request):
    return JsonResponse({
        'status': 'ok'
    })

def user_home(request):
    user_id = 1
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
    return JsonResponse({
        'data': data
    })


