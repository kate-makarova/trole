from trole_game.dice_system.models import CharacterStats, CharacterClass, CharacterSkills, BaseMechanics


class Logic:

    def __init__(self, game_id):
        self.game_id = game_id
        self.mechanics = BaseMechanics.objects.get(game_id=self.game_id)

    def getCharacterFullStats(self, character):
        stats = CharacterStats.objects.get(character=character)
        classes = CharacterClass.object.filter(character=character)
        skills = CharacterSkills.objects.filter(character=character)
        health = self.calculateHealth(stats)
        skills = self.calculateSkillDamage(stats, classes, skills)
        meta = {
            "health": health,
            "basic_physical_melee_damage": 0,
            "basic_physical_range_damage": 0,
            "basic_magical_damage": 0,
            "classes": [],
            "skills": [],
        }
        for char_class in classes:
            meta['classes'].append({
                "id": char_class.id,
                "name": char_class.name,
                "level": char_class.level
            })

        # for skill in skills:
        #     meta['skills'].append({
        #         "id": skill.id,
        #         "name": skill.name,
        #         "is_spell": skill.is_spell,
        #         ""
        #     })


    def calculateHealth(self, stats):
        for stat in stats:
            if stat.id == self.mechanics.health_stat.id:
                return stat.value * self.mechanics.health_multiplier
        return False

    def calculateBaseMeleePhysicalDamage(self, stats, classes):
        total_melee_damage = 0
        for char_class in classes:
            stat_id = char_class.base_stat.id

            for stat in stats:
                if stat.id == stat_id:
                    total_melee_damage += char_class.base_attack_melee_physical_multiplier * stat.value
        return total_melee_damage

    def calculateBaseRangedPhysicalDamage(self, stats, classes):
        total_melee_damage = 0
        for char_class in classes:
            stat_id = char_class.base_stat.id

            for stat in stats:
                if stat.id == stat_id:
                    total_melee_damage += char_class.base_attack_ranged_physical_multiplier * stat.value
        return total_melee_damage

    def calculateBaseMagicalDamage(self, stats, classes):
        total_melee_damage = 0
        for char_class in classes:
            stat_id = char_class.base_stat.id

            for stat in stats:
                if stat.id == stat_id:
                    total_melee_damage += char_class.base_attack_magical_multiplier * stat.value
        return total_melee_damage

    def calculateSkillDamage(self, stats, classes, skills):
        for skill in skills:
            stat_id = skill.base_stat_multiplier.id

            for stat in stats:
                if stat.id == stat_id:
                    skill['damage'] = skill.character_class.base_stat_multiplier * stat.value

        return skills
