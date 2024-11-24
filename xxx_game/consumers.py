import json
import bcrypt
from channels.generic.websocket import AsyncWebsocketConsumer

from pymongo import MongoClient
mongo_client = MongoClient("mongo")
db = mongo_client["webapp"]
user_collection = db["users"]
game_collection = db["games"]
game_user_collection = db["game_users"]
global_salt = b'$2b$12$ldSsU24BK6EPANRbUpvXRu'


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
        feeling = text_data_json["feeling"]
        # username = text_data_json["username"]
        user = get_user_from_auth(cookie_parse(dict(self.scope["headers"])))
        if user:
            username = user.get('username')
        else:
            username = "Guest"
        
        # auth = cookie_parse(dict(self.scope["headers"]))
        # create_post_test(auth)

        # create_post_test(self.scope["headers"])
        create_post(username, content, feeling)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "content": content, "feeling": feeling, "username":username}
        )

    # Receive message from room group
    async def chat_message(self, event):
        content = event["content"]
        feeling = event["feeling"]
        username = event["username"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"content": content, "feeling": feeling, "username": username}))

def cookie_parse(headers):
    cookie_header = headers.get(b"cookie", b"").decode("utf-8")
    cookies = dict(cookie.split("=") for cookie in cookie_header.split("; "))
    auth_token = cookies.get("auth_token")
    return auth_token

def get_user_from_auth(auth_token):
    # If no auth_token exists or if the search turns up empty, returns None.
    # Can be used anywhere like this: user = get_user_from_auth(request).
    # Can then get fields from it like this: user.get('username')
    # Make sure to do a None check in case either the user isn't logged in or the auth token isn't in the database.
    # Check the index function to see an example of how to use this.
    if auth_token is None:
        return None

    auth_token_hash = bcrypt.hashpw(auth_token.encode(), global_salt)

    user = user_collection.find_one({"auth_token_hash" : auth_token_hash})

    return user

def create_post(username, content, feeling):
    post = { 
    'username': username,
    'content': content,
    'feeling': feeling,
    'likes': []
     }
    
    db['posts'].insert_one(post)
