from django.utils.translation import gettext as _

class Participation:

    def get_participation_status(self):
        return {
            0: _('Cancelled'),
            1: _('Active'),
            2: _('Pending acceptance'),
            3: _('Suspended')
        }

    def get_participation_level(self):
        return {
            1: _('Super Admin'),
            2: _('Admin'),
            3: _('Moderator'),
            4: _('Participant')
        }