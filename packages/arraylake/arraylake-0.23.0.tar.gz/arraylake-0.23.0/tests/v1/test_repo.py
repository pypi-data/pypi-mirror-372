import copy
import itertools
import pickle
import secrets
import warnings
from contextlib import asynccontextmanager
from contextlib import nullcontext as does_not_raise
from datetime import timedelta
from functools import partial
from unittest.mock import patch

import boto3
import bson
import numpy as np
import pytest
from tests.v1.helpers.test_utils import (
    metastore_params,
    metastore_params_only_mongo,
    metastore_params_sessions,
)

from .. import has_ipytree, has_rich

from arraylake import config
from arraylake.client import Client
from arraylake.exceptions import (
    CommitFailedError,
    DocumentNotFoundError,
    InvalidPrefixError,
)
from arraylake.repos.v1.chunkstore import BaseChunkstore
from arraylake.repos.v1.repo import (
    AsyncRepo,
    LocalReadSession,
    LocalWriteSession,
    _dispatch_over_collections,
)
from arraylake.repos.v1.types import Branch, ChunkHash, ReferenceData, SessionID
from arraylake.types import Author


def copy_async_repo(arepo):
    db_class = type(arepo.db)
    db_copy = db_class(arepo.db._config)
    current = arepo.chunkstore.object_store
    cs_copy = BaseChunkstore(
        type(current)(bucket_name=current.bucket_name, kwargs=current.constructor_kwargs),
        prefix=arepo.chunkstore.prefix,
        schema_version=arepo.chunkstore.schema_version,
        inline_threshold_bytes=arepo.chunkstore.inline_threshold_bytes,
    )
    repo_name = arepo.repo_name
    author = arepo.author
    return AsyncRepo(db_copy, cs_copy, repo_name, author)


@pytest.mark.asyncio
@pytest.mark.add_object_store("gs")
async def test_async_repo_serialization(new_async_repo):
    # new_async_repo is not checked out by default.
    await new_async_repo.checkout()
    serialized = pickle.dumps(new_async_repo)
    async_repo_2 = pickle.loads(serialized)
    # confirm we did not serialize the full commit history
    assert async_repo_2._commit_data is None


@pytest.mark.add_object_store("gs")
def test_sync_repo_serialization(new_sync_repo):
    serialized = pickle.dumps(new_sync_repo)
    repo2 = pickle.loads(serialized)

    # confirm we did not serialize the full commit history
    assert repo2._arepo._commit_data is None

    # test that serialized repo is not in a committable state
    repo2._set_doc("/atlantic.json", content={"foo": 1, "bar": 2})
    repo2.commit("foo")


@pytest.mark.asyncio
@pytest.mark.add_object_store("gs")
async def test_ping_async(new_async_repo):
    await new_async_repo.ping()


@pytest.mark.asyncio
@pytest.mark.add_object_store("gs")
async def test_ping_sync(new_sync_repo):
    new_sync_repo.ping()


@pytest.mark.asyncio
async def test_checkout_main_in_empty_repo(new_sync_repo):
    new_sync_repo.checkout()


@pytest.mark.asyncio
async def test_checkout_main_with_commits_to_other_branches(new_sync_repo):
    new_sync_repo.new_branch("new_branch")
    new_sync_repo._set_doc("/atlantic.json", content={"foo": 1, "bar": 2})
    new_sync_repo.commit("commit in new_branch")
    new_sync_repo.checkout()
    new_sync_repo.checkout("main")


@asynccontextmanager
async def with_old_commit(repo):
    with patch.object(repo, "_single_commit", repo._old_style_single_commit):
        with patch.object(repo, "_rebase", repo._old_style_rebase):
            yield repo


@asynccontextmanager
async def with_new_commit(repo):
    yield repo


