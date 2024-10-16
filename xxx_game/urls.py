from django.urls import path, re_path
from .views import custom_static_view

from . import views

urlpatterns = [
    path("", views.index, name = "index"),
    path('static/<path:path>', custom_static_view),
    path("login", views.login, name = "login"),
    path("register", views.register, name = "register"),
    path("logout", views.logout, name = "logout"),
    path("create_post",views.createpost,name="create_post")

]