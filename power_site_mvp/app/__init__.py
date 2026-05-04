"""PowerSite MVP application package."""

try:
    from . import vworld_domain_patch as _vworld_domain_patch

    _vworld_domain_patch.patch()

    from . import parcel_resolver as _parcel_resolver

    _parcel_resolver.patch()
except Exception:
    # Runtime safety patches must never prevent the API app from booting.
    pass