@pytest.mark.asyncio
@pytest.mark.parametrize("overrides", [with_new_commit, with_old_commit])
async def test_async_docs_lifecycle(new_async_repo, overrides):
    await new_async_repo.checkout()
    async with overrides(new_async_repo) as repo:
        with pytest.raises(DocumentNotFoundError):
            await repo._get_doc("/atlantic.json")
        await repo._set_doc("/atlantic.json", content={"foo": 1, "bar": 2})
        assert await repo._get_doc("/atlantic.json") == {"foo": 1, "bar": 2}
        status = await repo.status()
        assert status.modified_paths == [("/atlantic.json", False)]
        # overwrite the same session
        await repo._set_doc("/atlantic.json", content={"foo": 2, "bar": 3})
        assert await repo._get_doc("/atlantic.json") == {"foo": 2, "bar": 3}
        # regression test for https://github.com/earth-mover/arraylake/issues/354
        status = await repo.status()
        assert status.modified_paths == [("/atlantic.json", False)]
        commit_0 = await repo.commit("first commit")
        # writing a different doc forces traversal of the parent_commit tree
        await repo._set_doc("/indian.json", content={})
        await repo.commit("added a new doc")
        assert await repo._get_doc("/atlantic.json") == {"foo": 2, "bar": 3}
        await repo._set_doc("/atlantic.json", content={"foo": 2, "bar": 2})
        assert await repo._get_doc("/atlantic.json") == {"foo": 2, "bar": 2}
        commit_1 = await repo.commit("replaced a doc")
        assert await repo._get_doc("/atlantic.json") == {"foo": 2, "bar": 2}
        with pytest.warns(UserWarning, match="not on a branch tip"):
            await repo.checkout(commit_0)
        assert await repo._get_doc("/atlantic.json") == {"foo": 2, "bar": 3}
        with pytest.raises(IOError):
            await repo._set_doc("/unwriteable.json", content={"a": 1})
        with pytest.raises(IOError):
            await repo._del_doc("/atlantic.json")
        with pytest.raises(RuntimeError, match="not on a branch tip"):
            await repo.commit("this won't work")
        await repo.checkout("main")
        await repo._del_doc("/atlantic.json")
        with pytest.raises(DocumentNotFoundError):
            await repo._get_doc("/atlantic.json")
        await repo.commit("deleted a doc")
        with pytest.raises(ValueError, match="not found"):
            await repo.checkout("non-existent-ref")
        await repo.new_branch("dev")
        with pytest.raises(ValueError, match="already exists"):
            await repo.new_branch("dev")
        await repo._set_doc("/pacific.json", content={"foo": 2, "bar": 2})
        await repo.commit("commit on a new branch")
        await repo.checkout("main")
        with pytest.raises(DocumentNotFoundError):
            await repo._get_doc("/pacific.json")
        # multi getter / setter methods
        lake_docs = {
            "/lakes/champlain.json": {"color": "green"},
            "/lakes/superior.json": {"color": "brown"},
            "/lakes/washington.json": {"color": "blue"},
        }
        await repo._set_docs(lake_docs)
        assert await repo._get_docs(list(lake_docs)) == lake_docs
        await repo.commit("replaced a bunch of docs")
        await repo._del_docs(["/lakes/superior.json", "/lakes/washington.json"])
        assert await repo._get_docs(list(lake_docs)) == {"/lakes/champlain.json": {"color": "green"}}


@pytest.mark.parametrize("metastore_class_and_config", metastore_params + metastore_params_sessions)
@pytest.mark.parametrize("checkout", [True, False])
def test_sync_docs_lifecycle(new_sync_repo, checkout):
    repo = new_sync_repo
    if checkout:
        repo.checkout()
    with pytest.raises(DocumentNotFoundError):
        repo._get_doc("/atlantic.json")
    repo._set_doc("/atlantic.json", content={"foo": 1, "bar": 2})
    assert repo._get_doc("/atlantic.json") == {"foo": 1, "bar": 2}
    commit_0 = repo.commit("first commit")
    # writing a different doc forces traversal of the parent_commit tree
    repo._set_doc("/indian.json", content={})
    repo.commit("added a doc")
    assert repo._get_doc("/atlantic.json") == {"foo": 1, "bar": 2}
    repo._set_doc("/atlantic.json", content={"foo": 2, "bar": 2})
    assert repo._get_doc("/atlantic.json") == {"foo": 2, "bar": 2}
    commit_1 = repo.commit("replaced a doc")
    assert repo._get_doc("/atlantic.json") == {"foo": 2, "bar": 2}
    with pytest.warns(UserWarning, match="not on a branch tip"):
        repo.checkout(commit_0)
    assert repo._get_doc("/atlantic.json") == {"foo": 1, "bar": 2}
    repo.checkout("main")
    repo._del_doc("/atlantic.json")
    with pytest.raises(DocumentNotFoundError):
        repo._get_doc("/atlantic.json")
    repo.commit("deleted a doc")
    repo.new_branch("dev")
    repo._set_doc("/pacific.json", content={"foo": 2, "bar": 2})
    repo.commit("added a new doc")
    repo.checkout("main")
    with pytest.raises(DocumentNotFoundError):
        repo._get_doc("/pacific.json")
    # multi getter / setter methods
    lake_docs = {
        "/lakes/champlain.json": {"color": "green"},
        "/lakes/superior.json": {"color": "brown"},
        "/lakes/washington.json": {"color": "blue"},
    }
    repo._set_docs(lake_docs)
    assert repo._get_docs(list(lake_docs)) == lake_docs
    repo.commit("set many docs")
    repo._del_docs(["/lakes/superior.json", "/lakes/washington.json"])
    assert repo._get_docs(list(lake_docs)) == {"/lakes/champlain.json": {"color": "green"}}


