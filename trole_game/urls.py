from django.urls import path
from .views import index, UserHome, UserGetByUsername

urlpatterns = [
    path('api/', index, name='index'),
    path('api/home', UserHome.as_view(), name='home'),
    path('api/user/get-by-username/<str:username>', UserGetByUsername.as_view())
]