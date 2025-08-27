import json
import os
import sys
import warnings
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import numpy as np
import pytest
from numcodecs import BZ2, LZMA, Blosc, Delta, GZip, PackBits, Zlib
from numpy.random import default_rng
from packaging.version import Version
from structlog.testing import capture_logs

from arraylake.config import config
from arraylake.repos.v1.chunkstore import mk_chunkstore_from_uri
from arraylake.repos.v1.chunkstore.fsspec_compat import FSConfig
from arraylake.repos.v1.virtual import (
    make_v3_store,
    reformat_kerchunk_refs,
    scan_zarr_v2,
)

rng = default_rng(seed=42)

xr = pytest.importorskip("xarray")

from .. import requires_cfgrib, requires_fsspec, requires_kerchunk, requires_s3fs


@dataclass(frozen=True)
class Uploader:
    fs_config: FSConfig
    bucket: str

    def upload_file(self, local_path, remote_path):
        self.fs_config.fs.put(local_path, f"{self.bucket}/{remote_path}")
        url = f"{self.fs_config.protocol}://{self.bucket}/{remote_path}"
        return url


@pytest.fixture(scope="module")
def external_bucket_for_virtual_files(object_store_platform):
    # must match configuration of buckets setup up in compose.yaml
    if object_store_platform == "s3":
        return "externalbucket"
    elif object_store_platform == "gs":
        return "externalgcsbucket"
    else:
        assert False, f"Unknown object store platform: {object_store_platform}"


@pytest.fixture(scope="module")
def uploader_for_virtual_files(all_object_store_url_and_kwargs, external_bucket_for_virtual_files) -> Uploader:
    object_store_type, url, chunkstore_kws = all_object_store_url_and_kwargs
    # Why are we making a chunkstore here?
    # Because the object storage config is attached to the chunkstore.
    # Otherwise we would have to recreate all of the logic for parsing and validating the object storage config
    # in order to run these tests.
    chunkstore = mk_chunkstore_from_uri(url, object_store=object_store_type, inline_threshold_bytes=0, **chunkstore_kws)
    fs_config = chunkstore._get_fs_config()
    return Uploader(fs_config=fs_config, bucket=external_bucket_for_virtual_files)


@pytest.fixture(scope="module")
def ds():
    shape = (10, 20, 30)
    da = xr.DataArray(
        data=rng.random(shape), dims=["time", "y", "x"], coords={"time": np.arange(shape[0])}, name="foo", attrs={"bar": "baz"}
    )
    return da.to_dataset()


@pytest.fixture(scope="module")
def raster_da():
    import rioxarray

    shape = (3, 1024, 512)
    da = xr.DataArray(
        data=rng.integers(low=1, high=256, size=shape),
        dims=["band", "y", "x"],
        name="foo",
    )
    return da.rio.write_crs("epsg:4326", inplace=True)


@pytest.fixture(scope="module")
def ds_all_types():
    shape = (10, 20, 30)

    times = xr.date_range("2000-01-01", periods=shape[0])
    coords = {
        "time": times,
        "time_str": times.strftime("%Y-%m-%d"),
        "time_bounds": xr.DataArray(np.stack((times, times.shift(1)), axis=1), dims=("time", "bounds")),
        "x": np.linspace(0, 10, shape[2]),
        "y": np.linspace(20, 30, shape[1]),
        "z": 3.4,
    }

    ds = xr.Dataset(
        coords=coords,
        attrs={
            "title": "ds_all_types",
            "int_attr": 1,
            "float_attr": 2.5,
            "bool_attr": True,
            "mixed_type_list_attr": [1, 1.5, "foo", True, None],
            "dict_attr": {"foo": "bar", "int": 5},
        },
    )

    ds["scalar_var"] = xr.DataArray(4.3, attrs={"description": "scalar_var"})
    ds["str_var"] = xr.DataArray(["a", "b", "c", "d", "e", "f", "g", "h", "i", ""], dims=("time",), attrs={"description": "str_var"})
    ds["bool_var"] = xr.DataArray(rng.integers(0, 2, size=shape, dtype=bool), dims=["time", "y", "x"], attrs={"description": "bool_var"})
    ds["uint8_var"] = xr.DataArray(
        rng.integers(0, 16, size=shape, dtype=np.uint8), dims=["time", "y", "x"], attrs={"description": "uint8_var"}
    )
    ds["int16_var"] = xr.DataArray(
        rng.integers(0, 100, size=shape, dtype=np.int16), dims=["time", "y", "x"], attrs={"description": "int16_var"}
    )
    ds["float32_var"] = xr.DataArray(rng.random(shape, dtype=np.float32), dims=["time", "y", "x"], attrs={"description": "float32_var"})
    ds["float64_var"] = xr.DataArray(rng.random(shape, dtype=np.float64), dims=["time", "y", "x"], attrs={"description": "float64_var"})
    ds["float64_var_with_nan"] = ds["float64_var"].where(ds["float64_var"] > 0.5)
    ds["float64_var_with_nan"].attrs["description"] = "float64_var"

    return ds