@pytest.mark.asyncio
@pytest.mark.parametrize("overrides", [with_new_commit, with_old_commit])
async def test_async_chunks_lifecycle(new_async_repo, overrides) -> None:
    await new_async_repo.checkout()
    async with overrides(new_async_repo) as repo:
        with pytest.raises(DocumentNotFoundError):
            await repo._get_chunk("/foo/bar/c0/0")

        key = "/foo/c0/1/1"
        data0 = b"\x00\x01\x02"
        await repo._set_chunk(key, data=data0)
        assert await repo._get_chunk(key) == data0
        assert await repo._get_chunk(key, validate=True) == data0
        commit_0 = await repo.commit("set some chunks")
        data1 = b"\x00\x01\x02\x03"
        await repo._set_chunk(key, data=data1)
        assert await repo._get_chunk(key) == data1
        commit_1 = await repo.commit("replaced a chunk")
        assert await repo._get_chunk(key) == data1
        with pytest.warns(UserWarning, match="not on a branch tip"):
            await repo.checkout(commit_0)
        assert await repo._get_chunk(key) == data0
        with pytest.raises(IOError):
            await repo._set_chunk(key, data=data0)
        await repo.checkout("main")
        assert await repo._get_chunk(key) == data1
        await repo._del_chunk(key)
        with pytest.raises(DocumentNotFoundError):
            assert await repo._get_chunk(key)

        # multi getter / setter methods
        multi_chunks = {
            "/foo/c0/0/0": b"\x00\x00\x00",
            "/foo/c0/0/1": b"\x00\x00\x01",
            "/foo/c0/0/2": b"\x00\x00\x02",
        }
        await repo._set_chunks(multi_chunks)
        assert await repo._get_chunks(list(multi_chunks)) == multi_chunks
        await repo.commit("set many chunks")
        await repo._del_chunks(["/foo/c0/0/0", "/foo/c0/0/2"])
        assert await repo._get_chunks(list(multi_chunks)) == {"/foo/c0/0/1": b"\x00\x00\x01"}

        hash = ChunkHash(method="sha256", token="abc")
        # ref_data = ReferenceData.new_materialized_v0(uri="s3://test/spam.hdf", length=1000, hash=hash)
        # await repo._set_chunk_ref("foo/bar/c0/1", reference_data=ref_data)
        # await repo._set_chunk_refs({"foo/baz/c0/2": ref_data})

        ref_data = ReferenceData.new_materialized_v1(length=1000, hash=hash, sid=SessionID("abc"))
        await repo._set_chunk_ref("foo/bar/c0/1", reference_data=ref_data)
        await repo._set_chunk_refs({"foo/baz/c0/2": ref_data})


def test_sync_chunks_lifecycle(new_sync_repo) -> None:
    repo = new_sync_repo
    with pytest.raises(DocumentNotFoundError):
        repo._get_chunk("/foo/bar/c0/0")
    key = "/foo/c0/1/1"
    data0 = b"\x00\x01\x02"
    repo._set_chunk(key, data=data0)
    assert repo._get_chunk(key) == data0
    commit_0 = repo.commit("set a chunk")
    data1 = b"\x00\x01\x02\x03"
    repo._set_chunk(key, data=data1)
    assert repo._get_chunk(key) == data1
    commit_1 = repo.commit("repalced a chunk")
    assert repo._get_chunk(key) == data1
    with pytest.warns(UserWarning, match=r"You are not on a branch tip.*"):
        repo.checkout(commit_0)
    assert repo._get_chunk(key) == data0
    repo.checkout("main")
    assert repo._get_chunk(key) == data1
    repo._del_chunk(key)
    with pytest.raises(DocumentNotFoundError):
        repo._get_chunk(key)

    # multi getter / setter methods
    multi_chunks = {
        "/foo/c0/0/0": b"\x00\x00\x00",
        "/foo/c0/0/1": b"\x00\x00\x01",
        "/foo/c0/0/2": b"\x00\x00\x02",
    }
    repo._set_chunks(multi_chunks)
    assert repo._get_chunks(list(multi_chunks)) == multi_chunks
    repo.commit("set a bunch of chunks")
    repo._del_chunks(["/foo/c0/0/0", "/foo/c0/0/2"])
    assert repo._get_chunks(list(multi_chunks)) == {"/foo/c0/0/1": b"\x00\x00\x01"}

    hash = ChunkHash(method="sha256", token="abc")
    # ref_data = ReferenceData.new_materialized_v0(uri="s3://test/spam.hdf", length=1000, hash=hash)
    # repo._set_chunk_ref("foo/bar/c0/1", reference_data=ref_data)
    # repo._set_chunk_refs({"foo/baz/c1/2": ref_data})

    ref_data = ReferenceData.new_materialized_v1(length=1000, hash=hash, sid=SessionID("abc"))
    repo._set_chunk_ref("foo/bar/c0/1", reference_data=ref_data)
    repo._set_chunk_refs({"foo/baz/c1/2": ref_data})


