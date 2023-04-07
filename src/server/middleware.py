import time
import uuid
from functools import partial
from typing import List

from aiohttp import web
from aiohttp.web import middleware
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from share import config
from share.log import LoggerMixin


def check_path(path: str, check_list: List[str]):
    result = False
    for r in check_list:
        if path.startswith(r):
            result = True
    return result


class Middleware(LoggerMixin):
    @middleware
    async def set_uid(self, request: Request, handler: partial):
        message_uid = str(uuid.uuid4())
        request["uid"] = message_uid
        return await handler(request)

    @middleware
    async def authorize(self, request: Request, handler: partial):
        if check_path(request.path, config.CHECK_PATH_TO_AUTHORIZE) and request.method != "OPTIONS":
            token = request.headers.get("Authorization")
            if token:
                if token == config.TOKEN:
                    return await handler(request)
                else:
                    return web.Response(text="Unauthorized", status=401)
            else:
                return web.Response(text="Need Authorization token", status=403)
        return await handler(request)

    @middleware
    async def time_count(self, request: Request, handler: partial):
        if check_path(request.path, config.CHECK_PATH_TO_COUNT_TIME):
            message_uid = request.get("uid")
            time_start = time.time()
            self.logger.debug(f"[{message_uid}] Start handle: {request.method} {request.path}.")
            response: Response = await handler(request)
            self.logger.info(
                f"[{message_uid}] Stop handle: {request.method} {request.path}. "
                f"Estimate time: {time.time() - time_start}"
            )
            return response
        return await handler(request)

    def get_middlewares(self, use_auth: bool = True):
        middlewares = [self.set_uid]

        if config.CHECK_PATH_TO_COUNT_TIME:
            middlewares.append(self.time_count)

        if config.CHECK_PATH_TO_AUTHORIZE and use_auth:
            middlewares.append(self.authorize)

        return middlewares
