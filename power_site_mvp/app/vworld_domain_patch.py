from __future__ import annotations

import os
from typing import Callable

from . import vworld


DEPLOYED_VWORLD_DOMAIN = "https://power-site-mvp-72ay.vercel.app"
_PATCHED = False
_ORIGINAL_SERVICE_DOMAIN: Callable[[], str] | None = None


def patch() -> None:
    global _PATCHED, _ORIGINAL_SERVICE_DOMAIN
    if _PATCHED:
        return
    _ORIGINAL_SERVICE_DOMAIN = vworld.service_domain
    vworld.service_domain = service_domain
    _PATCHED = True


def service_domain() -> str:
    """Return the VWorld service URL registered for production."""
    if _running_on_vercel():
        public_url = os.getenv("APP_PUBLIC_URL", "").strip()
        return _with_https_scheme(public_url or DEPLOYED_VWORLD_DOMAIN)

    explicit = os.getenv("VWORLD_DOMAIN", "").strip()
    if explicit:
        return _with_https_scheme(explicit)
    return vworld.DEFAULT_DOMAIN


def _running_on_vercel() -> bool:
    return bool(os.getenv("VERCEL", "").strip() or os.getenv("VERCEL_URL", "").strip())


def _with_https_scheme(url: str) -> str:
    value = str(url or "").strip().rstrip("/")
    if not value:
        return value
    if value.startswith(("http://", "https://")):
        return value
    return f"https://{value}"
