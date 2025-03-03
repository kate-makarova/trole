import asyncio
import collections
import functools
import itertools
import logging
import time
import uuid
import boto3
from botocore.exceptions import ClientError

from channels.exceptions import ChannelFull
from channels.layers import BaseChannelLayer

from messanger.models import ChatParticipation
from .serializers import registry
from .utils import (
    _close_redis,
    _consistent_hash,
    _wrap_close,
    create_pool,
    decode_hosts,
)

logger = logging.getLogger(__name__)


class ChannelLock:
    """
    Helper class for per-channel locking.

    Once a lock is released and has no waiters, it will also be deleted,
    to mitigate multi-event loop problems.
    """

    def __init__(self):
        self.locks = collections.defaultdict(asyncio.Lock)
        self.wait_counts = collections.defaultdict(int)

    async def acquire(self, channel):
        """
        Acquire the lock for the given channel.
        """
        self.wait_counts[channel] += 1
        return await self.locks[channel].acquire()

    def locked(self, channel):
        """
        Return ``True`` if the lock for the given channel is acquired.
        """
        return self.locks[channel].locked()

    def release(self, channel):
        """
        Release the lock for the given channel.
        """
        self.locks[channel].release()
        self.wait_counts[channel] -= 1
        if self.wait_counts[channel] < 1:
            del self.locks[channel]
            del self.wait_counts[channel]


class BoundedQueue(asyncio.Queue):
    def put_nowait(self, item):
        if self.full():
            # see: https://github.com/django/channels_redis/issues/212
            # if we actually get into this code block, it likely means that
            # this specific consumer has stopped reading
            # if we get into this code block, it's better to drop messages
            # that exceed the channel layer capacity than to continue to
            # malloc() forever
            self.get_nowait()
        return super(BoundedQueue, self).put_nowait(item)


class SQSChannelLayer(BaseChannelLayer):
    """
    Dynamo channel layer.

    It routes all messages into DynamoDB.
    """
    def _init_(self,
               prefix="asgi",
               serializer_format="msgpack",
               random_prefix_length=12,
               symmetric_encryption_keys=None,
               ):
        self.prefix=prefix
        self.receive_count = 0
        self.receive_event_loop = None
        self.client_prefix = uuid.uuid4().hex
        self.receive_buffer = collections.defaultdict(
            functools.partial(BoundedQueue, self.capacity)
        )
        # Detached channel cleanup tasks
        self.receive_cleaners = []
        # Per-channel cleanup locks to prevent a receive starting and moving
        # a message back into the main queue before its cleanup has completed
        self.receive_clean_locks = ChannelLock()
        self.sqs = boto3.client("sqs")
        self._serializer = registry.get_serializer(
            serializer_format,
            # As we use a sorted set to expire messages we need to guarantee uniqueness, with 12 bytes.
            random_prefix_length=random_prefix_length,
            expiry=self.expiry,
            symmetric_encryption_keys=symmetric_encryption_keys,
        )

    def get_queue(self, channel_name):
        """
        Gets an SQS queue by name.

        :param name: The name that was used to create the queue.
        :return: A Queue object.
        """
        try:
            queue = self.sqs.get_queue_by_name(QueueName=name)
            logger.info("Got queue '%s' with URL=%s", name, queue.url)
        except ClientError as error:
            logger.exception("Couldn't get queue named %s.", name)
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

    async def group_add(self, group, channel):
        #todo

    async def group_discard(self, group, channel):
        #todo

    async def group_send(self, group, message):
        participations = ChatParticipation.objects.filter(chat_id=group)
        for participation in participations:
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



