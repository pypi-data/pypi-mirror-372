from __future__ import annotations

import pickle
from collections.abc import Iterator, Sequence
from datetime import datetime
from uuid import uuid4

import pytest

from .. import requires_rich

from arraylake.exceptions import DocumentNotFoundError
from arraylake.repos.v1.commits import CommitData, CommitLog, CommitTree
from arraylake.repos.v1.types import Branch, Commit, Tag
from arraylake.types import DBID

# NOTE: for now, these tests assume a linear commit history, which is all that we are attempting to support
# in our product at the moment. As we add support for branching, we will need to update these tests to include
# branching behavior.


def gen_commits(dbids: Iterator[DBID], ncommits: int = 10) -> list[DBID]:
    # returns a list of made-up commits for testing
    commits = []
    base_commit = None
    for n, dbid in zip(range(ncommits), dbids):
        new_commit = Commit(
            id=dbid,
            session_id=uuid4().hex,
            session_start_time=datetime.now(),
            parent_commit=base_commit,
            commit_time=datetime.now(),
            author_email="fake@user.com",
            message=f"Commit {n}",
        )
        # machine tokens won't have name data
        # simulate this by giving only every second
        # commit an author name
        if n % 2:
            new_commit.author_name = "Fake User"
        commits.append(new_commit)
        base_commit = new_commit.id
    return commits


@pytest.fixture(scope="module")
def commit_list(helpers):
    return gen_commits(helpers.random_dbids, ncommits=10)


@pytest.fixture(scope="module")
def tag_list(commit_list) -> Sequence[Tag]:
    kwargs = dict(created_at=datetime.utcnow(), message=None, author_name="A", author_email="a@b.com")
    # randomly assign tags and branches to commits
    return [Tag(label="v0.1", commit=commit_list[2], **kwargs), Tag(label="v0.2", commit=commit_list[8], **kwargs)]


@pytest.fixture(scope="module")
def branch_list(commit_list) -> Sequence[Branch]:
    return [
        Branch(id="main", commit_id=commit_list[-1].id),
    ]


@pytest.fixture(scope="module")
def commit_data(commit_list, tag_list, branch_list):
    return CommitData(commit_list=commit_list, tag_list=tag_list, branch_list=branch_list)


def test_empty_commit_data():
    commit_data = CommitData(commit_list=[], tag_list=[], branch_list=[])
    commit_id, branch = commit_data.get_ref("main")
    assert branch == "main"
    assert commit_id is None


def test_get_refs_by_tag(commit_data, tag_list):
    for tag in tag_list:
        commit_id, branch_name = commit_data.get_ref(tag.label)
        assert commit_id == tag.commit.id


def test_get_refs_by_branch(commit_data, branch_list):
    for branch in branch_list:
        commit_id, branch_name = commit_data.get_ref(branch.id)
        assert commit_id == branch.commit_id
        assert branch_name == branch.id


def test_get_refs_by_commit(commit_data, commit_list):
    for commit in commit_list:
        # not strictly necessary to cast commit.id as str() but we support both interfaces so this validates that it works
        commit_id, _ = commit_data.get_ref(str(commit.id))
        assert commit_id == commit.id
        commit_id, _ = commit_data.get_ref(commit.id)
        assert commit_id == commit.id


def test_tree(commit_data, commit_list):
    parent_commit_id, _ = commit_data.get_ref("main")
    tree = commit_data.get_commit_tree(parent_commit_id)
    all_commits = list(tree.walk())
    assert len(all_commits) == len(commit_list)
    Ncommits = len(commit_list)
    for n in range(Ncommits):
        assert all_commits[n] == commit_list[-n - 1].id


@pytest.mark.parametrize("ncommits", [1, 10, 1000, 5000, 10_000])
def test_commit_tree_size(ncommits, helpers):
    """Test that we handle history of arbitrary size, and order of walk is consistent
    with commit order."""
    _commit_list = gen_commits(helpers.random_dbids, ncommits)
    commits = {commit.id: commit for commit in _commit_list}
    most_recent_commit_id = _commit_list[-1].id
    tree = CommitTree(most_recent_commit_id, commits)
    walked_commits = [c for c in tree.walk()]

    assert len(walked_commits) == ncommits

    # the input list we generated is in order of creation
    # we reverse it to get its history, then we compare that to
    # the lineage we retrieve from walk, which, given an initial
    # commit should yield historic commits
    input_commit_history = reversed(_commit_list)
    for i, r in enumerate(input_commit_history):
        commit_id = walked_commits[i]
        assert r.id == commit_id


def test_commit_tree_single_entry(helpers):
    """Test that we handle a tree with a single commit, i.e. without history"""
    _commit_list = gen_commits(helpers.random_dbids, 1)
    commits = {commit.id: commit for commit in _commit_list}
    most_recent_commit_id = _commit_list[0].id
    tree = CommitTree(most_recent_commit_id, commits)

    walked_commits = list(tree.walk())
    assert len(walked_commits) == 1
    assert walked_commits[0] == tree.commit_id


@pytest.mark.parametrize("base_commit_id", [None, "foo"])
def test_commit_tree_base_commit_not_found(base_commit_id):
    """Test we raise with a bad base commit"""
    _commit_list = []
    commits = {}
    with pytest.raises(KeyError, match="Error retrieving commit id"):
        tree = CommitTree(base_commit_id, {})
        list(tree.walk())


def test_commit_tree_child_commit_not_found(helpers):
    """Test we raise with a bad commit somewhere in the history"""
    _commit_list = gen_commits(helpers.random_dbids, 4)
    # replace a commit with a bad commit id
    _commit_list[2].parent_commit = "abc"
    commits = {commit.id: commit for commit in _commit_list}

    with pytest.raises(KeyError, match="Error retrieving commit id"):
        tree = CommitTree(_commit_list[-1].id, commits)
        list(tree.walk())


@pytest.mark.parametrize("ncommits", [1, 10, 1000, 5000, 10_000])
def test_commit_tree_pickleable(ncommits, helpers):
    _commit_list = gen_commits(helpers.random_dbids, ncommits)
    commits = {commit.id: commit for commit in _commit_list}
    most_recent_commit_id = _commit_list[-1].id
    tree = CommitTree(most_recent_commit_id, commits)

    pickled = pickle.dumps(tree)
    assert type(pickled) == bytes

    unpickled_tree = pickle.loads(pickled)
    walked_commits = [c for c in unpickled_tree.walk()]
    assert len(walked_commits) == ncommits


@requires_rich
def test_commit_log_print(commit_data, capfd):
    parent_commit_id, _ = commit_data.get_ref("main")
    log = CommitLog("repo-name", parent_commit_id, commit_data)
    log.rich_output()

    # captures stdout
    out, err = capfd.readouterr()
    parts = out.split("\n")
    assert parts[1] == "Author: Fake User <fake@user.com>"
    assert parts[7] == "Author: <fake@user.com>"
