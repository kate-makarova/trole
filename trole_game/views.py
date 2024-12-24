from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse

from trole_game.models import Character, Game


def home(request):
    return JsonResponse({
        'status': 'ok'
    })

@login_required
def user_main(request, user_id):
    return JsonResponse({
        'status': 'ok'
    })


