from django.urls import resolve
from rest_framework import permissions

from trole_game.misc.permissions import GamePermissions

class AccessLevelPermission(permissions.BasePermission):
    message = 'Access denied'

    def has_permission(self, request, view):
        current_url = resolve(request.path_info).url_name

        if current_url in [
            'game'
            'episode_list',
            'character_list',
            'article',
            'article_index'
        ]:
            game_id = request.query_params.get('game_id')
            return GamePermissions.check_game_access(game_id, request.user)

        if current_url in [
            'episode',
            'get_posts_by_episode'
        ]:
            episode_id = request.query_params.get('episode_id')
            return GamePermissions.check_episode_access(episode_id, request.user)

        return False