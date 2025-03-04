import logging
import uuid
import boto3
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
        while True:
            pass
        # message = None
        # while message is None:
        #     try:
        #         messages = self.sqs.receive_message(
        #             QueueUrl=channel,
        #             MessageAttributeNames=["All"],
        #             MaxNumberOfMessages=1,
        #             WaitTimeSeconds=10,
        #         )
        #     except ClientError as error:
        #         logger.exception("Couldn't receive messages from queue: %s", channel)
        #         raise error
        #     else:
        #         print(messages)
        #         try:
        #             m = messages['Messages'][0]
        #             message = {
        #                 "message_id": m['MessageId'],
        #                 "body": m["Body"],
        #                 "type": "string"
        #                 }
        #             return channel, message
        #         except:
        #             pass

    async def new_channel(self, prefix="specific"):
        # name = f"{uuid.uuid4().hex}"
        # try:
        #     queue = self.sqs.create_queue(QueueName=name, Attributes={})
        #     logger.info("Created queue '%s' with URL=%s", name, queue['QueueUrl'])
        # except ClientError as error:
        #     logger.exception("Couldn't create queue named '%s'.", name)
        #     raise error
        # else:
        #     return queue['QueueUrl']
        return 'test'


    def update_participation(self, group, channel):
        participation = ChatParticipation.objects.filter(
            chat_type=1,  private_chat_id=group['chat_id'],  user_setting__user_id=group['user_id']
        ).first()

        if not participation:
            raise ValueError("No matching ChatParticipation found")

        participation.channel_name = channel
        participation.save()

    async def group_add(self, group, channel):
        await database_sync_to_async(self.update_participation)(group, channel)

    async def group_discard(self, group, channel):
        group_id = 1
        user_id = 1
        participation = ChatParticipation.objects.filter(chat_type=1, private_chat_id=group_id,  user_setting__user_id=user_id)[0]
        participation.channel_name = None
        participation.save()

    async def group_send(self, group, message):
        participations = ChatParticipation.objects.filter(chat_id=group)
        for participation in participations:
            if participation.channel_name is not None:
                try:
                    await self.send(participation.channel_name, message)
                except ClientError as error:
                    logger.exception("Send message failed: %s", message)
                    raise error
                else:
                    return True
