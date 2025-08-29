import functools
import hashlib
import os
import pickle  # nosec
import socket
from collections.abc import Callable
from contextlib import suppress
from typing import Any, TypeVar, cast

import diskcache
import diskcache.core
from diskcache import Lock
from platformdirs import user_cache_dir
from redis import Redis

REDIS_CACHE_ENDPOINT = os.environ.get("CACHE_URL")
REDIS_CLIENT = None

TVar = TypeVar("TVar")
TFun = TypeVar("TFun", bound=Callable[..., Any])

if REDIS_CACHE_ENDPOINT:
    try:
        host, _port = REDIS_CACHE_ENDPOINT.split(":", maxsplit=1)
        port = int(_port)

        # Try to connect to redis endpoint
        socket.create_connection((host, port), timeout=2)

        REDIS_CLIENT = Redis(
            host=host,
            port=port,
            ssl=True,
            username="batch-rw-user",
            password=os.environ.get("CACHE_BATCH_RW_USER_PASSWORD"),
        )
    except (OSError, ValueError):
        REDIS_CLIENT = None

DISK_CACHE = diskcache.Cache(user_cache_dir("fluid-labels", "fluidattacks"))


# 4 weeks
TTL = 604800 * 4


def make_hashable(item: Any) -> str:  # noqa: ANN401
    serialized_object = pickle.dumps(item)

    return hashlib.sha256(serialized_object).hexdigest()


def generate_cache_key(func: Any, args: Any, kwargs: dict[Any, Any]) -> str:  # noqa: ANN401
    key = f"{func.__module__}.{func.__name__}-"
    key += str(make_hashable((args, kwargs)))
    return hashlib.sha256(key.encode()).hexdigest()


def dual_cache(func: TVar) -> TVar:
    _func = cast("Callable[..., Any]", func)

    @functools.wraps(_func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        if os.environ.get("SKIP_FA_LABELS_CACHE_USE"):
            return _func(*args, **kwargs)

        cache_key = generate_cache_key(_func, args, kwargs)

        # Try to recover from disk cache
        if value := DISK_CACHE.get(cache_key):
            return value
        # Try to recover from Redis cache (ElastiCache) if available
        if REDIS_CLIENT:
            cached_result = REDIS_CLIENT.get(cache_key)

            if cached_result:
                result = pickle.loads(  # noqa: S301
                    cached_result,
                )
                with Lock(DISK_CACHE, "dual_cache"):
                    DISK_CACHE.set(
                        cache_key,
                        result,
                        expire=TTL,
                        retry=True,
                    )  # Save to disk with TTL

                return result

        # Run the function and store the result in both caches
        result = _func(*args, **kwargs)
        with suppress(diskcache.core.Timeout), Lock(DISK_CACHE, "dual_cache"):
            DISK_CACHE.set(cache_key, result, expire=TTL, retry=True)  # Save to disk with TTL
        if REDIS_CLIENT:
            REDIS_CLIENT.setex(cache_key, TTL, pickle.dumps(result))  # Save to Redis with TTL
        return result

    return cast("TVar", wrapper)
