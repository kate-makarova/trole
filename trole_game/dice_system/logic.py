from random import random, randrange

from trole_game.dice_system.models import CharacterStats, CharacterClass, CharacterSkills, BaseMechanics, \
    DefinedAttackStatModifiers


class Logic:

    def __init__(self, game_id):
        self.game_id = game_id
        self.mechanics = BaseMechanics.objects.get(game_id=self.game_id)
        self.modifiers = DefinedAttackStatModifiers.objects.get(game_id=self.game_id)

    def getCharacterBaseMeta(self, character):
        stats = CharacterStats.objects.get(character=character)
        health = self.calculateHealth(stats)
        classes = CharacterClass.object.filter(character=character)
        meta = {
            "health": health,
            "basic_physical_melee_damage": None,
            "basic_physical_range_damage": None,
            "classes": [],
            "skills": [],
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
            "skills": [],
        }
        for char_class in classes:
            meta['classes'].append({
                "id": char_class.id,
                "name": char_class.name,
                "level": char_class.level
            })

        for skill in skills:
            meta['skills'].append({
                "id": skill.id,
                "name": skill.name,
                "is_spell": skill.is_spell,
                "base_damage": self.calculateSkillDamage(stats, classes, skill)
            })


    def getStatModifyer(self, stat, stat_value):
        for modifier in self.modifiers:
            if stat.id == modifier.stat.id and stat_value == modifier.stat_value:
                return modifier.value
        return False

    def getStatValue(self, stats, target_stat):
        for stat in stats:
            if stat.id == target_stat.id:
                return stat.value
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

    def calculatMeleePhysicalDamage(self, stats, classes, dN):
        total_melee_damage = 0
        for char_class in classes:
            stat_value = self.getStatValue(stats, char_class.base_stat_melee)
            melee_damage = self.rollDice(dN) + self.getStatModifyer(char_class.base_stat_melee, stat_value)
            if melee_damage > total_melee_damage:
                total_melee_damage = melee_damage
        return total_melee_damage

    def calculateRangedPhysicalDamage(self, stats, classes, dN):
        total_range_damage = 0
        for char_class in classes:
            stat_value = self.getStatValue(stats, char_class.base_stat_melee)
            range_damage = self.rollDice(dN) + self.getStatModifyer(char_class.base_stat_range, stat_value)
            if range_damage > total_range_damage:
                total_range_damage = range_damage
        return total_range_damage

    def calculateMagicalDamage(self, stats, classes, dN):
        total_magic_damage = 0
        for char_class in classes:
            stat_value = self.getStatValue(stats, char_class.base_stat_magic)
            magic_damage = self.rollDice(dN) + self.getStatModifyer(char_class.base_stat_range, stat_value)
            if magic_damage > total_magic_damage:
                total_magic_damage = magic_damage
        return total_magic_damage

    def calculateSkillDamage(self, stats, classes, skill):
        total_skill_damage = 0
        for char_class in classes:
            stat_value = self.getStatValue(stats, skill.base_stat)
            skill_damage = self.rollDice(skill.dice_type) + self.getStatModifyer(char_class.base_stat_range, stat_value)
            if skill_damage > total_skill_damage:
                total_skill_damage = skill_damage
        return total_skill_damage
