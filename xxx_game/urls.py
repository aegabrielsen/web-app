from django.urls import path, re_path
from .views import custom_static_view

from . import views

urlpatterns = [
    path("", views.index,name = "index"),
    path('static/<path:path>', custom_static_view),
]