import asyncio
import logging
import time
import types
from abc import ABCMeta
from functools import wraps
from logging import Logger
from typing import Any, AsyncContextManager, ContextManager

_LOGGER = logging.getLogger(__name__)


def is_async_callable(f: Any):
    if not callable(f):
        return False
    if isinstance(f, types.FunctionType):
        return asyncio.iscoroutinefunction(f)
    if hasattr(f, '__call__'):  # noqa: B004 I want to check __call__ attribute, not to test if f is callable
        return asyncio.iscoroutinefunction(f.__call__)


class AbstractTimeMeasurer(metaclass=ABCMeta):  # noqa B024: this is an abstract class
    def __init__(
            self,
            message: str, *,
            inline_time: bool = False,
            logger: Logger = _LOGGER,
            warning_threshold: float = None,
            extra: dict[str, Any] = None
    ):
        self._message = message
        self._inline_time = inline_time
        self._logger = logger
        self._warning_threshold = warning_threshold
        self._extra = {} if extra is None else dict(extra)

        self._start = None

    def _log(self):
        end = time.time()

        diff = (end - self._start) * 1000
        extra = {
            "time (ms)": diff,
            "start": time.strftime("%X %Z", time.gmtime(self._start)),
            "end": time.strftime("%X %Z", time.gmtime(end)),
            **self._extra
        }
        if self._inline_time:
            message = f"{self._message} execution time is {diff:.2f} ms"
        else:
            message = self._message
        if self._warning_threshold is not None and diff > self._warning_threshold:
            self._logger.warning(message, extra=extra)
        else:
            self._logger.debug(message, extra=extra)


class TimeMeasurer(AbstractTimeMeasurer, ContextManager):
    def __enter__(self):
        self._start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._log()


class AsyncTimeMeasurer(AbstractTimeMeasurer, AsyncContextManager):
    async def __aenter__(self):
        self._start = time.time()

    async def __aexit__(self, __exc_type, __exc_value, __traceback):
        self._log()


def log_time(f=None, *, logger: Logger = _LOGGER, title: str = None, warning_threshold: float = None):
    def decorator(f):
        fname = (f.__qualname__ if hasattr(f, '__qualname__') else f.__name__) if title is None else title

        if is_async_callable(f):
            @wraps(f)
            async def wrapper(*args, **kwargs):
                async with AsyncTimeMeasurer(
                        fname, inline_time=True, logger=logger, warning_threshold=warning_threshold,
                        extra={'f_args': args, 'f_kwargs': kwargs}
                ):
                    return await f(*args, **kwargs)
        else:
            @wraps(f)
            def wrapper(*args, **kwargs):
                with TimeMeasurer(
                        fname, inline_time=True, logger=logger, warning_threshold=warning_threshold,
                        extra={'f_args': args, 'f_kwargs': kwargs}
                ):
                    return f(*args, **kwargs)

        return wrapper

    if f is not None:
        return decorator(f)
    return decorator
