import threading
from typing import Any

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from labels.config.cache import dual_cache

_thread_local = threading.local()


def _get_session_with_retry(
    retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: tuple[int, ...] = (500, 502, 503, 504),
    pool_connections: int = 10,
    pool_maxsize: int = 10,
) -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=pool_connections,
        pool_maxsize=pool_maxsize,
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_session() -> requests.Session:
    if not hasattr(_thread_local, "session"):
        _thread_local.session = _get_session_with_retry()
    return _thread_local.session


@dual_cache
def make_get(url: str, *, content: bool = False, **kwargs: Any) -> Any | None:  # noqa: ANN401
    timeout = float(kwargs.pop("timeout", 30))
    response: Response = get_session().get(url, timeout=timeout, **kwargs)

    try:
        if response.status_code != 200:
            return None

        if content:
            return response.content.decode("utf-8")

        return response.json()
    except ValueError:
        return None
    finally:
        response.close()
