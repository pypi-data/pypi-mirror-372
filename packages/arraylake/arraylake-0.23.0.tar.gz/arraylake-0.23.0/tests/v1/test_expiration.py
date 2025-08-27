import secrets
from operator import attrgetter

import pytest
from arraylake_mongo_metastore import MongoMetastore, MongoMetastoreConfig
from arraylake_mongo_metastore.expiration.generate import (
    BranchPointer,
    CannotSquashReachableCommit,
    Pointer,
    ReachableCommit,
    dangling_commits,
    reachable_commits,
    squash_commits,
    unsafe_delete_dangling_commits,
)

from arraylake.repos.v1.types import BranchName, CollectionName

metadata_collection = CollectionName("metadata")
chunks_collection = CollectionName("chunks")
nodes_collection = CollectionName("nodes")


@pytest.mark.asyncio
@pytest.fixture()
async def db():
    # TODO: Flip managed_sessions=True or remove entirely once managed sessions are mandatory.
    config = MongoMetastoreConfig("mongodb://localhost:27017/mongodb", managed_sessions=False)
    metastore = MongoMetastore(config)
    db_name = f"db_{secrets.token_hex(8)}"
    db = await metastore.create_database(db_name)
    yield db


async def test_squash_commits(db, helpers):
    """Creates 5 committed sessions and then squashes the first 4

    Verifies data doesn't change if looked from the last commit, and that
    sessions have been superseded and have fewer documents.
    """

    # we write some data

    meta0 = helpers.gen_docs(2, prefix=f"meta/root/foo-")
    session0, commit_id_0 = await helpers.make_commit(db, {metadata_collection: meta0}, parent_commit=None)
    await db.update_branch("main", session_id=session0, base_commit=None, new_commit=commit_id_0, new_branch=True)

    meta1 = helpers.gen_docs(2, prefix=f"meta/root/foo-")
    chunks1 = helpers.gen_chunks(2, path=f"data/root/foo-")
    session1, commit_id_1 = await helpers.make_commit(
        db, {metadata_collection: meta1, chunks_collection: chunks1}, parent_commit=commit_id_0
    )
    await db.update_branch("main", session_id=session1, base_commit=commit_id_0, new_commit=commit_id_1, new_branch=False)

    # we write more data in a different session
    meta2 = helpers.gen_docs(2, prefix=f"meta/root/bar-")
    chunks2 = helpers.gen_chunks(2, path=f"data/root/bar-")
    session2, commit_id_2 = await helpers.make_commit(
        db, {metadata_collection: meta2, chunks_collection: chunks2}, parent_commit=commit_id_1
    )
    await db.update_branch("main", session_id=session2, base_commit=commit_id_1, new_commit=commit_id_2, new_branch=False)

    # session3 overwrites data from session 2
    session3, commit_id_3 = await helpers.make_commit(
        db, {metadata_collection: meta2, chunks_collection: chunks2}, parent_commit=commit_id_2
    )
    await db.update_branch("main", session_id=session3, base_commit=commit_id_2, new_commit=commit_id_3, new_branch=False)

    # session4 overwrites data from session 2 again, but adds some new data of its own
    meta4 = helpers.gen_docs(1, prefix=f"meta/root/baz-")
    chunks4 = helpers.gen_chunks(1, path=f"data/root/baz-")
    session4, commit_id_4 = await helpers.make_commit(
        db, {metadata_collection: {**meta2, **meta4}, chunks_collection: {**chunks2, **chunks4}}, parent_commit=commit_id_3
    )
    await db.update_branch("main", session_id=session4, base_commit=commit_id_3, new_commit=commit_id_4, new_branch=False)

    # session5 writes some more new data
    meta5 = helpers.gen_docs(2, prefix=f"meta/root/final-")
    chunks5 = helpers.gen_chunks(2, path=f"data/root/final-")
    session5, commit_id_5 = await helpers.make_commit(
        db, {metadata_collection: meta5, chunks_collection: chunks5}, parent_commit=commit_id_4
    )
    await db.update_branch("main", session_id=session5, base_commit=commit_id_4, new_commit=commit_id_5, new_branch=False)

    all_metas = [*meta1, *meta2, *meta4, *meta5]
    docs_before_supersede = [
        doc async for doc in db.get_docs(all_metas, collection=metadata_collection, session_id="foo", base_commit=commit_id_5)
    ]
    # chunks have to be requested node by node
    chunks_before_supersede = [
        doc async for doc in db.get_docs(chunks1, collection=chunks_collection, session_id="foo", base_commit=commit_id_5)
    ]
    chunks_before_supersede.extend(
        [doc async for doc in db.get_docs(chunks2, collection=chunks_collection, session_id="foo", base_commit=commit_id_5)]
    )
    chunks_before_supersede.extend(
        [doc async for doc in db.get_docs(chunks5, collection=chunks_collection, session_id="foo", base_commit=commit_id_5)]
    )

    # Here we do the operation under test
    await squash_commits(metastore=db, into=commit_id_4, ancestors=[commit_id_3, commit_id_2, commit_id_1], supersede_batch_size=1)

    # now all the checks
    sorter = attrgetter("id")

    # some commits were deleted
    commits = sorted([commit async for commit in db.get_commits(last_seen_commit=None, limit=0)], key=sorter)
    assert [commit.id for commit in commits] == [commit_id_0, commit_id_4, commit_id_5]

    # the commit tree is preserved
    commit0, commit4, commit5 = commits
    assert commit5.parent_commit == commit4.id
    assert commit4.parent_commit == commit0.id

    docs_after_supersede = [
        doc async for doc in db.get_docs(all_metas, collection=metadata_collection, session_id="foo", base_commit=commit_id_5)
    ]
    chunks_after_supersede = [
        doc async for doc in db.get_docs(chunks1, collection=chunks_collection, session_id="foo", base_commit=commit_id_5)
    ]
    chunks_after_supersede.extend(
        [doc async for doc in db.get_docs(chunks2, collection=chunks_collection, session_id="foo", base_commit=commit_id_5)]
    )
    chunks_after_supersede.extend(
        [doc async for doc in db.get_docs(chunks5, collection=chunks_collection, session_id="foo", base_commit=commit_id_5)]
    )

    # check all docs before and after the squash are the same, if looked from the last commit
    assert sorted(docs_before_supersede, key=sorter) == sorted(docs_after_supersede, key=sorter)
    assert sorted(chunks_before_supersede, key=sorter) == sorted(chunks_after_supersede, key=sorter)

    # we verify:
    # - session 1 writes 2 meta and 2 chunks
    # - session 2 is completely overwritten so 0 docs
    # - session 3 is completely overwritten so 0 docs
    # - session 4 has 3 meta and 3 chunks
    # - session 5 has 2 meta and 2 chunks
    for coll in [metadata_collection, chunks_collection]:
        paths = [path async for path in db.get_all_paths_for_session(session_id=session1, base_commit=None, collection=coll)]
        assert len(paths) == 2

        paths = [path async for path in db.get_all_paths_for_session(session_id=session2, base_commit=commit_id_1, collection=coll)]
        assert len(paths) == 0

        paths = [path async for path in db.get_all_paths_for_session(session_id=session3, base_commit=commit_id_2, collection=coll)]
        assert len(paths) == 0

        paths = [path async for path in db.get_all_paths_for_session(session_id=session4, base_commit=commit_id_3, collection=coll)]
        assert len(paths) == 3

        paths = [path async for path in db.get_all_paths_for_session(session_id=session5, base_commit=commit_id_4, collection=coll)]
        assert len(paths) == 2

    paths = [path async for path in db.get_all_paths_for_session(session_id=session1, base_commit=None, collection=nodes_collection)]
    assert len(paths) == 3

    paths = [path async for path in db.get_all_paths_for_session(session_id=session2, base_commit=commit_id_1, collection=nodes_collection)]
    assert len(paths) == 3

    paths = [path async for path in db.get_all_paths_for_session(session_id=session3, base_commit=commit_id_2, collection=nodes_collection)]
    assert len(paths) == 0

    paths = [path async for path in db.get_all_paths_for_session(session_id=session4, base_commit=commit_id_3, collection=nodes_collection)]
    assert len(paths) == 2

    paths = [path async for path in db.get_all_paths_for_session(session_id=session5, base_commit=commit_id_4, collection=nodes_collection)]
    assert len(paths) == 3


