from django.urls import path
from .views import index, user_home

urlpatterns = [
    path('', index, name='index'),
    path('home', user_home, name='home'),
]