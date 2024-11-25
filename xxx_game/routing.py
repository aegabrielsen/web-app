# Idk what this does, it is from a tutorial
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("websocket", consumers.Consumer.as_asgi()),
    path("ws/chat/", consumers.Consumer.as_asgi()),
    path("ws/game/", consumers.GameConsumer.as_asgi()),
]