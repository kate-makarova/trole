from django.utils.translation import gettext as _
from trole_game.models import Game, UserGameParticipation


class GamePermissions:

    @staticmethod
    def get_levels():
        return {
            0: _('Open to guests'),
            1: _('Open to users'),
            2: _('Open to participants')
        }

    def check_game_access(self, game_id, user_id):
        game = Game.objects.get(pk=game_id)

        if game.permission_level == 0:
            return True

        if user_id != 0 and game.permission_level == 1:
            return True

        participation = UserGameParticipation.objects.get(game_id=game_id, user_id=user_id)

        if len(participation) and participation[0].status == 1:
            return True

        return False

