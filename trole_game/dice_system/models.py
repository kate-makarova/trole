from django.db import models
from django.db.models import CASCADE, DO_NOTHING
from rest_framework.request import Empty

from trole_game.models import Game, Episode, Character

class Fight(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    episode = models.ForeignKey(Episode, on_delete=DO_NOTHING, null=True, default=Empty)

class DefinedStats(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    name = models.CharField(max_length=100)
    max = models.IntegerField(null=True, default=Empty)

class BaseMechanics(models.Model):
    name = models.CharField(100)
    health_stat = models.ForeignKey(DefinedStats, on_delete=DO_NOTHING)
    health_multiplier = models.IntegerField()

class DefinedSpellActionPont(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    name = models.CharField(100)

class DefinedExpLevels(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    level_number = models.IntegerField()
    required_experience = models.IntegerField()

class DefinedCharacterClass(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    playable = models.BooleanField(default=True)
    locked_by_default = models.BooleanField(default=False)

class DefinedWeaponType(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()

class DefinedCharacterClassFeatures(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    character_class = models.ForeignKey(DefinedCharacterClass, on_delete=CASCADE)
    level = models.IntegerField()
    number_of_action_points = models.IntegerField()
    number_of_bonus_action_points = models.IntegerField()
    number_of_spells = models.IntegerField()
    number_of_cantrips = models.IntegerField()
    main_stat_damage_modifier = models.IntegerField()

class DefinedCharacterClassSpellPoints(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    character_class = models.ForeignKey(DefinedCharacterClass, on_delete=CASCADE)
    level = models.IntegerField()
    spell_point = models.ForeignKey(DefinedSpellActionPont, on_delete=CASCADE)
    value = models.IntegerField()

class DefinedCharacterClassStats(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    character_class = models.ForeignKey(DefinedCharacterClass, on_delete=CASCADE)
    level = models.IntegerField()
    stat = models.ForeignKey(DefinedStats, on_delete=CASCADE)
    value = models.IntegerField()

class DefinedAttackStatModifiers(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    stat = models.ForeignKey(DefinedStats, on_delete=CASCADE)
    stat_value = models.IntegerField()
    value = models.IntegerField()

class ClassAvailability(models.Model):
    required_class = models.ForeignKey(DefinedCharacterClass, on_delete=DO_NOTHING)
    required_level = models.IntegerField()

class DefinedBaseAttack(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    action_point_cost = models.IntegerField()
    dice_type = models.IntegerField(null=True, default=None)
    use_class_base_stat = models.BooleanField(True)
    base_stat = models.IntegerField(null=True, default=None)

class DefinedSkill(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    is_spell = models.BooleanField(default=False)
    is_cantrip = models.BooleanField(default=False)
    dice_type = models.IntegerField(null=True, default=None)
    use_class_base_stat = models.BooleanField(True)
    base_stat = models.IntegerField(null=True, default=None)
    action_point_cost = models.IntegerField()
    bonus_action_cost = models.IntegerField()
    spell_point_type = models.ForeignKey(DefinedSpellActionPont, on_delete=DO_NOTHING)
    spell_point_cost = models.IntegerField()

class SkillAvailability(models.Model):
    skill = models.ForeignKey(DefinedSkill, on_delete=CASCADE)
    is_basic = models.BooleanField(default=False)
    required_class = models.ForeignKey(DefinedCharacterClass, on_delete=DO_NOTHING)
    required_level = models.IntegerField()

class FightCharacters(models.Model):
    fight = models.ForeignKey(Fight, on_delete=DO_NOTHING)
    character = models.ForeignKey(Character, on_delete=DO_NOTHING)

class Mob(models.Model):
    name = models.CharField(max_length=200)
    fight = models.ForeignKey(Fight, on_delete=DO_NOTHING)
    health = models.IntegerField()
    character_level = models.IntegerField()
    is_dead = models.BooleanField(default=False)
    experience_on_kill = models.IntegerField()

class MobStats(models.Model):
    mob = models.ForeignKey(Mob, on_delete=CASCADE)
    stat = models.ForeignKey(DefinedStats, on_delete=CASCADE)
    value = models.IntegerField()

class MobClass(models.Model):
    mob = models.ForeignKey(Mob, on_delete=CASCADE)
    mob_class = models.ForeignKey(DefinedCharacterClass, on_delete=DO_NOTHING)
    class_level = models.IntegerField()

class MobSkills(models.Model):
    mob = models.ForeignKey(Mob, on_delete=CASCADE)
    skill = models.ForeignKey(DefinedSkill, on_delete=DO_NOTHING)

class CharacterBasics(models.Model):
    character = models.ForeignKey(Character, on_delete=CASCADE)
    level = models.IntegerField()
    experience = models.IntegerField()

class CharacterStats(models.Model):
    character = models.ForeignKey(Character, on_delete=CASCADE)
    stat = models.ForeignKey(DefinedStats, on_delete=CASCADE)
    value = models.IntegerField()

class CharacterClass(models.Model):
    character = models.ForeignKey(Character, on_delete=CASCADE)
    character_class = models.ForeignKey(DefinedCharacterClass, on_delete=DO_NOTHING)
    class_level = models.IntegerField()

class CharacterSkills(models.Model):
    character = models.ForeignKey(Character, on_delete=CASCADE)
    skill = models.ForeignKey(DefinedSkill, on_delete=DO_NOTHING)
    character_class = models.ForeignKey(DefinedCharacterClass, on_delete=DO_NOTHING)
    
class CharacterModifiers(models.Model):
    character = models.ForeignKey(Character, on_delete=CASCADE)
    stat = models.ForeignKey(DefinedStats, on_delete=DO_NOTHING, null=True, default=None)
    base_attack = models.ForeignKey(DefinedBaseAttack, on_delete=DO_NOTHING, null=True, default=None)
    skill = models.ForeignKey(DefinedSkill, on_delete=DO_NOTHING, null=True, default=None)
    value = models.JSONField()

class FightLogTurn(models.Model):
    fight = models.ForeignKey(Fight, on_delete=CASCADE)
    round_number = models.IntegerField()
    fight_start = models.BooleanField(default=False)
    fight_finish = models.BooleanField(default=False)
    summary = models.TextField()
    details = models.JSONField()

class FightLogCharacter(models.Model):
    fight = models.ForeignKey(Fight, on_delete=CASCADE)
    turn = models.ForeignKey(FightLogTurn, on_delete=CASCADE)
    character = models.ForeignKey(Character, on_delete=CASCADE)
    details = models.JSONField()
    is_down = models.BooleanField()

class FightLogMob(models.Model):
    fight = models.ForeignKey(Fight, on_delete=CASCADE)
    turn = models.ForeignKey(FightLogTurn, on_delete=CASCADE)
    mob = models.ForeignKey(Mob, on_delete=CASCADE)
    details = models.JSONField()
    is_dead = models.BooleanField()