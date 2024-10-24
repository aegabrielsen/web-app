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
    path('like_post/<str:post_id>/', views.like_posts, name='like_post')
    


]