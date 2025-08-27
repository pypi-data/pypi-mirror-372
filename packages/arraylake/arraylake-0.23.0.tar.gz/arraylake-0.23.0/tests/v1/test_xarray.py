import sys
from collections import Counter
from unittest import mock

import pytest
from tests.v1.helpers.test_utils import get_sync_repo

from .. import has_dask, requires_xarray

pytest.importorskip("xarray")

all_dsets = [
    pytest.param("air_temperature", marks=pytest.mark.slow),
    pytest.param("air_temperature_gradient", marks=pytest.mark.slow),
    pytest.param("basin_mask", marks=pytest.mark.slow),
    pytest.param("ASE_ice_velocity", marks=pytest.mark.slow),
    pytest.param("rasm", marks=pytest.mark.slow),
    pytest.param("ROMS_example", marks=pytest.mark.slow),
    pytest.param("tiny"),
    pytest.param("eraint_uvz", marks=pytest.mark.slow),
    pytest.param("ersstv5", marks=pytest.mark.slow),
]


class CountingDict:
    def __init__(self):
        self._dict = {}
        self._contains_calls = Counter()
        self._getitem_calls = Counter()
        self._setitem_calls = []

    def __contains__(self, key) -> bool:
        if key in self._dict:
            self._contains_calls.update([key])
        return key in self._dict

    def __getitem__(self, key):
        if key in self._dict:
            self._getitem_calls.update([key])
        return self._dict[key]

    def __setitem__(self, *args, **kwargs):
        return self._dict.__setitem__(*args, **kwargs)

    def update(self, other):
        self._setitem_calls.extend(other)
        return self._dict.update(other)

    def clear(self):
        return self._dict.clear()

    def items(self):
        return self._dict.items()

    def was_used(self) -> bool:
        return self._contains_calls and self._getitem_calls and self._setitem_calls


def assert_cache_is_correct(docs_cache, chunk_refs_cache, group, dsname, ds) -> None:
    for cache in [docs_cache, chunk_refs_cache]:
        assert cache.was_used
        assert not cache._dict  # cache was cleared

    expected = [f"meta/root/{group}/{dsname}.group.json"]
    expected.extend([f"meta/root/{group}/{dsname}/{var}.array.json" for var in ds.variables])

    expected.extend([f"meta/root/{group}/{dsname}/{var}.array.json" for var in ds.xindexes])
    assert set(docs_cache._setitem_calls) == set(expected)

    expected = [f"data/root/{group}/{dsname}/{var}/c0" for var in ds.xindexes]
    assert set(chunk_refs_cache._setitem_calls) == set(expected)


@requires_xarray
def test_empty_root_group(new_sync_repo) -> None:
    import xarray as xr

    ds = xr.Dataset()
    ds.to_zarr(new_sync_repo.store, zarr_version=3)
    arepo = new_sync_repo._arepo
    with mock.patch.object(arepo, "_prefetched_docs", CountingDict()) as docs_cache, mock.patch.object(
        arepo, "_prefetched_chunk_refs", CountingDict()
    ) as chunk_refs_cache:
        new_sync_repo.to_xarray()
        assert not chunk_refs_cache.was_used()  # no chunk refs need to be loaded
        assert docs_cache.was_used()
        assert not docs_cache._dict  # cache was cleared

        # assert set(docs_cache._setitem_calls) == {"meta/root.group.json"}
        assert docs_cache._contains_calls["meta/root.group.json"] <= 3
        assert docs_cache._getitem_calls["meta/root.group.json"] <= 2

    with mock.patch.object(arepo, "_prefetched_docs", CountingDict()) as docs_cache, mock.patch.object(
        arepo, "_prefetched_chunk_refs", CountingDict()
    ) as chunk_refs_cache:
        new_sync_repo.root_group
        assert not chunk_refs_cache.was_used()  # no chunk refs need to be loaded
        assert docs_cache.was_used()
        assert not docs_cache._dict  # cache was cleared

        # assert set(docs_cache._setitem_calls) == {"meta/root.group.json"}
        assert docs_cache._contains_calls["meta/root.group.json"] == 2
        assert docs_cache._getitem_calls["meta/root.group.json"] == 1


@requires_xarray
def test_xarray_root_group(new_sync_repo) -> None:
    import xarray as xr

    ds = xr.tutorial.open_dataset("tiny")
    ds.to_zarr(new_sync_repo.store, zarr_version=3)
    arepo = new_sync_repo._arepo
    with mock.patch.object(arepo, "_prefetched_docs", CountingDict()) as docs_cache, mock.patch.object(
        arepo, "_prefetched_chunk_refs", CountingDict()
    ) as chunk_refs_cache:
        new_sync_repo.to_xarray()
        assert not chunk_refs_cache.was_used()  # no chunk refs need to be loaded
        assert docs_cache.was_used()
        assert not docs_cache._dict  # cache was cleared

        # assert set(docs_cache._setitem_calls) == {
        #     "meta/root.group.json",
        #     "meta/root/tiny.array.json",
        # }
        # TODO: revise these numbers when min xarray is 2023.12.0
        assert docs_cache._contains_calls["meta/root.group.json"] <= 3
        assert docs_cache._contains_calls["meta/root/tiny.array.json"] <= 5
        assert docs_cache._getitem_calls["meta/root.group.json"] <= 2
        assert docs_cache._getitem_calls["meta/root/tiny.array.json"] <= 3

    with mock.patch.object(arepo, "_prefetched_docs", CountingDict()) as docs_cache, mock.patch.object(
        arepo, "_prefetched_chunk_refs", CountingDict()
    ) as chunk_refs_cache:
        new_sync_repo.root_group
        assert not chunk_refs_cache.was_used()  # no chunk refs need to be loaded
        assert docs_cache.was_used()
        assert not docs_cache._dict  # cache was cleared

        assert set(docs_cache._setitem_calls) == {"meta/root.group.json"}
        assert docs_cache._contains_calls["meta/root.group.json"] <= 2
        assert docs_cache._getitem_calls["meta/root.group.json"] <= 1


