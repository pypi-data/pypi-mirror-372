import inspect
from contextvars import ContextVar
from functools import wraps
from typing import Callable, ContextManager, Optional

_LOG_EXTRAS = ContextVar[dict]('_LOG_EXTRAS')


def get_log_extras() -> dict:
    try:
        return _LOG_EXTRAS.get()
    except LookupError:
        return {}


class LogExtrasManager(ContextManager):
    __slots__ = ('_extras', '_token')

    def __init__(self, extras: dict):
        self._extras = extras
        self._token = None

    def __enter__(self) -> None:
        self._token = _LOG_EXTRAS.set(self._extras)

    def __exit__(self, *exc) -> Optional[bool]:
        _LOG_EXTRAS.reset(self._token)
        return super().__exit__(*exc)


def update_log_extras(*, __to_str__: bool = True, **kwargs) -> LogExtrasManager:
    extras = dict(get_log_extras())
    extras.update({k: str(v) if __to_str__ else v for k, v in kwargs.items()})
    return LogExtrasManager(extras)


def with_log_extras(**params):
    """
    params is a mapping from extras key to constant value or to callable (called for function params)
    """

    constant_params = {}
    callable_params = {}

    for key, value in params.items():
        (callable_params if isinstance(value, Callable) else constant_params)[key] = value

    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            signature = inspect.signature(f)
            binding = signature.bind(*args, **kwargs)
            binding.apply_defaults()
            extras = {k: v(binding.arguments) for k, v in callable_params.items()}
            with update_log_extras(**constant_params, **extras):
                return f(*args, **kwargs)

        return wrap

    return decorator
