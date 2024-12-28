from django.utils.translation import gettext as _

class Participation:

    @staticmethod
    def get_participation_status():
        return {
            0: _('Cancelled'),
            1: _('Active'),
            2: _('Pending acceptance'),
            3: _('Suspended')
        }

    @staticmethod
    def get_participation_role():
        return {
            1: _('Super Admin'),
            2: _('Admin'),
            3: _('Moderator'),
            4: _('Participant')
        }