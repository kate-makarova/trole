import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from messanger.models import ChatParticipation


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print('Are we there?', flush=True)
      #  self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
      #  self.room_group_name = f"chat_{self.room_name}"
        self.room_group_name = 1
        user_id = 1

        participation = ChatParticipation.objects.filter(
            chat_type=1, private_chat_id=1, user_setting__user_id=1
        ).first()

        participation.channel_name = 'test'
        participation.save()


        # Join room group
        # async_to_sync(self.channel_layer.group_add)(
        #     {'group_id': self.room_group_name,
        #      'user_id': user_id},
        #     self.channel_name
        # )

        self.accept()

    def test(self):
        participation = ChatParticipation.objects.filter(
            chat_type=1, private_chat_id=1, user_setting__user_id=1
        ).first()

        participation.channel_name = 'test'
        participation.save()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            {'group_id': self.room_group_name,
             'user_id': 1},
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        print('Are were here?', flush=True)
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))