from django.urls import path
from .views import index, UserHome, UserGetByUsername, GetGameById, GetEpisodeList, GetCharacterList, GetEpisodeById, \
    GetPostsByEpisode, Autocomplete, EpisodeCreate, CharacterCreate

urlpatterns = [
    path('api/', index, name='index'),
    path('api/home', UserHome.as_view(), name='home'),
    path('api/user/get-by-username/<str:username>', UserGetByUsername.as_view()),
    path('api/game/<int:id>', GetGameById.as_view(), name='game'),
    path('api/episode-list/<int:game_id>', GetEpisodeList.as_view(), name='episode_list'),
    path('api/character-list/<int:game_id>', GetCharacterList.as_view(), name='character_list'),
    path('api/episode/<int:id>', GetEpisodeById.as_view(), name='get_episode'),
    path('api/episode-posts/<int:episode_id>', GetPostsByEpisode.as_view(), name='get_posts_by_episode'),
    path('api/autocomplete/<str:class_name>/<str:search>', Autocomplete.as_view(), name='autocomplete'),
    path('api/episode-create', EpisodeCreate.as_view(), name='episode_create'),
    path('api/character-create', CharacterCreate.as_view(), name='character_create')
]
