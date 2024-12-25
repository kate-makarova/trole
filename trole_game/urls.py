from django.urls import path
from .views import index, UserHome, UserGetByUsername, GetGameById, GetEpisodeList, GetCharacterList

urlpatterns = [
    path('api/', index, name='index'),
    path('api/home', UserHome.as_view(), name='home'),
    path('api/user/get-by-username/<str:username>', UserGetByUsername.as_view()),
    path('api/game/<int:id>', GetGameById.as_view(), name='game'),
    path('api/episode-list/<int:game_id>', GetEpisodeList.as_view(), name='episode_list'),
    path('api/character-list/<int:game_id>', GetCharacterList.as_view(), name='character_list')
]