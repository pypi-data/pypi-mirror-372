from __future__ import annotations

import asyncio
import json
import re
import uuid

import hypothesis
import hypothesis.strategies as st
import pytest
import zarr
from arraylake_mongo_metastore import MongoMetastoreConfig, MongoSessionedMetastore
from arraylake_mongo_metastore.expiration.generate import squash_commits
from hypothesis import assume
from hypothesis.stateful import (
    HealthCheck,
    RuleBasedStateMachine,
    Settings,
    invariant,
    precondition,
    rule,
    run_state_machine_as_test,
)
from tests.v1.helpers.test_utils import metastore_params_only_mongo

from arraylake.repos.v1.commits import CommitData
from arraylake.repos.v1.repo import AsyncRepo, Repo
from arraylake.repos.v1.types import CommitID

name_strategy = st.from_regex(r"[a-zA-Z0-9_\-.]{1,7}", fullmatch=True).filter(lambda s: s != "." and s != "..")
path_strategy = st.lists(name_strategy, min_size=1, max_size=5).map(lambda names: "/".join(names))


@st.composite
def meta_doc_strategy(draw):
    key = draw(name_strategy)
    value = draw(st.integers(max_value=999999999, min_value=-999999999))
    return {key: value}


def meta_doc_strategy_as_bytes():
    return meta_doc_strategy().map(lambda doc: bytes(json.dumps(doc), "utf-8"))


@st.composite
def chunk_doc_strategy(draw):
    key = draw(name_strategy)
    value = draw(st.integers(max_value=999999999, min_value=-999999999))
    return {key: value}


def chunk_doc_strategy_as_bytes():
    return chunk_doc_strategy().map(lambda doc: bytes(json.dumps(doc), "utf-8"))


meta_path_strategy = path_strategy.map(lambda p: f"meta/root/{p}")
chunk_path_strategy = path_strategy.map(lambda p: f"data/root/{p}")


def metas():
    return st.dictionaries(meta_path_strategy, meta_doc_strategy_as_bytes(), min_size=1, max_size=5)


def coord_st(num_dim=3):
    return st.lists(st.integers(min_value=0, max_value=999), min_size=num_dim, max_size=num_dim).map(lambda cs: "/".join(map(str, cs)))


@st.composite
def single_array_chunks(draw):
    path = draw(chunk_path_strategy)
    dim = draw(st.integers(min_value=1, max_value=4))
    coords = draw(st.lists(coord_st(dim), min_size=1, max_size=3))
    paths = [path + "/c" + coord for coord in coords]
    return {path: draw(chunk_doc_strategy_as_bytes()) for path in paths}


@st.composite
def chunks(draw):
    result = {}
    for d in draw(st.lists(single_array_chunks(), min_size=1, max_size=3)):
        result.update(d)
    return result


