import asyncio
import datetime
import pickle
import random
import string
from collections.abc import Mapping, Sequence
from functools import partial
from operator import attrgetter
from typing import Any, Optional
from unittest.mock import create_autospec, patch
from uuid import uuid4

import httpx
import pytest
from arraylake_mongo_metastore import MongoMetastoreDatabase
from arraylake_mongo_metastore.expiration.generate import squash_commits
from arraylake_mongo_metastore.jmespath_util import JMESParseError
from arraylake_mongo_metastore.mongo_metastore_database import SizeMetrics
from arraylake_mongo_metastore.utils import replace_many_and_check
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from numcodecs import Blosc
from pymongo.errors import BulkWriteError, DuplicateKeyError
from pymongo.results import InsertOneResult
from tests.v1.helpers.test_utils import metastore_params_only_mongo

from arraylake.config import config
from arraylake.exceptions import CommitNotFoundException
from arraylake.metastore import HttpMetastoreDatabase, MetastoreDatabase, http_metastore
from arraylake.metastore.abc import MultipleNodesInChunksRequest, NodeCreationConflict
from arraylake.repos.v1.types import (
    ChunkHash,
    CollectionName,
    CommitID,
    DocResponse,
    NewCommit,
    NewTag,
    Path,
    ReferenceData,
    SessionID,
)

metadata_collection = CollectionName("metadata")
chunks_collection = CollectionName("chunks")
nodes_collection = CollectionName("nodes")


def an_id(n: int) -> str:
    return "".join(random.choices(string.hexdigits, k=n))


def _generate_random_doc():
    "Generate a doc with some fake content"
    return {"id": an_id(5), "data": an_id(10)}


@pytest.mark.asyncio
async def test_metastore_serialization(metastore):
    pickle.loads(pickle.dumps(metastore))
    try:
        await metastore.delete_database("foobar", imsure=True, imreallysure=True)  # make sure it's not there
    except Exception:
        pass
    db = await metastore.create_database("foobar")
    try:
        pickle.loads(pickle.dumps(db))
    finally:
        await metastore.delete_database("foobar", imsure=True, imreallysure=True)


@pytest.mark.asyncio
async def test_delete_metastore_db(metastore):
    try:
        await metastore.delete_database("db_to_erase", imsure=True, imreallysure=True)  # make sure it's not there
    except Exception:
        pass
    db = await metastore.create_database("db_to_erase")
    # raise value error if imsures are not set
    with pytest.raises(ValueError):
        await metastore.delete_database("db_to_erase")

    await metastore.delete_database("db_to_erase", imsure=True, imreallysure=True)

    # raise ValueError if db doesn't exist
    with pytest.raises(ValueError):
        await metastore.delete_database("db_to_erase", imsure=True, imreallysure=True)


# TODO: The schema validation that this is testing was not a part of any active
# code paths. I have disabled the test because metastore._validate_schema() is
# currently unused.
#
# @pytest.mark.asyncio
# async def test_open_uninitialized_db_raises(metastore):
#     with pytest.raises(ValueError):
#         db = await metastore.open_database("not-a-db")


@pytest.mark.asyncio
async def test_duplicate_db_raises(metastore):
    try:
        db = await metastore.delete_database("duplicate", imsure=True, imreallysure=True)
    except Exception:
        pass
    db = await metastore.create_database("duplicate")
    with pytest.raises(ValueError):
        db = await metastore.create_database("duplicate")
    await metastore.delete_database("duplicate", imsure=True, imreallysure=True)


# this test only applies to the mongo metastore, as such we don't use the parameterized fixtures
@pytest.mark.asyncio
async def test_mongo_metastore_construct_from_motor_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017/mongodb")
    motor_db = client.get_database("foo")

    mdb = MongoMetastoreDatabase(motor_db)
    assert mdb._OPEN
    info = await mdb.ping()
    assert info


@pytest.mark.asyncio
async def test_metastore_db_repr(metastore_database):
    r = repr(metastore_database)
    assert type(metastore_database).__name__ in r


# TODO: unit tests for all MetastoreDatabase methods


@pytest.mark.asyncio
@pytest.fixture()
async def db(metastore):
    db_name = an_id(5)
    db = await metastore.create_database(db_name)
    yield db
    await metastore.delete_database(db_name, imsure=True, imreallysure=True)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "collection,items",
    [
        (metadata_collection, {f"meta/root/a/path/{an_id(5)}.json": _generate_random_doc() for n in range(10)}),
        (chunks_collection, {f"data/root/a/path/c{n}/{10*n+1}": _generate_random_doc() for n in range(10)}),
    ],
)
async def test_add_docs(db, collection: CollectionName, items: Mapping[Path, Any]):
    db_name = an_id(5)
    paths = list(items)
    docs = list(items.values())
    session_id = SessionID(an_id(5))

    # write docs
    await db.add_docs(items, collection=collection, session_id=session_id, base_commit=None)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "collection,items",
    [
        (metadata_collection, {f"meta/root/a/path/{an_id(5)}.json": _generate_random_doc() for n in range(10)}),
        (chunks_collection, {f"data/root/a/path/c{n}/{10*n+1}": _generate_random_doc() for n in range(10)}),
    ],
)
async def test_get_docs(db, collection: CollectionName, items: Mapping[Path, Any]):
    paths = list(items)
    docs = list(items.values())
    session_id = SessionID(an_id(5))

    # write docs
    await db.add_docs(items, collection=collection, session_id=session_id, base_commit=None)

    async def do_test(renamed_path):
        renamed_paths = [path.replace("a/path", renamed_path, 1) for path in paths]
        # read all paths
        resp_paths = [d.path async for d in db.get_docs(renamed_paths, collection=collection, session_id=session_id, base_commit=None)]
        assert len(resp_paths) == len(items)
        assert sorted(renamed_paths) == sorted(resp_paths)

        # read different orders
        # we don't guarantee order, but we do expect the queries to yield the same resulting documents
        req_paths_1 = [renamed_paths[0], renamed_paths[-1]]
        req_paths_2 = [renamed_paths[-1], renamed_paths[0]]
        resp_1_paths = [d.path async for d in db.get_docs(req_paths_1, collection=collection, session_id=session_id, base_commit=None)]
        resp_2_paths = [d.path async for d in db.get_docs(req_paths_2, collection=collection, session_id=session_id, base_commit=None)]
        assert len(resp_1_paths) == len(resp_2_paths) == 2
        assert sorted(req_paths_1) == sorted(resp_1_paths)
        assert sorted(req_paths_1) == sorted(resp_2_paths)

        # req empty
        resp_paths = [d.path async for d in db.get_docs([], collection=collection, session_id=session_id, base_commit=None)]
        assert len(resp_paths) == 0

        # req doc not found
        req_paths = ["not-a-path/c1"]
        resp_paths = [d.path async for d in db.get_docs(req_paths, collection=collection, session_id=session_id, base_commit=None)]
        assert len(resp_paths) == 0

        # partial find
        req_paths = [
            renamed_paths[0],
            renamed_paths[0] + "42",
        ]  # this works both for metadata and chunks, where we cannot request a different node
        resp_paths = [d.path async for d in db.get_docs(req_paths, collection=collection, session_id=session_id, base_commit=None)]
        assert len(resp_paths) == 1
        assert req_paths[0] == resp_paths[0]

        # req duplicate yields one doc
        paths_dupes = [renamed_paths[0], renamed_paths[0]]
        resp_paths = [d.path async for d in db.get_docs(paths_dupes, collection=collection, session_id=session_id, base_commit=None)]
        assert len(resp_paths) == 1

        # check that we yield the same results at different sizes of batching configuration
        for i in (1, 3, 5, 10, 50):
            with config.set({"async.batch_size": i}):
                resp_paths = [
                    d.path async for d in db.get_docs(renamed_paths, collection=collection, session_id=session_id, base_commit=None)
                ]
                assert len(resp_paths) == 10
                assert sorted(renamed_paths) == sorted(resp_paths)

    await do_test("a/path")
    await db.rename("a/path", "b/path", session_id=session_id, base_commit=None)
    await do_test("b/path")
    await db.rename("b/path", "b/path2", session_id=session_id, base_commit=None)
    await do_test("b/path2")