@pytest.fixture(scope="module", params=["hdf5", "netcdf3"])
def file_options(ds, request):
    if request.param == "hdf5":
        chunksizes = (1, 10, 30)
        # setting fletcher32=True causes decompression to fail
        encoding = {
            v: {"zlib": True, "shuffle": True, "complevel": 2, "fletcher32": False, "contiguous": False, "chunksizes": chunksizes}
            for v in ds
        }
        engine = "netcdf4"
        extra_kwargs = {"error": "warn"}
    elif request.param == "netcdf3":
        encoding = {}
        engine = "scipy"
        extra_kwargs = {"max_chunk_size": 10}

    return {"file_type": request.param, "engine": engine, "encoding": encoding, "extra_kwargs": extra_kwargs}


@pytest.fixture(scope="module")
def netcdf_file_on_object_storage(tmp_path_factory, ds, file_options, uploader_for_virtual_files, helpers) -> str:
    base_dir = tmp_path_factory.mktemp("hdf_data")
    engine = file_options["engine"]
    fname = f"test-{helpers.an_id(5)}-{engine}.nc"
    full_path = base_dir / fname
    ds.to_netcdf(full_path, engine=file_options["engine"], encoding=file_options["encoding"])

    url = uploader_for_virtual_files.upload_file(str(base_dir / fname), fname)
    return url


@requires_kerchunk
@pytest.fixture(scope="module")
def kerchunk_refs(uploader_for_virtual_files, netcdf_file_on_object_storage, file_options) -> dict[str, Any]:
    storage_options = uploader_for_virtual_files.fs_config.constructor_kwargs

    if file_options["file_type"] == "hdf5":
        from kerchunk.hdf import SingleHdf5ToZarr

        refs = SingleHdf5ToZarr(netcdf_file_on_object_storage, storage_options=storage_options).translate()
    elif file_options["file_type"] == "netcdf3":
        from kerchunk.netCDF3 import NetCDF3ToZarr

        refs = NetCDF3ToZarr(netcdf_file_on_object_storage, storage_options=storage_options).translate()
    else:
        raise ValueError(f"Unknown file type {file_options['file_type']}")

    return refs


@requires_kerchunk
@requires_fsspec
@pytest.fixture(scope="module")
def kerchunk_refs_on_object_storage(kerchunk_refs, tmp_path_factory, uploader_for_virtual_files, helpers):
    fname = f"test-{helpers.an_id(5)}-kerchunk.json"
    base_dir = tmp_path_factory.mktemp("kerchunk_refs")
    full_path = base_dir / fname
    with open(full_path, "wb") as f:
        f.write(json.dumps(kerchunk_refs).encode())
    url = uploader_for_virtual_files.upload_file(str(base_dir / fname), fname)
    return url


