from datetime import timedelta
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Tuple, TypeVar, Union

try:
    from typing import Protocol
except ImportError:  # 3.7 python
    from typing_extensions import Protocol

_TTLTypes = Union[int, float, str, timedelta, None]
TTL = Union[_TTLTypes, Callable[[Any], _TTLTypes]]


class CallableCacheCondition(Protocol):
    def __call__(self, result: Any, args: Tuple, kwargs: Dict[str, Any], key: str = "") -> bool:
        ...


CacheCondition = Union[CallableCacheCondition, str, None]

AsyncCallableResult_T = TypeVar("AsyncCallableResult_T")
Callable_T = TypeVar("Callable_T", bound=Callable)
AsyncCallable_T = Callable[..., Awaitable[AsyncCallableResult_T]]
Decorator = Callable[..., AsyncCallable_T]

if TYPE_CHECKING:
    from . import Command
    from .backends.interface import Backend


class Middleware(Protocol):
    def __call__(
        self,
        call: AsyncCallable_T,
        cmd: "Command",
        backend: "Backend",
        *args,
        **kwargs,
    ) -> Awaitable[AsyncCallableResult_T]:
        ...
