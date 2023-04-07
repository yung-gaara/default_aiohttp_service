import functools
import pickle

import pika


def worker_error(func):
    @functools.wraps(func)
    def wrapper(self, *args):
        props = args[2]
        properties = pika.BasicProperties(correlation_id=props.correlation_id)
        try:
            return func(self, *args)
        except Exception as e:
            self.logger.exception(e)
            self.publish_message(
                message=pickle.dumps({"error": {"error_code": 1, "message": f"Error from worker: {e}"}, "result": []}),
                props=properties,
            )

    return wrapper
