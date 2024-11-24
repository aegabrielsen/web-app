import json
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

        self.send(text_data=json.dumps({"content": text_data_json["content"], "feeling": text_data_json["feeling"]}))