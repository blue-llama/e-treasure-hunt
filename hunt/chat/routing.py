from django.urls import path

from hunt.chat import consumers

websocket_urlpatterns = [
    path("ws/<str:room_name>/", consumers.ChatConsumer.as_asgi()),  # Using asgi
]
