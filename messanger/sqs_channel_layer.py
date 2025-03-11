import asyncio
import json
import logging
import uuid
import datetime
from logging import DEBUG

import boto3
import botocore
from asgiref.sync import sync_to_async
from botocore.exceptions import ClientError
from channels.db import database_sync_to_async

from channels.layers import BaseChannelLayer
from django.db import transaction

from messanger.models import ChatParticipation, PrivateChatPost
from trole_game.util.bb_translator import form_html

logger = logging.getLogger(__name__)


class SQSChannelLayer(BaseChannelLayer):
    """
    SQQ channel layer.

    It routes all messages into SQS.
    """

    def __init__(self, prefix="asgi"):
        self.prefix = prefix
        self.receive_count = 0
        self.receive_event_loop = None
        self.client_prefix = uuid.uuid4().hex
        self.sqs = boto3.client("sqs")

    async def send(self, channel, message):
        try:
            response = self.sqs.send_message(
                QueueUrl=channel,
                MessageBody=message
            )
        except ClientError as error:
            logger.exception("Send message failed: %s", message)
            raise error
        else:
            return response

    async def send_heartbeat(self, channel):
        while True:
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds or as required
            await self.send(channel, json.dumps({"type": "heartbeat", "message": ''}))

    async def receive(self, channel):
        message = None

        # Start by entering the polling loop
        while message is None:
            try:
                # Poll for messages
                messages = self.sqs.receive_message(
                    QueueUrl=channel,
                    MessageAttributeNames=["All"],
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=1,  # Long polling for 1 second
                )



                # Log the result for debugging
                #logger.info(f"Received SQS response: {messages}")

                # Allow the event loop to yield control (non-blocking)
                await asyncio.sleep(0)

                if 'Messages' in messages:
                    # Process the received message
                    m = messages['Messages'][0]
                    message = {
                        "message_id": m['MessageId'],
                        "message": m["Body"],
                        "type": "chat.message"
                    }

                  #  logger.info(m)

                    # Delete message from queue after processing
                    self.sqs.delete_message(
                        QueueUrl=channel,
                        ReceiptHandle=m['ReceiptHandle']
                    )

                    return message
                else:
                    # No messages, continue polling
                    pass # logger.info("No messages received")


            except ClientError as error:
                if error.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                    print(f"Error: The SQS queue does not exist anymore")
                    return

                else:
                    logger.exception("Couldn't receive messages from queue: %s", channel)
                    raise error

            except Exception as e:
                logger.exception("Error receiving or processing messages: %s", e)
                await asyncio.sleep(1)  # Avoid tight loop in case of error

    async def new_channel(self, prefix="specific"):
        name = f"{uuid.uuid4().hex}"
        try:
            queue = self.sqs.create_queue(QueueName=name, Attributes={})
            logger.info("Created queue '%s' with URL=%s", name, queue['QueueUrl'])
            self.sqs.send_message(
                QueueUrl=queue['QueueUrl'],
                MessageBody=json.dumps({"type": "heartbeat", "message": "connection"})
            )
            return queue['QueueUrl']
        except ClientError as error:
            logger.exception("Couldn't create queue named '%s'.", name)
            raise error



    def update_participation(self, group, channel, add=True):
        participation = ChatParticipation.objects.filter(
            chat_type=1,  private_chat_id=group['group_id'],  user_id=group['user_id']
        ).first()
        logger.info(participation)
        if not participation:
            raise ValueError("No matching ChatParticipation found")

        if participation.channel_name is not None:
            try:
                self.sqs.delete_queue(QueueUrl=participation.channel_name)
            except:
                pass

        if add:
            participation.channel_name = channel
        else:
            participation.channel_name = None
        participation.save()

    async def group_add(self, group, channel):
        await database_sync_to_async(self.update_participation)(group, channel)

    async def group_discard(self, group, channel):
        await database_sync_to_async(self.update_participation)(group, channel, False)

    def get_channels(self, group):
        channels = ChatParticipation.objects.filter(
            chat_type=group['type'],  private_chat_id=group['group_id']
        ).exclude(channel_name=None).values_list('channel_name', flat=True)
        return list(channels)

    def save_message(self, chat_id, message):
        data = json.loads(message)
        post = PrivateChatPost.objects.create(
            chat_id=chat_id,
            author_id=data['user']['id'],
            date_created=datetime.datetime.now(),
            content_bb=data['text'],
            content_html=form_html(data['text'])
        )
        data['id'] = post.id
        return json.dumps(data)

    async def group_send(self, group, message):
        message = await database_sync_to_async(self.save_message)(group['group_id'], message)
        channels = await database_sync_to_async(self.get_channels)(group)
        for channel in channels:
            try:
                await self.send(channel, message)
            except ClientError as error:
                logger.exception("Send message failed: %s", message)
                raise error