@pytest.mark.asyncio
async def test_commit_metadata(new_async_repo):
    await new_async_repo.checkout()
    repo = new_async_repo
    assert len(list(await repo.commit_log())) == 0
    await repo._set_doc("/meta/root/foo.json", content={"a": 1})

    first_commit_id = await repo.commit("first commit")

    await repo._set_doc("/meta/root/bar.json", content={"a": 2})
    await repo._del_doc("/meta/root/foo.json")

    # TODO: make this more than a smoke test
    status = await repo.status()
    if has_rich:
        status.rich_output()
    status._repr_html_()

    next_commit_id = await repo.commit("Added a new doc, deleted an old one")

    commits = list(await repo.commit_log())
    assert len(commits) == 2

    # commits appear in reverse order

    assert commits[1].id == first_commit_id
    assert commits[1].message == "first commit"
    assert commits[1].session_start_time <= commits[1].commit_time
    # these are set in the repo constructor
    assert commits[1].author_name == "Test User"
    assert commits[1].author_email == "foo@icechunk.io"

    assert commits[0].id == next_commit_id
    assert commits[0].message.startswith("Added a new doc")
    assert commits[0].session_start_time <= commits[0].commit_time
    assert commits[0].author_name == "Test User"
    assert commits[0].author_email == "foo@icechunk.io"

    # TODO: make these more than smoke tests
    if has_rich:
        (await repo.commit_log()).rich_output()
    (await repo.commit_log())._repr_html_()


@pytest.mark.asyncio
async def test_empty_commits(new_async_repo):
    await new_async_repo.checkout()
    repo = new_async_repo
    assert len(list(await repo.commit_log())) == 0

    # first try empty commit on an empty repo
    with pytest.warns(UserWarning, match="No changes to commit"):
        commit_id = await repo.commit("Attempting to commit with no changes")
        assert commit_id is None

    # now a happy case commit
    await repo._set_doc("/meta/root/foo.json", content={"a": 1})
    first_commit_id = await repo.commit("first commit")
    commits = list(await repo.commit_log())
    assert len(commits) == 1

    # now am empty commit on top of an existing commit
    with pytest.warns(UserWarning, match="No changes to commit"):
        attempted_commit_id = await repo.commit("Attempting to commit again with no changes")
        assert attempted_commit_id == first_commit_id


@pytest.mark.asyncio
async def test_get_commits_sorted(new_async_repo):
    await new_async_repo.checkout()
    for i in range(13):
        await new_async_repo._set_doc("/meta/root/foo.json", content={"a": i})
        await new_async_repo.commit(f"commit {i=}")
    for size in [0, 1, 3, 13]:
        with config.set({"batch_size_for_commits": size}):
            commits = await new_async_repo.get_commits()
        assert all(tuple(newer.id > older.id for newer, older in itertools.pairwise(commits)))


@pytest.mark.asyncio
async def test_commit_metadata_users_apis(metastore_database, chunkstore_bucket):
    repo_name = "repo_test"
    human_author = Author(name="First Last", email="first-last@earthmover.io")
    machine_author = Author(email="svc-account@earthmover.io")
    r = partial(AsyncRepo, metastore_database, chunkstore_bucket, repo_name)

    repo = r(author=human_author)
    await repo.checkout()
    await repo._set_doc("/meta/root/foo.json", content={"a": 1})
    await repo.commit("first commit")

    repo = r(author=machine_author)
    await repo.checkout()
    await repo._set_doc("/meta/root/foo.json", content={"a": 2})
    await repo.commit("second commit - machine")

    commits = list(await repo.commit_log())
    assert len(commits) == 2
    human_commit = commits[1]
    machine_commit = commits[0]

    assert human_commit.author_name == "First Last"
    assert human_commit.author_email == "first-last@earthmover.io"
    assert human_commit.author_entry() == "First Last <first-last@earthmover.io>"

    assert not (machine_commit.author_name)
    assert machine_commit.author_email == "svc-account@earthmover.io"
    assert machine_commit.author_entry() == "<svc-account@earthmover.io>"


