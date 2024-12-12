from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
import datetime
from django.shortcuts import render

from trole_game.models import Character, Game


def game_episode(request, id):
    now = datetime.datetime.now()
    html = '<html lang="en"><body>It is now %s.</body></html>' % now
    return render(request, "polls/detail.html", {"poll": p})

@login_required
def user_main(request, user_id):
    user = User.objects.get(pk=user_id)
    characters = Character.objects.get(user_id=user_id)
    games = Game.objects.filter(game__is_on_main_page=True)
    data = {
        user: {
            'name': user.username
        },
        characters: characters,
        games: games
    }


