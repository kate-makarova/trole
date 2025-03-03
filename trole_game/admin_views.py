import datetime
from django.contrib.auth.models import User
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.paginator import Paginator

from trole_game.util.bb_translator import translate_bb, form_html
from trole_game.models import UserSetting, Page, SiteStatistics, NewsArticle


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

class AdminUserList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, page=1):

        user_list = User.objects.all().order_by('id')
        paginator = Paginator(user_list, 30)  # Show 30 contacts per page.

        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        data = []
        for user in page_obj.object_list:
            setting = UserSetting.objects.filter(user_id=user.id)

            if not len(setting):
                setting = UserSetting.objects.create(
                    user_id=user.id,
                    ui_language='en',
                    timezone='UTC',
                )
            else:
                setting = setting[0]

            data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "language": setting.ui_language,
                "timezone": setting.timezone,
                "theme": setting.theme
            })

        return Response({"data": data})

class AdminStats(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):

        stats = SiteStatistics.objects.all().order_by('key')

        data = []
        for stat in stats:

            data.append({
                "key": stat.key,
                "name": stat.name,
                "value": stat.get_stat(),
            })

        return Response({"data": data})

class NewsArticleCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        article = NewsArticle.objects.create(
            name=request.data['name'],
            image=request.data['image'],
            language=request.data['language'],
            content_bb=request.data['content'],
            content_html=form_html(request.data['content']),
            user_created=request.user,
            date_created=datetime.datetime.now()
        )

        return Response({"data": article.id})