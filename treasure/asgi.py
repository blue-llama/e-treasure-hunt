"""
WSGI config for treasure project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
from django.core.asgi import get_asgi_application

# Daphne requires we run this function before importing anything else
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "treasure.settings")
app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from hunt.chat import routing


application = ProtocolTypeRouter(
    {
        "http": app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
        ),
    }
)
