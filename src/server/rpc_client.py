import asyncio
import pickle

from aio_pika import DeliveryMode
from aio_pika import ExchangeType
from aio_pika import IncomingMessage
from aio_pika import Message
from aio_pika import connect
from aiohttp import web

from share.config import RPC_CLIENT_CONFIG


async def init_rabbitmq_client(app: web.Application):
    app["rabbitmq"] = await RpcClient(
        task_exchange_name=RPC_CLIENT_CONFIG["task_exchange_name"],
        result_exchange_name=RPC_CLIENT_CONFIG["result_exchange_name"],
        task_queue_name=RPC_CLIENT_CONFIG["task_queue_name"],
        result_queue_name=RPC_CLIENT_CONFIG["result_queue_name"],
        rabbit_connection_str=RPC_CLIENT_CONFIG["rabbit_connection_str"],
        timeout_rpc_client=RPC_CLIENT_CONFIG["timeout_rpc_client"],
    ).connect()


class RpcClient:
    def __init__(
        self,
        task_exchange_name,
        result_exchange_name,
        task_queue_name,
        result_queue_name,
        rabbit_connection_str,
        timeout_rpc_client,
    ):
        self.task_exchange_name = task_exchange_name
        self.result_exchange_name = result_exchange_name
        self.task_queue_name = task_queue_name
        self.result_queue_name = result_queue_name
        self.timeout_rpc_client = timeout_rpc_client

        self.task_exchange = None
        self.result_exchange = None
        self.result_queue = None

        self.connection = None
        self.channel = None
        self.futures = {}
        self.loop = asyncio.get_event_loop()
        self.connection_str = rabbit_connection_str

    async def connect(self):
        self.connection = await connect(self.connection_str, loop=self.loop)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)

        self.task_exchange = await self.channel.declare_exchange(self.task_exchange_name, ExchangeType.DIRECT)
        self.result_exchange = await self.channel.declare_exchange(self.result_exchange_name, ExchangeType.DIRECT)
        self.result_queue = await self.channel.declare_queue(self.result_queue_name, durable=True)

        await self.result_queue.bind(self.result_exchange_name, routing_key=self.result_queue_name)
        await self.result_queue.consume(self.on_response)
        task_queue = await self.channel.declare_queue(self.task_queue_name, durable=True)
        await task_queue.bind(self.task_exchange_name, routing_key=self.task_queue_name)
        return self

    def on_response(self, message: IncomingMessage):
        future = self.futures.pop(str(message.correlation_id), None)
        if future and not future.cancelled():
            future.set_result(message.body)
        message.ack()

    async def send_message(self, message, correlation_id: str):
        future = self.loop.create_future()
        self.futures[correlation_id] = future
        if self.channel.is_closed:
            await self.connect()
        try:
            await self.task_exchange.publish(
                Message(
                    pickle.dumps(message),
                    content_type="text/plain",
                    correlation_id=correlation_id,
                    delivery_mode=DeliveryMode.PERSISTENT,
                    reply_to=self.result_queue_name,
                ),
                routing_key=self.task_queue_name,
            )
            result = await asyncio.wait_for(future, timeout=self.timeout_rpc_client)
        except TimeoutError as e:
            future = self.futures.pop(str(correlation_id), None)
            if future and not future.cancelled():
                future.cancel()
            raise e
        return result
