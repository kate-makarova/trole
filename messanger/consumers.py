import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('django')

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug('Connect')
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

        # Send message to room group
        await self.channel_layer.group_send(
            {"type": 1,
             "group_id": self.room_group_name},
            text_data
        )

    # Receive message from room group
    async def chat_message(self, event):
        logger.info(event)
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=message)
