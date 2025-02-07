import datetime
from django.contrib.auth.models import User
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from trole_game.util.bb_translator import translate_bb, form_html
from trole_game.models import UserSetting, Page


class AdminUserCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):

        user = User.objects.create_user(
            username=request.data['username'],
            email=request.data['email'],
            password=request.data['password'],
            is_staff=False,
            is_superuser=False,
        )

        UserSetting.objects.create(
            user=user,
            ui_language='en',
            timezone='UTC',
        )

        return Response({"data": user.id})

class AdminPageCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):

        page = Page.objects.create(
            name=request.data['name'],
            language=request.data['language'],
            path=request.data['path'],
            content_bb=request.data['content'],
            content_html= form_html(request.data['content']),
            user_created=request.user,
            date_created=datetime.datetime.now()
        )

        return Response({"data": page.id})