from dataclasses import dataclass

import pytest

pytest.importorskip("hypothesis")
pytest.importorskip("xarray")

import asyncio
import copy
import json

import hypothesis.strategies as st
import pytest
from arraylake_mongo_metastore import MongoMetastoreConfig, MongoSessionedMetastore
from arraylake_mongo_metastore.spec import MAX_TAG_OR_COMMIT_MESSAGE_SIZE
from hypothesis import note
from hypothesis.stateful import (
    Bundle,
    RuleBasedStateMachine,
    Settings,
    consumes,
    initialize,
    invariant,
    precondition,
    rule,
    run_state_machine_as_test,
)
from tests.v1.helpers.test_utils import metastore_params_only_mongo

from .test_stateful_hierarchy import clear_metastore_async, mk_new_repo

import arraylake.strategies as alst
from arraylake.asyn import sync
from arraylake.repos.v1.types import CommitID
from arraylake.repos.v1.zarr_util import ENTRY_POINT_METADATA

# JSON file contents, keep it simple
contents = st.dictionaries(
    st.text(st.characters(categories=["L", "N"], max_codepoint=0x017F), min_size=1), st.integers(min_value=-10_000, max_value=10_000)
)


@dataclass
class TagModel:
    commit_id: str
    message: str | None


class Model:
    def __init__(self, **kwargs):
        self.store: dict = {"zarr.json": json.loads(ENTRY_POINT_METADATA)}

        self.changes_made: bool = False
        self.is_at_branch_head: bool = True

        self.HEAD: None | str = None
        self.branch: None | str = None

        # commits and tags are a mapping from id to store-dict
        self.commits: dict[str, dict] = {}
        self.tags: dict[str, TagModel] = {}
        # TODO: This is only tracking the HEAD,
        # Should we  model the branch as an ordered list of commits?
        self.branches: dict[str, str] = {}

    def __setitem__(self, key, value):
        self.changes_made = True
        self.store[key] = value

    def __getitem__(self, key):
        return self.store[key]

    @property
    def has_commits(self) -> bool:
        return bool(self.commits)

    def commit(self, id_: CommitID) -> None:
        as_str = str(id_)
        self.commits[as_str] = copy.deepcopy(self.store)
        self.changes_made = False
        self.HEAD = as_str

        assert self.branch is not None
        self.branches[self.branch] = as_str

    def checkout_commit(self, ref: CommitID | str) -> None:
        assert str(ref) in self.commits
        # deepcopy so that we allow changes, but the committed store remains unchanged
        # TODO: consider Frozen stores in self.commit?
        self.store = copy.deepcopy(self.commits[str(ref)])
        self.changes_made = False
        self.HEAD = str(ref)
        self.is_at_branch_head = False
        self.branch = None

    def new_branch(self, name):
        self.branch = name
        self.is_at_branch_head = True
        assert self.HEAD is not None
        # TODO: A branch is not created till a *new* commit is made.
        # self.branches[name] = self.HEAD

    def checkout_branch(self, ref: str) -> None:
        self.checkout_commit(self.branches[ref])
        self.is_at_branch_head = True
        self.branch = ref

    def delete_branch(self, branch_name):
        del self.branches[branch_name]

    def tag(self, tag_name, commit_id, message):
        if commit_id is None:
            assert self.HEAD is not None
            commit_id = self.HEAD
        self.tags[tag_name] = TagModel(commit_id=str(commit_id), message=message)

    def checkout_tag(self, ref):
        self.checkout_commit(self.tags[str(ref)].commit_id)

    def delete_tag(self, tag_name):
        del self.tags[tag_name]

    def list_prefix(self, prefix: str):
        assert prefix == ""
        return tuple(self.store)


