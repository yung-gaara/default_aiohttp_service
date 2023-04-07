from aiohttp import web

from server.middleware import Middleware
from server.routes import setup_routes
from server.rpc_client import init_rabbitmq_client
from share import config


def init():
    app = web.Application(client_max_size=config.MAX_FILE_SIZE, middlewares=Middleware().get_middlewares())

    app.on_startup.append(init_rabbitmq_client)
    setup_routes(app)

    return app


def start():
    app = init()
    web.run_app(app, host=config.SERVER_HOST, port=config.SERVER_PORT)
