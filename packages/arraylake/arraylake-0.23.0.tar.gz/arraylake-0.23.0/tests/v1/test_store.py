import json

import pytest
import zarr
from zarr._storage.v3 import StoreV3
from zarr.tests.test_storage_v3 import StoreV3Tests

from arraylake.repos.v1.repo import Repo


@pytest.mark.xfail(reason="Tests against the zarr test suite currently fails majority of tests")
class TestArraylakeStoreV3(StoreV3Tests):
    """Test our AL store against the zarr-python store test suite."""

    # how do we clean this up?
    @pytest.fixture(autouse=True)
    def repo(self, new_sync_repo):
        self.repo = new_sync_repo

    def create_store(self):
        return self.repo.store


@pytest.fixture
def populated_zarr_store(new_sync_repo):
    store = new_sync_repo.store
    root = zarr.open_group(store)
    a = root.create_group("aa")
    b = a.create_group("bb")
    c = root.create_group("aa_abb")
    d = root.create_group("aa/implicit/cc")
    e = root.create_group("dd")
    f = root.create_group("aa/second-implicit/third-implicit/nothing")
    h = b.create_group("hh")
    i = b.create_group("ii")
    j = b.create_dataset("j-nested", shape=100, chunks=10)
    data = root.create_dataset("baz", shape=100, chunks=10)
    data2 = d.create_dataset("nested", shape=100, chunks=10)
    return store


def test_list_operations(populated_zarr_store: StoreV3):
    store = populated_zarr_store
    expected = [
        "zarr.json",
        "meta/root.group.json",
        "meta/root/aa.group.json",
        "meta/root/aa/bb.group.json",
        "meta/root/aa/bb/hh.group.json",
        "meta/root/aa/bb/ii.group.json",
        "meta/root/aa/bb/j-nested.array.json",
        "meta/root/aa/implicit/cc.group.json",
        "meta/root/aa/implicit/cc/nested.array.json",
        "meta/root/aa/second-implicit/third-implicit/nothing.group.json",
        "meta/root/aa_abb.group.json",
        "meta/root/dd.group.json",
        "meta/root/baz.array.json",
    ]

    assert sorted(list(store)) == sorted(expected)
    assert sorted(store.list_prefix("")) == sorted(expected)


@pytest.mark.xfail(reason="Our listdir interface returns excessive documents, inconsistent with the zarr-python interface")
def test_listdir_operations(populated_zarr_store: StoreV3):
    store = populated_zarr_store
    listings = {
        "": ["meta", "zarr.json"],
        "meta": ["root", "root.group.json"],
        "meta/root": ["aa", "aa.group.json", "aa_abb.group.json", "baz.array.json", "dd.group.json"],
        "meta/root/aa": ["bb.group.json", "implicit", "second-implicit", "bb"],
        "meta/root/aa/second-implicit": ["third-implicit"],
        "meta/root/aa/second-implicit/third-implicit": ["nothing.group.json"],
        "meta/root/aa/second-implicit/third-implicit/nothing": [],
        "meta/root/aa/implicit": ["cc", "cc.group.json"],
        "meta/root/aa/implicit/cc": ["nested.array.json"],
    }

    # list_dir yields fully resolved paths to files within the specific key
    # list_dir _must_ append a trailing slash / to prefixes

    for key, expected in listings.items():
        assert sorted(store.listdir(key)) == sorted(expected), key
        assert sorted(store.listdir(key + "/")) == sorted(expected), key


def test_list_dir_operations(populated_zarr_store: StoreV3):
    """
    TODO: Why these tests fail:
    AL yields default group.json documents for explicitly created groups. For example, in executing:
        root.create_group("aa")
    We will return document:
        'meta/root/aa/group.json'
    This is inconsistent with zarr-python, which does not produce these group.json documents, and infers the group from
    the directory structure.
    """
    store = populated_zarr_store

    assert store.list_dir("") == (["zarr.json"], ["meta/"])

    with pytest.raises(TypeError, match=r"list_dir\(\) missing 1 required positional argument: \'prefix\'"):
        store.list_dir()

    listings = {
        "meta/": (["meta/root.group.json"], ["meta/root/"]),
        "meta/root/": (
            ["meta/root/aa.group.json", "meta/root/aa_abb.group.json", "meta/root/dd.group.json", "meta/root/baz.array.json"],
            ["meta/root/aa/"],
        ),
        "meta/root/aa/": (["meta/root/aa/bb.group.json"], ["meta/root/aa/implicit/", "meta/root/aa/second-implicit/", "meta/root/aa/bb/"]),
        "meta/root/aa/implicit/": (["meta/root/aa/implicit/cc.group.json"], ["meta/root/aa/implicit/cc/"]),
        "meta/root/aa/second-implicit/": ([], ["meta/root/aa/second-implicit/third-implicit/"]),
        "meta/root/aa/second-implicit/third-implicit/": (["meta/root/aa/second-implicit/third-implicit/nothing.group.json"], []),
    }

    for key, expected in listings.items():
        keys, groups = store.list_dir(key)
        keys, groups = sorted(keys), sorted(groups)
        expected_keys, expected_groups = sorted(expected[0]), sorted(expected[1])
        assert keys == expected_keys, key
        assert groups == expected_groups, key

        with pytest.raises(AssertionError, match=""):
            # trim the trailing slash off, which should cause an exception
            _key = key[:-1]
            store.list_dir(_key)