@pytest.mark.asyncio
async def test_status(new_async_repo: AsyncRepo):
    await new_async_repo.checkout()
    repo = new_async_repo
    ss = await repo.status()
    assert len(ss.modified_paths) == 0

    await repo._set_doc("/foo.json", content={"foo": 1})
    ss = await repo.status()
    assert len(ss.modified_paths) == 1

    docs = {f"/foo-{i}.json": {"foo": 1} for i in range(1500)}
    await repo._set_docs(docs)
    with pytest.warns(UserWarning, match="results were limited"):
        ss = await repo.status()

    # default enforced
    with pytest.warns(UserWarning, match="results were limited"):
        await repo.status()
        assert len(ss.modified_paths) == 1000

    # still configurable, no warning
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        ss = await repo.status(limit=2000)
    assert len(ss.modified_paths) == 1501

    # 0 respected
    with pytest.warns(UserWarning, match="results were limited"):
        ss = await repo.status(limit=0)
    assert len(ss.modified_paths) == 1501


@pytest.mark.asyncio
async def test_status_move_only(new_async_repo: AsyncRepo):
    await new_async_repo.checkout()
    await new_async_repo._set_doc("meta/root/foo.group.json", content={"foo": 1})
    commit = await new_async_repo.commit("add foo group")
    await new_async_repo._rename("foo", "bar")
    ss = await new_async_repo.status()
    assert sorted(ss.modified_paths) == sorted([("meta/root/bar.group.json", False), ("meta/root/foo.group.json", True)])


def test_session_accessor(new_sync_repo):
    new_sync_repo.checkout()
    assert isinstance(new_sync_repo.session, LocalWriteSession)
    new_sync_repo.checkout(for_writing=False)
    assert isinstance(new_sync_repo.session, LocalReadSession)


def test_reprs(new_sync_repo):
    repr(new_sync_repo)
    if has_rich:
        new_sync_repo.status().rich_output()
        new_sync_repo.commit_log.rich_output()
    new_sync_repo.status()._repr_html_()
    new_sync_repo.commit_log._repr_html_()

    new_sync_repo._set_doc("/foo.json", content={"foo": 1})
    commit_id1 = new_sync_repo.commit("Initial commit from repo1")

    assert str(commit_id1) in new_sync_repo.status()._repr_html_()


def test_fast_forward_sync(new_sync_repo):
    # this is just a smoke test
    new_sync_repo.fast_forward()
    with pytest.warns(UserWarning, match="No changes to commit."):
        new_sync_repo.commit("test commit", auto_ff=False)
    with pytest.warns(UserWarning, match="No changes to commit."):
        new_sync_repo.commit("another test commit")


@pytest.mark.asyncio
@pytest.mark.parametrize("overrides", [with_new_commit, with_old_commit])
async def test_fast_forward_async(new_async_repo, overrides):
    repo1 = new_async_repo
    await repo1.checkout()
    repo2 = copy_async_repo(repo1)
    await repo2.checkout()
    async with overrides(repo1) as repo1:
        async with overrides(repo2) as repo2:
            # check we can ff a branch with no commits
            await repo1._set_doc("/foo.json", content={"foo": 1})
            await repo1.commit("Initial commit from repo1")

            await repo1._set_doc("/foo.json", content={"foo": 1})
            await repo1.commit("Second commit from repo1")

            await repo2._set_doc("/bar.json", content={"foo": 1})
            await repo2.commit("Initial commit from repo2")


@pytest.mark.asyncio
async def test_fast_forward_race_condition_deterministic(new_async_repo):
    """Simulates a scenario with multiple committers achieving resolution.

    This test uses two repos: repo1, repo2. It patches the rebase call of repo2, such that
    when repo2 calls _rebase() it also triggers a write/commit from repo1. This tests the
    scenario of repo2 successfully updating its state, but that state changing prior to it
    attempting its next commit.
    """
    repo1 = new_async_repo
    await repo1.checkout()
    repo2 = copy_async_repo(repo1)
    await repo2.checkout()

    await repo1._set_doc(f"foo.json", content={"foo": "foo"})
    await repo1.commit(f"repo1: write1")

    # The following creates a function that can replace the built-in _rebase
    # method of our repo object. In addition to calling _rebase, it immediately
    # triggers a commit in a separate repo. This simulates the scenarios of a repo
    # being updated by a separate caller while the target repo is mid-process of
    # attempting to commit with its own view of the latest state.
    _original_rebase = repo2._rebase
    count = 0

    async def fake_rebase(*args, **kwargs):
        nonlocal count
        await _original_rebase(*args, **kwargs)
        if count == 0:
            await repo1._set_doc(f"baz.json", content={"foo": "foo"})
            await repo1.commit(f"repo1: write2")
            count += 1

    with patch.object(repo2, "_rebase", fake_rebase):
        await repo2._set_doc(f"bar.json", content={"foo": "foo"})
        await repo2.commit(f"repo2: write1")
        commits = list(await repo2.commit_log())
        messages = [c.message for c in commits]
        expected_messages_order = [
            "repo2: write1",
            "repo1: write2",
            "repo1: write1",
        ]
        assert expected_messages_order == messages


