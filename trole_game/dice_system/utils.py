from trole_game.dice_system.models import CharacterStats, CharacterClass, CharacterSkills, BaseMechanics


class Logic:

    def __init__(self, game_id):
        self.game_id = game_id
        self.mechanics = BaseMechanics.objects.get(game_id=self.game_id)

    def getFullCharacterStats(self, character):
        stats = CharacterStats.objects.get(character=character)
        classes = CharacterClass.object.filter(character=character)
        skills = CharacterSkills.objects.filter(character=character)
        health = self.calculateHealth(stats)
        skills = self.calculateSkillDamage(stats, classes, skills)

    def calculateHealth(self, stats):
        for stat in stats:
            if stat.id == self.mechanics.health_stat.id:
                return stat.value * self.mechanics.health_multiplier
        return False

    def calculateSkillDamage(self, stats, classes, skills):
        for skill in skills:
            stat_id = skill.character_class.base_stat.id

            for stat in stats:
                if stat.id == stat_id:
                    skill['damage'] = skill.character_class.base_stat_multiplier * stat.value

        return skills
