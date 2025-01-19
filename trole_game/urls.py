from django.urls import path

from .admin_views import AdminUserCreate
from .breadcrumb_views import Breadcrumbs
from .views import index, UserHome, UserGetByUsername, GetGameById, GetEpisodeList, GetCharacterList, GetEpisodeById, \
    GetPostsByEpisode, Autocomplete, EpisodeCreate, CharacterCreate, StaticList, GameCreate, PostCreate, \
    CharacterAutocomplete, GameJoin, GetArticleById, GetIndexArticle, SetPostsRead, ArticleCreate, \
    ArticleUpdate, GameList, PostUpdate, CharacterSheetTemplateGet, GetPageByPath, CharacterSheetTemplateUpdate

urlpatterns = [
    path('api/', index, name='index'),
    path('api/home', UserHome.as_view(), name='home'),
    path('api/game-list', GameList.as_view(), name='game_list'),
    path('api/user/get-by-username/<str:username>', UserGetByUsername.as_view()),
    path('api/game/<int:id>', GetGameById.as_view(), name='game'),
    path('api/episode-list/<int:game_id>', GetEpisodeList.as_view(), name='episode_list'),
    path('api/character-list/<int:game_id>', GetCharacterList.as_view(), name='character_list'),
    path('api/episode/<int:id>', GetEpisodeById.as_view(), name='episode'),
    path('api/episode-posts/<int:episode_id>', GetPostsByEpisode.as_view(), name='get_posts_by_episode'),
    path('api/autocomplete/<str:class_name>/<str:search>', Autocomplete.as_view(), name='autocomplete'),
    path('api/character-autocomplete/<int:game_id>/<str:search>', CharacterAutocomplete.as_view(), name='character_autocomplete'),
    path('api/static-list/<str:class_name>', StaticList.as_view(), name='static_list'),
    path('api/episode-create', EpisodeCreate.as_view(), name='episode_create'),
    path('api/character-create', CharacterCreate.as_view(), name='character_create'),
    path('api/game-create', GameCreate.as_view(), name='game_create'),
    path('api/game-join', GameJoin.as_view(), name='game_join'),
    path('api/post-create', PostCreate.as_view(), name='post_create'),
    path('api/article/<int:game_id>/<int:id>', GetArticleById.as_view(), name='article'),
    path('api/article-index/<int:game_id>', GetIndexArticle.as_view(), name='article_index'),
    path('api/article-create', ArticleCreate.as_view(), name='article_create'),
    path('api/post-update/<int:id>', PostUpdate.as_view(), name='post_update'),
    path('api/article-update/<int:id>', ArticleUpdate.as_view(), name='article_update'),
    path('api/breadcrumbs/<str:path>', Breadcrumbs.as_view(), name='breadcrumbs'),
    path('api/set-posts-read/<int:episode_id>', SetPostsRead.as_view(), name='set_posts_read'),
    path('api/character-sheet-template/<int:game_id>',
         CharacterSheetTemplateGet.as_view(),
         name='get_character_sheet_template'),
    path('api/character-sheet-template-update/<int:id>',
         CharacterSheetTemplateUpdate.as_view(),
         name='get_character_sheet_template_update'),
    path('api/page/<str:path>', GetPageByPath.as_view(), name='page_get'),

    path('api/admin-user-create', AdminUserCreate.as_view(), name='admin_user_create'),
]