@pytest.mark.asyncio
async def test_get_docs_parallel_sessions(db):
    """This test verifies that different sessions can write docs concurrently and not see each other's changes."""
    meta_items: Mapping[Path, Mapping[str, Any]] = {f"meta/root/path/{an_id(5)}.json": _generate_random_doc() for n in range(10)}
    chunk_items: Mapping[Path, Mapping[str, Any]] = {f"data/root/path_renamed/c{n}/{10*n+1}": _generate_random_doc() for n in range(10)}
    # items_2 has the same paths, but different contents than items
    meta_items_2: Mapping[Path, Mapping[str, Any]] = {k: _generate_random_doc() for k in meta_items}
    chunk_items_2: Mapping[Path, Mapping[str, Any]] = {k: _generate_random_doc() for k in chunk_items}

    session_id = SessionID(an_id(5))
    session_id_2 = SessionID(an_id(5))

    await db.add_docs(meta_items, collection=metadata_collection, session_id=session_id, base_commit=None)
    await db.rename("path", "path_renamed", session_id=session_id, base_commit=None)
    await db.add_docs(meta_items_2, collection=metadata_collection, session_id=session_id_2, base_commit=None)
    await db.rename("path", "path_renamed", session_id=session_id_2, base_commit=None)
    await db.add_docs(chunk_items, collection=chunks_collection, session_id=session_id, base_commit=None)
    await db.add_docs(chunk_items_2, collection=chunks_collection, session_id=session_id_2, base_commit=None)

    async def check_get_docs(collection: CollectionName, req_paths: Sequence[Path]) -> None:
        resp = [(d.path, d.content) async for d in db.get_docs(req_paths, collection=collection, session_id=session_id, base_commit=None)]
        resp_2 = [
            (d.path, d.content) async for d in db.get_docs(req_paths, collection=collection, session_id=session_id_2, base_commit=None)
        ]

        assert len(resp) == len(resp_2) == 10

        # assert keys are consistent
        assert {r[0] for r in resp} == set(req_paths)
        assert {r[0] for r in resp_2} == set(req_paths)

        # assert contents are different
        assert len({r[1]["data"] for r in resp} - {r[1]["data"] for r in resp_2}) == 10

    await check_get_docs(metadata_collection, [path.replace("path", "path_renamed", 1) for path in meta_items])
    await check_get_docs(chunks_collection, chunk_items)


@pytest.mark.asyncio
async def test_get_docs_with_commit_history(db, helpers):
    """This test simulates get_docs with a a history of commits.

    get_docs retrieves data for a given session and optionally all data in history
    from a given commit id. We create a sequence of commits, each with different content,
    and assert that get_docs retrieves appropriate content at each step.
    """

    meta_a = helpers.gen_docs(10, prefix="some/array")
    meta_b = helpers.gen_docs(10, prefix="some/array")
    meta_a_modified_content = {k: _generate_random_doc() for k in meta_a}

    chunks_a = helpers.gen_chunks(10, path="some/array")
    chunks_b = helpers.gen_chunks(10, path="some/array")
    chunks_a_modified_content = {k: {"uri": f"s3://testbucket/{uuid4()}"} for k in chunks_a}

    assert meta_a.keys() == meta_a_modified_content.keys()
    assert chunks_a.keys() == chunks_a_modified_content.keys()

    async def mk_commit(metas, chunks, parent_commit):
        return await helpers.make_commit(db, {metadata_collection: metas, chunks_collection: chunks}, parent_commit=parent_commit)

    # create a commit history
    session_1, commit_id_1 = await mk_commit(meta_a, chunks_a, None)
    session_2, commit_id_2 = await mk_commit(meta_a, chunks_a, parent_commit=commit_id_1)
    session_3, commit_id_3 = await mk_commit(meta_a_modified_content, chunks_a_modified_content, parent_commit=commit_id_2)
    session_4, commit_id_4 = await mk_commit(meta_b, chunks_b, parent_commit=commit_id_3)

    # first sesssion has no history, contents should be docs_a
    first = [d.path async for d in db.get_docs(meta_a, collection=metadata_collection, session_id=session_1, base_commit=None)]
    assert len(first) == 10
    assert set(first) == set(meta_a)

    first = [d.path async for d in db.get_docs(chunks_a, collection=chunks_collection, session_id=session_1, base_commit=None)]
    assert len(first) == 10
    assert set(first) == set(chunks_a)

    # second session we indicate a commit history, but still just docs_a, so we did an overwrite
    # we assert the data in content is unchanged
    second = [
        d.content["data"] async for d in db.get_docs(meta_a, collection=metadata_collection, session_id=session_2, base_commit=commit_id_1)
    ]
    assert len(second) == 10
    assert set(second) == {c["data"] for c in meta_a.values()}

    second = [
        d.content["uri"] async for d in db.get_docs(chunks_a, collection=chunks_collection, session_id=session_2, base_commit=commit_id_1)
    ]
    assert len(second) == 10
    assert set(second) == {c["uri"] for c in chunks_a.values()}

    # third session, still docs_a, but we overwrite contents for the same keys
    third = [
        d.content["data"] async for d in db.get_docs(meta_a, collection=metadata_collection, session_id=session_3, base_commit=commit_id_2)
    ]
    assert len(third) == 10
    assert set(third) != {c["data"] for c in meta_a.values()}
    assert set(third) == {c["data"] for c in meta_a_modified_content.values()}

    third = [
        d.content["uri"] async for d in db.get_docs(chunks_a, collection=chunks_collection, session_id=session_3, base_commit=commit_id_2)
    ]
    assert len(third) == 10
    assert set(third) != {c["uri"] for c in chunks_a.values()}
    assert set(third) == {c["uri"] for c in chunks_a_modified_content.values()}

    # fourth session, we expect to get docs a + b back
    req_keys = list(meta_a) + list(meta_b)
    fourth = [
        d.content["data"]
        async for d in db.get_docs(req_keys, collection=metadata_collection, session_id=session_4, base_commit=commit_id_3)
    ]
    assert len(fourth) == 20
    expected_values = list(meta_a_modified_content.values()) + list(meta_b.values())
    assert set(fourth) == {c["data"] for c in expected_values}

    req_keys = list(chunks_a) + list(chunks_b)
    fourth = [
        d.content["uri"] async for d in db.get_docs(req_keys, collection=chunks_collection, session_id=session_4, base_commit=commit_id_3)
    ]
    assert len(fourth) == 20
    expected_values = list(chunks_a_modified_content.values()) + list(chunks_b.values())
    assert set(fourth) == {c["uri"] for c in expected_values}


@pytest.mark.asyncio
async def test_get_docs_with_bad_commit(db, helpers):
    docs_a = helpers.gen_docs(10, prefix="meta/a/")
    docs_a_modified_content = {k: _generate_random_doc() for k in docs_a}
    session_1, commit_id_1 = await helpers.make_commit(db, {metadata_collection: docs_a})
    c = helpers.new_random_dbid()
    with pytest.raises((ValueError, CommitNotFoundException), match=f"Error retrieving commit id {c}"):
        [d async for d in db.get_docs(docs_a, collection=metadata_collection, session_id=session_1, base_commit=c)]


@pytest.mark.asyncio
async def test_get_count_all_docs_for_session(db, helpers):
    # TODO: Find a nicer way to only run for one or the other type
    if not isinstance(db, MongoMetastoreDatabase):
        pytest.skip(reason="This test only applies to MongoMetastoreDatabase")

    session_id = SessionID("abc123")

    # utility to call the op as state updates
    async def get_count():
        return await db._get_count_all_docs_for_session(
            session_id, collection=metadata_collection
        ) + await db._get_count_all_docs_for_session(session_id, collection=chunks_collection)

    # create a base case
    first_meta_docs = helpers.gen_docs(5)
    first_chunk_docs = helpers.gen_chunks(5)
    await db.add_docs(first_meta_docs, collection=metadata_collection, session_id=session_id, base_commit=None)
    await db.add_docs(first_chunk_docs, collection=chunks_collection, session_id=session_id, base_commit=None)
    assert await get_count() == 10

    # add more docs
    second_meta_docs = helpers.gen_docs(5)
    second_chunk_docs = helpers.gen_chunks(5)
    await db.add_docs(second_meta_docs, collection=metadata_collection, session_id=session_id, base_commit=None)
    await db.add_docs(second_chunk_docs, collection=chunks_collection, session_id=session_id, base_commit=None)
    assert await get_count() == 20

    # adding the same docs returns the same count
    await db.add_docs(second_meta_docs, collection=metadata_collection, session_id=session_id, base_commit=None)
    await db.add_docs(second_chunk_docs, collection=chunks_collection, session_id=session_id, base_commit=None)
    assert await get_count() == 20

    # removing the same docs returns the same count
    await db.del_docs(list(second_meta_docs), collection=metadata_collection, session_id=session_id, base_commit=None)
    await db.del_docs(list(second_chunk_docs), collection=chunks_collection, session_id=session_id, base_commit=None)
    assert await get_count() == 20


