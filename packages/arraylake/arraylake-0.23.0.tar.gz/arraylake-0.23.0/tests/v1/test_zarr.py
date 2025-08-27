import json

import pytest
import zarr
from numpy.random import default_rng

from arraylake.config import config
from arraylake.exceptions import ExpectedChunkNotFoundError
from arraylake.repos.v1.repo import Repo

rng = default_rng(seed=42)


@pytest.fixture
def repo(new_sync_repo):
    return new_sync_repo


def test_store_interface(repo):
    assert "zarr.json" in repo.store
    assert not "bizarre.json" in repo.store

    array_meta = json.dumps(
        {
            "shape": [10000, 1000],
            "data_type": "<f8",
            "chunk_grid": {"type": "regular", "chunk_shape": [1000, 100], "separator": "/"},
            "chunk_memory_layout": "C",
            "compressor": {"codec": "https://purl.org/zarr/spec/codec/gzip/1.0", "configuration": {"level": 1}},
            "fill_value": "NaN",
            "extensions": [],
            "attributes": {"foo": 42, "bar": "apples", "baz": [1, 2, 3, 4]},
        }
    ).encode()
    repo.store["meta/root/foo.array.json"] = array_meta
    assert "meta/root/foo.array.json" in repo.store
    assert array_meta == repo.store["meta/root/foo.array.json"]

    data0 = b"\x00\x01\x02"
    repo.store["data/root/foo/c0"] = data0
    assert "data/root/foo/c0" in repo.store
    assert data0 == repo.store["data/root/foo/c0"]

    assert repo.store.getsize("") == len(data0)
    # pretty sure that this command should be relative to the root of the store
    assert repo.store.getsize("foo") == len(data0)

    commit_0 = repo.commit("first commit")
    assert "meta/root/foo.array.json" in repo.store
    assert "data/root/foo/c0" in repo.store
    assert repo.store["data/root/foo/c0"] == data0
    data1 = b"\x00\x01\x02\x03"
    repo.store["data/root/foo/c0"] = data1
    assert repo.store["data/root/foo/c0"] == data1

    assert repo.store.getsize("") == len(data1)

    orig_data = {"data/root/foo/c0": data1, "meta/root/foo.array.json": array_meta}
    assert repo.store.getitems(["data/root/foo/c0", "meta/root/foo.array.json"]) == orig_data
    repo.commit("replaced some data")
    data2 = b"\x00\x01\x02\x04"
    new_data = {"data/root/foo/c1": data2, "meta/root/bar.group.json": json.dumps({"name": "bar"}).encode()}
    repo.store.setitems(new_data)
    assert repo.store.getitems(list(new_data)) == new_data
    repo.commit("set multiple documents")
    assert repo.store.getitems(list(new_data)) == new_data
    assert repo.store.getitems(list(new_data) + list(orig_data)) == {**new_data, **orig_data}

    assert repo.store.getsize("") == len(data1) + len(data2)

    del repo.store["meta/root/bar.group.json"]
    with pytest.raises(KeyError):
        repo.store["meta/root/bar.group.json"]
    repo.commit("deleted a document")
    with pytest.raises(KeyError):
        repo.store["meta/root/bar.group.json"]

    with pytest.raises(KeyError):
        repo.store["data/root/foo/c2"]

    repo.store.delitems(["data/root/foo/c0", "data/root/foo/c1"])
    assert repo.store.getitems(["data/root/foo/c0", "data/root/foo/c1"]) == {}

    assert repo.store.getsize("") == 0

    with pytest.raises(ValueError):
        # Q: I don't understand why this raises ValueError and not KeyError.
        # A: Because it is not just a not-present key. It is actually an invalid value for the key.
        repo.store["random/key"]

    repo.commit("more deletes")

    # test that we can delete something and then re-add it in a session
    repo.store["meta/root/baz.group.json"] = json.dumps({"name": "baz"}).encode()
    del repo.store["meta/root/baz.group.json"]
    repo.store["meta/root/baz.group.json"] = json.dumps({"name": "bing"}).encode()
    assert "meta/root/baz.group.json" in repo.store
    assert json.loads(repo.store["meta/root/baz.group.json"]) == {"name": "bing"}

    # test special cases for zarr.json
    items = repo.store.getitems(["zarr.json", "meta/root/foo.array.json"])
    assert "zarr.json" in items