@requires_xarray
@pytest.mark.parametrize("dsname", all_dsets)
@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info.major == 3 and sys.version_info.minor == 10, reason="kerchunk 0.2.8 is needed, but is 3.11+")
async def test_xarray_tutorial_datasets(chunkstore_bucket, user, dsname, dask_client, use_dask, helpers) -> None:
    import xarray as xr

    sync_repo = await get_sync_repo(chunkstore_bucket, helpers.random_repo_id(), user, shared=False)
    ds = xr.tutorial.open_dataset(dsname)
    group = f"xarray_tutorial/{dsname}"
    arepo = sync_repo._arepo
    for v in ds.variables:
        # deleting encoding eliminates test failures by elminating lossy serialization techniques
        # (e.g. scale_factor)
        ds[v].encoding = {}

    if use_dask:
        if not has_dask:
            pytest.skip("dask not installed")
        ds = ds.chunk()

    with dask_client:
        ds.to_zarr(sync_repo.store, zarr_version=3, group=group, mode="w")

        ds_expected = xr.tutorial.open_dataset(dsname)

        ds_actual = xr.open_dataset(sync_repo.store, group=group, zarr_version=3, engine="zarr")
        with mock.patch.object(arepo, "_prefetched_docs", CountingDict()) as docs_cache, mock.patch.object(
            arepo, "_prefetched_chunk_refs", CountingDict()
        ) as chunk_refs_cache:
            ds_to_xarray_actual = sync_repo.to_xarray(group=group)
            assert_cache_is_correct(docs_cache, chunk_refs_cache, "xarray_tutorial", dsname, ds_actual)
        assert not arepo._prefetched_docs
        assert not arepo._prefetched_chunk_refs
        xr.testing.assert_identical(ds_expected, ds_actual)

        xr.testing.assert_identical(ds_expected, ds_to_xarray_actual)
        xr.testing.assert_identical(ds_actual, ds_to_xarray_actual)

        sync_repo.commit("sealing the deal with a commit")

        ds_actual = xr.open_dataset(sync_repo.store, group=group, zarr_version=3, engine="zarr")
        with mock.patch.object(arepo, "_prefetched_docs", CountingDict()) as docs_cache, mock.patch.object(
            arepo, "_prefetched_chunk_refs", CountingDict()
        ) as chunk_refs_cache:
            ds_to_xarray_actual = sync_repo.to_xarray(group=group)
            assert_cache_is_correct(docs_cache, chunk_refs_cache, "xarray_tutorial", dsname, ds_actual)
        assert not arepo._prefetched_docs
        assert not arepo._prefetched_chunk_refs

        xr.testing.assert_identical(ds_expected, ds_actual)
        xr.testing.assert_identical(ds_expected, ds_to_xarray_actual)


@requires_xarray
@pytest.mark.parametrize("group", [None, "/", "foo/bar"])
def test_to_xarray_groups(new_sync_repo, group) -> None:
    import xarray as xr

    ds_expected = xr.tutorial.open_dataset("tiny")
    ds_expected.to_zarr(new_sync_repo.store, group=group, zarr_version=3, consolidated=False)
    ds_actual = new_sync_repo.to_xarray(group=group)
    assert not new_sync_repo._arepo._prefetched_docs
    assert not new_sync_repo._arepo._prefetched_chunk_refs

    xr.testing.assert_identical(ds_expected, ds_actual)

    ds_actual = new_sync_repo.to_xarray(group)
    assert not new_sync_repo._arepo._prefetched_docs
    assert not new_sync_repo._arepo._prefetched_chunk_refs
    xr.testing.assert_identical(ds_expected, ds_actual)


@requires_xarray
def test_to_xarray_exceptions(new_sync_repo):
    with pytest.raises(
        ValueError,
        match="Setting `zarr_version` is not allowed here. Arraylake only supports `zarr_version=3`",
    ):
        new_sync_repo.to_xarray(group="foo/bar", zarr_version=2)
    assert not new_sync_repo._arepo._prefetched_docs
    assert not new_sync_repo._arepo._prefetched_chunk_refs

    with pytest.raises(
        ValueError,
        match="Setting `engine` is not allowed here. Arraylake only supports `engine='zarr'`",
    ):
        new_sync_repo.to_xarray(group="foo/bar", engine="netcdf")
    assert not new_sync_repo._arepo._prefetched_docs
    assert not new_sync_repo._arepo._prefetched_chunk_refs