@pytest.mark.asyncio
async def test_get_count_all_docs_for_session_empty_collection(db):
    if not isinstance(db, MongoMetastoreDatabase):
        pytest.skip(reason="This test only applies to MongoMetastoreDatabase")

    session_id = SessionID("abc123")
    result = await db._get_count_all_docs_for_session(session_id, collection=metadata_collection)
    assert result == 0


@pytest.mark.asyncio
async def test_get_count_all_docs_for_multi_session(db, helpers):
    if not isinstance(db, MongoMetastoreDatabase):
        pytest.skip(reason="This test only applies to MongoMetastoreDatabase")

    session_id = SessionID("abc123")
    session_id_2 = SessionID("def456")

    async def get_count(sid: SessionID) -> int:
        return await db._get_count_all_docs_for_session(sid, collection=metadata_collection) + await db._get_count_all_docs_for_session(
            sid, collection=chunks_collection
        )

    result_1 = await get_count(session_id)
    result_2 = await get_count(session_id_2)
    assert result_1 == result_2 == 0

    # add docs to session 1
    first_meta_docs = helpers.gen_docs(5)
    first_chunk_docs = helpers.gen_chunks(5)
    await db.add_docs(first_meta_docs, collection=metadata_collection, session_id=session_id, base_commit=None)
    await db.add_docs(first_chunk_docs, collection=chunks_collection, session_id=session_id, base_commit=None)
    assert await get_count(session_id) == 10
    # session 2 should have nothing
    assert await get_count(session_id_2) == 0

    # add the same docs to session 2
    await db.add_docs(first_meta_docs, collection=metadata_collection, session_id=session_id_2, base_commit=None)
    await db.add_docs(first_chunk_docs, collection=chunks_collection, session_id=session_id_2, base_commit=None)
    assert await get_count(session_id_2) == 10

    # add new docs to session 2
    session_2_meta_docs = helpers.gen_docs(5)
    session_2_chunk_docs = helpers.gen_chunks(5)
    await db.add_docs(session_2_meta_docs, collection=metadata_collection, session_id=session_id_2, base_commit=None)
    await db.add_docs(session_2_chunk_docs, collection=chunks_collection, session_id=session_id_2, base_commit=None)
    assert await get_count(session_id) == 10
    # second session should be changed
    assert await get_count(session_id_2) == 20


async def test_get_all_paths_for_commit(db: HttpMetastoreDatabase, helpers):
    meta_a = helpers.gen_docs(10, prefix="some/array")
    meta_b = helpers.gen_docs(10, prefix="some/array")

    async def mk_commit(metas, parent_commit):
        return await helpers.make_commit(db, {metadata_collection: metas, chunks_collection: {}}, parent_commit=parent_commit)

    session_1, commit_id_1 = await mk_commit(meta_a, None)

    docs = [d.path async for d in db.get_all_paths_for_commit(commit_id_1, collection="metadata")]
    assert sorted(docs) == sorted(meta_a.keys())

    session_2, commit_id_2 = await mk_commit(meta_b, commit_id_1)
    docs = [d.path async for d in db.get_all_paths_for_commit(commit_id_2, collection="metadata")]
    assert sorted(docs) == sorted(meta_b.keys())

    # verify that in the case of one commit with multiple sessions, we yield the paths from all
    # sessions
    # squash is not applicable on the client, so we don't run the test there
    if not isinstance(db, HttpMetastoreDatabase):
        await squash_commits(db, CommitID(commit_id_2), ancestors=[CommitID(commit_id_1)])
        docs = [d.path async for d in db.get_all_paths_for_commit(commit_id_2, collection="metadata")]
        assert sorted(docs) == sorted(list(meta_a.keys()) + list(meta_b.keys()))


@pytest.mark.asyncio
async def test_get_all_paths_for_session(db: HttpMetastoreDatabase, helpers):
    session_id = SessionID("abc123")
    first_meta_docs = helpers.gen_docs(5)
    first_chunk_docs = helpers.gen_chunks(5)
    second_meta_docs = helpers.gen_docs(5)
    second_chunk_docs = helpers.gen_chunks(5)
    await db.add_docs(first_meta_docs, collection=metadata_collection, session_id=session_id, base_commit=None)
    await db.add_docs(first_chunk_docs, collection=chunks_collection, session_id=session_id, base_commit=None)
    res = [d async for d in db.get_all_paths_for_session(session_id=session_id, collection=metadata_collection, base_commit=None)] + [
        d async for d in db.get_all_paths_for_session(session_id=session_id, collection=chunks_collection, base_commit=None)
    ]
    assert len(res) == 10
    assert {*first_meta_docs, *first_chunk_docs} == {r.path for r in res}

    await db.add_docs(first_meta_docs, collection=metadata_collection, session_id=session_id, base_commit=None)
    await db.add_docs(first_chunk_docs, collection=chunks_collection, session_id=session_id, base_commit=None)
    res = [d async for d in db.get_all_paths_for_session(session_id=session_id, collection=metadata_collection, base_commit=None)] + [
        d async for d in db.get_all_paths_for_session(session_id=session_id, collection=chunks_collection, base_commit=None)
    ]
    assert len(res) == 10
    assert {*first_meta_docs, *first_chunk_docs} == {r.path for r in res}

    await db.add_docs(second_meta_docs, collection=metadata_collection, session_id=session_id, base_commit=None)
    await db.add_docs(second_chunk_docs, collection=chunks_collection, session_id=session_id, base_commit=None)
    res = [d async for d in db.get_all_paths_for_session(session_id=session_id, collection=metadata_collection, base_commit=None)] + [
        d async for d in db.get_all_paths_for_session(session_id=session_id, collection=chunks_collection, base_commit=None)
    ]
    assert len(res) == 20
    assert {*first_meta_docs, *first_chunk_docs, *second_meta_docs, *second_chunk_docs} == {r.path for r in res}

    await db.del_docs(list(second_meta_docs), collection=metadata_collection, session_id=session_id, base_commit=None)
    await db.del_docs(list(second_chunk_docs), collection=chunks_collection, session_id=session_id, base_commit=None)
    res = [d async for d in db.get_all_paths_for_session(session_id=session_id, collection=metadata_collection, base_commit=None)] + [
        d async for d in db.get_all_paths_for_session(session_id=session_id, collection=chunks_collection, base_commit=None)
    ]
    assert len(res) == 20
    assert {*first_meta_docs, *first_chunk_docs, *second_meta_docs, *second_chunk_docs} == {r.path for r in res}


@pytest.mark.asyncio
@pytest.mark.parametrize("limit,res_count", [(0, 10), (1, 1), (5, 5), (10, 10), (15, 10)])
async def test_get_all_paths_for_session_with_limit(helpers, db: HttpMetastoreDatabase, limit: int, res_count: int):
    session_id = SessionID("abc123")
    first_docs = helpers.gen_docs(10)
    await db.add_docs(first_docs, collection=metadata_collection, session_id=session_id, base_commit=None)
    res = [
        d async for d in db.get_all_paths_for_session(session_id=session_id, collection=metadata_collection, limit=limit, base_commit=None)
    ]
    assert len(res) == res_count
    assert all([first_docs.get(r.path) for r in res])


