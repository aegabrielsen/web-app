from django.urls import path, re_path
from .views import custom_static_view

from . import views

urlpatterns = [
    path("", views.index, name = "index"),
    path('static/<path:path>', custom_static_view),
    path("login", views.login, name = "login"),
    path("register", views.register, name = "register"),
    path("logout", views.logout, name = "logout"),
    path("create_post",views.create_post,name="create_post"),
    path("chat", views.chat, name = "chat"),
    path('like_post/<str:post_id>/', views.like_posts, name='like_post'),
    path('game_lobby', views.game_lobby, name = 'game_lobby'),
    path('game_room/<str:id>', views.game_room, name = 'game_room'),
    path('game/<str:id>', views.game, name = 'game'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('create_game/', views.create_game, name = 'create_game'),
    path('games/', views.get_game, name = 'games'),
    path('players/<str:id>', views.get_game_player, name = 'players'),
    path('game_chat', views.game_chat, name = 'game_chat'),
    path('game_chat_list/<str:id>', views.game_chat_list, name = 'game_chat_list'),
    path('leave_game/<str:id>', views.leave_game, name = 'leave_game'),
    path('finish_game/<str:id>', views.finish_game, name = 'finish_game'),
    path('join_game/<str:join_code>', views.join_game, name = 'join_game'),
    path('check_game_start/<str:id>', views.check_game_start, name = 'delete_game'),
]