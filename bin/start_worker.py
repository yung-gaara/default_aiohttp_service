import share.config as config
from share.log import setup_logging
from worker.worker import Worker

setup_logging()


worker = Worker(
    config.RABBIT_QUEUE_CONFIG.task_exchange_name,
    config.RABBIT_QUEUE_CONFIG.task_queue_name,
    config.RABBIT_QUEUE_CONFIG.result_queue_name,
    config.RABBIT_QUEUE_CONFIG.result_exchange_name,
    config.RABBIT_QUEUE_CONFIG.rabbit_connection_string,
)
worker.start()
