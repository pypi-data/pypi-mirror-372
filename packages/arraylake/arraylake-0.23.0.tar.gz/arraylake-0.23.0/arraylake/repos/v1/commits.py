"""
DEPRECATED: This V1 commits module is pending removal.
V1 repositories are legacy and will be phased out in favor of Icechunk repositories.
This module and all its contents are scheduled for removal in a future version.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping, MutableMapping
from dataclasses import dataclass
from html import escape
from typing import Callable, TypeVar

from arraylake.exceptions import CommitNotFoundException
from arraylake.repos.v1.types import (
    Branch,
    BranchName,
    Commit,
    CommitHistory,
    CommitID,
    DBIDBytes,
    Tag,
    TagName,
)

Node = TypeVar("Node")
K = TypeVar("K")
V = TypeVar("V")


def get_ref(
    ref: CommitID | str,
    commits: Mapping[CommitID, Commit] | None = None,
    branches: Mapping[BranchName, CommitID] | None = None,
    tags: Mapping[TagName, CommitID] | None = None,
) -> tuple[CommitID | None, BranchName | None]:
    if branches is not None:
        as_branch_name = BranchName(str(ref))
        maybe_branch_commit = branches.get(as_branch_name)
        if maybe_branch_commit:
            return (maybe_branch_commit, as_branch_name)

    if ref == "main":
        # We want the main branch to magically "exist" without users creating it
        # Other branches should fail to checkout if they have not been created by the user.
        # This enables the following use cases:
        #   - A user does `repo.checkout()` on a new repo
        #   - A user creates a repo, makes commits to branch "foo",
        #     and then tries to checkout main, which doesn't exist yet
        return (None, BranchName("main"))

    if tags is not None:
        commit: CommitID | None = tags.get(TagName(str(ref)))
        if commit is not None:
            return (commit, None)

    if commits is not None:
        if isinstance(ref, str):
            try:
                ref = CommitID.fromhex(ref)
            except ValueError:
                # Not a commit we will try branches and tags
                pass

        if isinstance(ref, DBIDBytes):
            if ref in commits:
                return (ref, None)
            else:
                raise ValueError(f"Commit {ref!r} was not found in commit history.")

    # no commits or tags were found for `ref`,
    # and we weren't asked for 'main' branch of an empty repo
    raise ValueError(f"Ref {ref!r} was not found in branches, tags, or commits.")


def walk_commits(start_id: CommitID, get_node: Callable[[CommitID], Node], get_parent: Callable[[Node], CommitID | None]) -> Iterator[Node]:
    """Traverses a tree-like commit data structure, starting in the provided commit.

    Parameters
    ----------
    start_id : CommitID
        The node at which to start the traversal
    get_node: Callable[[CommitID], Node]
        Inspect the tree data structure and get the node that corresponds to the given CommitID
    get_parent: Callable[[Node], CommitID | None]
        Retrieve the parent node (or none if initial commit)

    Returns
    -------
    An iterator to the chain of nodes, traversed through the "parent link"
    """
    node: Node | None
    try:
        node = get_node(start_id)
    except KeyError:
        raise CommitNotFoundException(f"Error retrieving commit id {start_id}, root does not exist in provided commits")
    while node:
        yield node
        parent_id = get_parent(node)
        if parent_id is not None:
            try:
                node = get_node(parent_id)
            except KeyError:
                raise CommitNotFoundException(f"Error retrieving commit id {parent_id}, parent does not exist in provided commits")
        else:
            node = None


@dataclass()
class CommitTree:
    """Lightweight structure to retrieve history for a given commit.

    Note: this structure is a little unnecessary and isn't a tree as the name would suggest.
    It is simply a holder for a a collection of commits and presents a single sequential history
    for the provided commit_id via `walk()`. It could be simplified to a utility function, but is maintained
    due to it's pervasive usage throughout the codebase.
    """

    commit_id: CommitID
    all_commits: Mapping[CommitID, Commit]

    def _get_node(self, commit_id):
        return self.all_commits[commit_id]

    def _get_parent(self, commit):
        return commit.parent_commit

    def walk(self) -> CommitHistory:
        "Construct the lineage for the provided commit_id over provided commits"
        for commit in walk_commits(start_id=self.commit_id, get_node=self._get_node, get_parent=self._get_parent):
            yield commit.id


class CommitData:
    """Data structure containing all the commit information for a session."""

    commits: Mapping[CommitID, Commit]
    """Mapping of commit ID to full Commit object"""
    tags: Mapping[TagName, CommitID]
    """Mapping of tag name to Commit ID"""
    branches: Mapping[BranchName, CommitID]
    """Mapping of branch name to Commit ID"""

    def __init__(self, commit_list: Iterable[Commit], tag_list: Iterable[Tag], branch_list=Iterable[Branch]):
        self.commits = {commit.id: commit for commit in commit_list}
        self.tags = {tag.label: tag.commit.id for tag in tag_list}
        self.branches = {branch.id: branch.commit_id for branch in branch_list}

    def get_commit_tree(self, commit_id: CommitID) -> CommitTree:
        """Get the commit tree for a given commit ID.

        Args:
            commit_id: the commit ID to start from

        Returns:
            CommitTree
        """
        return CommitTree(commit_id, self.commits)

    def get_ref(self, ref: str | CommitID) -> tuple[CommitID | None, BranchName | None]:
        """Get the commit ID for a given commit, tag or branch name.

        Args:
            ref: commit_id, tag or branch name

        Returns:
            CommitID, BranchName
        """
        return get_ref(ref, self.commits, self.branches, self.tags)


def invert_mapping(mapping: Mapping[K, V]):
    merged: MutableMapping[V, list[K]] = defaultdict(list)
    for k, v in mapping.items():
        merged[v].append(k)
    return merged


@dataclass(frozen=True)
class CommitLog:
    """Used to display commit history to the user."""

    repo_name: str
    """Name of the repo"""
    commit_id: CommitID | None
    """Current commit ID"""
    commit_data: CommitData
    """Repo commit data"""

    def __iter__(self):
        """Iterate through commit history, newest to oldest.

        Yields:
            Commit
        """
        if self.commit_id is None:
            return
        tree = CommitTree(self.commit_id, self.commit_data.commits)
        for commit_id in tree.walk():
            yield self.commit_data.commits[commit_id]

    def __len__(self):
        """Number of commits in the log."""
        return len([c for c in self])

    def rich_output(self, console=None):
        from rich.console import Console
        from rich.padding import Padding

        if console is None:
            console = Console()

        for commit in self:
            console.print(f"[yellow]commit [bold]{commit.id}[/bold] [/yellow]")
            console.print(f"Author: {commit.author_entry()}")
            console.print(f"Date:   {commit.commit_time}")
            console.print(Padding(commit.message, (1, 4)))

    def _repr_html_(self):
        html = """<ul style="list-style-type: none; margin: 0; padding: 0;">\n"""

        def row(col1: str, col2: str) -> str:
            return f"""   <tr><td style="text-align:right">{col1}</td><td style="text-align:left">{col2}</td></tr>"""

        commit_tags = invert_mapping(self.commit_data.tags)
        for commit in self:
            html += """ <li>\n  <table style="border: 1px dashed grey">\n"""
            html += row("Commit ID", "<b>" + escape(str(commit.id)) + "</b>")
            html += row("Author", escape(commit.author_entry()))
            html += row("Date", escape(commit.commit_time.isoformat()))

            tags = commit_tags[commit.id]
            if tags:
                html += row("Tags", ", ".join(tags))
            html += "\n  </table>\n"
            message = escape(commit.message).replace("\n", "<br />")
            html += f"""  <p style="padding: 1em 2em;">{message}</p>\n"""
            html += " </li>\n"
        html += "</ul>\n"

        return html