@pytest.fixture(
    scope="module",
    params=[
        {"driver": "GTiff", "compress": None, "blockxsize": 256, "blockysize": 256},
        {"driver": "GTiff", "compress": "LZMA", "blockxsize": 256, "blockysize": 256},
        {"driver": "GTiff", "blockxsize": 256, "blockysize": 256},
    ],
)
def gtiff_on_object_storage(request, tmp_path_factory, raster_da, uploader_for_virtual_files, helpers) -> str:
    base_dir = tmp_path_factory.mktemp("tiff_data")
    fname = f"{helpers.an_id(5)}-test.tiff"
    full_path = base_dir / fname

    with warnings.catch_warnings():
        from rasterio.errors import NotGeoreferencedWarning

        warnings.simplefilter("ignore", NotGeoreferencedWarning)
        raster_da.rio.to_raster(full_path, **request.param)

    url = uploader_for_virtual_files.upload_file(str(base_dir / fname), fname)
    return url


@pytest.fixture(
    scope="module",
    params=[
        {"driver": "COG", "compress": "LZMA", "tiled": True, "windowed": True, "blockxsize": 256, "blockysize": 256},
        {"driver": "COG", "compress": "LZMA", "tiled": True, "windowed": False, "blockxsize": 256, "blockysize": 256},
    ],
)
def cog_on_object_storage(request, tmp_path_factory, raster_da, uploader_for_virtual_files, helpers) -> str:
    base_dir = tmp_path_factory.mktemp("tiff_data")
    fname = f"{helpers.an_id(5)}-test.tiff"
    full_path = base_dir / fname

    with warnings.catch_warnings():
        from rasterio.errors import NotGeoreferencedWarning

        warnings.simplefilter("ignore", NotGeoreferencedWarning)
        raster_da.rio.to_raster(full_path, **request.param)

    url = uploader_for_virtual_files.upload_file(str(base_dir / fname), fname)
    return url


@pytest.fixture(scope="module", params=["default", "manual"])
def zarr_v2_encoding(request) -> dict:
    if request.param == "default":
        return None
    else:
        encoding = {
            "x": {"filters": [Delta(dtype="f8")]},
            "y": {"filters": [Delta(dtype="f8")], "compressor": Blosc()},
            "time": {"compressor": Blosc()},
            "scalar_var": {},
            "str_var": {"compressor": LZMA(preset=1)},
            "bool_var": {"filters": [PackBits()], "compressor": GZip()},
            "uint8_var": {"compressor": Zlib(level=2), "chunks": (10, 10, 10)},
            "int16_var": {"compressor": Zlib(level=2)},
            "float32_var": {"compressor": Blosc(cname="zstd", clevel=3, shuffle=2)},
            "float64_var": {"compressor": BZ2(level=2)},
            "float64_var_with_nan": {"compressor": Zlib(level=2)},
        }
        return encoding


@pytest.fixture(scope="module")
def grib_on_object_storage(tmp_path_factory, ds_all_types, uploader_for_virtual_files, helpers):
    cfgrib = pytest.importorskip("cfgrib")
    from cfgrib.xarray_to_grib import to_grib

    if Version(xr.__version__) > Version("2024.9.0") and Version(cfgrib.__version__) < Version("0.9.14.1"):
        # https://github.com/ecmwf/cfgrib/issues/400
        pytest.xfail(reason="cfgrib < 0.9.14.1 does not support xr > 2024.9.0")

    base_dir = tmp_path_factory.mktemp("grib_data")
    fname = f"{helpers.an_id(5)}-test.grib"

    ds_grib = ds_all_types[["float64_var_with_nan"]].rename({"x": "longitude", "y": "latitude", "float64_var_with_nan": "t"}).drop_vars("z")
    del ds_grib.attrs["dict_attr"]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        to_grib(ds_grib, base_dir / fname)

    url = uploader_for_virtual_files.upload_file(str(base_dir / fname), fname)
    return url


@pytest.fixture(scope="module")
def zarr_v2_on_object_storage(ds_all_types, zarr_v2_encoding, uploader_for_virtual_files, helpers) -> str:
    fs_config = uploader_for_virtual_files.fs_config

    url = f"{fs_config.protocol}://{uploader_for_virtual_files.bucket}/{helpers.an_id(5)}-test.zarr"
    mapper = fs_config.fs.get_mapper(url)
    mapper.clear()
    ds_all_types.to_zarr(mapper, encoding=zarr_v2_encoding)
    return url