class AsWithoutSquashing(RuleBasedStateMachine):
    def __init__(self, squashed_repo, unsquashed_repo):
        super().__init__()
        print("-------  Starting new flow -------")
        self.can_commit = False
        self.has_metas = False
        self.has_chunks = False
        self.commits = []

        self.squashed_repo = squashed_repo
        self.unsquashed_repo = unsquashed_repo

        self.squashed_repo.checkout()
        self.unsquashed_repo.checkout()

        zarr.group(store=self.squashed_repo.store)
        zarr.group(store=self.unsquashed_repo.store)

    @rule(chunks=chunks())
    def add_chunks(self, chunks):
        self.squashed_repo.store.setitems(chunks)
        self.unsquashed_repo.store.setitems(chunks)
        self.can_commit = True
        self.has_chunks = True

    @rule(metas=metas())
    def add_metas(self, metas):
        self.squashed_repo.store.setitems(metas)
        self.unsquashed_repo.store.setitems(metas)
        self.can_commit = True
        self.has_metas = True

    @rule(data=st.data())
    @precondition(lambda self: self.has_metas)
    def overwrite_metas(self, data):
        print(f"Overwriting metas")
        all_metas = self.unsquashed_repo.store.list_prefix("meta")
        path_st = st.sampled_from(all_metas)
        paths = data.draw(st.sets(path_st, min_size=1, max_size=len(all_metas)), label="Meta overwrite paths")
        items = {}
        for path in paths:
            items[path] = data.draw(meta_doc_strategy_as_bytes(), label="Meta overwrite document")

        self.squashed_repo.store.setitems(items)
        self.unsquashed_repo.store.setitems(items)
        self.can_commit = True

    @rule(data=st.data())
    @precondition(lambda self: self.has_chunks)
    def overwrite_chunks(self, data):
        print(f"Overwriting chunks")
        all_chunks = self.unsquashed_repo.store.list_prefix("data")
        path_st = st.sampled_from(all_chunks)
        paths = data.draw(st.sets(path_st, min_size=1, max_size=len(all_chunks)), label="Chunk overwrite paths")
        items = {}
        for path in paths:
            items[path] = data.draw(chunk_doc_strategy_as_bytes(), label="Chunk overwrite document")

        self.squashed_repo.store.setitems(items)
        self.unsquashed_repo.store.setitems(items)
        self.can_commit = True

    @rule()
    @precondition(lambda self: self.can_commit)
    def commit(self):
        commit_id = self.squashed_repo.commit("a commit")
        self.unsquashed_repo.commit("a commit")
        self.can_commit = False
        self.commits.append(commit_id)

    @rule(data=st.data())
    @precondition(lambda self: len(self.commits) > 1)
    def squash(self, data):
        slice_st = st.slices(len(self.commits)).filter(lambda s: s.step == 1)
        commits_st = slice_st.map(lambda s: self.commits[s]).filter(lambda cs: len(cs) > 1)
        commits = data.draw(commits_st, label="Commits to squash")
        batch_size = data.draw(st.integers(min_value=1, max_value=100), label="supersede batch size")
        print(f"Squashing commits: {commits!r}")

        num_commits_before_squash = len(self.commits)
        self.squashed_repo.squash_commits(
            into=commits[-1],
            commits=list(reversed(commits[0:-1])),
            supersede_batch_size=batch_size,
        )

        self.squashed_repo.commit_data(refresh=True)
        new_commits = [c.id for c in self.squashed_repo.commit_log]
        new_commits.reverse()
        self.commits = new_commits
        num_commits_after_squash = len(self.commits)
        print(f"Commits before: {num_commits_before_squash}  Commits after: {num_commits_after_squash}")

        assert num_commits_after_squash < num_commits_before_squash

    # ------------------------   checks ---------------------------

    @rule(data=st.data())
    @precondition(lambda self: self.has_metas)
    def check_some_meta_docs(self, data):
        squashed_paths = sorted(self.squashed_repo.store.list_prefix("meta"))

        path_st = st.sampled_from(squashed_paths)
        paths = data.draw(st.sets(path_st, min_size=1), label="Keys to check")

        print(f"Checking {len(paths)} metadata docs")

        assert self.squashed_repo.store.getitems(paths) == self.unsquashed_repo.store.getitems(paths)

    @rule(data=st.data())
    @precondition(lambda self: self.has_chunks)
    def check_some_chunk_docs(self, data):
        """We need to be careful in this one because getitems
        can only retrieve chunks for a single node"""

        squashed_paths = sorted(self.squashed_repo.store.list_prefix("data"))

        path = data.draw(st.sampled_from(squashed_paths), label="Node to check")
        node, _ = path.rsplit("/c", 1)
        paths = [p for p in squashed_paths if re.match(rf"{node}/c[\d/]+$", p)]

        print(f"Checking {len(paths)} chunk docs")

        assert self.squashed_repo.store.getitems(paths) == self.unsquashed_repo.store.getitems(paths)

    @invariant()
    @precondition(lambda self: self.has_metas or self.has_chunks)
    def check_list_prefix(self):
        squashed_paths = sorted(self.squashed_repo.store.list_prefix(""))
        unsquashed_paths = sorted(self.unsquashed_repo.store.list_prefix(""))
        assert sorted(squashed_paths) == sorted(unsquashed_paths)


def patch_repos():
    """This is a hack to easily call async methods from a sync context"""

    async def async_squash_commits(
        self,
        into: CommitID,
        commits: list[CommitID],
        supersede_batch_size: int,
    ) -> None:
        await squash_commits(self.db, into, commits, supersede_batch_size)

    def sync_commit_data(self, refresh: bool = False) -> CommitData:
        return self._synchronize(self._arepo.commit_data, refresh)

    def sync_squash_commits(
        self,
        into: CommitID,
        commits: list[CommitID],
        supersede_batch_size: int,
    ) -> None:
        return self._synchronize(self._arepo.squash_commits, into, commits, supersede_batch_size)

    AsyncRepo.squash_commits = async_squash_commits
    Repo.commit_data = sync_commit_data
    Repo.squash_commits = sync_squash_commits


@pytest.mark.parametrize("metastore_class_and_config", metastore_params_only_mongo)
@pytest.mark.slow
def test_commit_squashing(new_sync_repo, event_loop):
    # TODO: Flip managed_sessions=True when it becomes a required setting.
    config = MongoMetastoreConfig("mongodb://localhost:27017/mongodb", managed_sessions=True)
    metastore = MongoSessionedMetastore(config)
    rand = str(uuid.uuid4()).replace("-", "")
    squashed_repo_name = f"test_squash_{rand}___squashed"
    unsquashed_repo_name = f"test_squash_{rand}___unsquashed"

    patch_repos()

    async def mk_test_instance():
        metastore._client.close
        try:
            await metastore.delete_database(squashed_repo_name, imsure=True, imreallysure=True)
            await metastore.delete_database(unsquashed_repo_name, imsure=True, imreallysure=True)
        except:
            pass

        squashed_db = await metastore.create_database(squashed_repo_name)
        unsquashed_db = await metastore.create_database(unsquashed_repo_name)

        author = new_sync_repo._arepo.author
        chunkstore = new_sync_repo._arepo.chunkstore

        squashed_repo = Repo.from_metastore_and_chunkstore(
            metastore_db=squashed_db, chunkstore=chunkstore, name=squashed_repo_name, author=author
        )
        unsquashed_repo = Repo.from_metastore_and_chunkstore(
            metastore_db=unsquashed_db, chunkstore=chunkstore, name=unsquashed_repo_name, author=author
        )

        return AsWithoutSquashing(squashed_repo, unsquashed_repo)

    def mk_test_instance_sync():
        return event_loop.run_until_complete(mk_test_instance())

    settings = Settings(max_examples=50, verbosity=hypothesis.Verbosity.verbose, deadline=None, suppress_health_check=list(HealthCheck))
    run_state_machine_as_test(mk_test_instance_sync, settings=settings)
