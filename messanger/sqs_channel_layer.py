import logging
import uuid
import boto3
from botocore.exceptions import ClientError

from channels.layers import BaseChannelLayer

from messanger.models import ChatParticipation

logger = logging.getLogger(__name__)

class SQSChannelLayer(BaseChannelLayer):
    """
    SQQ channel layer.

    It routes all messages into SQS.
    """
    def _init_(self,
               prefix="asgi",
               ):
        self.prefix=prefix
        self.receive_count = 0
        self.receive_event_loop = None
        self.client_prefix = uuid.uuid4().hex
        # Detached channel cleanup tasks
        self.receive_cleaners = []
        # Per-channel cleanup locks to prevent a receive starting and moving
        # a message back into the main queue before its cleanup has completed

        self.sqs = boto3.client("sqs")


    def get_queue(self, channel_name):
        """
        Gets an SQS queue by name.

        :param name: The name that was used to create the queue.
        :return: A Queue object.
        """
        try:
            queue = self.sqs.get_queue_by_name(QueueName=channel_name)
            logger.info("Got queue '%s' with URL=%s", channel_name, queue.url)
        except ClientError as error:
            logger.exception("Couldn't get queue named %s.", channel_name)
            raise error
        else:
            return queue

    async def send(self, channel, message):
        message_attributes = {}

        queue = self.get_queue(channel)
        try:
            response = queue.send_message(
                MessageBody=message, MessageAttributes=message_attributes
            )
        except ClientError as error:
            logger.exception("Send message failed: %s", message)
            raise error
        else:
            return response

    async def new_channel(self, prefix="specific"):
        name = f"{prefix}.{self.client_prefix}!{uuid.uuid4().hex}"
        try:
            queue = self.sqs.create_queue(QueueName=name, Attributes={})
            logger.info("Created queue '%s' with URL=%s", name, queue.url)
        except ClientError as error:
            logger.exception("Couldn't create queue named '%s'.", name)
            raise error
        else:
            return queue

    # async def group_add(self, group, channel):
    #     #todo
    #
    # async def group_discard(self, group, channel):
    #     #todo

    async def group_send(self, group, message):
        participations = ChatParticipation.objects.filter(chat_id=group).select_related('user')
        for participation in participations:
            if participation.status == 1:
                try:
                    queue = self.get_queue(self, participation.channel_name)
                    response = queue.send_message(
                        MessageBody=message, MessageAttributes={}
                    )
                except ClientError as error:
                    logger.exception("Send message failed: %s", message)
                    raise error
                else:
                    return response