# little ugly - this only tests the http metastore, based on the conditional half way down
@pytest.mark.asyncio
async def test_get_docs_batch_partial_failure(db):
    """Test that a partial failure for batched requests yields no results.

    This test simulates partial failure of a batch request. i.e. if our call to get_docs is batched
    into 5 requests, and one of those requests fail, then we should fail the entire call (rather
    than return partial results).

    It does this by patching `http_metastore.HttpMetastoreDatabase._get_docs`. The patched version of this
    function has two side_effects configured: the first looks like a success result, the second is an exception.
    side_effects listed like this will yield these as results to successive calls to the function, i.e.: the first
    call will succeeed, the second will fail.

    Our test asserts that the function is called twice, and that the call raises an exception (even though one of its
    sub-calls to _get_docs was a success).
    """

    if not isinstance(db, HttpMetastoreDatabase):
        pytest.skip(reason="This test only applies to HttpMetastore")

    # set up
    db_name = an_id(5)
    items: Mapping[Path, Mapping[str, Any]] = {f"/a/path/{an_id(5)}.json": _generate_random_doc() for n in range(10)}
    paths = list(items)
    docs = list(items.values())
    session_id = SessionID(an_id(5))

    # add docs
    await db.add_docs(items, collection=metadata_collection, session_id=session_id, base_commit=None)

    def gen_fake_doc_response(content):
        """Utility to generate a fake doc response for use in mocked tests"""
        return DocResponse(id="507f191e810c19729de860ea", session_id="bla", path="/1/2/3.json", content=content)

    async def fake_good_response():
        """A fake async generator to yield happy case results"""
        for p in docs[:2]:
            yield gen_fake_doc_response(p)

    # mock HttpMetastoreDatabase_get_docs
    # the first time it is called yield good results
    # the second time, throw a http error
    mock__get_docs = create_autospec(
        http_metastore.HttpMetastoreDatabase._get_docs, side_effect=[fake_good_response(), httpx.RequestError("test failure")]
    )

    # we have written 10 documents
    # batching in 2s should mean up to 5 requests
    batch_size = 2
    if isinstance(db, HttpMetastoreDatabase):
        with config.set({"async.batch_size": batch_size}):
            with patch("arraylake.metastore.http_metastore.HttpMetastoreDatabase._get_docs", mock__get_docs):
                with pytest.raises(httpx.RequestError):
                    resp_paths = [
                        d.path async for d in db.get_docs(paths, collection=metadata_collection, session_id=session_id, base_commit=None)
                    ]


@pytest.mark.asyncio
async def test_del_shared_prefix(db, helpers):
    session1 = SessionID("session1")
    docs_a = helpers.gen_docs(2, prefix="meta/root/foo/a/")
    docs_aa = helpers.gen_docs(2, prefix="meta/root/foo/aa/")
    docs_b = helpers.gen_docs(2, prefix="meta/root/foo/b/")
    for docs in [docs_a, docs_aa, docs_b]:
        await db.add_docs(docs, collection=metadata_collection, session_id=session1, base_commit=None)

    ld = partial(db.list, collection=metadata_collection, session_id=session1, base_commit=None, all_subdirs=True)

    # we've created 6 total docs
    all_docs = [d async for d in ld("meta/root/foo/")]
    assert len(all_docs) == 6

    # deleting foo/b should give us 2 fewer docs
    await db.del_prefix(prefix="meta/root/foo/b", collection=metadata_collection, session_id=session1, base_commit=None)
    all_docs = [d async for d in ld("meta/root/foo/")]
    assert len(all_docs) == 4

    # deleting foo/a should give us 2 fewer docs
    # we want to ensure that we don't accidentally prefix match foo/aa
    await db.del_prefix(prefix="meta/root/foo/a", collection=metadata_collection, session_id=session1, base_commit=None)
    all_docs = [d async for d in ld("meta/root/foo/")]
    assert len(all_docs) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "collection,mk_docs",
    [
        (metadata_collection, lambda prefix, helpers: helpers.gen_docs(10, prefix=prefix)),
        (chunks_collection, lambda path, helpers: helpers.gen_chunks(10, path=path)),
    ],
)
async def test_del_prefix(db, helpers, collection, mk_docs):
    session1 = SessionID("session1")
    docs_prefix_a = mk_docs("meta/root/a/", helpers)
    docs_prefix_b1 = mk_docs("meta/root/b/", helpers)
    docs_prefix_b2 = mk_docs("meta/root/b/nested/deep/", helpers)
    await db.add_docs(docs_prefix_a, collection=collection, session_id=session1, base_commit=None)
    await db.add_docs({**docs_prefix_b1, **docs_prefix_b2}, collection=collection, session_id=session1, base_commit=None)

    # simulate a commit
    # TODO: shift more of this functionality into the metastore?
    commit_info = NewCommit(
        session_id=session1,
        session_start_time=datetime.datetime.utcnow(),
        parent_commit=None,
        commit_time=datetime.datetime.utcnow(),
        author_name="Test Author",
        author_email="test@author.com",
        message="First commit",
    )
    commit1 = await db.new_commit(commit_info)

    session2 = SessionID("session2")
    await db.del_prefix(prefix="meta/root/b", collection=collection, session_id=session2, base_commit=commit1)
    a_docs = [doc async for doc in db.get_docs(list(docs_prefix_a), collection=collection, session_id=session2, base_commit=commit1)]
    b_docs_s1 = [
        doc async for doc in db.get_docs(list(docs_prefix_b1), collection=collection, session_id=session1, base_commit=commit1)
    ] + [doc async for doc in db.get_docs(list(docs_prefix_b2), collection=collection, session_id=session1, base_commit=commit1)]
    b_docs_s2 = [
        doc async for doc in db.get_docs(list(docs_prefix_b1), collection=collection, session_id=session2, base_commit=commit1)
    ] + [doc async for doc in db.get_docs(list(docs_prefix_b2), collection=collection, session_id=session2, base_commit=commit1)]

    assert len(a_docs) == 10
    assert len(b_docs_s1) == 20
    assert len(b_docs_s2) == 0

    # for metadata (not for chunks) we can request multiple nodes in the same get_docs call
    if collection == metadata_collection:
        meta_docs_s1 = [
            doc
            async for doc in db.get_docs(
                list(docs_prefix_b1) + list(docs_prefix_b2), collection=collection, session_id=session1, base_commit=commit1
            )
        ]
        meta_docs_s2 = [
            doc
            async for doc in db.get_docs(
                list(docs_prefix_b1) + list(docs_prefix_b2), collection=collection, session_id=session2, base_commit=commit1
            )
        ]
        assert len(b_docs_s1) == 20
        assert len(b_docs_s2) == 0

    # no error when deleting a non-existent prefix
    await db.del_prefix(prefix="meta/root/c", collection=collection, session_id=session2, base_commit=commit1)

    # deleting root prefix deletes everything
    await db.del_prefix(prefix="", collection=collection, session_id=session2, base_commit=commit1)
    all_docs = (
        [doc async for doc in db.get_docs(list(docs_prefix_a), collection=collection, session_id=session2, base_commit=commit1)]
        + [doc async for doc in db.get_docs(list(docs_prefix_b1), collection=collection, session_id=session2, base_commit=commit1)]
        + [doc async for doc in db.get_docs(list(docs_prefix_b2), collection=collection, session_id=session2, base_commit=commit1)]
    )

    assert len(all_docs) == 0


@pytest.mark.asyncio
async def test_rebase_no_conflicts(db, helpers):
    branch_name = "test-branch"
    session0, commit_ids, _, _ = await helpers.make_commits_to_branch(db, 5, 10, branch_name)

    # create a commit, but set its parent to be the first commit we created
    session_id, final_commit_id = await helpers.make_commit(
        db,
        {metadata_collection: helpers.gen_docs(5, prefix=f"meta/root/"), chunks_collection: helpers.gen_chunks(5, path="data/root")},
        parent_commit=commit_ids[0],
    )

    # Delete this once arraylake 0.7.6 is no longer supported
    new_base_id = await db.old_style_rebase(final_commit_id, branch_name)
    assert new_base_id == commit_ids[-1]

    new_base_id = await db.rebase(base_commit=commit_ids[0], session_id=session_id, upstream_branch=branch_name)
    assert new_base_id == commit_ids[-1]


@pytest.mark.asyncio
async def test_rebase_with_conflicts_raises(db, helpers):
    """Test scenarios where an update would be invalid."""
    branch_name = "test-branch"
    session0, commit_ids, docs, _ = await helpers.make_commits_to_branch(db, 5, 10, branch_name, overwrite_paths=True)

    session_id, final_commit_id = await helpers.make_commit(db, {metadata_collection: docs[0]}, parent_commit=commit_ids[0])

    # Delete this once arraylake 0.7.6 is no longer supported
    with pytest.raises(ValueError, match=f"Conflicting paths found for rebase {commit_ids[0]}"):
        await db.old_style_rebase(final_commit_id, branch_name)

    with pytest.raises(ValueError, match=f"Conflicting paths found for rebase {commit_ids[0]}"):
        await db.rebase(base_commit=commit_ids[0], session_id=session_id, upstream_branch=branch_name)