def test_store_hierarchy(repo):
    repo.root_group.attrs["title"] = "test store hierarchy"
    repo.commit("initial commit")
    original_commit = repo._arepo._session.base_commit

    # this should be automatically populated when the repo is created
    entry_point_meta = json.loads(repo.store["zarr.json"])
    assert entry_point_meta["metadata_key_suffix"] == ".json"

    assert repo.store.listdir("/") == ["data", "meta", "zarr.json"]
    assert repo.store.listdir("") == ["data", "meta", "zarr.json"]
    assert repo.store.listdir("data") == ["root"]
    assert repo.store.listdir("data/") == ["root"]
    assert repo.store.listdir("meta") == ["root.group.json"]
    assert repo.store.listdir("meta/") == ["root.group.json"]
    assert repo.store.listdir("other_prefix") == []
    assert repo.store.listdir("other_prefix/") == []

    domains = ("land", "sea", "air")
    variables = ("temperature", "pressure", "density")
    arrays = ("min", "max", "mean")

    all_meta_docs = {}  # type: dict[str, bytes]
    for lev0 in domains:
        all_meta_docs[f"meta/root/{lev0}.group.json"] = json.dumps({}).encode()
        for lev1 in variables:
            # parent is not required by spec, just helps our test
            all_meta_docs[f"meta/root/{lev0}/{lev1}.group.json"] = json.dumps({"parent": lev0}).encode()
            for lev2 in arrays:
                all_meta_docs[f"meta/root/{lev0}/{lev1}/{lev2}.array.json"] = json.dumps({"parent": lev1}).encode()

    all_chunks = {}  # type: dict[str, bytes]
    for lev0 in domains:
        for lev1 in variables:
            for lev2 in arrays:
                all_chunks[f"data/root/{lev0}/{lev1}/{lev2}/c0"] = b"\x00"
                all_chunks[f"data/root/{lev0}/{lev1}/{lev2}/c1"] = b"\x01"

    all_docs = {**all_meta_docs, **all_chunks}

    all_expected_docs = sorted(list(all_docs) + ["meta/root.group.json", "zarr.json"])
    all_meta_doc_keys = sorted(list(all_meta_docs)) + ["meta/root.group.json"]

    def write_full_hierarchy():
        repo.store.setitems(all_meta_docs)
        # important that these are done in separate steps
        repo.store.setitems(all_chunks)

    def check_full_hierarchy():
        assert sorted(repo.store.list_prefix("meta/root")) == sorted(all_meta_doc_keys)
        assert sorted(repo.store.list_prefix("meta/root/")) == sorted(set(all_meta_doc_keys) - {"meta/root.group.json"})
        assert sorted(repo.store.list_prefix("data/root")) == sorted(all_chunks)
        assert sorted(repo.store.list_prefix("data/root/")) == sorted(all_chunks)
        assert sorted(repo.store.listdir("meta/root")) == sorted([f"{lev0}.group.json" for lev0 in domains] + [lev0 for lev0 in domains])
        assert sorted(repo.store.listdir("meta/root/")) == sorted([f"{lev0}.group.json" for lev0 in domains] + [lev0 for lev0 in domains])
        for lev0 in domains:
            lev0_meta = sorted([doc for doc in all_meta_doc_keys if lev0 in doc])
            assert sorted(repo.store.list_prefix(f"meta/root/{lev0}")) == lev0_meta
            assert sorted(repo.store.list_prefix(f"meta/root/{lev0}/")) == sorted(set(lev0_meta) - {f"meta/root/{lev0}.group.json"})
            lev0_meta = sorted([f"{lev1}.group.json" for lev1 in variables] + [lev1 for lev1 in variables])
            assert sorted(repo.store.listdir(f"meta/root/{lev0}")) == lev0_meta
            assert sorted(repo.store.listdir(f"meta/root/{lev0}/")) == lev0_meta
            for lev1 in variables:
                lev2_meta = sorted([f"{lev2}.array.json" for lev2 in arrays])
                assert sorted(repo.store.listdir(f"meta/root/{lev0}/{lev1}")) == lev2_meta
                assert sorted(repo.store.listdir(f"meta/root/{lev0}/{lev1}/")) == lev2_meta
                for lev2 in arrays:
                    prefix = f"data/root/{lev0}/{lev1}/{lev2}"
                    assert sorted(repo.store.listdir(prefix)) == sorted(["c0", "c1"])
                    assert sorted(repo.store.listdir(prefix + "/")) == sorted(["c0", "c1"])

    write_full_hierarchy()
    check_full_hierarchy()

    assert sorted(repo.store.list_prefix("")) == sorted(all_expected_docs)
    assert sorted(repo.store.keys()) == sorted(all_expected_docs)
    assert sorted(list(repo.store)) == sorted(all_expected_docs)
    assert len(repo.store) == len(all_expected_docs)

    repo.commit("first commit")
    check_full_hierarchy()

    # make sure other branches don't see this
    with pytest.warns(UserWarning):
        # casting original_commit as str() is not necessary but is valid
        repo.checkout(str(original_commit))
    repo.new_branch("testing")
    assert repo.store.listdir("") == ["data", "meta", "zarr.json"]
    assert repo.store.listdir("/") == ["data", "meta", "zarr.json"]
    repo.checkout("main")

    # overwrite something
    repo.store["meta/root/land.group.json"] = json.dumps({"new": True}).encode()
    check_full_hierarchy()
    commit_id = repo.commit("set lots of stuff")
    check_full_hierarchy()

    # test bad commit, this casts to CommitID but is invalid
    with pytest.raises(ValueError, match="was not found in commit history."):
        repo.checkout(str(commit_id)[::-1])

    # delete data
    for path in repo.store.list_prefix("meta/root/land"):
        del repo.store[path]

    # this case is interesting: we're deleting the land group metadata, implying that the group is deleted
    # however, the result is that we're left with an implicit group.
    assert "meta/root/land.group.json" not in repo.store
    assert sorted(repo.store.listdir("meta/root")) == sorted(["air", "air.group.json", "sea", "sea.group.json"])
    assert sorted(repo.store.listdir("meta/root/")) == sorted(["air", "air.group.json", "sea", "sea.group.json"])
    expected_prefixes = sorted([doc for doc in all_meta_doc_keys if "land" not in doc])
    assert sorted(repo.store.list_prefix("meta/root")) == sorted(expected_prefixes)
    assert sorted(repo.store.list_prefix("meta/root/")) == sorted(set(expected_prefixes) - {"meta/root.group.json"})
    repo.commit("deleted some stuff")
    assert sorted(repo.store.listdir("meta/root")) == sorted(["air", "air.group.json", "sea", "sea.group.json"])
    assert sorted(repo.store.listdir("meta/root/")) == sorted(["air", "air.group.json", "sea", "sea.group.json"])
    assert sorted(repo.store.list_prefix("meta/root")) == sorted(expected_prefixes)
    assert sorted(repo.store.list_prefix("meta/root/")) == sorted(set(expected_prefixes) - {"meta/root.group.json"})

    del repo.store["meta/root/air/pressure/min.array.json"]
    assert "meta/root/air/pressure/min.array.json" not in repo.store

    # delete chunk
    prefix = "data/root/land/temperature/min"
    del repo.store[f"{prefix}/c0"]
    assert repo.store.listdir(prefix) == [f"c1"]
    assert repo.store.listdir(prefix + "/") == [f"c1"]
    assert repo.store.list_prefix(prefix) == [f"{prefix}/c1"]
    assert repo.store.list_prefix(prefix + "/") == [f"{prefix}/c1"]
    repo.commit("deleted a chunk")
    assert repo.store.listdir(prefix) == [f"c1"]
    assert repo.store.listdir(prefix + "/") == [f"c1"]
    assert repo.store.list_prefix(prefix) == [f"{prefix}/c1"]
    assert repo.store.list_prefix(prefix + "/") == [f"{prefix}/c1"]

    del repo.store["data/root/air/pressure/max/c0"]
    assert "data/root/air/pressure/max/c0" not in repo.store

    # multiple deletes
    items_to_delete = ["data/root/air/pressure/min/c0", "data/root/air/pressure/min/c1", "meta/root/air/pressure/min.array.json"]
    repo.store.delitems(items_to_delete)
    for name in items_to_delete:
        assert name not in repo.store

    # erase prefix
    repo.store.erase_prefix("data/root/air/temperature")
    assert repo.store.listdir("data/root/air/temperature") == []
    assert repo.store.listdir("data/root/air/temperature/") == []

    # now write everything again
    write_full_hierarchy()
    check_full_hierarchy()
    repo.commit("rewrote everything")
    check_full_hierarchy()


