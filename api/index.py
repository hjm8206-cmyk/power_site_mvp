from pathlib import Path
import os
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


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

from power_site_mvp.app.main import app