@pytest.mark.asyncio
async def test_rebase_conflict_detection(db, helpers):
    meta_doc = {f"meta/root/foo.json": {"data": str(uuid4())}}
    meta_doc_2 = {f"meta/root/bar.json": {"data": str(uuid4())}}
    chunk_doc = {f"data/root/c0/1/2": {"data": str(uuid4())}}
    chunk_doc_2 = {f"data/root/c0/0/0": {"data": str(uuid4())}}

    configurations = [
        [[meta_doc, meta_doc_2], []],
        [[meta_doc, meta_doc], meta_doc],
        [[chunk_doc, chunk_doc_2], []],
        # chunk document conflicts don't get reported by full path
        [[chunk_doc, chunk_doc], "data/root"],
        [[meta_doc, chunk_doc], []],
    ]

    for commit_docs, expected_failure in configurations:
        commit_ids = []
        sessions = []
        parent_commit_id = None
        branch_name = f"test-branch-{uuid4()}"
        for i, docs in enumerate(commit_docs):
            collection = chunks_collection if list(docs)[0].startswith("data") else metadata_collection
            session, commit_id = await helpers.make_commit(db, {collection: docs}, parent_commit=parent_commit_id)
            commit_ids.append(commit_id)
            sessions.append(session)
            await db.update_branch(
                branch_name,
                session_id=session,
                base_commit=parent_commit_id,
                new_commit=commit_id,
                new_branch=True if not parent_commit_id else False,
            )
            parent_commit_id = commit_id

        if expected_failure:
            with pytest.raises(ValueError, match=rf"Conflicting paths found for rebase None->{branch_name}") as e_info:
                # FIXME: this is not a good test, it should be a commit_id that is not on the list
                # Delete this once arraylake 0.7.6 is no longer supported
                await db.old_style_rebase(commit_ids[0], branch_name)

            with pytest.raises(ValueError, match=rf"Conflicting paths found for rebase None->{branch_name}") as e_info:
                # FIXME: this is not a good test, it should be a commit_id that is not on the list
                await db.rebase(base_commit=None, session_id=sessions[0], upstream_branch=branch_name)

            for path in expected_failure:
                assert path in str(e_info.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("bad_branch_name", ["test", "branch", "test-branc", "test-branch-x", "bad", ""])
async def test_rebase_bad_branch_raises(db, helpers, bad_branch_name):
    branch_name = "test-branch"
    session0, commit_ids, _, _ = await helpers.make_commits_to_branch(db, 5, 10, branch_name)

    # the correct branch should work
    session_id, final_commit_id = await helpers.make_commit(
        db, {metadata_collection: helpers.gen_docs(5, prefix=f"meta/root/")}, parent_commit=commit_ids[0]
    )

    # Delete this once arraylake 0.7.6 is no longer supported
    assert commit_ids[-1] == await db.old_style_rebase(final_commit_id, branch_name)
    with pytest.raises(ValueError, match="Branch does not exist, rebase is unavailable"):
        await db.old_style_rebase(final_commit_id, bad_branch_name)

    assert commit_ids[-1] == await db.rebase(base_commit=commit_ids[-1], session_id=session_id, upstream_branch=branch_name)
    with pytest.raises(ValueError, match="Branch does not exist, rebase is unavailable"):
        await db.rebase(base_commit=commit_ids[-1], session_id=session_id, upstream_branch=bad_branch_name)


@pytest.mark.asyncio
async def test_rebase_no_shared_history_raises(db, helpers):
    "Tests that valid commits but with different histories does not yield success results"
    branch_1_name = "test-branch-1"
    branch_2_name = "test-branch-2"
    session0, commit_ids_1, _, _ = await helpers.make_commits_to_branch(db, 5, 10, branch_1_name)
    session1, commit_ids_2, _, _ = await helpers.make_commits_to_branch(db, 5, 10, branch_2_name)

    target_commit_id, parent_commit_id = commit_ids_1[1], commit_ids_1[0]

    # Delete this once arraylake 0.7.6 is no longer supported
    with pytest.raises(ValueError, match=f"No shared parent. Parent {parent_commit_id} does not exist in history for"):
        await db.old_style_rebase(target_commit_id, branch_2_name)

    with pytest.raises(ValueError, match=f"No shared parent. Parent {parent_commit_id} does not exist in history for"):
        await db.rebase(base_commit=parent_commit_id, session_id="abc", upstream_branch=branch_2_name)


@pytest.mark.asyncio
async def test_rebase_no_parent(db, helpers):
    """Scenario is that someone is on a new branch and has no parent."""
    branch_name = "test-branch"
    session0, commit_ids, _, _ = await helpers.make_commits_to_branch(db, 5, 10, branch_name)

    session_id, final_commit_id = await helpers.make_commit(
        db, {metadata_collection: helpers.gen_docs(5, prefix=f"meta/root/")}, parent_commit=None
    )
    # Delete this once arraylake 0.7.6 is no longer supported
    assert commit_ids[-1] == await db.old_style_rebase(final_commit_id, branch_name)
    assert commit_ids[-1] == await db.rebase(base_commit=None, session_id=session_id, upstream_branch=branch_name)


@pytest.mark.asyncio
async def test_rebase_already_latest(db, helpers):
    branch_name = "test-branch"
    session0, commit_ids, _, _ = await helpers.make_commits_to_branch(db, 5, 10, branch_name)
    session_id, final_commit_id = await helpers.make_commit(
        db, {metadata_collection: helpers.gen_docs(5, prefix=f"meta/root/")}, parent_commit=commit_ids[-1]
    )
    # Delete this once arraylake 0.7.6 is no longer supported
    assert commit_ids[-1] == await db.old_style_rebase(final_commit_id, branch_name)
    assert commit_ids[-1] == await db.rebase(base_commit=commit_ids[-1], session_id=session_id, upstream_branch=branch_name)


@pytest.mark.asyncio
async def test__get_conflicting_paths_commited_sessions(db, helpers):
    if not isinstance(db, MongoMetastoreDatabase):
        pytest.skip(reason="This test only applies to MongoMetastoreDatabase")

    conflict_docs = {"meta/root/foo.json": {"data": "abc"}, "meta/root/bar.json": {"data": "def"}}
    conflict_chunks = {"foo/bar/c0/0": {"data": "abc"}, "foo/bar/c0/1": {"data": "def"}}
    docs = {"meta/root/no-conflict.json": {"data": "xyz"}, **conflict_docs}
    chunks = {"foo/bar/c10/10": {"data": "xyz"}, **conflict_chunks}
    session1 = SessionID(an_id(5))
    await db.add_docs(docs, collection=metadata_collection, session_id=session1, base_commit=None)
    await db.add_docs(chunks, collection=chunks_collection, session_id=session1, base_commit=None)
    commit = await helpers.commit_session(db, session1, parent_commit=None)

    session2 = SessionID(an_id(5))
    new_docs = {"meta/root/other-no-conflict.json": {"data": "ghi"}, **conflict_docs}
    new_chunks = {"other-no-conflict/c0/0": {"data": "ghi"}, **conflict_chunks}
    await db.add_docs(new_docs, collection=metadata_collection, session_id=session2, base_commit=commit)
    await db.add_docs(new_chunks, collection=chunks_collection, session_id=session2, base_commit=commit)

    conflicting_paths = [d async for d in db._get_conflicting_paths(session2, commit, [session1], match_limit=5)]
    assert sorted(dict(conflict_docs, **conflict_chunks)) == sorted({path for (path, _sessions) in conflicting_paths})
    assert [[session1]] * 4 == [sessions for (_path, sessions) in conflicting_paths]


@pytest.mark.asyncio
async def test__get_conflicting_paths_uncommitted_session(db):
    if not isinstance(db, MongoMetastoreDatabase):
        pytest.skip(reason="This test only applies to MongoMetastoreDatabase")

    docs = {"meta/root/foo.json": {"data": "abc"}, "meta/root/bar.json": {"data": "def"}}
    chunks = {"foo/bar/c10/10": {"data": "xyz"}, "foo/bar/c0/0": {"data": "def"}}
    session_ids = []

    for i in range(5):
        session = SessionID(an_id(5))
        await db.add_docs(docs, collection=metadata_collection, session_id=session, base_commit=None)
        await db.add_docs(chunks, collection=chunks_collection, session_id=session, base_commit=None)
        session_ids.append(session)

    conflicting_paths = [d async for d in db._get_conflicting_paths(session_ids[0], None, session_ids[1:], match_limit=5)]
    # TODO: currently uncommitted chunk conflicts don't return the full path, they skip the coords part
    assert len(conflicting_paths) == 3
    for _, conflicting_sessions in conflicting_paths:
        assert sorted(conflicting_sessions) == sorted(session_ids[1:])


@pytest.mark.asyncio
async def test__get_conflicting_paths_with_deletes(db):
    if not isinstance(db, MongoMetastoreDatabase):
        pytest.skip(reason="This test only applies to MongoMetastoreDatabase")

    docs = {"meta/root/foo.json": {"data": "abc"}}
    chunks = {"root/foo/c0/0": {"data": "abc"}}
    session_ids = []

    for i in range(2):
        session = SessionID(an_id(5))
        await db.add_docs(docs, collection=metadata_collection, session_id=session, base_commit=None)
        await db.add_docs(chunks, collection=chunks_collection, session_id=session, base_commit=None)
        await db.del_docs([k for k in docs], collection=metadata_collection, session_id=session, base_commit=None)
        await db.del_docs([k for k in chunks], collection=chunks_collection, session_id=session, base_commit=None)
        session_ids.append(session)

    conflicting_paths = [d async for d in db._get_conflicting_paths(session_ids[0], None, session_ids[1:], match_limit=5)]
    # TODO: currently uncommitted chunk conflicts don't return the full path, they skip the coords part
    assert sorted(list(docs) + ["root/foo"]) == sorted(path for path, _ in conflicting_paths)
    assert [[session_ids[1]], [session_ids[1]]] == [sessions for _, sessions in conflicting_paths]


@pytest.mark.asyncio
async def test_replace_many_and_check(db):
    if not isinstance(db, MongoMetastoreDatabase):
        pytest.skip(reason="This test only applies to MongoMetastoreDatabase")

    mdb = db._db
    collection = mdb.get_collection("temporary")
    replace_and_check = partial(replace_many_and_check, unique_key_fields={"session_id", "path"})

    docs = [{"session_id": 123, "path": "/a/b", "foo": "bar"}, {"session_id": 123, "path": "/a/c", "foo": "baz"}]
    await replace_and_check(collection, docs)

    all_docs = [doc async for doc in collection.find()]
    assert len(all_docs) == 2
    for d in all_docs:
        d.pop("_id")
        assert d in docs

    # now write the same two docs again
    docs2 = [
        {"session_id": 123, "path": "/a/b", "foo": "baz"},
        {"session_id": 123, "path": "/a/c", "deleted": 1},
        {"session_id": 123, "path": "/a/d", "foo": "inserted"},
    ]
    await replace_and_check(collection, docs2)

    # there should now be 3 docs (2 updated and one new)
    all_docs = [doc async for doc in collection.find()]
    assert len(all_docs) == 3
    for d in all_docs:
        d.pop("_id")
        assert d in docs2

    # now mock a failure case
    async def fake_bulk_write(collection, docs, **kwargs):
        raise BulkWriteError(results={})

    with patch("motor.motor_asyncio.AsyncIOMotorCollection.bulk_write", fake_bulk_write):
        with pytest.raises(RuntimeError, match="Failed to insert all documents"):
            await replace_and_check(collection, docs)


@pytest.mark.asyncio
async def test_list_chunk_keys(db):
    """Regression test for https://linear.app/earthmover/issue/EAR-787/change-in-list-prefix-behavior-with-trailing-slash-in-070#comment-20aa8f75"""
    keys = ["data/root/foo/bar/c0/0", "data/root/foo/bar/c9/9"]
    chunk = {key: {"data": "xyz"} for key in keys}
    session1 = SessionID(an_id(5))
    await db.add_docs(chunk, collection=chunks_collection, session_id=session1, base_commit=None)
    for prefix in [
        "data",
        "data/",
        "data/root",
        "data/root/",
        "data/root/foo",
        "data/root/foo/",
        "data/root/foo/bar",
        "data/root/foo/bar/",
    ]:
        res = [
            path async for path in db.list(prefix, collection=chunks_collection, session_id=session1, base_commit=None, all_subdirs=True)
        ]
        assert sorted(res) == sorted(keys)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filter_expr,expected",
    [
        ("connector.cloud_mask > `5`", ["meta/root/implicit/one.array.json", "meta/root/hdf5/two.array.json"]),
        ("connector.cloud_mask == `10`", ["meta/root/implicit/one.array.json"]),
        ("connector.cloud_mask == `15`", ["meta/root/hdf5/two.array.json"]),
        (
            "space.cloud_mask_values[0] == `10` || connector.cloud_mask == `15`",
            ["meta/root/root.group.json", "meta/root/hdf5/two.array.json"],
        ),
    ],
)
async def test_jmespath_supported_features_multiple_results(db, filter_expr, expected):
    """Assert multiple matches yields multiple paths"""
    test_doc = {
        # doc has no attributes
        "meta/root/implicit/one.array.json": {},
        "meta/root/implicit/one.array.json": {
            "attributes": {"connector": {"cloud_mask": 10}},
        },
        "meta/root/hdf5/two.array.json": {
            "attributes": {"connector": {"cloud_mask": 15}},
        },
        "meta/root/root.group.json": {
            "attributes": {"space": {"cloud_mask_values": [10, 15]}},
        },
    }
    session_id = SessionID(an_id(5))
    await db.add_docs(test_doc, collection=metadata_collection, session_id=session_id, base_commit=None)

    res = [
        d async for d in db.list("meta/root", collection=metadata_collection, session_id=session_id, base_commit=None, filter=filter_expr)
    ]
    assert sorted(res) == sorted(expected)


