from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from trole_game.access_level import AccessLevelPermission
from trole_game.models import UserGameParticipation, Game, Episode, Article, Character


class Breadcrumbs(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, path):
        breadcrumbs = []

        if path == 'game':
            game = Game.objects.get(pk=request.GET.get('0'))
            breadcrumbs = [
                get_game_link(game.id, request.user.id),
                {"name": game.name, "path": "/game/" + str(game.id)},
            ]

        if path == 'character-list':
            game = Game.objects.get(pk=request.GET.get('0'))
            breadcrumbs = [
                get_game_link(game.id, request.user.id),
                {"name": game.name, "path": "/game/" + str(game.id)},
                {"name": "Character List", "path": "/character-list/" + str(game.id)}
            ]

        if path == 'episode-create':
            game = Game.objects.get(pk=request.GET.get('0'))
            breadcrumbs = [
                get_game_link(game.id, request.user.id),
                {"name": game.name, "path": "/game/" + str(game.id)},
                {"name": "Create Episode", "path": "/episode-create/" + str(game.id)}
            ]

        if path == 'episode-edit':
            episode = Episode.objects.get(pk=request.GET.get('0'))
            game = Game.objects.get(pk=episode.game_id)
            breadcrumbs = [
                get_game_link(game.id, request.user.id),
                {"name": game.name, "path": "/game/" + str(game.id)},
                {"name": episode.name, "path": "/episode/" + str(episode.id)},
                {"name": "Edit Episode", "path": "/episode-edit/" + str(episode.id)}
            ]

        if path == 'character-create':
            game = Game.objects.get(pk=request.GET.get('0'))
            breadcrumbs = [
                get_game_link(game.id, request.user.id),
                {"name": game.name, "path": "/game/" + str(game.id)},
                {"name": "Create Character", "path": "/character-create/" + str(game.id)}
            ]

        if path == 'character':
            character = Character.objects.get(pk=request.GET.get('0'))
            game = Game.objects.get(pk=character.game_id)
            breadcrumbs = [
                get_game_link(game.id, request.user.id),
                {"name": game.name, "path": "/game/" + str(game.id)},
                {"name": "Character List", "path": "/character-list/" + str(game.id)},
                {"name": character.name, "path": "/character/" + str(character.id)}
            ]

        if path == 'article-create':
            game = Game.objects.get(pk=request.GET.get('0'))
            article = Article.objects.get(game_id=request.GET.get('0'), pk=request.GET.get('1'))
            index_article = Article.objects.get(game_id=int(request.GET.get('0')), is_index=True)

            breadcrumbs = [
                get_game_link(game.id, request.user.id),
                {"name": game.name, "path": "/game/" + str(game.id)},
                {
                    "name": index_article.name,
                    "path": '/article/' + str(request.GET.get('0'))
                },
                {
                    "name": article.name,
                    "path": '/article/' + str(request.GET.get('0')) + '/' + str(request.GET.get('1'))
                }
            ]

        if path == 'episode':
            episode = Episode.objects.get(pk=request.GET.get('0'))
            breadcrumbs = [
                get_game_link(episode.game.id, request.user.id),
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


            breadcrumbs = [
                get_game_link(index_article.game.id, request.user.id),
                {"name": index_article.game.name, "path": "/game/" + str(index_article.game.id)},
            ]
            breadcrumbs += article_breadcrumbs

        return Response({"data": breadcrumbs})

def get_game_link(game_id, user_id):
    game = Game.objects.get(pk=game_id)
    participates = UserGameParticipation.objects.filter(game_id=game.id, user_id=user_id).count()
    if participates:
      return {"name": "My Games", "path": "/home"}

    else:
        return {"name": "Games", "path": "/games"}