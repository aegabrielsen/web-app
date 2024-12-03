from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name = "index"),
    path('static/avatar/<path:path>', views.avatar),
    path('static/css/<path:path>', views.custom_static_view, {"type": "css"}),
    path('static/images/<path:path>', views.custom_static_view, {"type": "images"}),
    path('static/js/<path:path>', views.custom_static_view, {"type": "js"}),
    path("login", views.login, name = "login"),
    path("register", views.register, name = "register"),
    path("logout", views.logout, name = "logout"),
    path("create_post",views.create_post,name="create_post"),
    path("chat", views.chat, name = "chat"),
    path("chat_list", views.chat_list, name = "chat_list"),
    path('like_post/<str:post_id>/', views.like_posts, name='like_post'),
    
    path('game/', views.game, name = 'game'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('get_players/', views.get_game_player, name = 'players'),
    path('leave_game/', views.leave_game, name = 'leave_game'),

    # path('create_game/', views.create_game, name = 'create_game'),
    # path('game_chat', views.game_chat, name = 'game_chat'),
    # path('game_chat_list/<str:id>', views.game_chat_list, name = 'game_chat_list'),
    # path('games/', views.get_game, name = 'games'),
    # path('finish_game/<str:id>', views.finish_game, name = 'finish_game'),
    # path('like_post_v1/<str:post_id>/', views.like_posts_ajax, name='like_post_v1'),
    # path('game_lobby', views.game_lobby, name = 'game_lobby'),
    # path('game_room/<str:id>', views.game_room, name = 'game_room'),
    # path('join_game/<str:join_code>', views.join_game, name = 'join_game'),
    # path('check_game_start/<str:id>', views.check_game_start, name = 'delete_game'),
]