@pytest.mark.asyncio
async def test_jmespath_supported_no_metadata(db):
    """Search applies over `attributes`. This tests various scenarios around no attributes available."""
    test_doc = {
        "meta/root/implicit/one.array.json": {},
        "meta/root/implicit/two.array.json": {"baz": 5},
        "meta/root/implicit/three.array.json": {"foo": {"attributes": {"a": "b"}}},
    }
    session_id = SessionID(an_id(5))
    await db.add_docs(test_doc, collection=metadata_collection, session_id=session_id, base_commit=None)
    expressions = ["attributes.a == 'b'", "a == 'b'", "baz == `5`"]
    for filter_expr in expressions:
        res = [
            d
            async for d in db.list(
                "meta/root",
                collection=metadata_collection,
                session_id=session_id,
                base_commit=None,
                filter=filter_expr,
            )
        ]
        assert not (res)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression",
    [
        "contains(flags[0].spec, 'a')",
        "flags[0].spec[0] == 'a'",
        "flags[0].spec[0:2] == ['a', 'b']",
        "flags[0].spec[2] == band",
        # a potentially unintuitive scenario, both do not exist and evaluate to null, so null == null
        "foo == bar",
        # a more concrete way to assert the former unintuitive test
        "contains(keys(@), 'flags') && contains(keys(@), 'band') && flags[0].spec[2] == band",
        "someNaN == 'NaN'",
        "number >= `3` && number <= `15`",
        '"eo:val" == `12`',
        '"created:at:time" <= `2022-05-01`',
    ],
)
async def test_jmespath_supported_features_truthy(db, expression):
    """Valid JMESPath queries that should match documents"""
    metadata = {
        "attributes": {
            "flags": [{"spec": ["a", "b", "c", "d", "e"]}],
            "band": "c",
            "number": 10,
            "numbers": [1, 2, 3, 4, 5],
            "eo:val": 12,
            "someNaN": "NaN",
            "created:at:time": "2021-05-10 22:22:23",
            "some": {"nested": {"prop": "foo"}},
        }
    }

    test_doc = {
        "meta/root/hdf5/three.array.json": metadata,
    }
    session_id = SessionID(an_id(5))
    await db.add_docs(test_doc, collection=metadata_collection, session_id=session_id, base_commit=None)
    res = [
        d async for d in db.list("meta/root", collection=metadata_collection, session_id=session_id, base_commit=None, filter=expression)
    ]
    assert res[0] == "meta/root/hdf5/three.array.json"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression",
    [
        "(!flags == `5` || flags == `10`) && foo == `10`",
        "foo[0] == `10`",
        'contains(keys(@), "foo") && contains(keys(@), "bar") && foo == bar',
        "foo == `10`",
        "someNaN == NaN",
        "someNaN == `NaN`",
    ],
)
async def test_jmespath_supported_features_falsey(db, expression):
    """Valid JMESPath queries that should not match documents"""
    metadata = {
        "attributes": {
            "flags": [{"spec": ["a", "b", "c", "d", "e"]}],
            "band": "c",
            "number": 10,
            "numbers": [1, 2, 3, 4, 5],
            "eo:val": 12,
            "someNaN": "NaN",
            "created:at:time": "2021-05-10 22:22:23",
            "some": {"nested": {"prop": "foo"}},
        }
    }

    test_doc = {
        "meta/root/hdf5/three.array.json": metadata,
    }
    session_id = SessionID(an_id(5))
    await db.add_docs(test_doc, collection=metadata_collection, session_id=session_id, base_commit=None)
    res = [
        d async for d in db.list("meta/root", collection=metadata_collection, session_id=session_id, base_commit=None, filter=expression)
    ]
    assert not len(res)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expression",
    [
        "avg(numbers)",  # avg
        "foo[?(a == `1` || b ==`2`) && c == `5`]",  # filter-projection
        "foo | bar",  # pipe
        "sort_by(Contents, &Date)",  # expref, sort_by
    ],
)
async def test_jmespath_unsupported_features_raises(db, expression):
    """We don't support many things. Assert a couple of valid examples to show that we raise in these scenarios."""
    metadata = {
        "attributes": {
            "flags": [{"spec": ["a", "b", "c", "d", "e"]}],
            "numbers": [1, 2, 3, 4, 5],
        }
    }
    test_doc = {
        "meta/root/hdf5/three.array.json": metadata,
    }
    session_id = SessionID(an_id(5))
    await db.add_docs(test_doc, collection=metadata_collection, session_id=session_id, base_commit=None)
    # http_metastore still uses ValueError, messaging is the same however
    with pytest.raises((JMESParseError, ValueError), match="Functionality*"):
        res = [
            d
            async for d in db.list("meta/root", collection=metadata_collection, session_id=session_id, base_commit=None, filter=expression)
        ]


