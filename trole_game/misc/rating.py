from django.utils.translation import gettext as _

class Rating:

    @staticmethod
    def get_ratings():
        return {
            1: {"name": _('G'), "description": ""},
            2: {"name": _('PG-13'), "description": ""},
            3: {"name": _('R'), "description": ""},
            4: {"name": _('NC-17'), "description": ""}
        }