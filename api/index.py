from pathlib import Path
import os
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

DEPLOYED_VWORLD_DOMAIN = "https://power-site-mvp-72ay.vercel.app"


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


def _request_origin(request) -> str:
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    if not host:
        return ""
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme or "https"
    return _with_https_scheme(f"{proto}://{host}")


def _runtime_vworld_domain(origin: str = "") -> str:
    current = os.getenv("VWORLD_DOMAIN", "").strip()
    if current and not _is_local_domain(current):
        return _with_https_scheme(current)

    if os.getenv("VERCEL", "").strip():
        return _with_https_scheme(os.getenv("APP_PUBLIC_URL") or DEPLOYED_VWORLD_DOMAIN)

    public_domain = os.getenv("APP_PUBLIC_URL") or os.getenv("VERCEL_PROJECT_PRODUCTION_URL") or os.getenv("VERCEL_URL")
    if public_domain:
        return _with_https_scheme(public_domain)

    if origin and not _is_local_domain(origin):
        return _with_https_scheme(origin)

    return _with_https_scheme(
        current
        or ""
    )


runtime_vworld_domain = _runtime_vworld_domain()
if runtime_vworld_domain:
    os.environ["VWORLD_DOMAIN"] = runtime_vworld_domain

from power_site_mvp.app.main import app


@app.middleware("http")
async def bind_vworld_domain_to_request_host(request, call_next):
    # VWorld validates each data request against the registered service URL.
    # On Vercel, always use the registered production service URL instead of
    # any stale localhost value that may remain in environment variables.
    runtime_domain = _runtime_vworld_domain(_request_origin(request))
    if runtime_domain and (
        os.getenv("VERCEL", "").strip()
        or _is_local_domain(os.getenv("VWORLD_DOMAIN", ""))
        or not os.getenv("VWORLD_DOMAIN", "").strip()
    ):
        os.environ["VWORLD_DOMAIN"] = runtime_domain
    return await call_next(request)