def test_list_prefix_operations(populated_zarr_store: StoreV3):
    store = populated_zarr_store
    expected_full_meta = [
        "meta/root.group.json",
        "meta/root/aa.group.json",
        "meta/root/aa/bb.group.json",
        "meta/root/aa/bb/hh.group.json",
        "meta/root/aa/bb/ii.group.json",
        "meta/root/aa/bb/j-nested.array.json",
        "meta/root/aa/implicit/cc.group.json",
        "meta/root/aa/implicit/cc/nested.array.json",
        "meta/root/aa/second-implicit/third-implicit/nothing.group.json",
        "meta/root/aa_abb.group.json",
        "meta/root/dd.group.json",
        "meta/root/baz.array.json",
    ]
    assert sorted(store.list_prefix("")) == sorted(expected_full_meta + ["zarr.json"])
    assert sorted(store.list_prefix("meta")) == sorted(expected_full_meta)
    assert sorted(store.list_prefix("meta/")) == sorted(expected_full_meta)

    with pytest.raises(ValueError, match="prefix must not begin with /"):
        store.list_prefix("/")

    expected_group_with_slash = [
        "meta/root/aa/bb.group.json",
        "meta/root/aa/implicit/cc.group.json",
        "meta/root/aa/implicit/cc/nested.array.json",
        "meta/root/aa/second-implicit/third-implicit/nothing.group.json",
        "meta/root/aa/bb/hh.group.json",
        "meta/root/aa/bb/ii.group.json",
        "meta/root/aa/bb/j-nested.array.json",
    ]
    assert sorted(store.list_prefix("meta/root/aa/")) == sorted(expected_group_with_slash)

    # prefix matches against the full key and does not assume the prefix is delimited
    # by a directory or file, we expect any path with the given prefix to match.
    expected_group_without_slash = [
        "meta/root/aa.group.json",
        "meta/root/aa/bb.group.json",
        "meta/root/aa/implicit/cc.group.json",
        "meta/root/aa/implicit/cc/nested.array.json",
        "meta/root/aa/second-implicit/third-implicit/nothing.group.json",
        "meta/root/aa_abb.group.json",
        "meta/root/aa/bb/hh.group.json",
        "meta/root/aa/bb/ii.group.json",
        "meta/root/aa/bb/j-nested.array.json",
    ]
    assert sorted(store.list_prefix("meta/root/aa")) == sorted(expected_group_without_slash)


def test_list_prefix_with_implicit_groups(populated_zarr_store: StoreV3):
    store = populated_zarr_store
    expected_implicit = ["meta/root/aa/second-implicit/third-implicit/nothing.group.json"]
    assert sorted(store.list_prefix("meta/root/aa/second-implicit")) == sorted(expected_implicit)


def test_list_direct_indexing(populated_zarr_store: StoreV3):
    store = populated_zarr_store
    root = zarr.open(store)
    for k in ["aa", "aa_abb", "aa/bb", "dd"]:
        as_prop = getattr(root, k)
        assert isinstance(as_prop, zarr.hierarchy.Group)
        assert isinstance(root[k], zarr.hierarchy.Group)
        assert isinstance(root[k + "/"], zarr.hierarchy.Group)

    for k in ["aa/implicit", "aa/implicit/cc", "aa/second-implicit/third-implicit", "aa/second-implicit/third-implicit/nothing"]:
        as_prop = getattr(root, k)
        assert isinstance(as_prop, zarr.hierarchy.Group)
        assert isinstance(root[k], zarr.hierarchy.Group)
        assert isinstance(root[k + "/"], zarr.hierarchy.Group)

    for k in ["baz", "aa/implicit/cc/nested"]:
        as_prop = getattr(root, k)
        assert isinstance(as_prop, zarr.core.Array)
        assert isinstance(root[k], zarr.core.Array)
        assert isinstance(root[k + "/"], zarr.core.Array)