@pytest.mark.parametrize("config_name", ["max_commit_attempts", "commit_max_attempts"])
@pytest.mark.parametrize("attempts", [0, 1])
def test_commit_observes_maximum_retry_limit(new_sync_repo, config_name, attempts):
    repo1 = new_sync_repo
    repo2 = copy.deepcopy(repo1)
    repo1.checkout()
    repo2.checkout()

    repo1._set_doc("/foo.json", content={"foo": 1})
    repo1.commit("Initial commit from repo1")
    repo1._set_doc("/foo.json", content={"foo": 1})
    repo1.commit("Second commit from repo1")

    with config.set({config_name: attempts}):
        with pytest.raises(CommitFailedError):
            repo2._set_doc("/bar.json", content={"foo": 1})
            repo2.commit("Initial commit from repo1")


@pytest.mark.parametrize(
    "prefix,collection_names,exception_handler",
    [
        ("", ("chunks", "metadata"), does_not_raise()),
        ("meta", ("metadata",), does_not_raise()),
        ("meta/root", ("metadata",), does_not_raise()),
        ("data", ("chunks",), does_not_raise()),
        ("data/root", ("chunks",), does_not_raise()),
        ("foo", (), pytest.raises(InvalidPrefixError)),
    ],
)
@pytest.mark.asyncio
async def test_dispatch_over_collections(prefix, collection_names, exception_handler):
    async def awaitable_function(prefix, collection=None, foo=None):
        return collection, foo

    with exception_handler:
        result = _dispatch_over_collections(awaitable_function, prefix, foo="bar")
        assert len(result) == len(collection_names)
        for i, fn in enumerate(result):
            collection, foo = await fn
            assert foo == "bar"
            assert collection.name == collection_names[i]

    async def awaitable_generator(prefix, collection=None, foo=None):
        yield collection, foo

    with exception_handler:
        result = _dispatch_over_collections(awaitable_generator, prefix, foo="bar")
        assert len(result) == len(collection_names)
        for i, agen in enumerate(result):
            collection, foo = await agen.__anext__()
            assert foo == "bar"
            assert collection.name == collection_names[i]


def test_tags_with_branches(new_sync_repo):
    repo = new_sync_repo

    def apply_and_verify_tag(label, message=None):
        actual = repo.tag(label, message=message)
        commit = next(iter(repo.commit_log))
        assert actual.commit == commit
        assert actual.message == message
        assert actual.label == label
        repr_ = repo.commit_log._repr_html_()
        assert "Tags" in repr_
        assert any(tag.label == label for tag in repo.tags)
        assert label in repr_

    assert "Tags" not in new_sync_repo.commit_log._repr_html_()
    with pytest.raises(ValueError):
        # no commits to tag
        repo.tag("foo")

    repo.root_group.attrs["n"] = 1
    c1 = repo.commit("1")
    assert not repo.tags
    assert "Tags" not in new_sync_repo.commit_log._repr_html_()

    apply_and_verify_tag("c1")
    assert repo.tags

    with pytest.raises(ValueError):
        # tag already exists
        repo.tag("c1")

    with pytest.raises(ValueError):
        # clashes with protected branch name
        repo.tag("main")

    repo.root_group.attrs["n"] = 2
    c2 = repo.commit("2")
    apply_and_verify_tag("c2")
    repo.tag("c2.1", str(c2))

    with pytest.raises(ValueError):
        # bad commit id
        repo.tag("c2", str(bson.ObjectId()))

    # go back to c1 and make a new branch
    with pytest.warns(UserWarning):
        repo.checkout(c1)
    repo.new_branch("dev")
    repo.root_group.attrs["branch"] = "dev"

    repo.commit("3")
    apply_and_verify_tag("d1", message="zoo")
    with pytest.raises(ValueError):
        # clashes with branch name
        repo.tag("dev")

    with pytest.raises(ValueError):
        # invalid message, must be string
        # TODO: This is a pydantic ValidationError. Shall we raise a nicer ValueError?
        repo.tag("z", message=1)

    with pytest.raises(ValueError, match="The maximum allowed message"):
        repo.tag("z", message="_" * 6_000)

    with pytest.raises(ValueError):
        # branch with existing tag name
        repo.new_branch("d1")

    for tag in repo.tags:
        with pytest.warns(UserWarning, match="branch tip"):
            repo.checkout(tag.label)

    repo.new_branch("zoo")
    # no commits, so a DB entry is not created yet
    with pytest.raises(ValueError):
        repo.tag("zoo")

    repo.delete_tag("c1")
    # TODO: would be nice to have `"c1" not in repo.tags`
    assert all(tag.label != "c1" for tag in repo.tags)

    with pytest.raises(ValueError, match="Tag 'foo' does not exist."):
        repo.delete_tag("foo")


