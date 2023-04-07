import functools
import typing as t
from collections import Callable

from aiohttp import web


def validate_data(data: t.Dict) -> None:
    if len(data) == 0:
        raise ValueError("Empty data")


def internal_error(func: Callable):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except Exception as e:
            self.logger.exception(str(e))
            return web.HTTPInternalServerError()

    return wrapper
