import asyncio
import json
import logging
import uuid
from logging import DEBUG

import boto3
from asgiref.sync import sync_to_async
from botocore.exceptions import ClientError
from channels.db import database_sync_to_async

from channels.layers import BaseChannelLayer
from django.db import transaction

from messanger.models import ChatParticipation

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

    async def receive(self, channel):
        # print('??')
        # while True:
        #     await asyncio.sleep(10)
        #     print('tick tack')
        # return True

        message = None
        while message is None:
            try:
                messages = self.sqs.receive_message(
                    QueueUrl=channel,
                    MessageAttributeNames=["All"],
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=3,
                )
                await asyncio.sleep(3)
                await self.send(channel, json.dumps({"type": "heartbeat", "message": ''}))
            except ClientError as error:
                logger.exception("Couldn't receive messages from queue: %s", channel)
                raise error
            else:
                try:
                    m = messages['Messages'][0]
                    message = {
                        "message_id": m['MessageId'],
                        "message": m["Body"],
                        "type": "chat.message"
                        }

                    self.sqs.delete_message(
                        QueueUrl=channel,
                        ReceiptHandle=m['ReceiptHandle']
                    )
                    return message
                except:
                    pass

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

    async def group_send(self, group, message):
        channels = await database_sync_to_async(self.get_channels)(group)
        for channel in channels:
            try:
                await self.send(channel, message)
            except ClientError as error:
                logger.exception("Send message failed: %s", message)
                raise error
