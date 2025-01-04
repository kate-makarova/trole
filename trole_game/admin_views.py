from django.contrib.auth.models import User
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from trole_game.models import UserSetting


class AdminUserCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):

        user = User.objects.create(
            username=request.data['username'],
            email=request.data['email'],
            password=request.data['password'],
            is_staff=False,
            is_superuser=False,
        )

        UserSetting.objects.create(
            user=user,
            language='en',
            timezone='UTC',
        )

        return Response({"data": user.id})