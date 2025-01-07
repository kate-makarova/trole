from django.utils.translation import gettext as _
from trole_game.models import Game, UserGameParticipation, Episode, Character


class GamePermissions:

    @staticmethod
    def get_levels():
        return {
            0: _('Open to guests'),
            1: _('Open to users'),
            2: _('Open to participants')
        }

    @staticmethod
    def check_game_access(game_id, user):
        game = Game.objects.get(pk=game_id)

        if game.permission_level == 0:
            return True

        if not user.is_authenticated and game.permission_level > 0:
            return False

        if user.is_authenticated and game.permission_level == 1:
            return True

        participation = UserGameParticipation.objects.filter(game_id=game_id, user_id=user.id)

        if len(participation) and participation[0].status == 1:
            return True

        return False

    @staticmethod
    def check_episode_access(episode_id, user_id):
        episode = Episode.objects.get(pk=episode_id)
        game = episode.game
        if game.permission_level > episode.permission_level:
            return GamePermissions.check_game_access(game.id, user_id)
        else:
            if episode.permission_level == 0:
                return True

            if user_id != 0 and episode.permission_level == 1:
                return True

            participation = Character.object.filter(episode_id=episode_id, user_id=user_id)

            if len(participation):
                return True

            return False




