import re
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from os.path import basename
from typing import Callable, Tuple, Union

import numpy as np
import pytest
import zarr
from numpy.testing import assert_array_equal
from tests.v1.helpers.test_utils import metastore_params_http_slow

from arraylake.metastore.abc import NoSourceToRename
from arraylake.repos.v1.types import Path


def maybe_commit(repo, should_commit):
    if should_commit:
        repo.commit(f"Commit {uuid.uuid4()}")


@pytest.mark.parametrize("committing", [False, True], ids=["not_committing", "committing"])
def test_group_move(new_sync_repo, committing) -> None:
    # This test was adapted, mostly verbatim, from
    # https://github.com/zarr-developers/zarr-python/blob/6ec746ef1242dd9fec26b128cc0b3455d28ad6f0/zarr/tests/test_hierarchy.py#L907
    g = new_sync_repo.root_group
    data = np.arange(100)
    g["boo"] = data
    maybe_commit(new_sync_repo, committing)

    data = np.arange(100)
    g["foo"] = data
    maybe_commit(new_sync_repo, committing)

    # We have /foo and /boo arrays

    g.move("foo", "bar")
    # We have have /boo and /bar arrays
    assert "foo" not in g
    assert "bar" in g
    assert_array_equal(data, g["bar"])
    maybe_commit(new_sync_repo, committing)

    g.move("bar", "foo/bar")
    # We have have /boo and /foo/bar arrays
    assert "bar" not in g
    assert "foo" in g
    assert "foo/bar" in g
    assert isinstance(g["foo"], zarr.Group)
    assert_array_equal(data, g["foo/bar"])
    maybe_commit(new_sync_repo, committing)

    g.move("foo", "foo2")
    # We have have /boo and /foo2/bar arrays
    assert "foo" not in g
    assert "foo/bar" not in g
    assert "foo2" in g
    assert "foo2/bar" in g
    assert isinstance(g["foo2"], zarr.Group)
    assert_array_equal(data, g["foo2/bar"])
    maybe_commit(new_sync_repo, committing)

    g2 = g["foo2"]
    g2.move("bar", "/bar")
    # We have have /boo and /bar arrays
    assert "foo2" in g
    assert "foo2/bar" not in g
    maybe_commit(new_sync_repo, committing)

    # This is a change from the upstream test
    assert "bar" in g

    assert "meta/root/bar.array.json" in g._store
    if g._chunk_store:
        assert "data/root/bar/c0" in g._chunk_store
    else:
        assert "data/root/bar/c0" in g._store
    assert isinstance(g["foo2"], zarr.Group)
    assert_array_equal(data, g["bar"])

    with pytest.raises(ValueError):
        g2.move("bar", "bar2")

    with pytest.raises(ValueError):
        g.move("bar", "boo")


# TODO: we disable http_metastore because it's too slow for this test. Reenable when it's faster
@pytest.mark.parametrize("metastore_class_and_config", metastore_params_http_slow)
@pytest.mark.parametrize("committing", [False, True], ids=["not_committing", "committing"])
def test_store_rename(new_sync_repo, committing) -> None:
    # This test was adapted, from https://github.com/zarr-developers/zarr-python/blob/6ec746ef1242dd9fec26b128cc0b3455d28ad6f0/zarr/tests/test_storage.py#L412
    store = new_sync_repo.store
    root = "meta/root/"

    store[root + "a"] = '{"a":1}'
    store[root + "b"] = '{"b":1}'
    maybe_commit(new_sync_repo, committing)
    store[root + "c/d"] = '{"c":1}'
    maybe_commit(new_sync_repo, committing)
    store[root + "c/e/f"] = '{"d":1}'
    maybe_commit(new_sync_repo, committing)
    store[root + "c/e/g"] = '{"e":1}'
    maybe_commit(new_sync_repo, committing)

    store.rename("c/e", "c/e2")
    maybe_commit(new_sync_repo, committing)
    assert root + "c/d" in store
    assert root + "c/e" not in store
    assert root + "c/e/f" not in store
    assert root + "c/e/g" not in store
    assert root + "c/e2" not in store
    assert root + "c/e2/f" in store
    assert root + "c/e2/g" in store
    store.rename("c/e2", "c/e")
    assert root + "c/d" in store
    assert root + "c/e2" not in store
    assert root + "c/e2/f" not in store
    assert root + "c/e2/g" not in store
    assert root + "c/e" not in store
    assert root + "c/e/f" in store
    assert root + "c/e/g" in store
    maybe_commit(new_sync_repo, committing)
    store.rename("c", "c1/c2/c3")
    maybe_commit(new_sync_repo, committing)
    assert root + "a" in store
    assert root + "c" not in store
    assert root + "c/d" not in store
    assert root + "c/e" not in store
    assert root + "c/e/f" not in store
    assert root + "c/e/g" not in store
    assert root + "c1" not in store
    assert root + "c1/c2" not in store
    assert root + "c1/c2/c3" not in store
    assert root + "c1/c2/c3/d" in store
    assert root + "c1/c2/c3/e" not in store
    assert root + "c1/c2/c3/e/f" in store
    assert root + "c1/c2/c3/e/g" in store
    store.rename("c1/c2/c3", "c")
    maybe_commit(new_sync_repo, committing)
    assert root + "c" not in store
    assert root + "c/d" in store
    assert root + "c/e" not in store
    assert root + "c/e/f" in store
    assert root + "c/e/g" in store
    assert root + "c1" not in store
    assert root + "c1/c2" not in store
    assert root + "c1/c2/c3" not in store
    assert root + "c1/c2/c3/d" not in store
    assert root + "c1/c2/c3/e" not in store
    assert root + "c1/c2/c3/e/f" not in store
    assert root + "c1/c2/c3/e/g" not in store