def test_zarr_delete_prefix(repo: Repo) -> None:
    root_group = repo.root_group
    assert root_group.attrs == {}
    air_group = root_group.create_group("air")
    air_group.attrs["domain"] = "atmospheric"
    air_temp_array = air_group.create("temperature", shape=100, chunks=10, dtype="i4", fill_value=0)
    air_temp_array.attrs["units"] = "K"

    airr_group = root_group.create_group("airr")
    airr_group.attrs["domain"] = "aatmospheric"
    airr_temp_array = airr_group.create("temperature", shape=100, chunks=10, dtype="i4", fill_value=0)
    airr_temp_array.attrs["units"] = "K"

    del root_group["air"]
    assert list(root_group) == ["airr"]


def test_zarr_arrays_and_groups(repo) -> None:
    root_group = repo.root_group
    assert root_group.attrs == {}
    air_group = root_group.create_group("air")
    air_group.attrs["domain"] = "atmospheric"
    air_temp_array = air_group.create("temperature", shape=100, chunks=10, dtype="i4", fill_value=0)
    air_temp_array.attrs["units"] = "K"
    ocean_group = root_group.create_group("ocean")
    # no compressor is a regression test for https://github.com/earth-mover/arraylake/issues/304
    ocean_temp_array = ocean_group.create("temperature", shape=(10, 10), chunks=10, dtype="i4", fill_value=0, compressor=None)
    ocean_temp_array.attrs["units"] = "K"
    ocean_group.attrs["domain"] = "oceanic"
    assert root_group["air"] == air_group

    repo.commit("created some groups")
    assert ocean_temp_array[0, 0] == 0
    ocean_temp_array[:] = 1
    assert ocean_temp_array[0, 0] == 1
    c1 = repo.commit("wrote some data")
    ocean_temp_array[:5] = 2
    assert ocean_temp_array[0, 0] == 2
    assert ocean_temp_array[5, 0] == 1
    ocean_temp_array.attrs["foo"] = 1

    assert repo.store.getsize("") == 400  # 10 uncompressed chunks of 10 4-byte ints each in foo
    air_temp_array[:] = 1  # these are compressed
    assert repo.store.getsize("") == 456  # ironically, the compressed arrays are bigger than the uncompressed ones

    repo.commit("overwrote some data")
    with pytest.warns(UserWarning):
        repo.checkout(str(c1))
    assert ocean_temp_array[0, 0] == 1

    # this doesn't work because attrs are cached on the client side; need to reload
    # assert 'foo' not in ocean_temp_array.attrs
    ocean_temp_array = ocean_group["temperature"]
    assert "foo" not in ocean_temp_array.attrs

    # these tests don't work because of a zarr bug
    # https://github.com/zarr-developers/zarr-python/issues/1228
    assert list(root_group.group_keys()) == ["air", "ocean"]
    assert list(root_group.groups()) == [("air", air_group), ("ocean", ocean_group)]

    # not sure here
    repo.checkout()

    singleton_array = air_group.create("empty_array", shape=(), chunks=(), dtype="i4", fill_value=0)
    singleton_array[...] = 1
    assert singleton_array[...] == 1
    repo.commit("created a singleton array")

    # now delete some stuff
    del root_group["air/temperature"]
    assert "air" in root_group
    assert "temperature" not in root_group["air"]

    # move a group
    # root_group.move("ocean", "sea")
    # assert "ocean" not in root_group
    # assert "sea" in root_group


