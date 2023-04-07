import logging
import logging.config
from typing import ClassVar

from share.config import LOGGING_CONFIG


class CustomFilter(logging.Filter):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def filter(self, record):
        for k, v in self.__dict__.items():
            record.__setattr__(k, v)
        return True


class LoggerMixin(object):
    """LoggerMixin

    This mixin class provides class field ``logger`` to derived classes. Name of this ``logger`` is
    'absolute module path of derived class'.'qualified name of derived class'

    Example:

        >>> # In module ``package0.package1.module_example``
        >>> class SomeClassWithLoggerMixin(LoggerMixin):
        ...     pass
        >>>

        In this case logger name of this class is
        ``package0.package1.module_example.SomeClassWithLoggableMixin``
    """

    logger: ClassVar[logging.Logger]

    def __init_subclass__(cls, **kwargs) -> None:
        cls.logger = logging.getLogger(f"{cls.__module__}.{cls.__name__}")


def setup_logging():
    if LOGGING_CONFIG:
        logging.config.dictConfig(LOGGING_CONFIG)

        custom_fields = LOGGING_CONFIG.pop("custom_fields", {})
        if custom_fields:
            logger = logging.getLogger()
            for h in logger.handlers:
                h.addFilter(CustomFilter(**custom_fields))
