from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from trole_game.dice_system.models import Fight, FightCharacters, Mob, CharacterStats
from trole_game.dice_system.utils import Logic
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
            "characters": [],
            "mobs": []
        }

        for character_id in request.data['characters']:
            participation = FightCharacters.objects.create(
                fight=fight,
                character_id=character_id
            )
            character = Character.objects.get(pk=character_id)
            character_meta = logic.getCharacterFullStats(character)

            fight['characters'].append({
                "character": {
                    "id": character.id,
                    "name": character.name,
                    "avatar": character.avatar
                },
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

        return Response({"data": data})