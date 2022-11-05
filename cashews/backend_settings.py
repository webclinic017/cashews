from typing import Any, Callable, Dict, Type, Union
from urllib.parse import parse_qsl, urlparse

from .backends.interface import Backend
from .backends.memory import Memory
from .exceptions import BackendNotAvailable

try:
    from .backends.client_side import BcastClientSide
    from .backends.redis import Redis
except ImportError:
    BcastClientSide, Redis = None, None

try:
    import diskcache  # noqa: F401
except ImportError:
    DiskCache = None
else:
    from .backends.diskcache import DiskCache


_NO_REDIS_ERROR = "Redis backend requires `redis` to be installed."
_CUSTOM_ERRORS = {
    "redis": _NO_REDIS_ERROR,
    "rediss": _NO_REDIS_ERROR,
    "diskcache": "Disk backend requires `diskcache` to be installed.",
}
_BACKENDS = {}
BackendOrFabric = Union[Type[Backend], Callable[[Dict[str, Any]], Backend]]


def register_backend(alias: str, backend_class: BackendOrFabric, pass_uri: bool = False):
    _BACKENDS[alias] = (backend_class, pass_uri)


def _redis_fabric(**params: Any) -> Union[Redis, BcastClientSide]:
    if params.pop("client_side", None):
        return BcastClientSide(**params)
    return Redis(**params)


register_backend("mem", Memory)
if Redis:
    register_backend("redis", _redis_fabric, pass_uri=True)
    register_backend("rediss", _redis_fabric, pass_uri=True)
if DiskCache:
    register_backend("disk", DiskCache)


def settings_url_parse(url):
    parse_result = urlparse(url)
    params = dict(parse_qsl(parse_result.query))
    params = _fix_params_types(params)

    alias = parse_result.scheme
    if alias == "":
        return Memory, {"disable": True}

    if alias not in _BACKENDS:
        error = _CUSTOM_ERRORS.get(alias, f"wrong backend alias {alias}")
        raise BackendNotAvailable(error)
    backend_class, pass_uri = _BACKENDS[alias]
    if pass_uri:
        params["address"] = url.split("?")[0]
    return backend_class, params


def _fix_params_types(params: Dict[str, str]) -> Dict[str, Union[str, int, bool, float]]:
    new_params = {}
    bool_keys = ("safe", "enable", "disable", "client_side")
    true_values = (
        "1",
        "true",
    )
    for key, value in params.items():
        if key.lower() in bool_keys:
            value = value.lower() in true_values
        elif value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass
        new_params[key.lower()] = value
    return new_params
