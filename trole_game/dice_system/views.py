from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from trole_game.dice_system.models import Fight, FightCharacters, Mob
from trole_game.dice_system.logic import Logic
from trole_game.models import Character


class StartFight(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        logic = Logic(request.data['game'])

        fight = Fight.objects.create(
            game_id = request.data['game'],
            episode_id = request.data['episode']
        )

        data = {
            "fight": fight.id,
            "turn": 1,
            "live_characters": len(request.data['characters']),
            "live_mobs": 0,
            "characters": [],
            "mobs": []
        }

        for character_id in request.data['characters']:
            participation = FightCharacters.objects.create(
                fight=fight,
                character_id=character_id
            )
            character = Character.objects.get(pk=character_id)
            if character.user.id == request.user.id:
                character_meta = logic.getCharacterFullMeta(character)
            else:
                character_meta = logic.getCharacterBaseMeta(character)

            fight['characters'].append({
                "character": {
                    "id": character.id,
                    "name": character.name,
                    "avatar": character.avatar,
                    "is_mine": character.user.id == request.user.id
                },
                "system": logic.mechanics.name,
                "meta": character_meta
            })

        for mob_data in request.data['mobs']:
            mob = Mob.objects.create(
                name=mob_data['name'],
                fight=fight,
                health=mob_data['health'],
                character_level=mob_data['character_level'],
                is_dead=False,
                experience_on_kill=mob_data['experience']
            )
            data['mobs'].append({
                "id": mob.id,
                "name": mob.name,
                "health": mob.heath,
                "level": mob.character_level,
                "experience": mob.experience_on_kill,
                "is_dead": mob.is_dead
            })
            if not mob.is_dead:
                data['live_mobs'] += 1

        return Response({"data": data})

class TakeAction(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):




        return Response({"data": True})