@pytest.mark.xfail(reason="Metadata docs are not currently counted by getsize()")
def test_getsize(repo):
    mem_store = zarr.MemoryStoreV3()

    kwargs = dict(shape=(20, 20), chunks=(10, 10), dtype="i4", fill_value=0, path="foo/bar", zarr_version=3)
    data = rng.integers(0, 100, size=kwargs["shape"], dtype=kwargs["dtype"])

    z1 = zarr.create(store=repo.store, **kwargs)
    z1[:] = data

    z2 = zarr.create(store=mem_store, **kwargs)
    z2[:] = data

    assert repo.store.listdir("") == mem_store.listdir("")
    assert repo.store.getsize("") == mem_store.getsize("")


def test_zarr_array_more_than_20_chunks(repo) -> None:
    ntries = 10
    for _ in range(ntries):
        array = repo.root_group.create("bigarray", shape=(1000), chunks=(5,))
        array[:] = 1
        all_docs = repo.store.list_prefix("data/root")
        assert len(all_docs) == 200
        all_docs = repo.store.list_prefix("data/root/")
        assert len(all_docs) == 200
        # checkout to 'reset' session
        repo.checkout("main")


def test_commit_new_branch(new_sync_repo):
    # EAR-1010
    repo = new_sync_repo
    zarr.group(repo.store)
    zarr.group(repo.store, path="MA")
    repo.new_branch("21")
    repo.commit("new commit")


