class CharacterSheet:

    @staticmethod
    def get_field_type():
        return {
            1: _('Text field'),
            2: _('Textarea'),
            3: _('Select'),
            4: _('Radio buttons'),
            5: _('Check buttons')
        }