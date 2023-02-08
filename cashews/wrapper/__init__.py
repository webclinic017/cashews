from cashews.backends.interface import _BackendInterface
from cashews.decorators import context_cache_detect

from .backend_settings import register_backend  # noqa
from .commands import CommandWrapper
from .decorators import DecoratorsWrapper
from .disable_control import ControlWrapper
from .transaction import TransactionWrapper

__all__ = ["Cache", "register_backend"]


class Cache(
    TransactionWrapper,
    ControlWrapper,
    CommandWrapper,
    DecoratorsWrapper,
    _BackendInterface,
):
    detect = context_cache_detect
