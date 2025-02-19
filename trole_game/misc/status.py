from django.utils.translation import gettext as _

class GameStatus:

    @staticmethod
    def get_game_status():
        return {
            0: _('Cancelled'),
            1: _('Active'),
            2: _('Archived'),
            3: _('Suspended')
        }

class EpisodeStatus:

    @staticmethod
    def get_episode_status():
        return {
            0: _('Cancelled'),
            1: _('Active'),
            2: _('Finished'),
            3: _('Archived'),
            4: _('Suspended')
        }

class CharacterStatus:

    @staticmethod
    def get_character_status():
        return {
            0: _('Cancelled'),
            1: _('Active'),
            2: _('Pending')
        }