def _raise_if_zarr_v3():
    import zarr
    from packaging.version import Version

    if Version(zarr.__version__) > Version("3.0.0.a0"):
        raise ImportError("Legacy Arraylake Repos are not supported by zarr-python 3.0 at this time!")