async def test_cannot_squash_reachable_commits(db, helpers):
    """
    Create a chain of commits: main - - -> c3 -> c2 -> c1.
    Then attach four new commits to c2: foo - - -> foo2 -> foo1 -> c1.

    Assert c2 and c1 cannot be squashed because c1 would drop foo's history.
    """
    _, (c1, c2, c3), _, _ = await helpers.make_commits_to_branch(db, 3, 2, BranchName("main"), parent_commit_id=None)
    await db.update_branch("foo", base_commit=None, new_commit=c1, new_branch=True)
    _, (foo1, foo2), _, _ = await helpers.make_commits_to_branch(db, 2, 2, "foo", parent_commit_id=c1)

    with pytest.raises(CannotSquashReachableCommit) as exc_info:
        await squash_commits(metastore=db, into=c2, ancestors=[c1], supersede_batch_size=1)
    assert exc_info.value.pointers == {BranchPointer(branch=BranchName("foo"))}


def pointed_by_branch(commit: ReachableCommit, branch: BranchName):
    def reached(pointer: Pointer):
        if isinstance(pointer, BranchPointer):
            return pointer.branch == branch
        else:
            return False

    return any([reached(pointer) for pointer in commit.reachable_from])


async def test_reachable_commits(db, helpers):
    """
    Create a chain of commits: main - - -> c4 -> c3 -> c2 -> c1.
    Then attach four new commits to c2: foo - - -> foo4 -> foo3 -> foo2 -> foo1 -> c2 -> c1.
    Asserts:
        - c_n is reachable from c4
        - c_n is reachable by main
        - c2 and c1 are reachable by foo
        - foo_n + c2 + c1 are reachable from foo4
        - all the previous are reachable by foo
        - foo_n in not reachable by main
    """
    _, (c1, c2, c3, c4), _, _ = await helpers.make_commits_to_branch(db, 4, 2, "main", parent_commit_id=None)

    await db.update_branch("foo", base_commit=None, new_commit=c2, new_branch=True)
    _, (foo1, foo2, foo3, foo4), _, _ = await helpers.make_commits_to_branch(db, 4, 2, "foo", parent_commit_id=c2)

    res = list(await reachable_commits(db, c4, to_commit=None))
    assert res[0].commit.id == c4
    (r4, r3, r2, r1) = res
    assert [c.commit.id for c in res] == [c4, c3, c2, c1]
    assert all([pointed_by_branch(c, BranchName("main")) for c in res])
    assert all([pointed_by_branch(c, BranchName("foo")) for c in [r2, r1]])

    res = list(await reachable_commits(db, foo4, to_commit=None))
    assert res[0].commit.id == foo4
    (r4, r3, r2, r1, oldc2, oldc1) = res

    assert [c.commit.id for c in res] == [foo4, foo3, foo2, foo1, c2, c1]
    assert all([pointed_by_branch(c, BranchName("foo")) for c in res])
    assert not (any([pointed_by_branch(c, BranchName("main")) for c in [r1, r2, r3, r4]]))