@pytest.mark.parametrize("committing", [False, True], ids=["not_committing", "committing"])
def test_move_then_delete(new_sync_repo, committing) -> None:
    root = new_sync_repo.root_group
    data = np.arange(100)
    root["array"] = data
    maybe_commit(new_sync_repo, committing)

    zarr.group(store=new_sync_repo.store, path="group")
    maybe_commit(new_sync_repo, committing)

    root.move("array", "array_moved")
    maybe_commit(new_sync_repo, committing)
    root.move("group", "group_moved")
    maybe_commit(new_sync_repo, committing)

    assert len([g for g in root.groups()]) > 0
    assert len([a for a in root.arrays()]) > 0

    del root["array_moved"]
    maybe_commit(new_sync_repo, committing)
    del root["group_moved"]
    maybe_commit(new_sync_repo, committing)
    assert [g for g in root.groups()] == []
    assert [a for a in root.arrays()] == []


@pytest.mark.parametrize("committing", [False, True], ids=["not_committing", "committing"])
def test_delete_then_move(new_sync_repo, committing) -> None:
    root = new_sync_repo.root_group
    data = np.arange(100)
    root["array"] = data
    maybe_commit(new_sync_repo, committing)

    zarr.group(store=new_sync_repo.store, path="group")
    maybe_commit(new_sync_repo, committing)

    del root["array"]
    maybe_commit(new_sync_repo, committing)
    del root["group"]
    maybe_commit(new_sync_repo, committing)

    with pytest.raises(ValueError, match="does not exist"):
        root.move("array", "array_moved")

    with pytest.raises(ValueError, match="does not exist"):
        root.move("group", "group_moved")


@pytest.mark.parametrize("committing", [False, True], ids=["not_committing", "committing"])
def test_add_to_source_of_a_move(new_sync_repo, committing) -> None:
    root = new_sync_repo.root_group

    zarr.group(store=new_sync_repo.store, path="group")
    maybe_commit(new_sync_repo, committing)
    zarr.group(store=new_sync_repo.store, path="group")
    data = np.arange(100)
    root["array"] = data
    maybe_commit(new_sync_repo, committing)

    root.move("group", "group_moved")
    root.move("array", "array_moved")

    zarr.group(store=new_sync_repo.store, path="group")
    maybe_commit(new_sync_repo, committing)
    zarr.group(store=new_sync_repo.store, path="group")
    data = np.arange(100)
    root["array"] = data
    maybe_commit(new_sync_repo, committing)

    assert sorted([g for (g, _) in root.groups()]) == sorted(["group", "group_moved"])
    assert sorted([a for (a, _) in root.arrays()]) == sorted(["array", "array_moved"])


def test_move_to_invalid_name(new_sync_repo) -> None:
    root = new_sync_repo.root_group
    zarr.group(store=new_sync_repo.store, path="group")
    with pytest.raises(ValueError):
        root.move("group", "not/./valid")
    with pytest.raises(ValueError):
        root.move("group", "not/../valid")


