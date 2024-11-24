'''import json
from channels.generic.websocket import WebsocketConsumer

class Consumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        print(text_data_json["content"])
        print(text_data_json["feeling"])
        # message = text_data_json["message"]

        self.send(text_data=json.dumps({"content": text_data_json["content"], "feeling": text_data_json["feeling"]}))'''
# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # self.room_group_name = f"chat_{self.room_name}"
        self.room_group_name = f"chat_room"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json["content"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "content": content}
        )

    # Receive message from room group
    async def chat_message(self, event):
        content = event["content"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"content": content}))