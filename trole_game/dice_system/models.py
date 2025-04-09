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

class DefinedExpLevels(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    level_number = models.IntegerField()
    required_experience = models.IntegerField()

class DefinedCharacterClass(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    base_stat = models.ForeignKey(DefinedStats, on_delete=DO_NOTHING)
    playable = models.BooleanField(default=True)
    locked_by_default = models.BooleanField(default=False)

class DefinedCharacterClassFeatures(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    character_class = models.ForeignKey(DefinedCharacterClass, on_delete=CASCADE)
    level = models.IntegerField()
    number_of_action_points = models.IntegerField()
    number_of_bonus_action_points = models.IntegerField()
    number_of_spells = models.IntegerField()
    number_of_cantrips = models.IntegerField()
    main_stat_damage_modifier = models.IntegerField()

class DefinedCharacterClassStats(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    character_class = models.ForeignKey(DefinedCharacterClass, on_delete=CASCADE)
    level = models.IntegerField()
    stat = models.ForeignKey(DefinedStats, on_delete=CASCADE)
    value = models.IntegerField()

class ClassAvailability(models.Model):
    required_class = models.ForeignKey(DefinedCharacterClass, on_delete=DO_NOTHING)
    required_level = models.IntegerField()

class DefinedSkill(models.Model):
    game = models.ForeignKey(Game, on_delete=CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    is_spell = models.BooleanField(default=False)
    is_cantrip = models.BooleanField(default=False)

class SkillAvailability(models.Model):
    skill = models.ForeignKey(DefinedSkill, on_delete=CASCADE)
    is_basic = models.BooleanField(default=False)
    required_class = models.ForeignKey(DefinedCharacterClass, on_delete=DO_NOTHING)
    required_level = models.IntegerField()

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




