from django.utils.translation import gettext as _

class Participation:

    def get_display_category(self):
        return {
            0: _('Participant'),
            1: _('Bookmarked'),
        }