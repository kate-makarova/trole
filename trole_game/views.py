from django.http import HttpResponse
import datetime
from django.shortcuts import render


def game_episode(request, id):
    now = datetime.datetime.now()
    html = '<html lang="en"><body>It is now %s.</body></html>' % now
    return render(request, "polls/detail.html", {"poll": p})