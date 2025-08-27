import importlib
from typing import Optional, Tuple

import pytest
from packaging.version import Version


# https://github.com/pydata/xarray/blob/aa4361dafbf69e5872d8870ce73d082ac9400db0/xarray/tests/__init__.py#L49-L61
def _importorskip(modname: str, minversion: Optional[str] = None) -> tuple[bool, pytest.MarkDecorator]:
    """
    Check if a module can be imported and skip the test if it cannot.

    Args:
        modname (str): The name of the module to import.
        minversion (str | None, optional): The minimum version of the module required. Defaults to None.

    Returns:
        tuple[bool, pytest.MarkDecorator]: A tuple containing a boolean indicating whether the module was successfully imported and a pytest.MarkDecorator object to skip the test if the module was not imported.

    Raises:
        ImportError: If the required module cannot be imported or if the minimum version requirement is not satisfied.
    """
    try:
        mod = importlib.import_module(modname)
        has = True
        if minversion is not None:
            if Version(mod.__version__) < Version(minversion):
                raise ImportError("Minimum version not satisfied")
    except ImportError:
        has = False
    func = pytest.mark.skipif(not has, reason=f"requires {modname}")
    return has, func


has_typer, requires_typer = _importorskip("typer")
has_rich, requires_rich = _importorskip("rich")
has_ipytree, requires_ipytree = _importorskip("ipytree")
has_s3fs, requires_s3fs = _importorskip("s3fs")
has_xarray, requires_xarray = _importorskip("xarray")
has_dask, requires_dask = _importorskip("dask")
has_distributed, requires_distributed = _importorskip("distributed")
has_kerchunk, requires_kerchunk = _importorskip("kerchunk")
has_fsspec, requires_fsspec = _importorskip("fsspec")
has_cfgrib, requires_cfgrib = _importorskip("cfgrib")
has_icechunk, requires_icechunk = _importorskip("icechunk")
has_zarr_v3, requires_zarr_v3 = _importorskip("zarr", minversion="3")
