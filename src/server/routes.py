import os
from pathlib import Path
from typing import Union

import aiohttp_cors
from aiohttp import web
from aiohttp.web_urldispatcher import UrlDispatcher
from aiohttp_swagger3 import RapiDocUiSettings
from aiohttp_swagger3 import ReDocUiSettings
from aiohttp_swagger3 import SwaggerDocs
from aiohttp_swagger3 import SwaggerUiSettings

from server.views.task import TaskHandler
from share import config

VERSION_PATH = config.BASE_PATH / Path("../VERSION")
COMPONENT_PATH = config.BASE_PATH / Path("../server/components.yaml")


def get_version():
    with open(VERSION_PATH) as f:
        return f.read()


def redirect_response(redirect_url: str) -> None:
    """
    Raise an HTTP/302 Redirect exception to given URL

    :param redirect_url: Redirect to this url
    :type redirect_url: str
    :raise: aiohttp.web.HTTPFound
    """
    raise web.HTTPFound(redirect_url)


def add_routes(router: Union[SwaggerDocs, UrlDispatcher]):
    router.add_route("*", r"/api/task", TaskHandler)


def setup_routes(app, is_swagger: bool = True):
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )

    if is_swagger:
        app.router.add_route("GET", "/", lambda x: redirect_response("/swagger"))
        app.router.add_route("POST", "/", lambda x: redirect_response("/swagger"))

        swagger = SwaggerDocs(
            app,
            title=config.SWAGGER_TITLE,
            version=get_version(),
            description=config.SWAGGER_DESCRIPTION,
            swagger_ui_settings=SwaggerUiSettings(path="/swagger"),
            redoc_ui_settings=ReDocUiSettings(path="/redoc"),
            rapidoc_ui_settings=RapiDocUiSettings(path="/rapidoc"),
            components=COMPONENT_PATH,
            validate=False,
        )

        add_routes(swagger)
    else:
        add_routes(app.router)

    for route in list(app.router.routes()):
        cors.add(route, webview=True)
