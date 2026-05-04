from __future__ import annotations

import os


def _with_https_scheme(url: str) -> str:
    value = str(url or "").strip().rstrip("/")
    if not value:
        return value
    if value.startswith(("http://", "https://")):
        return value
    return f"https://{value}"


def _is_local_domain(url: str) -> bool:
    value = str(url or "").strip().lower()
    return "localhost" in value or "127.0.0.1" in value or value.startswith("http://0.0.0.0")


vercel_domain = os.getenv("APP_PUBLIC_URL") or os.getenv("VERCEL_PROJECT_PRODUCTION_URL") or os.getenv("VERCEL_URL")
if vercel_domain and (not os.getenv("VWORLD_DOMAIN") or _is_local_domain(os.getenv("VWORLD_DOMAIN", ""))):
    os.environ["VWORLD_DOMAIN"] = _with_https_scheme(vercel_domain)

from app.main import app


@app.middleware("http")
async def bind_vworld_domain_to_request_host(request, call_next):
    if os.getenv("VERCEL") and not os.getenv("APP_PUBLIC_URL"):
        host = request.headers.get("x-forwarded-host") or request.headers.get("host")
        if host:
            proto = request.headers.get("x-forwarded-proto") or request.url.scheme or "https"
            os.environ["VWORLD_DOMAIN"] = _with_https_scheme(f"{proto}://{host}")
    return await call_next(request)