def test_commit_new_branch(new_sync_repo):
    repo = new_sync_repo

    repo.root_group.attrs["n"] = 1
    c1 = repo.commit("1")

    repo.root_group.attrs["n"] = 2
    with pytest.raises(ValueError, match="The maximum allowed message"):
        repo.commit("_" * 6_000)
    c2 = repo.commit("2")

    # go back to c1 and make a new branch
    with pytest.warns(UserWarning):
        repo.checkout(c1)
    repo.new_branch("dev")
    repo.root_group.attrs["branch"] = "dev"
    d1 = repo.commit("1")

    assert sorted(repo.branches, key=lambda b: b.id) == [Branch(id="dev", commit_id=d1), Branch(id="main", commit_id=c2)]

    repo.delete_branch("dev")
    assert all(branch.id != "dev" for branch in repo.branches)

    with pytest.raises(ValueError, match="Branch 'foo' does not exist."):
        repo.delete_branch("foo")

    with pytest.raises(ValueError, match="Deleting the 'main' branch"):
        repo.delete_branch("main")


def test_repo_tree(new_sync_repo):
    new_sync_repo.root_group.attrs["title"] = "root title"
    baz_group = new_sync_repo.root_group.create_group("foo/bar/baz")
    baz_group.attrs["title"] = "/foo/bar/baz title"
    spam_array = baz_group.create("spam", shape=100, chunks=10, dtype="<f4", fill_value=-1.0)
    spam_array.attrs["description"] = "spam array description"
    root_array = new_sync_repo.root_group.create("root_array", shape=10, chunks=10, dtype="<f4")
    root_array.attrs["missing_value"] = np.nan  # EAR-682
    float_array = new_sync_repo.root_group.create("/1/2/3/float_array", shape=10, chunks=10, dtype="<f4")
    int_array = new_sync_repo.root_group.create("/1/2/3/int_array", shape=10, chunks=10, dtype="i4")
    bool_array = new_sync_repo.root_group.create("/1/2/3/bool_array", shape=10, chunks=10, dtype="bool")

    unicode_input_dtype = "<U2"
    new_sync_repo.root_group.create("/1/2/3/unicode_array", shape=10, chunks=10, dtype=unicode_input_dtype)

    tree = new_sync_repo.tree()
    assert tree.attributes == dict(new_sync_repo.root_group.attrs)
    assert list(tree.arrays.keys()) == ["root_array"]
    assert tree.trees["foo"].trees["bar"].trees["baz"].attributes == dict(baz_group.attrs)
    assert tree.trees["foo"].arrays == {}
    assert list(tree.trees["foo"].trees.keys()) == ["bar"]
    assert tree.trees["foo"].trees["bar"].trees["baz"].arrays["spam"].data_type == spam_array.dtype
    assert tree.trees["foo"].trees["bar"].trees["baz"].arrays["spam"].fill_value == spam_array.fill_value
    assert tree.trees["foo"].trees["bar"].trees["baz"].arrays["spam"].attributes == dict(spam_array.attrs)
    assert tree.trees["1"].trees["2"].trees["3"].arrays["float_array"].data_type == float_array.dtype
    assert tree.trees["1"].trees["2"].trees["3"].arrays["int_array"].data_type == int_array.dtype
    assert tree.trees["1"].trees["2"].trees["3"].arrays["bool_array"].data_type == bool_array.dtype

    # An array where a unicode dtype get's set to a dict via zarr v3
    assert isinstance(tree.trees["1"].trees["2"].trees["3"].arrays["unicode_array"].data_type, dict)
    assert tree.trees["1"].trees["2"].trees["3"].arrays["unicode_array"].data_type["type"] == unicode_input_dtype

    # depth 1
    tree = new_sync_repo.tree(depth=1)
    assert tree.attributes == dict(new_sync_repo.root_group.attrs)
    assert list(tree.trees.keys()) == ["foo", "1"]
    assert list(tree.arrays.keys()) == ["root_array"]
    assert tree.trees["foo"].trees == {}
    assert tree.trees["foo"].arrays == {}

    if has_rich:
        import rich

        tree = new_sync_repo.tree()._as_rich_tree()
        assert isinstance(tree, rich.tree.Tree)
        assert tree.label == "/"
        assert len(tree.children) == 3  # foo, 3, and root_array

    if has_ipytree:
        import ipytree

        tree = new_sync_repo.tree()._as_ipytree()
        assert isinstance(tree, ipytree.Tree)
        assert len(tree.nodes) == 1  # root node
        assert tree.nodes[0].name == ""
        assert len(tree.nodes[0].nodes) == 3  # foo, 3, and root_array