def test_list_casting(populated_zarr_store: StoreV3):
    """
    list() a store is list_dir
    therefore it must come with a trailing /

    list(root)
    --> call function __len__
    ----> call function <genexpr>
    ------> call function __iter__
    --------> call function list_dir
    ----------> call function list_prefix
    ------------> call function _wrap_async_iter
    """
    store = populated_zarr_store
    root = zarr.open(store)
    assert sorted(list(root)) == sorted(["aa", "aa_abb", "dd", "baz"])
    assert sorted(list(root["aa"])) == sorted(["bb", "second-implicit", "implicit"])
    assert sorted(list(root["aa/second-implicit"])) == sorted(["third-implicit"])
    assert sorted(list(root["aa/implicit"])) == sorted(["cc"])
    assert sorted(list(root["aa_abb"])) == []


def test_list_group_keys_containing_explicit_groups(populated_zarr_store: StoreV3):
    store = populated_zarr_store
    root = zarr.open(store)
    assert sorted(list(root.group_keys())) == sorted(["aa", "aa_abb", "dd"])
    assert sorted(list(root["aa/bb"].group_keys())) == sorted(["ii", "hh"])

    # these groups are implicit, but we're directly requesting them and their
    # _contents_ are explicit, so these yield appropriate results.
    assert sorted(list(root["aa/implicit"].group_keys())) == sorted(["cc"])
    assert sorted(list(root["aa/implicit/cc"].group_keys())) == []


def test_list_group_keys_containing_implicit_groups(populated_zarr_store: StoreV3):
    store = populated_zarr_store
    root = zarr.open(store)
    assert sorted(list(root["aa"].group_keys())) == sorted(["implicit", "bb", "second-implicit"])


def test_implict_groups(new_sync_repo: Repo):
    repo = new_sync_repo
    root_group = repo.root_group
    store = repo.store

    # store = MemoryStoreV3()
    # root_group = zarr.open_group(store=store, zarr_version=3)

    root_group.create_group("real")
    root_group.create_group("real/impa/impb/impc")
    root_group.create_dataset("real/impdata/impdatab/baz", shape=100, chunks=10)
    imp_group = root_group.create_group("implicit/group")
    imp_group.create_group("a/b/c/d")
    root_group.create_dataset("baz", shape=100, chunks=10)

    assert sorted(list(root_group)) == sorted(["baz", "implicit", "real"])

    # test list_dir on the root dir
    exp_files, exp_dirs = (["meta/root/real.group.json", "meta/root/baz.array.json"], ["meta/root/implicit/", "meta/root/real/"])
    files, dirs = store.list_dir("meta/root/")
    assert sorted(files) == sorted(exp_files)
    assert sorted(dirs) == sorted(exp_dirs)

    # test list_dir on the implicit dir
    exp_files, exp_dirs = (["meta/root/implicit/group.group.json"], ["meta/root/implicit/group/"])
    files, dirs = store.list_dir("meta/root/implicit/")
    assert sorted(files) == sorted(exp_files)
    assert sorted(dirs) == sorted(exp_dirs)

    # implicit with nesting
    exp_files, exp_dirs = (["meta/root/implicit/group.group.json"], ["meta/root/implicit/group/"])
    files, dirs = store.list_dir("meta/root/implicit/")
    assert sorted(files) == sorted(exp_files)
    assert sorted(dirs) == sorted(exp_dirs)

    # test list_dir on the explicit dir
    exp_files, exp_dirs = ([], ["meta/root/implicit/group/a/b/c/"])
    files, dirs = store.list_dir("meta/root/implicit/group/a/b/")
    assert sorted(files) == sorted(exp_files)
    assert sorted(dirs) == sorted(exp_dirs)

    # test group_keys on the root
    assert sorted(list(root_group.group_keys())) == sorted(["implicit", "real"])

    # test listdir
    assert sorted(store.listdir("meta/root/")) == sorted(["baz.array.json", "implicit", "real.group.json", "real"])
    assert sorted(store.listdir("meta/root/implicit/group")) == sorted(["a"])
    assert sorted(store.listdir("meta/root/real")) == sorted(["impa", "impdata"])
    assert sorted(store.listdir("meta/root/real/impdata/impdatab")) == sorted(["baz.array.json"])
    assert sorted(store.listdir("meta/root/real/impdata/impdatab/baz")) == sorted([])

    # test list_prefix
    assert sorted(store.list_prefix("meta/root")) == sorted(
        [
            "meta/root.group.json",
            "meta/root/baz.array.json",
            "meta/root/implicit/group.group.json",
            "meta/root/implicit/group/a/b/c/d.group.json",
            "meta/root/real.group.json",
            "meta/root/real/impa/impb/impc.group.json",
            "meta/root/real/impdata/impdatab/baz.array.json",
        ]
    )
