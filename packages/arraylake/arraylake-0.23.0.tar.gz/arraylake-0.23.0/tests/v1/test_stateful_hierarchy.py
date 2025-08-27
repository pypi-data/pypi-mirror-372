import asyncio
import copy
import os.path
import re
import time
import unittest
from contextlib import closing
from dataclasses import dataclass
from enum import Enum, auto
from itertools import zip_longest
from operator import itemgetter

import hypothesis
import hypothesis.extra.numpy as npst
import hypothesis.strategies as st
import numpy as np
import pytest
import zarr
from arraylake_mongo_metastore import MongoMetastoreConfig, MongoSessionedMetastore
from hypothesis import assume, note
from hypothesis.stateful import (
    Bundle,
    HealthCheck,
    RuleBasedStateMachine,
    Settings,
    consumes,
    initialize,
    invariant,
    precondition,
    rule,
    run_state_machine_as_test,
)
from numpy.testing import assert_array_equal
from tests.v1.helpers.test_utils import metastore_params_only_mongo

# TODO: replace with "from zarr import ..."  when the EXPERIMENTAL flag is unnecessary
from zarr._storage.v3 import MemoryStoreV3

from arraylake import Client
from arraylake.asyn import sync
from arraylake.repos.v1.repo import Repo


@st.composite
def unique(draw, strategy):
    # https://stackoverflow.com/questions/73737073/create-hypothesis-strategy-that-returns-unique-values
    seen = draw(st.shared(st.builds(set), key="key-for-unique-elems"))
    return draw(strategy.filter(lambda x: x not in seen).map(lambda x: seen.add(x) or x))


# A hypotesis strategy to generate group/array names
name_strategy = st.from_regex(r"[a-zA-Z0-9_\-.]{1,7}", fullmatch=True).filter(lambda s: s != "." and s != "..")
branch_name_strategy = unique(strategy=st.text(min_size=1))