@requires_s3fs
@pytest.mark.skipif(sys.version_info.major == 3 and sys.version_info.minor == 10, reason="kerchunk 0.2.8 is needed, but is 3.11+")
@pytest.mark.parametrize(
    "write_group,new_path,open_group",
    [
        [None, None, None],
        [None, "foo", "foo"],
        ["", "foo", "foo"],
        ["/", "foo", "foo"],
        ["bar", "/", "bar"],
        ["bar", "foo", "foo/bar"],
        ["/bar", "foo", "foo/bar"],
        ["/bar", "foo/", "foo/bar"],
        ["/bar", "foo/", "/foo/bar"],
        ["/bar", "foo/", "/foo/bar/"],
        ["bar/spam", "foo", "foo/bar/spam"],
        [None, "a/b/c/foo", "a/b/c/foo"],
    ],
)
def test_make_v3_store_memory_store(ds, write_group, new_path, open_group):
    v2_store = {}
    ds.to_zarr(v2_store, zarr_version=2, group=write_group)
    v3_store = make_v3_store(v2_store, new_path=new_path)

    assert all("//" not in k for k in v3_store)
    assert all("\\" not in k for k in v3_store)

    ds_v3 = xr.open_zarr(v3_store, zarr_version=3, group=open_group)
    xr.testing.assert_identical(ds, ds_v3)


def test_make_v3_store_refs():
    v2_refs = {
        ".zgroup": {"version": 2},
        ".zattrs": {"title": "root-group"},
        "foo/.zgroup": {"version": 2},
        "foo/.zattrs": {"title": "foo-group"},
        "foo/bar/.zarray": {"shape": (100,), "chunks": (10,), "dtype": "f8", "compressor": None, "order": "C", "fill_value": -9999},
        "foo/bar/.zattrs": {},
        "foo/bar/0": ["s3://bar.nc", 0, 123],
        "spam/.zarray": {"shape": (100, 100), "chunks": (10, 10), "dtype": "f8", "compressor": None, "order": "C", "fill_value": -9999},
        "spam/.zattrs": {},
        "spam/0.0": ["s3://spam.nc", 17, 456],
        "step/.zarray": {"chunks": [], "compressor": None, "dtype": "<f8", "fill_value": None, "order": "C", "shape": [], "zarr_format": 2},
        "step/.zattrs": {"_ARRAY_DIMENSIONS": []},
        "step/": "base64:AAAAAACgd0A=",
        ".zmetadata": {"foo": "skip me!"},
    }

    v3_refs = make_v3_store(v2_refs)
    assert sorted(v3_refs.keys()) == [
        "data/root/foo/bar/c0",
        "data/root/spam/c0/0",
        "data/root/step/c0",
        "meta/root.group.json",
        "meta/root/foo.group.json",
        "meta/root/foo/bar.array.json",
        "meta/root/spam.array.json",
        "meta/root/step.array.json",
    ]
    assert v3_refs["meta/root.group.json"] == {"attributes": {"title": "root-group"}}
    assert v3_refs["meta/root/foo.group.json"] == {"attributes": {"title": "foo-group"}}
    assert v3_refs["meta/root/foo/bar.array.json"] == {
        "attributes": {},
        "chunk_grid": {"chunk_shape": [10], "separator": "/", "type": "regular"},
        "chunk_memory_layout": "C",
        "compressor": None,
        "data_type": "f8",
        "extensions": [],
        "fill_value": -9999,
        "shape": [100],
    }
    assert v3_refs["data/root/foo/bar/c0"] == ["s3://bar.nc", 0, 123]
    assert v3_refs["data/root/spam/c0/0"] == ["s3://spam.nc", 17, 456]

    with capture_logs() as cap_logs:
        make_v3_store({"not a v2 key": 123})
        assert "skipping unrecognized key:" in cap_logs[0]["event"]


