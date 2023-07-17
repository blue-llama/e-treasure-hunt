import json

from channels.generic.websocket import AsyncWebsocketConsumer  # The class we're using
from asgiref.sync import sync_to_async  # Implement later
from hunt.models import ChatMessage
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        username = data["username"]
        room = data["room"]
        team = data["team"]

        await self.save_message(username, team, room, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "message": message, "username": username},
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps({"message": message, "username": username})
        )

    @sync_to_async
    def save_message(self, username, team, room_name, message):
        try:
            team_user = User.objects.get(username=team)
            ChatMessage.objects.create(
                name=username,
                team=team_user,
                room=room_name,
                content=message,
            )
        except User.objects.DoesNotExist:
            # We don't know which team made this message, so don't save it
            pass