@dataclass
class MoveCommandSpec:
    """Represents a zarr move operation. Used to parametrize test_move_command test.

    This object represent the following operations:
    ```
        group = zarr.open_group(path=self.group, mode="r+")
        group.move(self.source, self.destination)
    ```

    Attributes:
      group: A `zarr.Group` will be instantiated at this path, and a
             `zarr.Group.move` operation will be executed on it.
      source: Source path for the move operation.
      destination: Destination path for the move operation.
      should_fail: If truethy, assert that the operation raises.
                   If Callable, also call it with the exception as argument.
    """

    group: Path
    source: Path
    destination: Path
    should_fail: Union[bool, Callable[[Exception], None]] = False


@dataclass
class MoveTestSpec:
    """Used to parametrize `test_move_command` test. Represents the setup,
    execution and assertions of a zarr move test.

    Attributes:
      explicit_groups: These groups will be created explicitly, and in order, as a first step in the test.
      arrays: These arrays will be initialized with random data and 2 chunks, after groups are created.
      move: A list of move operations to execute
      expected_arrays: The existence of store keys for all these arrays will be asserted
      expected_groups: The existence of store keys for all these groups will be asserted
      case: Used for test reporting and selection


    Additionally, it will be asserted that no other keys are present in the store.
    """

    explicit_groups: Iterable[Path]
    arrays: Iterable[Path]
    move: Iterable[MoveCommandSpec]
    expected_arrays: Iterable[Path]
    expected_groups: Iterable[Path]
    case: str = None

    def test_id(self):
        return re.sub(r"\W", "_", self.case)


def valid_no_source_to_rename_error(err):
    if not isinstance(err, NoSourceToRename):
        assert isinstance(err, ValueError)
        assert "No source" in str(err)