def test_reformat_kerchunk_refs():
    # empty refs
    meta_docs, chunk_refs, inlined_refs = reformat_kerchunk_refs({}, "foo")
    assert meta_docs == {}
    assert chunk_refs == {}
    assert inlined_refs == {}

    # special case when kerchunk provides refs key
    meta_docs, chunk_refs, inlined_refs = reformat_kerchunk_refs({"refs": {}}, "foo")
    assert meta_docs == {}
    assert chunk_refs == {}
    assert inlined_refs == {}

    # v2 refs
    refs = {
        ".zgroup": {"version": 2},
        ".zattrs": {"title": "foo-group"},
        "bar/.zarray": {"shape": (100, 100), "chunks": (10, 10), "dtype": "f8", "compressor": None, "order": "C", "fill_value": -9999},
        "bar/.zattrs": {},
    }

    meta_docs, chunk_refs, inlined_refs = reformat_kerchunk_refs(refs, "foo")
    assert set(meta_docs.keys()) == {"meta/root/foo.group.json", "meta/root/foo/bar.array.json"}
    assert meta_docs["meta/root/foo.group.json"] == {"attributes": {"title": "foo-group"}}
    assert meta_docs["meta/root/foo/bar.array.json"] == {
        "attributes": {},
        "chunk_grid": {"chunk_shape": [10, 10], "separator": "/", "type": "regular"},
        "chunk_memory_layout": "C",
        "compressor": None,
        "data_type": "f8",
        "extensions": [],
        "fill_value": -9999,
        "shape": [100, 100],
    }
    assert inlined_refs == {}

    # FIXME: pointing to the root group currently fails
    # meta_docs, chunk_refs = reformat_kerchunk_refs(refs, '')
    # assert meta_docs['meta/root.group.json'] == {"attributes": {"title": "foo-group"}}


@requires_s3fs
def test_virtual_errors(new_sync_repo) -> None:
    # TODO: do we want to define a custom exception type for these errors
    UnsupportedVirtualFileError = ValueError
    with pytest.raises(UnsupportedVirtualFileError, match="s3"):
        with pytest.warns(FutureWarning, match="netcdf"):
            new_sync_repo.add_virtual_hdf("foo/", "hdf/")
    with pytest.raises(UnsupportedVirtualFileError, match="s3"):
        new_sync_repo.add_virtual_netcdf("foo/", "netcdf/")
    with pytest.raises(UnsupportedVirtualFileError, match="s3"):
        new_sync_repo.add_virtual_zarr("foo/", "zarr/")


@requires_s3fs
@pytest.mark.add_object_store("gs")
@pytest.mark.parametrize("pass_extra_kwargs", [False, True])
@pytest.mark.skipif(sys.version_info.major == 3 and sys.version_info.minor == 10, reason="kerchunk 0.2.8 is needed, but is 3.11+")
def test_virtual_netcdf(new_sync_repo, netcdf_file_on_object_storage, file_options, ds, pass_extra_kwargs) -> None:
    ds_expected = ds

    repo = new_sync_repo

    with pytest.warns(FutureWarning):
        repo.add_virtual_hdf(netcdf_file_on_object_storage, "deprecated")
    with pytest.raises(ValueError):
        repo.add_virtual_netcdf(netcdf_file_on_object_storage, "error_expected", storage_options={"foo": "bar"})
    with pytest.raises(ValueError):
        repo.add_virtual_netcdf(netcdf_file_on_object_storage, "error_expected", inline_threshold=100)

    if pass_extra_kwargs:
        kwargs = file_options["extra_kwargs"]
    else:
        kwargs = {}
    repo.add_virtual_netcdf(netcdf_file_on_object_storage, "a/b/c", **kwargs)

    group = repo.root_group["a/b/c"]
    assert "foo" in group
    array = group["foo"]
    assert array.shape == (10, 20, 30)
    try:
        expected_chunks = file_options["encoding"]["foo"]["chunksizes"]
    except KeyError:
        expected_chunks = array.shape
    assert array.chunks == expected_chunks
    np.testing.assert_equal(ds_expected.foo.values, array[:])

    ds = xr.open_dataset(repo.store, group="a/b/c", engine="zarr", zarr_version=3, chunks={})
    xr.testing.assert_identical(ds, ds_expected)


