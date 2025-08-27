import importlib.metadata

from arraylake.client import AsyncClient, Client
from arraylake.config import config
from arraylake.repos.v1 import repo

__version__ = importlib.metadata.version("arraylake")


def _warn_on_zarr_version():
    import warnings

    import zarr
    from packaging.version import Version

    if Version(zarr.__version__) < Version("3.0.0.a0"):
        import zarr._storage.store

        zarr._storage.store.v3_api_available = True
        warnings.filterwarnings(action="ignore", category=FutureWarning, message=r"The experimental Zarr V3 implementation .*")


_warn_on_zarr_version()

__all__ = ["__version__", "AsyncClient", "Client", "config", "repo"]