@pytest.mark.asyncio
async def test_jmespath_bad_expression_raises(db):
    session_id = SessionID(an_id(5))
    expression = "XXC****&&"
    with pytest.raises((JMESParseError, ValueError), match=r"invalid token"):
        res = [
            d
            async for d in db.list("meta/root", collection=metadata_collection, session_id=session_id, base_commit=None, filter=expression)
        ]


@pytest.mark.asyncio
@pytest.mark.parametrize("compressor", [None, {"configuration": Blosc().get_config()}])
async def test_tree_with_compressor(db, compressor):
    test_doc = {
        "meta/root/hdf5/DataOne.array.json": {
            "attributes": {"_ARRAY_DIMENSIONS": ["phony_dim_0", "phony_dim_1"], "filters": None},
            "chunk_grid": {"chunk_shape": [16, 1], "separator": "/", "type": "regular"},
            "chunk_memory_layout": "C",
            "compressor": compressor,
            "data_type": "<f8",
            "extensions": [],
            "fill_value": 0.0,
            "shape": [16, 1],
        }
    }
    session = SessionID(an_id(5))
    await db.add_docs(test_doc, collection=metadata_collection, session_id=session, base_commit=None)
    _tree = await db.tree("meta/root/", session_id=session, base_commit=None)
    assert "hdf5" in _tree.trees
    assert _tree.trees["hdf5"].arrays["DataOne"].compressor == compressor


@pytest.mark.asyncio
async def test_tree_with_bad_commit(db, helpers):
    docs_a = helpers.gen_docs(10, prefix="meta/a/")
    docs_a_modified_content = {k: _generate_random_doc() for k in docs_a}
    session_1, commit_id_1 = await helpers.make_commit(db, {metadata_collection: docs_a})
    c, s = helpers.new_random_dbid(), "abc"
    with pytest.raises((ValueError, CommitNotFoundException), match=f"Error retrieving commit id {c}"):
        await db.tree("meta/root", session_id=s, base_commit=c)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filter_expr,expected",
    [
        ("connector.cloud_mask > `5`", ["implicit", "hdf5"]),
        ("connector.cloud_mask == `10`", ["implicit"]),
        ("connector.cloud_mask == `15`", ["hdf5"]),
        (
            "space.cloud_mask_values[0] == `10` || connector.cloud_mask == `15`",
            ["root", "hdf5"],
        ),
    ],
)
async def test_tree_multiple_results(db, filter_expr, expected):
    """Assert multiple matches yields multiple paths"""
    test_doc = {
        # doc has no attributes
        "meta/root/implicit/one.array.json": {},
        "meta/root/implicit/one.array.json": {
            "attributes": {"connector": {"cloud_mask": 10}},
        },
        "meta/root/hdf5/two.array.json": {
            "attributes": {"connector": {"cloud_mask": 15}},
        },
        "meta/root/root.group.json": {
            "attributes": {"space": {"cloud_mask_values": [10, 15]}},
        },
    }
    session_id = SessionID(an_id(5))
    await db.add_docs(test_doc, collection=metadata_collection, session_id=session_id, base_commit=None)

    _tree = await db.tree("meta/root", session_id=session_id, base_commit=None, filter=filter_expr)
    assert len(_tree.trees) == len(expected)
    assert sorted(list(_tree.trees)) == sorted(expected)


def _gen_chunk_doc(length, chunk_id="chunk-id", version=0, sid=None):
    hash = ChunkHash(method="foo", token=chunk_id)
    if version == 0:
        return ReferenceData.new_materialized_v0(uri=f"s3://arraylake-test/{chunk_id}", hash=hash, length=length).model_dump()
    if version == 1:
        if not sid:
            raise ValueError("sid must be provided when generating test ReferenceData")
        return ReferenceData.new_materialized_v1(length=length, hash=hash, sid=sid).model_dump()


async def _assert_size(db, prefix, session_id, commit_id, expected):
    size = await db.getsize(prefix, session_id=session_id, base_commit=commit_id)
    exp_count, exp_bytes = expected
    assert size.number_of_chunks == exp_count
    assert size.total_chunk_bytes == exp_bytes


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "prefix,expected",
    [
        # this is 3 because we actually perform the getsize operation at the _node_
        # level. this means that in our sample input data below, the fact that
        # chunk-id exists beneath two nodes (a, b) means that it will be counted twice.
        # if not for this detail, you would expect this number to be 2.
        (
            "",
            (3, 3000),
        ),
        (
            "data/root/a",
            (1, 1000),
        ),
        (
            "data/root/b",
            (2, 2000),
        ),
    ],
)
@pytest.mark.parametrize("rdv", [0, 1])
async def test_getsize(db, prefix, expected, rdv):
    session_id = SessionID("abc123")
    metadata_collection = CollectionName("metadata")
    chunk_collection = CollectionName("chunks")
    await _assert_size(db, "", session_id, None, (0, 0))
    # create a base case
    md_docs = {
        "meta/root/a.array.json": {},
        "meta/root/b.array.json": {},
    }
    version_args = {"version": rdv, "sid": session_id} if rdv == 1 else {"version": rdv}
    chunk_docs = {
        "data/root/a/c1": _gen_chunk_doc(1000, "chunk-id", **version_args),
        "data/root/a/c2": _gen_chunk_doc(1000, "chunk-id", **version_args),
        "data/root/b/c42/0": _gen_chunk_doc(1000, "chunk-id", **version_args),
        "data/root/b/c55/0/1": _gen_chunk_doc(1000, "chunk2-id", **version_args),
    }

    await db.add_docs(md_docs, collection=metadata_collection, session_id=session_id, base_commit=None)
    await db.add_docs(chunk_docs, collection=chunk_collection, session_id=session_id, base_commit=None)
    await _assert_size(db, prefix, session_id, None, expected)


@pytest.mark.asyncio
@pytest.mark.parametrize("rdv", [0, 1])
async def test_getsize_with_revisions(db, helpers, rdv):
    session_id = SessionID("abc123")
    metadata_collection = CollectionName("metadata")
    chunks_collection = CollectionName("chunks")

    # create a base case
    md_docs = {"meta/root/a.array.json": {}}

    version_args = {"version": rdv, "sid": session_id} if rdv == 1 else {"version": rdv}
    docs = {
        "data/root/a/c0/1": _gen_chunk_doc(1000, "chunk-id", **version_args),
        "data/root/a/c2/4": _gen_chunk_doc(1000, "chunk-id", **version_args),
    }
    prefix, expected = (
        "data/root/a",
        (1, 1000),
    )

    # write some docs and assert sizes
    # we only need to write metadata docs the first time
    session_id, commit_id = await helpers.make_commit(
        db, docs={CollectionName("metadata"): md_docs, CollectionName("chunks"): docs}, parent_commit=None
    )
    await _assert_size(db, prefix, session_id, commit_id, expected)

    # write the same docs again, in a new version
    session_id, commit_id = await helpers.make_commit(db, docs={CollectionName("chunks"): docs}, parent_commit=commit_id)
    await _assert_size(db, prefix, session_id, commit_id, expected)

    # overwrite a path with a new chunk / length
    new_docs = {"data/root/a/c2/0": _gen_chunk_doc(2000, "chunk2-id")}
    session_id, commit_id = await helpers.make_commit(db, docs={CollectionName("chunks"): new_docs}, parent_commit=commit_id)
    await _assert_size(db, prefix, session_id, commit_id, (2, 3000))

    # add a doc in a new version
    new_docs = {"data/root/a/c3/5": _gen_chunk_doc(1000, "chunk3-id")}
    session_id, commit_id = await helpers.make_commit(db, {CollectionName("chunks"): new_docs}, parent_commit=commit_id)
    await _assert_size(db, prefix, session_id, commit_id, (3, 4000))

    # add a duplicate chunk-id for a new chunk pointer
    new_sid = helpers.an_id(5)
    version_args = {"version": rdv, "sid": new_sid} if rdv == 1 else {"version": rdv}
    docs = {
        "data/root/a/c3/6": _gen_chunk_doc(1000, "chunk3-id", **version_args),
    }
    session_id, commit_id = await helpers.make_commit(db, {CollectionName("chunks"): docs}, parent_commit=commit_id)

    # in v1 we expect this to report twice until the chunks have been (eventually) de duplicated.
    # in v0 we do not.
    if rdv == 1:
        await _assert_size(db, prefix, session_id, commit_id, (4, 5000))
    else:
        await _assert_size(db, prefix, session_id, commit_id, (3, 4000))