@pytest.mark.parametrize("metastore_class_and_config", metastore_params_only_mongo)
async def test_commit_waits(new_async_repo):
    waits = list(await new_async_repo._mk_commit_waits())
    assert len(waits) == 30
    assert waits[0:2] == [timedelta(0), timedelta(0)]
    assert all(w > timedelta(0) for w in waits[2:])
    assert all(w <= timedelta(30 * (1 + 0.5)) for w in waits[2:])


@pytest.mark.add_object_store("gs")
def test_repo_with_bucket_stores_chunks_in_bucket(client_config):
    repo_name = secrets.token_hex(20)
    client = Client()
    data = b"hello"
    with config.set({"chunkstore.inline_threshold_bytes": 0}):
        repo = client.create_repo(f"bucketty/{repo_name}", bucket_config_nickname="test")

    try:
        key = "/foo/c0/1/1"
        repo._set_chunk(key, data=data)
        assert repo._get_chunk(key) == data

        # check the chunk was written to the proper bucket
        repo_data = next(repo for repo in client.list_repos("bucketty") if repo.name == repo_name)
        path = f"arraylake-test-data/{repo_data.id.hex()}"

        s3 = boto3.client("s3", endpoint_url=repo_data.bucket.extra_config.get("endpoint_url"))
        obj_key = s3.list_objects_v2(Bucket=repo_data.bucket.name, Prefix=path)["Contents"][0]["Key"]
        written_data = s3.get_object(Bucket=repo_data.bucket.name, Key=obj_key)["Body"].read()
        assert written_data == data
    finally:
        client.delete_repo(f"bucketty/{repo_name}", imsure=True, imreallysure=True)


# This is a regression test to validate that we use the *entire* chunk key (hash
# + session_id) in the local chunk cache [EAR-988], not just the chunk hash.
def test_chunkstore_key(client_config):
    client = Client()
    with config.set({"chunkstore.inline_threshold_bytes": 0}):
        repo = client.get_or_create_repo(f"bucketty/chunk-cache-key", bucket_config_nickname="test")

    data = np.arange(10)
    repo.root_group.create_dataset("foo1", data=data, shape=data.shape, chunks=data.shape)
    repo.commit("1")
    repo.root_group.create_dataset("foo2", data=data, shape=data.shape, chunks=data.shape)
    repo.commit("2")
    try:
        np.testing.assert_equal(repo.root_group["foo2"][:], np.arange(10))
    finally:
        client.delete_repo(f"bucketty/chunk-cache-key", imsure=True, imreallysure=True)


def test_v1_repo_get_repo_flag_behavior():
    """Test that V1 repo opening is controlled by allow_v1_get_repo flag."""
    client = Client()

    # Create a V1 repo first with get_repo enabled
    with config.set({"repo.allow_v1_get_repo": True}):
        repo = client.get_or_create_repo("bucketty/v1-get-flag-test", bucket_config_nickname="test")
        repo.checkout(for_writing=True)

        # Test that get_repo works when flag is enabled
        retrieved_repo = client.get_repo("bucketty/v1-get-flag-test")
        assert retrieved_repo is not None

        # Test that write operations still work
        repo.checkout(for_writing=True)  # Should work
        assert repo.session.session_type.name == "write"

        session = repo.create_session(for_writing=True)  # Should work
        assert session.session_type.name == "write"

    try:
        # Now disable V1 repo opening and test that get_repo fails
        with config.set({"repo.allow_v1_get_repo": False}):
            # Test: get_repo should fail
            with pytest.raises(ValueError, match="V1 repositories can no longer be opened in the Arraylake client"):
                client.get_repo("bucketty/v1-get-flag-test")

    finally:
        # Clean up
        client.delete_repo("bucketty/v1-get-flag-test", imsure=True, imreallysure=True)
