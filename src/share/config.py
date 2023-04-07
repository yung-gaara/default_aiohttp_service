import json
import os
import typing
from dataclasses import dataclass
from pathlib import Path

BASE_PATH = Path(__file__).parent


# Logging config
LOGGING_CONFIG = ""
LOGGING_PATH = Path(os.getenv("LOGGING_PATH", BASE_PATH / Path("logging.json")))
if LOGGING_PATH.exists():
    LOGGING_CONFIG = json.load(LOGGING_PATH.open())


# rabbit configs
@dataclass
class RabbitConfig:
    host: str = os.environ.get("RABBIT_HOST", "rabbitmq")
    port: int = int(os.environ.get("RABBIT_PORT", 5672))
    user: str = os.environ.get("RABBITMQ_DEFAULT_USER", "user")
    password: str = os.environ.get("RABBITMQ_DEFAULT_PASS", "password")
    heartbeat: int = int(os.environ.get("RABBITMQ_HEARTBEAT", 0))

    def get_connection_string(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/?heartbeat={self.heartbeat}"


RABBIT_CONFIG = RabbitConfig()


@dataclass
class RabbitQueueConfig:
    rabbit_connection_string: str = RABBIT_CONFIG.get_connection_string()
    task_exchange_name: str = os.environ.get("RABBIT_EXCHANGE_TO_TASK", "task_exchange_name")
    task_queue_name: str = os.environ.get("RABBIT_QUEUE_TO_TASK", "task_queue_name")
    result_exchange_name: str = os.environ.get("RABBIT_EXCHANGE_TO_RESULT", "result_exchange_name")
    result_queue_name: str = os.environ.get("RABBIT_QUEUE_TO_RESULT", "result_queue_name")


TIMEOUT_RPC_CLIENT: typing.Optional[float] = None
if "TIMEOUT_RPC_CLIENT" in os.environ:
    TIMEOUT_RPC_CLIENT = float(os.environ["TIMEOUT_RPC_CLIENT"])

RABBIT_QUEUE_CONFIG = RabbitQueueConfig()

RPC_CLIENT_CONFIG = {
    "task_exchange_name": RABBIT_QUEUE_CONFIG.task_exchange_name,
    "task_queue_name": RABBIT_QUEUE_CONFIG.task_queue_name,
    "result_exchange_name": RABBIT_QUEUE_CONFIG.result_exchange_name,
    "result_queue_name": RABBIT_QUEUE_CONFIG.result_queue_name,
    "rabbit_connection_str": RABBIT_QUEUE_CONFIG.rabbit_connection_string,
    "timeout_rpc_client": TIMEOUT_RPC_CLIENT,
}


SERVER_HOST = "0.0.0.0"
SERVER_PORT = int(os.environ.get("SERVER_PORT", 3243))

MAX_FILE_SIZE = 50 * 1024 * 1024
CHECK_PATH_TO_AUTHORIZE: typing.List[str] = ["/api"]
CHECK_PATH_TO_COUNT_TIME: typing.List[str] = ["/api"]

TOKEN = os.environ.get("TOKEN")
if TOKEN is None:
    raise ValueError("Please set token before start")


# Swagger configs
SWAGGER_TITLE = os.environ.get("SWAGGER_TITLE", "Test server")
SWAGGER_DESCRIPTION = os.environ.get("SWAGGER_DESCRIPTION", "Test")
if SWAGGER_DESCRIPTION:
    SWAGGER_DESCRIPTION = SWAGGER_DESCRIPTION.replace(r"\n", "\n").replace(r"\t", "\t")
