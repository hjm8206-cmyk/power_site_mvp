from __future__ import annotations

import re
import time
from typing import Any, Dict

from . import vworld


_PATCHED = False
_ORIGINAL_QUERY = None

_RETRY_MARKERS = (
    "RemoteDisconnected",
    "Connection aborted",
    "Connection reset",
    "Read timed out",
    "502",
    "503",
    "504",
    "Bad Gateway",
    "Service Unavailable",
    "Gateway Timeout",
)


def patch() -> None:
    global _PATCHED, _ORIGINAL_QUERY
    if _PATCHED:
        return

    _ORIGINAL_QUERY = vworld.query_vworld_data_layer
    vworld.query_vworld_data_layer = query_vworld_data_layer_with_retry
    _PATCHED = True


def query_vworld_data_layer_with_retry(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    attempts = 4
    last_result: Dict[str, Any] = {}

    for attempt in range(attempts):
        result = _call_original_query_with_close_header(*args, **kwargs)
        result = _sanitize_result(result)
        last_result = result

        if result.get("features"):
            return result
        if not _is_retryable_failure(result):
            return result
        if attempt < attempts - 1:
            time.sleep(0.25 * (attempt + 1))

    if last_result:
        message = last_result.get("message") or "VWorld data API request failed"
        last_result["message"] = _sanitize_message(f"VWorld data API retry failed: {message}")
    return last_result


def _call_original_query_with_close_header(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    original_get = vworld.requests.get

    def get_with_headers(url: str, **request_kwargs: Any) -> Any:
        headers = dict(request_kwargs.pop("headers", {}) or {})
        headers.setdefault("Accept", "application/json")
        headers.setdefault("Connection", "close")
        headers.setdefault("User-Agent", "PowerSiteScoutOS/1.0")
        return original_get(url, headers=headers, **request_kwargs)

    vworld.requests.get = get_with_headers
    try:
        return _ORIGINAL_QUERY(*args, **kwargs)
    finally:
        vworld.requests.get = original_get


def _is_retryable_failure(result: Dict[str, Any]) -> bool:
    if result.get("ok") or result.get("features"):
        return False
    message = str(result.get("message") or "")
    return any(marker in message for marker in _RETRY_MARKERS)


def _sanitize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(result, dict):
        return result
    clean = dict(result)
    if "message" in clean:
        clean["message"] = _sanitize_message(clean.get("message"))
    if isinstance(clean.get("query"), dict):
        query = dict(clean["query"])
        if "message" in query:
            query["message"] = _sanitize_message(query.get("message"))
        clean["query"] = query
    return clean


def _sanitize_message(message: Any) -> str:
    value = str(message or "")
    value = re.sub(r"([?&]key=)[^&\s]+", r"\1***", value)
    value = re.sub(r"(key=)[^&\s]+", r"\1***", value)
    return value
