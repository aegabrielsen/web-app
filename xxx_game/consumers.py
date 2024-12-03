import json
import bcrypt
import requests
import html
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from pymongo import MongoClient
mongo_client = MongoClient("mongo")
db = mongo_client["webapp"]
user_collection = db["users"]
game_collection = db["games"]
game_user_collection = db["game_users"]
global_salt = b'$2b$12$ldSsU24BK6EPANRbUpvXRu'

intervals = {}

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
        post_id = str(create_post(username, content, feeling))

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "content": content, "feeling": feeling, "username":username, "id": post_id}
        )

    # Receive message from room group
    async def chat_message(self, event):
        content = html.escape(event["content"])
        feeling = html.escape(event["feeling"])
        username = html.escape(event["username"])
        post_id = event["id"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"content": content, "feeling": feeling, "username": username, "id": post_id}))


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = f"game_room"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        user = get_user_from_auth(cookie_parse(dict(self.scope["headers"])))
        if user:
            username = user.get('username')
        else:
            username = "Guest"

        game_user_collection.update_one({'username': username}, { "$set": { "score": "0", "answer": "NO ANSWER" }}, upsert=True)

        self.page = self.scope["url_route"]["kwargs"].get("page", "default_page")
        if self.page not in intervals:
            intervals[self.page] = asyncio.create_task(self.send_data_timer())


    async def disconnect(self, close_code):
        user = get_user_from_auth(cookie_parse(dict(self.scope["headers"])))

        if game_user_collection.count_documents({'username':user['username']}) > 0:
            game_user_collection.delete_many({'username':user['username']})
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "player_list": get_player_list()}
        )
        if game_user_collection.count_documents({}) < 1:
            # Cancel the interval task and remove it from the dictionary
            interval = intervals.pop(self.page, None)
            if interval:
                interval.cancel()

        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        answer = text_data_json["answer"]

        user = get_user_from_auth(cookie_parse(dict(self.scope["headers"])))
        if user:
            game_user_collection.update_one({'username': user.get('username')}, { "$set": { "answer": answer } })
        # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name, {"type": "chat.message", "player_list": get_player_list()}
        # )

    # Receive message from room group
    async def chat_message(self, event):
        player_list = event["player_list"]
       
        await self.send(json.dumps({"player_list": player_list}))
    
    async def send_data(self, event):
        trivia = event["trivia"]
        timer = event["timer"]
        last_answer = event["last_answer"]
        player_list = event["player_list"]
        await self.send(json.dumps({"trivia": trivia, "timer": timer, "last_answer": last_answer, "player_list": player_list}))

    async def send_data_timer(self):
        # channel_layer = get_channel_layer()
        timer = 0
        trivia = {'response_code': 0, 'results': [{'type': 'multiple', 'difficulty': 'medium', 'category': 'General Knowledge', 'question': 'The term &quot;scientist&quot; was coined in which year?', 'correct_answer': 'No last answer, game was paused due to lack of players', 'incorrect_answers': ['1933', '1942', '1796']}]}
        # above is an example question directly from the api. This will be used by default if something is broken.
        last_answer = "No last answer, app just resumed."
        try:
            while True:
                if timer == 0:
                    timer = 10 # Please note that if you change this you also need to modify the script in game.html
                    last_answer = trivia.get('results')[0].get('correct_answer')
                    update_scores(last_answer)
                    trivia = trivia_api()
                else:
                    timer -= 1

                await self.channel_layer.group_send(self.room_group_name, { "type": "send_data", "trivia": trivia, "timer": timer, "last_answer": last_answer, "player_list": get_player_list()})
                await asyncio.sleep(1)  # Send data every second
        except asyncio.CancelledError:
            pass

def update_scores(answer):
    players = game_user_collection.find({})
    for player in players:
        if player.get('answer') == answer:
                new_score = int(player.get('score')) + 1
                game_user_collection.update_one({'username': player.get('username')}, { "$set": { "answer": "NO ANSWER" } })
                game_user_collection.update_one({'username': player.get('username')}, { "$set": { "score": str(new_score) } })


def trivia_api():
    url = "https://opentdb.com/api.php?amount=1&type=multiple"
    trivia = {'response_code': 0, 'results': [{'type': 'multiple', 'difficulty': 'medium', 'category': 'General Knowledge', 'question': 'The term &quot;scientist&quot; was coined in which year?', 'correct_answer': '1833', 'incorrect_answers': ['1933', '1942', '1796']}]}
    # above is an example question directly from the api. This will be used by default if something is broken.        
    try:
        response = requests.get(url)

        if response.status_code == 200:
            trivia = response.json()
            return trivia
        else:
            print('Error:', response.status_code)
            return trivia
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return trivia
    # The following are examples of how to use it. Note that incorrect_answers returns a list of strings while the others return strings
    #   trivia = get_trivia()
    #   print(trivia)
    #   print(type(trivia))
    #   print(html.unescape(trivia.get('results')[0].get('question')))
    #   print(html.unescape(trivia.get('results')[0].get('correct_answer')))
    #   print(html.unescape(trivia.get('results')[0].get('incorrect_answers')))


def get_player_list():
    players = game_user_collection.find({})
    player_list = []
    for player in players:
        score = player.get('score', '99')
        player = user_collection.find_one({'username': player['username']})
        if player:
            player_list.append({'avatar':player.get('avatar') if player.get('avatar') else 'avatar/default.png', 'username': html.escape(player['username']), 'score': score})
        else:
            player_list.append({'avatar':'avatar/default.png', 'username': 'Guest', 'score': '0'})

    return player_list

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
    
    return db['posts'].insert_one(post).inserted_id # Returns the mongoDB _id of the post