def test_unsafe_use_fill_value_for_missing_chunks(new_sync_repo, object_store_config):
    s3fs = pytest.importorskip("s3fs")
    repo = new_sync_repo

    kwargs = dict(shape=(20, 20), chunks=(10, 10), dtype="i4", fill_value=0, path="foo/bar", zarr_version=3)
    data = rng.integers(0, 100, size=kwargs["shape"], dtype=kwargs["dtype"])

    z1 = zarr.create(store=repo.store, **kwargs)
    z1[:] = data

    # delete one of the chunks in the object store
    fs = s3fs.S3FileSystem(
        client_kwargs={"endpoint_url": object_store_config["s3.endpoint_url"]},
    )
    ref = repo._get_chunk_ref("data/root/foo/bar/c0/0")
    fs.delete(ref.uri)

    # test behavior
    # load just the chunk that we deleted
    with pytest.warns(UserWarning):
        with config.set({"chunkstore.unsafe_use_fill_value_for_missing_chunks": True}):
            expected = z1[0, 0]

    # load all the chunks (w/ one missing)
    with pytest.warns(UserWarning):
        with config.set({"chunkstore.unsafe_use_fill_value_for_missing_chunks": True}):
            expected = z1[:]

    # with the feature flag off, we still issue a warning and pass the boto error on through
    with pytest.warns(UserWarning):
        with config.set({"chunkstore.unsafe_use_fill_value_for_missing_chunks": False}):
            with pytest.raises(ExpectedChunkNotFoundError):
                expected = z1[0, 0]
