from django.utils.translation import gettext as _

class Participation:

    def get_participation_status(self):
        return {
            0: _('Cancelled'),
            1: _('Active'),
            2: _('Pending acceptance'),
            3: _('Suspended')
        }