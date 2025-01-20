from django.urls import resolve
from rest_framework import permissions

from trole_game.misc.permissions import GamePermissions
from trole_game.models import Episode, Character


class AccessLevelPermission(permissions.BasePermission):
    message = 'Access denied'

    def has_permission(self, request, view):
        resolved = resolve(request.path_info)
        current_url = resolved.url_name

        if current_url in ['game']:
            game_id = resolved.kwargs['id']
            return GamePermissions.check_game_access(game_id, request.user)

        if current_url in [
            'episode_list',
            'character_list',
            'article',
            'article_index'
        ]:
            game_id = resolved.kwargs['game_id']
            return GamePermissions.check_game_access(game_id, request.user)

        if current_url in [
            'character_sheet'
        ]:
            character_id = resolved.kwargs['character_id']
            character = Character.objects.get(pk=character_id)
            return GamePermissions.check_game_access(character.game.id, request.user)

        if current_url in [
            'episode'
        ]:
            episode_id = resolved.kwargs['id']
            episode = Episode.objects.get(pk=episode_id)
            return GamePermissions.check_game_access(episode.game.id, request.user)

        if current_url in [
            'get_posts_by_episode'
        ]:
            episode_id = resolved.kwargs['episode_id']
            episode = Episode.objects.get(pk=episode_id)
            return GamePermissions.check_game_access(episode.game.id, request.user)
           # return GamePermissions.check_episode_access(episode_id, request.user)

        return False