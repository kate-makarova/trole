from random import random, randrange

from trole_game.dice_system.models import CharacterStats, CharacterClass, CharacterSkills, BaseMechanics, \
    DefinedAttackStatModifiers, DefinedCharacterClassSpellPoints, CharacterModifiers


class Logic:

    def __init__(self, game_id):
        self.game_id = game_id
        self.mechanics = BaseMechanics.objects.get(game_id=self.game_id)
        self.statModifiers = DefinedAttackStatModifiers.objects.filter(game_id=self.game_id)
        self.spell_action_points = DefinedCharacterClassSpellPoints.objects.filter(game_id=self.game_id)

    def getCharacterBaseMeta(self, character):
        stats = CharacterStats.objects.get(character=character)
        health = self.calculateHealth(stats)
        classes = CharacterClass.object.filter(character=character)
        modifiers = CharacterModifiers.objects.filter(character=character)
        meta = {
            "health": health,
            "basic_physical_melee_damage": None,
            "basic_physical_range_damage": None,
            "classes": [],
            "base_actions:": [],
            "skills_and_spells": [],
            "action_points": None,
            "bonus_action_points": None,
            "pell_action_points": []
        }
        for char_class in classes:
            meta['classes'].append({
                "id": char_class.id,
                "name": char_class.name,
                "level": char_class.level
            })


        return meta

    def getCharacterFullMeta(self, character):
        stats = CharacterStats.objects.get(character=character)
        classes = CharacterClass.object.filter(character=character)
        skills = CharacterSkills.objects.filter(character=character)
        health = self.calculateHealth(stats)

        meta = {
            "health": health,
            "basic_physical_melee_damage": self.calculatMeleePhysicalDamage(stats, classes, 0),
            "basic_physical_range_damage": self.calculateRangedPhysicalDamage(stats, classes, 0),
            "classes": [],
            "base_actions:": [],
            "action_points": None,
            "skills_and_spells": [],
            "bonus_action_points": None,
            "spell_action_points": [self.calculateSpellActionPoints(classes)]
        }
        for char_class in classes:
            meta['classes'].append({
                "id": char_class.id,
                "name": char_class.name,
                "level": char_class.level
            })

        for skill in skills:
            meta['skills_and_spells'].append({
                "id": skill.id,
                "name": skill.name,
                "is_spell": skill.is_spell,
                "base_damage": self.calculateSkillDamage(stats, classes, skill)
            })


    def getStatModifyer(self, stat, stat_value):
        for modifier in self.statModifiers:
            if stat.id == modifier.stat.id and stat_value == modifier.stat_value:
                return modifier.value
        return False

    def getStatValue(self, stats, modifiers, target_stat):
        stat_value = 0
        for stat in stats:
            if stat.id == target_stat.id:
                stat_value += stat.value
                
        for modifier in modifiers:
            if modifier.stat.id == target_stat.id:
                stat_value += modifier.value
                
        return False

    def calculateHealth(self, stats):
        for stat in stats:
            if stat.id == self.mechanics.health_stat.id:
                return stat.value * self.mechanics.health_multiplier
        return False

    def rollDice(self, dN):
        if dN == 0:
            return 0
        return randrange(1, dN)

    def calculatBaseAttackDamage(self, action, stats, classes, modifiers, dN = None):
        total_action_damage = 0
        
        
        for char_class in classes:
            stat_value = self.getStatValue(stats, char_class.base_stat_melee)
            melee_damage = self.rollDice(dN) + self.getStatModifyer(char_class.base_stat_melee, stat_value)
            if melee_damage > total_action_damage:
                total_action_damage = melee_damage
        return total_action_damage

    def calculateSkillSpellDamage(self, skill, stats, classes, modifiers):
        total_skill_damage = 0
        for char_class in classes:
            stat_value = self.getStatValue(stats, skill.base_stat)
            skill_damage = self.rollDice(skill.dice_type) + self.getStatModifyer(char_class.base_stat_range, stat_value)
            if skill_damage > total_skill_damage:
                total_skill_damage = skill_damage
        return total_skill_damage

    def calculateSpellActionPoints(self, classes):
        spell_action_points = {}
        for char_class in classes:
            for spell_points in self.spell_action_points:
                if spell_points.character_class.id == char_class.id and spell_points.level == char_class.level:
                    value = spell_points.value
                    if spell_points.spell_point not in spell_action_points or value > spell_action_points[spell_points.spell_point]:
                        spell_action_points[spell_points.spell_point] = value

        return spell_action_points
