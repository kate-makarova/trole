from django.utils.translation import gettext as _

class CharacterEpisodeNotificationType:

    @staticmethod
    def get_types():
        return {
            0: _('Removed from Episode'),
            1: _('New Episode'),
            2: _('New Unread Post'),
            3: _('Episode Finished'),
            4: _('Episode Archived')
        }