def _assert_equal_tiff(expected_xarray, actual_xarray, actual_zarr):
    # rasterio reads as 'band' x 'x' x 'y'
    # tiffile (used by kerchunk) reads as 'y' x 'x' x 'band'
    expected_xarray_t = expected_xarray.transpose("y", "x", "band")
    assert actual_zarr.shape == expected_xarray_t.shape
    np.testing.assert_equal(expected_xarray_t.values, actual_zarr[:])

    # test with xarray
    # scan_tiff returns a bunch of "extra" metadata + renames dimensions (why??)
    # Therefore, we only compare the values and modifies some
    np.testing.assert_equal(expected_xarray_t.values, actual_xarray.values)


@requires_s3fs
@pytest.mark.parametrize("name", ["foo", pytest.param("foo/", id="trailing slash")])
@pytest.mark.add_object_store("gs")
@pytest.mark.skipif(sys.version_info.major == 3 and sys.version_info.minor == 10, reason="kerchunk 0.2.8 is needed, but is 3.11+")
def test_virtual_tiff_gtiff(name, new_sync_repo, gtiff_on_object_storage, raster_da) -> None:
    repo = new_sync_repo
    repo.checkout()

    component = str(uuid4())
    path = f"a/b/{component}"
    repo.add_virtual_tiff(gtiff_on_object_storage, path, name)

    array = repo.root_group[f"{path}/foo"]
    _ = repo.tree()

    ds = xr.open_dataset(repo.store, group=path, engine="zarr", zarr_version=3, chunks={})
    _assert_equal_tiff(raster_da, actual_xarray=ds["foo"], actual_zarr=array)


@requires_s3fs
@pytest.mark.add_object_store("gs")
@pytest.mark.skipif(sys.version_info.major == 3 and sys.version_info.minor == 10, reason="kerchunk 0.2.8 is needed, but is 3.11+")
def test_virtual_tiff_cog(new_sync_repo, cog_on_object_storage, raster_da) -> None:
    repo = new_sync_repo
    repo.checkout()

    repo.add_virtual_tiff(cog_on_object_storage, "a/b/c/", "foo")
    _ = repo.tree()

    group = repo.root_group["a/b/c/foo"]
    assert "0" in group
    array = group["0"]  # <- kerchunk processes COGs as multiscale arrays. Each overview/zoom level is given as its own array 0, 1, 2
    assert array.chunks == (512, 512, 3)

    ds = xr.open_dataset(repo.store, group="a/b/c/foo", engine="zarr", zarr_version=3, chunks={})
    _assert_equal_tiff(raster_da, actual_xarray=ds["0"], actual_zarr=array)


@requires_s3fs
# passing the uploader is necessary to get an fsspec context to work with
def test_scan_zarr_v2(ds_all_types, zarr_v2_on_object_storage, uploader_for_virtual_files) -> None:
    fs_config = uploader_for_virtual_files.fs_config
    refs = scan_zarr_v2(fs_config, zarr_v2_on_object_storage)

    # check that all metadata docs are
    expected_meta_keys = [".zattrs", ".zgroup"]
    for k in ds_all_types.variables:
        expected_meta_keys.extend([f"{k}/.zarray", f"{k}/.zattrs"])
    for k in expected_meta_keys:
        assert k in refs
        # here we only check the type
        # validation of metadata docs is deferred until make_v3_store
        assert isinstance(refs[k], dict)

    chunk_ref = refs["bool_var/0.0.0"]
    assert isinstance(chunk_ref, list)
    assert chunk_ref[0].startswith(zarr_v2_on_object_storage)
    assert chunk_ref[1] == 0  # offset
    assert chunk_ref[2] > 0  # length


@requires_s3fs
@pytest.mark.add_object_store("gs")
@pytest.mark.skipif(sys.version_info.major == 3 and sys.version_info.minor == 10, reason="kerchunk 0.2.8 is needed, but is 3.11+")
def test_virtual_zarr(new_sync_repo, zarr_v2_on_object_storage, uploader_for_virtual_files) -> None:
    fs_config = uploader_for_virtual_files.fs_config
    ds_expected = xr.open_zarr(zarr_v2_on_object_storage, storage_options=fs_config.constructor_kwargs)

    repo = new_sync_repo

    repo.add_virtual_zarr(zarr_v2_on_object_storage, "a/b/c")

    group = repo.root_group["a/b/c"]
    assert "float32_var" in group
    array = group["float32_var"]
    assert array.shape == (10, 20, 30)

    ds = xr.open_dataset(repo.store, group="a/b/c", engine="zarr", zarr_version=3, chunks={})
    try:
        xr.testing.assert_identical(ds, ds_expected)
    except ValueError as e:
        if "Compressed data" in str(e):
            pytest.xfail(reason="Test intermittently fails with 'Compressed data ended before the end-of-stream marker was reached'")
        else:
            raise e


