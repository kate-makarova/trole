from django.urls import path
from .views import index, UserHome, UserGetByUsername, GetGameById, GetEpisodeList, GetCharacterList, GetEpisodeById, \
    GetPostsByEpisode, Autocomplete, EpisodeCreate, CharacterCreate, StaticList, GameCreate, PostCreate, \
    CharacterAutocomplete, GameJoin, GetArticleById, GetIndexArticle

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
    path('api/character-autocomplete/<int:game_id>/<str:search>', CharacterAutocomplete.as_view(), name='character_autocomplete'),
    path('api/static-list/<str:class_name>', StaticList.as_view(), name='static_list'),
    path('api/episode-create', EpisodeCreate.as_view(), name='episode_create'),
    path('api/character-create', CharacterCreate.as_view(), name='character_create'),
    path('api/game-create', GameCreate.as_view(), name='game_create'),
    path('api/game-join', GameJoin.as_view(), name='game_join'),
    path('api/post-create', PostCreate.as_view(), name='post_create'),
    path('api/article/<int:id>', GetArticleById.as_view(), name='article'),
    path('api/article-index', GetIndexArticle.as_view(), name='article_index'),
]
