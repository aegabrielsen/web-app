"""
ASGI config for project1 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

# Websockets
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from xxx_game.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project1.settings')

# Original from before websockets
# application = get_asgi_application()

# Websockets
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket" : AllowedHostsOriginValidator(URLRouter(websocket_urlpatterns))
    }
)