@requires_cfgrib
@requires_s3fs
@pytest.mark.add_object_store("gs")
@pytest.mark.skipif(sys.version_info.major == 3 and sys.version_info.minor == 10, reason="kerchunk 0.2.8 is needed, but is 3.11+")
def test_virtual_grib(new_sync_repo, grib_on_object_storage):
    new_sync_repo.add_virtual_grib(grib_on_object_storage, "a/b/c")

    group = new_sync_repo.root_group["a/b/c"]
    assert "t" in group
    array = group["t"]
    assert array.shape == (10, 20, 30)


@requires_fsspec
@pytest.mark.skipif(sys.version_info.major == 3 and sys.version_info.minor == 10, reason="kerchunk 0.2.8 is needed, but is 3.11+")
def test_kerchunk_references_from_dict(new_sync_repo, ds, kerchunk_refs, file_options) -> None:
    ds_expected = ds
    refs = kerchunk_refs

    new_sync_repo.add_kerchunk_references(refs, "a/b/c")

    group = new_sync_repo.root_group["a/b/c"]
    assert "foo" in group
    array = group["foo"]
    assert array.shape == (10, 20, 30)

    try:
        expected_chunks = file_options["encoding"]["foo"]["chunksizes"]
    except KeyError:
        expected_chunks = array.shape
    assert array.chunks == expected_chunks
    np.testing.assert_equal(ds_expected.foo.values, array[:])

    ds = new_sync_repo.to_xarray(group="a/b/c")
    xr.testing.assert_identical(ds, ds_expected)


@requires_fsspec
@pytest.mark.skipif(sys.version_info.major == 3 and sys.version_info.minor == 10, reason="kerchunk 0.2.8 is needed, but is 3.11+")
def test_kerchunk_references_from_remote(
    new_sync_repo, ds, kerchunk_refs_on_object_storage, uploader_for_virtual_files, file_options
) -> None:
    ds_expected = ds

    storage_options = uploader_for_virtual_files.fs_config.constructor_kwargs
    new_sync_repo.add_kerchunk_references(kerchunk_refs_on_object_storage, "a/b/c", **storage_options)

    group = new_sync_repo.root_group["a/b/c"]
    assert "foo" in group
    array = group["foo"]
    assert array.shape == (10, 20, 30)

    try:
        expected_chunks = file_options["encoding"]["foo"]["chunksizes"]
    except KeyError:
        expected_chunks = array.shape
    assert array.chunks == expected_chunks
    np.testing.assert_equal(ds_expected.foo.values, array[:])

    ds = new_sync_repo.to_xarray(group="a/b/c")
    xr.testing.assert_identical(ds, ds_expected)


def test_add_kerchunk_references_errors(new_sync_repo) -> None:
    with pytest.raises(ValueError):
        # foo.json does not exist
        new_sync_repo.add_kerchunk_references("s3://foo.json", "a/b/c")

    with pytest.raises(NotImplementedError):
        # templates are not supported yet
        refs = {"templates": {"u": "server.domain/path", "f": "{{c}}"}, "refs": {".zgroup": {"zarr_format": 2}}}
        new_sync_repo.add_kerchunk_references(refs, "a/b/c")

    with pytest.raises(NotImplementedError):
        # gen is not supported yet
        refs = {
            "gen": [
                {
                    "key": "gen_key{{i}}",
                    "url": "http://{{u}}_{{i}}",
                    "offset": "{{(i + 1) * 1000}}",
                    "length": "1000",
                    "dimensions": {"i": {"stop": 5}},
                }
            ],
            "refs": {".zgroup": {"zarr_format": 2}},
        }
        new_sync_repo.add_kerchunk_references(refs, "a/b/c")
