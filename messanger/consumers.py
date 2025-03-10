import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

from messanger.models import ChatParticipation

logger = logging.getLogger('django')

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug('Connect')
        self.room_group_name = self.scope["url_route"]["kwargs"]["room_name"]
      #  self.room_group_name = f"chat_{self.room_name}"
       # self.room_group_name = 1
        user_id = 1
        user = self.scope
        print(user)

        logger.debug(self.channel_name)

        # Join room group
        await self.channel_layer.group_add(
            {'group_id': self.room_group_name,
             'user_id': user_id},
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):
        # Leave room group
        logger.debug('Disconnect')
        await self.channel_layer.group_discard(
            {'group_id': self.room_group_name,
             'user_id': 1},
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["text"]

        # Send message to room group
        # await self.channel_layer.group_send(
        #     {"type": 1,
        #      "group_id": self.room_group_name},
        #     message
        # )
        await self.channel_layer.send(
            self.channel_name
        , json.dumps({"type": "message", "message": message}))

    # Receive message from room group
    async def chat_message(self, event):
        print(event)
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=message)