@pytest.mark.asyncio
@pytest.mark.parametrize("rdv", [0, 1])
@pytest.mark.parametrize("metastore_class_and_config", metastore_params_only_mongo)
async def test_get_repo_size(db, helpers, rdv):
    session_id = SessionID("abc123")
    metadata_collection = CollectionName("metadata")
    chunks_collection = CollectionName("chunks")

    # create a base case
    md_docs = {"meta/root/a.array.json": {}}

    version_args = {"version": rdv, "sid": session_id} if rdv == 1 else {"version": rdv}
    docs = {
        "data/root/a/c0/1": _gen_chunk_doc(1000, "chunk-id", **version_args),
        "data/root/a/c2/4": _gen_chunk_doc(1000, "chunk-id", **version_args),
    }
    prefix, expected = (
        "data/root/a",
        (1, 1000),
    )

    # write some docs and assert sizes
    # we only need to write metadata docs the first time
    session_id, commit_id = await helpers.make_commit(
        db, docs={CollectionName("metadata"): md_docs, CollectionName("chunks"): docs}, parent_commit=None
    )
    sizes = await db.get_repo_size()
    sm = SizeMetrics(physical_chunks_count=1, logical_chunks_count=2, logical_size_bytes=2000, physical_size_bytes=1000)
    assert sizes == sm


@pytest.mark.asyncio
async def test_chunk_request_for_multiple_nodes_is_invalid(db):
    """Test we cannot request multiple nodes for chunks"""
    if isinstance(db, HttpMetastoreDatabase):
        with pytest.raises(ValueError, match="foo, bar|bar, foo"):
            [None async for _ in db.get_docs(["foo/c0", "bar/c0"], collection=chunks_collection, session_id="abc", base_commit=None)]
    elif isinstance(db, MongoMetastoreDatabase):
        with pytest.raises(MultipleNodesInChunksRequest) as ex_inf:
            [None async for _ in db.get_docs(["foo/c0", "bar/c0"], collection=chunks_collection, session_id="abc", base_commit=None)]
        assert sorted(ex_inf.value.paths) == sorted(["foo", "bar"])


@pytest.mark.asyncio
async def test_metadata_request_for_multiple_nodes_is_valid(db):
    """Test we can request multiple nodes for metadata"""
    session = SessionID(an_id(5))
    docs = {"a/foo.json": _generate_random_doc(), "a/bar.json": _generate_random_doc()}

    await db.add_docs(docs, collection="metadata", session_id=session, base_commit=None)
    res = [
        d.path
        async for d in db.get_docs(["a/foo.json", "a/bar.json"], collection=metadata_collection, session_id=session, base_commit=None)
    ]
    assert sorted(res) == sorted(["a/foo.json", "a/bar.json"])


@pytest.fixture
def db_and_write_params(db):
    # these settings reliably trigger the race condition on Ryan's machine
    if isinstance(db, MongoMetastoreDatabase):
        ndocs = 1
        nwrites = 100
    else:
        ndocs = 40
        nwrites = 10
    return db, ndocs, nwrites


@pytest.mark.asyncio
async def test_set_many_chunks_race_condition(db_and_write_params):
    db, ndocs, nwrites = db_and_write_params
    session = SessionID(an_id(6))
    collection = "chunks"

    # first insert array doc, this will trigger node creation for both the array metadata and the chunks
    await db.add_docs(
        {"meta/root/foo.array.json": _generate_random_doc()},
        collection="metadata",
        session_id=session,
        base_commit=None,
    )

    # many docs all at the same node
    futures = [
        db.add_docs(
            {f"data/root/foo/c0/{m}/{n}": _generate_random_doc() for n in range(ndocs)},
            collection=collection,
            session_id=session,
            base_commit=None,
        )
        for m in range(nwrites)
    ]
    # hope that this triggers the race condition
    await asyncio.gather(*futures)

    doc_list = [
        item async for item in db.list("data/root/foo", collection=collection, session_id=session, base_commit=None, all_subdirs=True)
    ]
    assert len(doc_list) == ndocs * nwrites


@pytest.mark.asyncio
@pytest.mark.parametrize("exception", [(DuplicateKeyError, "foo"), (BulkWriteError, {"writeErrors": [{"code": 11000}]})])
async def test_add_docs_node_conflict(db, exception):
    docs = {"meta/root/foo.json": {"data": "abc"}, "meta/root/bar.json": {"data": "def"}}
    session = SessionID(an_id(5))

    if isinstance(db, MongoMetastoreDatabase):
        exception_class, exception_contents = exception

        def raise_exception(*args, **kwargs):
            raise exception_class(exception_contents)

        with patch.object(AsyncIOMotorCollection, "insert_many", side_effect=raise_exception, autospec=True) as mock:
            with pytest.raises(NodeCreationConflict):
                await db.add_docs(docs, collection=metadata_collection, session_id=session, base_commit=None)
            assert mock.call_count == 5


@pytest.mark.parametrize("metastore_class_and_config", metastore_params_only_mongo)
async def test_can_read_old_schema_with_a_single_session_per_commit(db, helpers):
    special_msg = "old_style_set_session was here"

    def old_style_set_session(_self, commit, session_id):
        commit["session_id"] = session_id
        commit["message"] = special_msg

    with patch("arraylake_mongo_metastore.mongo_metastore_database.MongoMetastoreDatabase._set_session", new=old_style_set_session):
        commit_id = await helpers.make_commit(db, {metadata_collection: {"meta/root/foo.js": {}}})

    commits = [commit async for commit in db.get_commits(last_seen_commit=None, limit=0)]
    assert len(commits) == 1
    assert commits[0].message == special_msg


async def test_get_branches_by_name(db, helpers):
    session0, (c1, c2), _, _ = await helpers.make_commits_to_branch(db, 2, 2, "main", parent_commit_id=None)
    await db.update_branch("foo", session_id=session0, base_commit=None, new_commit=c1, new_branch=True)
    session1, (foo1, foo2), _, _ = await helpers.make_commits_to_branch(db, 2, 2, "foo", parent_commit_id=c1)
    await db.update_branch("bar", session_id=session1, base_commit=None, new_commit=foo1, new_branch=True)
    session2, (bar1, bar2), _, _ = await helpers.make_commits_to_branch(db, 2, 2, "bar", parent_commit_id=foo1)
    branches = await db.get_branches(names=["foo", "bar", "unknown"])
    assert len(branches) == 2
    (foo,) = (b for b in branches if b.id == "foo")
    (bar,) = (b for b in branches if b.id == "bar")
    assert foo.commit_id == foo2
    assert bar.commit_id == bar2


@pytest.mark.asyncio
async def test_new_tag_not_acknowledged(db, helpers):
    if isinstance(db, MongoMetastoreDatabase):
        session0, (c1,), _, _ = await helpers.make_commits_to_branch(db, 1, 2, "main", parent_commit_id=None)

        newtag = NewTag(label="new_tag", commit_id=c1, message=None, author_name="foo", author_email="foo@zoo.com")

        # TODO: for some reason I can't get patch.object to create an AsyncMock
        # so use this indirection instead.
        async def return_result():
            return InsertOneResult(inserted_id="foo", acknowledged=False)

        from unittest import mock

        with patch.object(AsyncIOMotorCollection, "insert_one", return_value=return_result(), autospec=True) as mock:
            with pytest.raises(ValueError):
                await db.new_tag(newtag)
            assert mock.call_count == 1