@st.composite
def array_strategy(draw):
    """A hypothesis strategy to generate small sized random arrays.

    Returns: a tuple of the array and a suitable random chunking for it.
    """
    array = draw(npst.arrays(dtype=npst.scalar_dtypes(), shape=npst.array_shapes(max_dims=4)))
    # We want this strategy to shrink towards arrays with smaller number of chunks
    # 1. st.integers() shrinks towards smaller values. So we use that to generate number of chunks
    numchunks = draw(st.tuples(*[st.integers(min_value=1, max_value=size) for size in array.shape]))
    # 2. and now generate the chunks tuple
    chunks = tuple(size // nchunks for size, nchunks in zip(array.shape, numchunks))
    return (array, chunks)


class SessionType(Enum):
    """Used in the Model to represent the current type of session"""

    PERSISTENT = auto()
    TRANSIENT = auto()


@dataclass
class SessionState:
    """We model our repo with a zarr MemoryStoreV3"""

    store: MemoryStoreV3
    changes_made: bool


class Model:
    """The model for our repo actions"""

    def __init__(self):
        self.sessions = {
            SessionType.PERSISTENT: SessionState(store=self._mk_store(), changes_made=False),
            SessionType.TRANSIENT: SessionState(store=self._mk_store(), changes_made=False),
        }
        self.current_session = SessionType.PERSISTENT
        self._checkpoint_model = None
        self.checkpoint_id = None

    def _mk_store(self):
        store = MemoryStoreV3()
        # create root group
        zarr.group(store=store)
        return store

    def reset_transient_session(self):
        self.sessions[SessionType.TRANSIENT] = SessionState(store=copy.deepcopy(self._checkpoint_model), changes_made=False)

    @property
    def _session(self):
        return self.sessions[self.current_session]

    @property
    def _store(self):
        return self._session.store

    def changes_made(self, made_changes=True):
        self._session.changes_made = made_changes

    @property
    def has_changes(self) -> bool:
        return self._session.changes_made

    def is_persistent_session(self):
        return self.current_session == SessionType.PERSISTENT

    def all_groups(self):
        matches = [
            re.search(r"(meta/root\.group\.json)|(meta/root/(.*)\.group\.json$)", path)
            for path in self._store.list_prefix("")
            if path.endswith(".group.json")
        ]
        res = [m.group(3) or "" for m in matches if m]
        return sorted(res, key=lambda s: s.count("/"))

    def all_arrays(self):
        matches = [path for path in self._store.list_prefix("") if path.endswith(".array.json")]
        res = [m.replace("meta/root/", "").replace(".array.json", "") for m in matches]
        return sorted(res, key=lambda s: s.count("/"))

    def can_add(self, parent: str, name: str) -> bool:
        path = f"{parent}/{name}".lstrip("/")
        return path not in self.all_groups() and path not in self.all_arrays()

    def get_group(self, path) -> zarr.Group:
        return zarr.open_group(path=path, mode="r+", store=self._store)

    def add_group(self, path):
        g1 = zarr.group(store=self._store, path=path)
        self.changes_made()

    def add_array(self, array, chunks, path):
        zarr.array(array, chunks=chunks, path=path, store=self._store)
        self.changes_made()

    def get_array(self, path):
        pass

    def rename(self, from_path, to_path):
        self._store.rename(from_path, to_path)
        self.changes_made()

    def delete(self, path):
        del self.get_group("/")[path]
        self.changes_made()

    def list_prefix(self, prefix):
        return self._store.list_prefix(prefix)

    def swap_sessions(self):
        assert self._session.changes_made, "Swapping sessions without appling any changes"
        if self.is_persistent_session():
            self.current_session = SessionType.TRANSIENT
        else:  # we currently are in transient store
            self.current_session = SessionType.PERSISTENT

    def has_checkpoint(self) -> bool:
        return self._checkpoint_model is not None

    def checkpoint(self, checkpoint_id):
        assert self.current_session == SessionType.PERSISTENT
        self._checkpoint_model = copy.deepcopy(self._session.store)
        self.checkpoint_id = checkpoint_id


class AsMemoryStore(RuleBasedStateMachine):
    def __init__(self, input_repo, metastore):
        super().__init__()
        note("-------  Starting new flow -------")

        self.metastore = metastore
        # Always create new repos. This allows us to start from a known empty state
        # And is necessary for hypothesis to shrink properly.
        # Failure to do this results in a "flaky data generation" error because some state
        # (e.g. branch names) persists between attempts to shrink a failing example
        persistent_repo = asyncio.run(mk_new_repo(repo=input_repo, metastore=metastore))
        transient_repo = asyncio.run(mk_new_repo(repo=input_repo, metastore=metastore))

        persistent_repo.checkout()
        transient_repo.checkout()

        # Make sure there is no persistent state on the repo
        assert not persistent_repo.commit_log.commit_data.branches
        assert not transient_repo.commit_log.commit_data.branches

        zarr.group(store=transient_repo.store)
        zarr.group(store=persistent_repo.store)
        self.repos = {
            SessionType.PERSISTENT: persistent_repo,
            SessionType.TRANSIENT: transient_repo,
        }
        self.model = Model()
        self.branch_names = []

    @property
    def repo(self):
        return self.repos[self.model.current_session]

    # -------------------- store operations -----------------------
    @rule(name=name_strategy, data=st.data())
    def add_group(self, name, data):
        parent = data.draw(st.sampled_from(self.model.all_groups()), label="Group parent")
        assume(self.model.can_add(parent, name))
        path = f"{parent}/{name}".lstrip("/")
        note(f"Adding group: path='{path}'")
        self.model.add_group(path)
        zarr.group(store=self.repo.store, path=path)

    @rule(data=st.data(), name=name_strategy, array_and_chunks=array_strategy())
    def add_array(self, data, name, array_and_chunks):
        array, chunks = array_and_chunks
        parent = data.draw(st.sampled_from(self.model.all_groups()), label="Array parent")
        assume(self.model.can_add(parent, name))
        path = f"{parent}/{name}".lstrip("/")
        note(f"Adding array:  path='{path}'  shape={array.shape}  chunks={chunks}")
        self.model.add_array(array, chunks, path)
        zarr.array(array, chunks=chunks, path=path, store=self.repo.store)

    @precondition(lambda self: bool(self.model.all_groups()))
    @precondition(lambda self: bool(self.model.all_arrays()))
    @rule(data=st.data())
    def move_array(self, data):
        array_path = data.draw(st.sampled_from(self.model.all_arrays()), label="Array move source")
        to_group = data.draw(st.sampled_from(self.model.all_groups()), label="Array move destination")

        # fixme renaiming to self?
        array_name = os.path.basename(array_path)
        assume(self.model.can_add(to_group, array_name))
        new_path = f"{to_group}/{array_name}".lstrip("/")
        note(f"moving array '{array_path}' -> '{new_path}'")
        self.model.rename(array_path, new_path)
        self.repo.store.rename(array_path, new_path)

    @precondition(lambda self: len(self.model.all_groups()) >= 2)
    @rule(data=st.data())
    def move_group(self, data):
        from_group = data.draw(st.sampled_from(self.model.all_groups()), label="Group move source")
        to_group = data.draw(st.sampled_from(self.model.all_groups()), label="Group move destination")
        assume(not to_group.startswith(from_group))

        from_group_name = os.path.basename(from_group)
        assume(self.model.can_add(to_group, from_group_name))
        # fixme renaiming to self?
        new_path = f"{to_group}/{from_group_name}".lstrip("/")
        note(f"moving group '{from_group}' -> '{new_path}'")
        self.model.rename(from_group, new_path)
        self.repo.store.rename(from_group, new_path)

    @precondition(lambda self: len(self.model.all_arrays()) >= 1)
    @rule(data=st.data())
    def delete_array_using_del(self, data):
        array_path = data.draw(st.sampled_from(self.model.all_arrays()), label="Array deletion target")
        note(f"Deleting array '{array_path}' using del")
        self.model.delete(array_path)
        del self.repo.root_group[array_path]

    @precondition(lambda self: len(self.model.all_groups()) >= 2)  # fixme don't delete root
    @rule(data=st.data())
    def delete_group_using_rmdir(self, data):
        group_path = data.draw(st.sampled_from(self.model.all_groups()), label="Group deletion target")
        assume(group_path != "")  # fixme
        note(f"Deleting group '{group_path}' using rmdir")
        self.model.delete(group_path)
        zarr.storage.rmdir(store=self.repo.store, path=group_path)

    @precondition(lambda self: len(self.model.all_groups()) >= 2)  # fixme don't delete root
    @rule(data=st.data())
    def delete_group_using_del(self, data):
        group_path = data.draw(st.sampled_from(self.model.all_groups()), label="Group deletion target")
        assume(group_path != "")  # fixme
        note(f"Deleting group '{group_path}' using del")
        self.model.delete(group_path)
        del self.repo.root_group[group_path]

    # ------------------------- session operations ---------------
    @precondition(lambda self: self.model.is_persistent_session())
    @precondition(lambda self: self.model.has_changes)
    @rule(branch_name=branch_name_strategy)
    def commit(self, branch_name):
        note(f"creating new branch: {branch_name}, known branches: {self.branch_names}")
        self.repo.new_branch(branch_name)
        self.branch_names += [branch_name]

        commit_id = self.repo.commit("some commit")
        num_commits = len(self.repo.commit_log)
        note(f"Committed repo: {num_commits} commits")
        self.model.changes_made(False)
        self.model.checkpoint(branch_name)

    @precondition(lambda self: self.model.has_changes)
    @rule()
    def swap_transient_persistent_sessions(self):
        note(f"Switching sessions from {self.model.current_session}")
        self.model.swap_sessions()

    @precondition(lambda self: not self.model.is_persistent_session())
    # fixme: we should be able to reset without commits
    @precondition(lambda self: self.model.has_checkpoint())
    @rule()
    def reset_transient_session(self):
        size = len(self.model.list_prefix(""))
        note(f"Resetting transient session with {size} keys")
        self.model.reset_transient_session()
        self.repo.checkout(self.model.checkpoint_id)

    # --------------- assertions -----------------
    def check_group_arrays(self, group):
        # note(f"Checking arrays of '{group}'")
        g1 = self.model.get_group(group)
        g2 = zarr.open_group(path=group, mode="r", store=self.repo.store)
        model_arrays = sorted(g1.arrays(), key=itemgetter(0))
        our_arrays = sorted(g2.arrays(), key=itemgetter(0))
        for (n1, a1), (n2, a2) in zip_longest(model_arrays, our_arrays):
            assert n1 == n2
            assert_array_equal(a1, a2)

    def check_subgroups(self, group_path):
        g1 = self.model.get_group(group_path)
        g2 = zarr.open_group(path=group_path, mode="r", store=self.repo.store)
        g1_children = [name for (name, _) in g1.groups()]
        g2_children = [name for (name, _) in g2.groups()]
        # note(f"Checking {len(g1_children)} subgroups of group '{group_path}'")
        assert g1_children == g2_children

    def check_list_prefix_from_group(self, group):
        prefix = f"meta/root/{group}"
        model_list = sorted(self.model.list_prefix(prefix))
        al_list = sorted(self.repo.store.list_prefix(prefix))
        # note(f"Checking {len(model_list)} keys under '{prefix}'")
        assert model_list == al_list

        prefix = f"data/root/{group}"
        model_list = sorted(self.model.list_prefix(prefix))
        al_list = sorted(self.repo.store.list_prefix(prefix))
        # note(f"Checking {len(model_list)} keys under '{prefix}'")
        assert model_list == al_list

    @precondition(lambda self: self.model.is_persistent_session())
    @rule(data=st.data())
    def check_group_path(self, data):
        t0 = time.time()
        group = data.draw(st.sampled_from(self.model.all_groups()))
        self.check_list_prefix_from_group(group)
        self.check_subgroups(group)
        self.check_group_arrays(group)
        t1 = time.time()
        note(f"Checks took {t1 - t0} sec.")

    @precondition(lambda self: self.model.is_persistent_session())
    @invariant()
    def check_list_prefix_from_root(self):
        model_list = self.model.list_prefix("")
        al_list = sorted(self.repo.store.list_prefix(""))
        note(f"Checking {len(model_list)} keys")
        assert sorted(model_list) == sorted(al_list)

    def teardown(self):
        note("tearing down...")
        repo = next(iter(self.repos.values()))
        sync(clear_metastore_async, name=repo.repo_name, metastore=self.metastore)


# TODO: http metastore testing is too slow for this
@pytest.mark.parametrize("metastore_class_and_config", metastore_params_only_mongo)
@pytest.mark.slow
def test_zarr_hierarchy(new_sync_repo):
    # TODO: Flip managed_sessions=True (or remove entirely) once it's mandatory.
    config = MongoMetastoreConfig("mongodb://localhost:27017/mongodb", managed_sessions=True)
    metastore = MongoSessionedMetastore(config)

    def mk_test_instance_sync():
        return AsMemoryStore(new_sync_repo, metastore)

    settings = Settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, max_examples=200)
    run_state_machine_as_test(mk_test_instance_sync, settings=settings)


async def mk_new_repo(repo, metastore):
    name = repo.repo_name
    author = repo._arepo.author
    chunkstore = repo._arepo.chunkstore
    db = await metastore.open_database(name)
    return Repo.from_metastore_and_chunkstore(metastore_db=db, chunkstore=chunkstore, name=name, author=author)


async def clear_metastore_async(name, metastore):
    await metastore.delete_database(name, imsure=True, imreallysure=True)
    await metastore.create_database(name)
