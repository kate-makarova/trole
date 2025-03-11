import datetime
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from messanger.models import ChatPost
from trole_game.util.bb_translator import form_html

logger = logging.getLogger('django')


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = self.scope["url_route"]["kwargs"]["room_name"]

        logger.debug(self.channel_name)

        # Join room group
        await self.channel_layer.group_add(
            {'group_id': self.room_group_name,
             'user_id': self.scope['user'].id},
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):
        # Leave room group
        logger.debug('Disconnect')
        await self.channel_layer.group_discard(
            {'group_id': self.room_group_name,
             'user_id': self.scope['user'].id},
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        id = ChatPost.objects.create(
            chat_id=self.room_group_name,
            author=data['user'].id,
            date_created = datetime.time,
            content_bb = data['text'],
            content_html = form_html(data['text'])
        )
        data['id'] = id

        # Send message to room group
        await self.channel_layer.group_send(
            {"type": 1,
             "group_id": self.room_group_name},
            json.dumps(data)
        )

    # Receive message from room group
    async def chat_message(self, event):
        logger.info(event)
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=message)