class MetastoreVCS(RuleBasedStateMachine):
    """
    We use bundles to track the state, since Hypothesis will then
    preferably draw the same value for different rules.
    e.g. create branch 'X', then delete branch 'X'
    """

    commits = Bundle("commits")
    tags = Bundle("tags")
    branches = Bundle("branches")

    def __init__(self, repo, metastore):
        super().__init__()

        note("----------")
        self.model = Model()

        # reset state
        self.metastore = metastore
        self.repo = asyncio.run(mk_new_repo(repo=repo, metastore=metastore))

    @initialize()
    def initialize(self):
        self.repo.checkout()
        self.model.branch = "main"
        # initialize with some data always
        self.set_doc(path="meta/root/1.json", content={"a": 1})

    @rule(path=alst.meta_paths, content=contents)
    def set_doc(self, path: str, content: dict):
        note(f"setting path {path!r} with {content!r}")
        if self.model.is_at_branch_head:
            self.repo.store.setitems({path: json.dumps(content)})
            self.model[path] = content
        else:
            # not at branch head, modifications not possible.
            with pytest.raises(OSError):
                self.repo.store.setitems({path: json.dumps(content)})

    @rule(message=st.text(max_size=MAX_TAG_OR_COMMIT_MESSAGE_SIZE), target=commits)
    @precondition(lambda self: self.model.changes_made)
    def commit(self, message):
        commit_id = self.repo.commit(message)
        note(f"Created commit: {commit_id}")
        self.model.commit(commit_id)
        return commit_id

    @rule(ref=commits, as_string=st.booleans())
    def checkout_commit(self, ref, as_string):
        note(f"Checking out commit {ref}, as_string={as_string}")
        with pytest.warns(match="You are not on a branch tip"):
            self.repo.checkout(str(ref) if as_string else ref)
        self.model.checkout_commit(ref)

    @rule(ref=st.one_of(branches, tags))
    def checkout_branch_or_tag(self, ref):
        """
        Tags and branches are combined here since checkout magically works for both.
        This test is relying on the model tracking tags and branches accurately.
        """
        if ref in self.model.tags:
            note(f"Checking out tag {ref!r}")
            with pytest.warns(match="You are not on a branch tip"):
                self.repo.checkout(ref)
            self.model.checkout_tag(ref)

        elif ref in self.model.branches:
            note(f"Checking out branch {ref!r}")
            self.repo.checkout(ref)
            self.model.checkout_branch(ref)

        else:
            note("Expecting error.")
            with pytest.raises(ValueError):
                self.repo.checkout(ref)

    def is_valid_branch_or_tag_name(self, name):
        # TODO: remove the first condition when we always create branches remotely.
        return name != self.model.branch and name not in self.model.tags and name not in self.model.branches

    # TODO: remove the precondition
    @precondition(lambda self: self.model.has_commits)
    @rule(name=st.text() | st.just("main"), target=branches)
    def new_branch(self, name):
        note(f"Creating branch {name!r}")
        if self.is_valid_branch_or_tag_name(name):
            self.repo.new_branch(name)
            self.model.new_branch(name)
        else:
            note("Expecting error.")
            with pytest.raises(ValueError):
                self.repo.new_branch(name)
        # returning this `name` to the Bundle is OK even if the branch was not created
        # This will test out checking out and deleting a branch that does not exist.
        return name

    @precondition(lambda self: self.model.has_commits)
    @rule(name=st.text(), commit_id=st.none() | commits, message=st.none() | st.text(max_size=MAX_TAG_OR_COMMIT_MESSAGE_SIZE), target=tags)
    def tag(self, name, commit_id, message):
        note(f"Creating tag {name!r} for commit {commit_id!r} with message {message!r}")
        if self.is_valid_branch_or_tag_name(name):
            self.repo.tag(name, commit_id, message=message)
            self.model.tag(name, commit_id, message)
        else:
            note("Expecting error.")
            with pytest.raises(ValueError):
                self.repo.tag(name, commit_id, message=message)
        # returning this `name` to the Bundle is OK even if the tag was not created
        # This will test out checking out and deleting a tag that does not exist.
        return name

    @rule(tag=consumes(tags))
    def delete_tag(self, tag):
        note(f"Deleting tag {tag!r}")
        if tag in self.model.tags:
            self.repo.delete_tag(tag)
            self.model.delete_tag(tag)
        else:
            note("Expecting error.")
            with pytest.raises(ValueError):
                self.repo.delete_tag(tag)

    @rule(branch=consumes(branches))
    def delete_branch(self, branch):
        note(f"Deleting branch {branch!r}")
        if branch in self.model.branches and branch != "main":
            self.repo.delete_branch(branch)
            self.model.delete_branch(branch)
        else:
            note("Expecting error.")
            with pytest.raises(ValueError):
                self.repo.delete_branch(branch)

    @invariant()
    def check_list_prefix_from_root(self):
        model_list = self.model.list_prefix("")
        al_list = self.repo.store.list_prefix("")

        assert sorted(model_list) == sorted(al_list)
        docs = self.repo.store.getitems(al_list)

        for k in model_list:
            assert self.model[k] == json.loads(docs[k])

    @invariant()
    def check_commit_data(self):
        commit_data = self.repo.commit_log.commit_data
        expected_tags = self.model.tags
        actual_tags = {tag.label: TagModel(commit_id=str(tag.commit.id), message=tag.message) for tag in self.repo.tags}
        assert actual_tags == expected_tags
        assert self.model.branches == {k: str(v) for k, v in commit_data.branches.items()}
        assert sorted(self.model.commits.keys()) == sorted(map(str, commit_data.commits.keys()))

    def teardown(self):
        note("tearing down...")
        sync(clear_metastore_async, name=self.repo.repo_name, metastore=self.metastore)


# TODO: http metastore testing is too slow for this
@pytest.mark.parametrize("metastore_class_and_config", metastore_params_only_mongo)
@pytest.mark.slow
def test_zarr_hierarchy(new_sync_repo):
    # TODO: Flip managed_sessions=True (or remove entirely) once it's mandatory.
    config = MongoMetastoreConfig("mongodb://localhost:27017/mongodb", managed_sessions=True)
    metastore = MongoSessionedMetastore(config)

    def mk_test_instance_sync():
        return MetastoreVCS(new_sync_repo, metastore)

    settings = Settings(deadline=None, max_examples=200)
    run_state_machine_as_test(mk_test_instance_sync, settings=settings)
