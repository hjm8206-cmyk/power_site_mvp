"""PowerSite MVP application package."""

try:
    from . import vworld_domain_patch as _vworld_domain_patch

    _vworld_domain_patch.patch()

    from . import parcel_resolver as _parcel_resolver

    _parcel_resolver.patch()
except Exception:
    # The resolver is a runtime safety net for cadastral lookup. Import-time
    # failures must never prevent the API app from booting.
    pass