# TODO: we disable http_metastore because it's too slow for this test. Reenable when it's faster
@pytest.mark.parametrize("metastore_class_and_config", metastore_params_http_slow)
@pytest.mark.parametrize("committing", [False, True], ids=["not_committing", "committing"])
@pytest.mark.parametrize(
    # We intentionally include objects around the source of the move, to verify
    # they are not being affected. In particular we make those objects names
    # have the move source as a prefix of their paths
    "spec",
    [
        MoveTestSpec(
            case="Error on attempt to move self",
            explicit_groups=["/", "foo"],
            arrays=[],
            move=[MoveCommandSpec("/", "foo", "foo", should_fail=True)],
            expected_arrays=[],
            expected_groups=["/", "/foo"],
        ),
        MoveTestSpec(
            case="Error on attempt to move to existing array",
            explicit_groups=["/", "source"],
            arrays=["/destination"],
            move=[MoveCommandSpec("/", "source", "destination", should_fail=True)],
            expected_arrays=["/destination"],
            expected_groups=["/", "/source"],
        ),
        MoveTestSpec(
            case="Error on attempt to move to root",
            explicit_groups=["/"],
            arrays=["/array"],
            move=[MoveCommandSpec("/", "array", "/", should_fail=True)],
            expected_arrays=["/array"],
            expected_groups=["/"],
        ),
        # this is the behavior MemoryStoreV3 has
        MoveTestSpec(
            case="Error on attempt to move root to group",
            explicit_groups=["/"],
            arrays=[],
            move=[MoveCommandSpec("/", "", "foo", should_fail=valid_no_source_to_rename_error)],
            expected_arrays=[],
            expected_groups=["/"],
        ),
        MoveTestSpec(
            case="Error on attempt to move to root as empty dir",
            explicit_groups=["/"],
            arrays=["/array"],
            move=[MoveCommandSpec("/", "array", "", should_fail=True)],
            expected_arrays=["/array"],
            expected_groups=["/"],
        ),
        MoveTestSpec(
            case="Error on attempt to move to empty name",
            explicit_groups=["/", "/foo", "/foo/bar"],
            arrays=[],
            move=[MoveCommandSpec("/foo", "bar", "", should_fail=True)],
            expected_arrays=[],
            expected_groups=["/", "/foo", "/foo/bar"],
        ),
        # error on attemp to move array to existing group without naming the destination array name
        # (it doesn't put it inside but fails, it should be `move source destination/source`)
        MoveTestSpec(
            case="Error on attempt to move array without naming the destination",
            explicit_groups=["/", "destination"],
            arrays=["/source"],
            move=[MoveCommandSpec("/", "source", "destination/", should_fail=True)],
            expected_arrays=["/source"],
            expected_groups=["/", "/destination"],
        ),
        MoveTestSpec(
            case="Rename an array from the root",
            explicit_groups=["/", "foo", "foo/source3"],
            arrays=["foo/source", "/foo/source2"],
            move=[MoveCommandSpec("/", "foo/source", "foo/target")],
            expected_arrays=["/foo/source2", "/foo/target"],
            expected_groups=["/", "/foo", "/foo/source3"],
        ),
        MoveTestSpec(
            case="Rename a group from the root",
            explicit_groups=["/", "foo", "foo/source", "foo/source/inner", "foo/source3"],
            arrays=["/foo/source2", "/foo/source/some-array"],
            move=[MoveCommandSpec("/", "foo/source", "foo/target")],
            expected_arrays=["/foo/source2", "/foo/target/some-array"],
            expected_groups=["/", "/foo", "/foo/target", "/foo/source3", "/foo/target/inner"],
        ),
        MoveTestSpec(
            case="Rename an array from its own directory",
            explicit_groups=["/", "foo", "foo/source3"],
            arrays=["/foo/source", "/foo/source2"],
            move=[MoveCommandSpec("/foo", "source", "target")],
            expected_arrays=["/foo/source2", "/foo/target"],
            expected_groups=["/", "/foo", "/foo/source3"],
        ),
        MoveTestSpec(
            case="Rename a group from its own directory",
            explicit_groups=["/", "foo", "foo/source", "foo/source/inner", "foo/source3"],
            arrays=["/foo/source2", "/foo/source/some-array"],
            move=[MoveCommandSpec("/foo", "source", "target")],
            expected_arrays=["/foo/source2", "/foo/target/some-array"],
            expected_groups=["/", "/foo", "/foo/target", "/foo/source3", "/foo/target/inner"],
        ),
        MoveTestSpec(
            case="Move an array from the root, nesting it in an implicit group",
            explicit_groups=["/", "foo", "foo/source3"],
            arrays=["/foo/source", "/foo/source2"],
            move=[MoveCommandSpec("/", "foo/source", "foo/bar/baz/target")],
            expected_arrays=["/foo/source2", "/foo/bar/baz/target"],
            expected_groups=["/", "/foo", "/foo/source3", "/foo/bar/baz"],
        ),
        MoveTestSpec(
            case="Move an array from its own directory, nesting it in an implicit group",
            explicit_groups=["/", "foo", "foo/source3"],
            arrays=["/foo/source", "/foo/source2"],
            move=[MoveCommandSpec("/foo", "source", "bar/baz/target")],
            expected_arrays=["/foo/source2", "/foo/bar/baz/target"],
            expected_groups=["/", "/foo", "/foo/source3", "/foo/bar/baz"],
        ),
        MoveTestSpec(
            case="Move a group from the root, nesting it in an implicit group",
            explicit_groups=["/", "foo", "foo/source", "foo/source3"],
            arrays=["/foo/source2", "/foo/source/array"],
            move=[MoveCommandSpec("/", "foo/source", "foo/bar/baz/target")],
            expected_arrays=["/foo/source2", "/foo/bar/baz/target/array"],
            expected_groups=["/", "/foo", "/foo/source3", "/foo/bar/baz", "/foo/bar/baz/target"],
        ),
        MoveTestSpec(
            case="Move a group from its own dir, nesting it in an implicit group",
            explicit_groups=["/", "foo", "foo/source", "foo/source3"],
            arrays=["/foo/source2", "/foo/source/array"],
            move=[MoveCommandSpec("/foo", "source", "bar/baz/target")],
            expected_arrays=["/foo/source2", "/foo/bar/baz/target/array"],
            expected_groups=["/", "/foo", "/foo/source3", "/foo/bar/baz", "/foo/bar/baz/target"],
        ),
        MoveTestSpec(
            case="Regression test for a bug property tests found",
            explicit_groups=["/", "/1"],
            arrays=["/1/0"],
            move=[
                MoveCommandSpec("/", "1/0", "0"),
                MoveCommandSpec("/", "/0", "1/0"),
            ],
            expected_arrays=["/1/0"],
            expected_groups=["/", "/1"],
        ),
        MoveTestSpec(
            case="Unnest multiple objects",
            explicit_groups=[
                "/",
                "/some/dir",
                "/some/dir/foo/source1",
                "/some/dir/foo/bar/source2",
                "/some/dir/foo/baz",
                "/some/dir/foo/baz/source3",
            ],
            arrays=["/source_a", "/some/source_b", "/some/dir/source_c", "/some/dir/foo/baz/source3/array"],
            move=[
                # We have to be explicit about the target name, saying "destination/" is not enough
                MoveCommandSpec("/", "some/dir/foo/source1", "destination/source1"),
                MoveCommandSpec("/", "some/dir/foo/bar/source2", "destination/source2"),
                MoveCommandSpec("/", "some/dir/foo/baz/source3", "destination/source3"),
            ],
            expected_arrays=["/source_a", "/some/source_b", "/some/dir/source_c", "/destination/source3/array"],
            expected_groups=[
                "/",
                "/some/dir",
                "/some/dir/foo/baz",
                "/destination",
                "/destination/source1",
                "/destination/source2",
                "destination/source3",
            ],
        ),
        # succession of moves of implicit groups into implicit groups, back and forth
        MoveTestSpec(
            case="Moves back and forth of implicit groups into implicit groups",
            explicit_groups=["/", "foo/source", "foo/source2"],
            arrays=["/foo/source/array"],
            move=[
                MoveCommandSpec("/", "foo/source", "bar/baz/target"),  # this triggers creation of /bar/baz group
                MoveCommandSpec("/", "bar/baz/target", "/foo/source"),  # this triggers creation of /foo group
                MoveCommandSpec("/", "foo/source", "some/other/place/target"),  # this triggers creation of /some/other/place group
                MoveCommandSpec(
                    "/some/other/place", "target", "even/deeper/new-target"
                ),  # this triggers creation of /some/other/place/even/deeper
            ],
            expected_arrays=["/some/other/place/even/deeper/new-target/array"],
            expected_groups=[
                "/",
                "foo/source2",
                "bar/baz",
                "foo",
                "some/other/place",
                "some/other/place/even/deeper",
                "some/other/place/even/deeper/new-target",
            ],
        ),
        MoveTestSpec(
            # This is a regression test for a bug we found
            case="Repeated move source",
            explicit_groups=["/", "rasm"],
            arrays=["/rasm/array"],
            move=[
                MoveCommandSpec("/", "rasm", "foo"),
                MoveCommandSpec("/", "foo", "bar"),
                MoveCommandSpec("/", "bar", "rasm"),
                MoveCommandSpec("/", "rasm", "bar/foo"),
                MoveCommandSpec("/", "bar", "rasm"),
            ],
            expected_arrays=["/rasm/foo/array"],
            expected_groups=["/", "/rasm", "/rasm/foo"],
        ),
        MoveTestSpec(
            case="Repeated move destination",
            explicit_groups=["/", "rasm"],
            arrays=["/rasm/array"],
            move=[
                MoveCommandSpec("/", "rasm", "foo"),
                MoveCommandSpec("/", "foo", "bar"),
                MoveCommandSpec("/", "bar", "foo"),
            ],
            expected_arrays=["/foo/array"],
            expected_groups=["/", "/foo"],
        ),
    ],
    ids=lambda spec: spec.test_id(),
)
def test_move_command(new_sync_repo, committing, spec):
    """Apply the operations defined in the spec and assert spec.expected_groups and spec.expected_arrays.

    If committing=True runs a commit after each move operation, before the assertions.
    """

    def combine_paths(*paths):
        return "/".join(paths).replace("//", "/")

    def array_keys(path):
        return [
            combine_paths("meta/root", f"{path}.array.json"),
            combine_paths("data/root", path, "c0"),
            combine_paths("data/root", path, "c1"),
        ]

    def group_keys(path):
        if path == "" or path == "/":
            return ["meta/root.group.json"]
        return [
            combine_paths("meta/root", f"{path}.group.json"),
        ]

    def create_array(path):
        zarr.array(np.random.rand(4), chunks=(2), path=path, store=new_sync_repo.store)
        return array_keys(path)

    def create_group(path):
        zarr.group(store=new_sync_repo.store, path=path)
        return group_keys(path)

    for group_path in spec.explicit_groups:
        create_group(group_path)

    if spec.explicit_groups:
        maybe_commit(new_sync_repo, committing)

    for array_path in spec.arrays:
        create_array(array_path)

    if spec.arrays:
        maybe_commit(new_sync_repo, committing)

    expected_keys = ["zarr.json"]
    for group_path in spec.expected_groups:
        expected_keys += group_keys(group_path)
    for array_path in spec.expected_arrays:
        expected_keys += array_keys(array_path)

    for move_spec in spec.move:
        group = zarr.open_group(path=move_spec.group, mode="r+", store=new_sync_repo.store)
        if move_spec.should_fail:
            with pytest.raises(Exception) as ex_info:
                group.move(move_spec.source, move_spec.destination)
            if callable(move_spec.should_fail):
                move_spec.should_fail(ex_info.value)
        else:
            group.move(move_spec.source, move_spec.destination)
            maybe_commit(new_sync_repo, committing)

    assert sorted(new_sync_repo.store.list_prefix("")) == sorted(expected_keys)