async def test_reachable_commits_stops_on_to_commit(db, helpers):
    _, (c1, c2, c3, c4), _, _ = await helpers.make_commits_to_branch(db, 4, 2, "main", parent_commit_id=None)
    res = list(await reachable_commits(db, c4, to_commit=c2))
    assert [c.commit.id for c in res] == [c4, c3, c2]


async def test_delete_dangling_commits(db, helpers) -> None:
    """
    Create a chain of commits: main_branch - - -> c5 -> c4 -> c3 -> c2 -> c1.
    Then attach four new commits to c2: foo - - -> foo4 -> foo3 -> foo2 -> foo1 -> c2 -> c1.
    Then attach four new commits to c3: bar - - -> bar4 -> bar3 -> bar2 -> bar1 -> c3 -> c2 -> c1.
    Then delete branch main, delete dangling commits, and assert that c5 and c4 are deleted.
    """

    _, (c1, c2, c3, c4, c5), _, _ = await helpers.make_commits_to_branch(db, 5, 2, "main_branch", parent_commit_id=None)

    await db.update_branch("foo", base_commit=None, new_commit=c2, new_branch=True)
    await db.update_branch("bar", base_commit=None, new_commit=c3, new_branch=True)

    _, (foo1, foo2, foo3, foo4), _, _ = await helpers.make_commits_to_branch(db, 4, 2, "foo", parent_commit_id=c2)
    _, (bar1, bar2, bar3, bar4), _, _ = await helpers.make_commits_to_branch(db, 4, 2, "bar", parent_commit_id=c3)

    assert len([commit async for commit in db.get_commits(last_seen_commit=None, limit=0)]) == 13

    assert await db.delete_branch("main_branch")
    dangling = []
    res = await unsafe_delete_dangling_commits(db, pre_delete=lambda doc: dangling.append(doc["_id"]))
    assert res == (2, 2)
    assert sorted(map(str, dangling)) == sorted([str(c4), str(c5)])

    remaining_commits = {commit.id async for commit in db.get_commits(last_seen_commit=None, limit=0)}

    assert len(remaining_commits) == 11
    assert c1 in remaining_commits
    assert c2 in remaining_commits
    assert c3 in remaining_commits
    assert c4 not in remaining_commits
    assert c5 not in remaining_commits


async def test_dangling_commit_detection(db, helpers):
    commits = []
    for i in range(5):
        meta = helpers.gen_docs(1, prefix="some/array")
        _, commit_id = await helpers.make_commit(db, {metadata_collection: meta}, parent_commit=None)
        commits.append(commit_id)

    await db.update_branch("foo", base_commit=None, new_commit=commits[-1], new_branch=True)

    res = [str(commit["_id"]) async for commit in dangling_commits(db)]
    assert len(res) == 4
    assert sorted(res) == sorted(map(str, commits[:-1]))
