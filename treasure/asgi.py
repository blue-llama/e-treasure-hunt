"""
WSGI config for treasure project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# Daphne requires we run this function before importing anything from the hunt
# application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "treasure.settings")
app = get_asgi_application()

from hunt.chat import routing  # noqa

application = ProtocolTypeRouter(
    {
        "http": app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
        ),
    }
)
