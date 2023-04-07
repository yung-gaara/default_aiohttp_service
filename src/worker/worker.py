import pickle
import typing as t
from abc import abstractmethod

import pika
from pika.adapters.blocking_connection import BlockingChannel

from share.log import LoggerMixin
from worker.utils import worker_error


class Worker(LoggerMixin):
    def __init__(
        self,
        task_exchange_name: str,
        task_queue_name: str,
        result_queue_name: str,
        result_exchange_name: str,
        rabbit_connection_string: str,
    ):
        self.task_exchange_name = task_exchange_name
        self.task_queue_name = task_queue_name
        self.result_queue_name = result_queue_name
        self.result_exchange_name = result_exchange_name
        self.connection = pika.BlockingConnection(pika.URLParameters(rabbit_connection_string))

        self.channel: BlockingChannel = self.connection.channel()
        self.set_up_qos()

        self.channel.exchange_declare(exchange=self.task_exchange_name, exchange_type="direct")
        self.channel.exchange_declare(exchange=self.result_exchange_name, exchange_type="direct")
        self.channel.queue_declare(queue=self.task_queue_name, durable=True)
        self.channel.queue_declare(queue=self.result_queue_name, durable=True)
        self.channel.queue_bind(
            exchange=self.task_exchange_name, queue=self.task_queue_name, routing_key=self.task_queue_name
        )
        self.channel.queue_bind(
            exchange=self.result_exchange_name, queue=self.result_queue_name, routing_key=self.result_queue_name
        )
        self.channel.basic_consume(on_message_callback=self._on_message, queue=self.task_queue_name)

    def set_up_qos(self):
        self.channel.basic_qos(prefetch_count=1)

    def stop(self):
        self.channel.stop_consuming()
        self.connection.close()

    def start(self):
        self.channel.start_consuming()

    @abstractmethod
    def get_result(self, data: t.Optional[t.Dict] = None):
        raise NotImplementedError

    @worker_error
    def _on_message(self, ch, method, props, body):
        try:
            self.logger.debug(f"[{props.correlation_id}] Start handle...")
            message = pickle.loads(body)
            properties = pika.BasicProperties(correlation_id=props.correlation_id)
            result_data = self.get_result(message.get("data"))
            result = {
                "error": {"error_code": 0, "message": ""},
                "result": result_data,
            }
            self.publish_message(message=pickle.dumps(result), props=properties)
        except Exception as e:
            raise e
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def publish_message(self, message: bytes, props: pika.BasicProperties):
        self.channel.basic_publish(
            exchange=self.result_exchange_name, body=message, routing_key=self.result_queue_name, properties=props
        )
