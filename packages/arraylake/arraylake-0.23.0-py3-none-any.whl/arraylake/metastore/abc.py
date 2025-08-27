from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Iterable, Mapping, Sequence
from typing import Any

from arraylake.repos.v1.types import (
    Branch,
    BranchName,
    CollectionName,
    Commit,
    CommitID,
    DocResponse,
    NewCommit,
    NewSession,
    NewTag,
    Path,
    PathSizeResponse,
    SessionExpirationUpdate,
    SessionID,
    SessionInfo,
    SessionPathsResponse,
    Tag,
    TagName,
    Tree,
)
from arraylake.types import Repo


class InvalidRequest(Exception):
    pass


class UnsupportedFeatureRequest(InvalidRequest):
    pass


class InvalidGetDocsRequest(InvalidRequest):
    pass


class NoSourceToRename(InvalidRequest):
    pass


class MultipleNodesInChunksRequest(InvalidGetDocsRequest):
    def __init__(self, paths: Iterable[Path]):
        self.message = "Multiple nodes detected in chunk request"
        self.paths = list(paths)


class RetryException(Exception):
    pass


class NodeCreationConflict(RetryException):
    pass


class Metastore(ABC):  # pragma: no cover
    @abstractmethod
    async def ping(self) -> dict[str, Any]:
        """Verify that the metastore is accessible and responsive to the client."""
        ...

    @abstractmethod
    async def list_databases(self) -> Sequence[Repo]: ...

    @abstractmethod
    async def create_database(self, name: str) -> MetastoreDatabase:
        """Create a new metastore database.

        Parameters
        ----------
        name : str
            Name of repo

        Returns
        -------
        MetastoreDatabase
        """
        ...

    @abstractmethod
    async def open_database(self, name: str) -> MetastoreDatabase:
        """Open an existing metastore database.

        Parameters
        ----------
        name : str
            Name of repo

        Returns
        -------
        MetastoreDatabase
        """
        ...

    @abstractmethod
    async def delete_database(self, name: str, *, imsure: bool = False, imreallysure: bool = False) -> None:
        """Delete an existing metastore database.

        Parameters
        ----------
        name : str
            Name of repo
        imsure, imreallsure : bool
            Confirm permanent deletion.
        """
        ...


class MetastoreDatabase(ABC):  # pragma: no cover
    async def ping(self):
        """Ping the MetastoreDatabase to check connectivity"""
        ...

    @abstractmethod
    def get_commits(self, *, last_seen_commit: CommitID | None, limit: int) -> AsyncGenerator[Commit, None]:
        """Get the complete commit history for the repo.

        Arguments
        ---------
        last_seen_commit: Return only commits older than this one
        limit: Number of results to return

        Returns
        -------
        tuple
            Tuple of Commit objects
        """
        ...

    @abstractmethod
    async def get_commit_by_id(self, commit_id: CommitID) -> Commit:
        """Get a single commit object for the repo.

        Returns
        -------
        Commit
            Commit object
        """
        ...

    @abstractmethod
    async def get_tags(self, names: Sequence[TagName] | None = None) -> tuple[Tag, ...]:
        """Get all the tags for the repo.

        Returns
        -------
        tuple
         Tuple of Tag objects
        """
        ...

    @abstractmethod
    async def get_branches(self, names: Sequence[BranchName] = ()) -> tuple[Branch, ...]:
        """Get all the branches for the repo.

        Parameters
        ----------
        names : Sequence[BranchName]
            Only return information for these branches

        Returns
        -------
        tuple
            Tuple of Branch objects. If `names` is empty, all branches are returned,
            otherwise, only the requested branch names.
        """
        ...

    @abstractmethod
    async def get_refs(self) -> tuple[tuple[Tag, ...], tuple[Branch, ...]]:
        """Get all tags and branches and their corresponding commits.

        Returns
        -------
        tuple
            Tags and Branches
        """
        ...

    @abstractmethod
    async def new_commit(self, commit_info: NewCommit) -> CommitID:
        """Create and return a new commit for a session.

        Returns
        -------
        CommitID
        """
        ...

    @abstractmethod
    async def new_tag(self, tag: NewTag) -> Tag:
        """Create a new tag."""
        ...

    @abstractmethod
    async def old_style_rebase(self, commit_id: CommitID, upstream_branch: BranchName) -> CommitID:
        """Old signature for rebase method, needed for tests and compatibility with clients <= 0.7.6

        Delete this method once arraylake 0.7.6 is no longer supported
        """
        ...

    @abstractmethod
    async def rebase(self, base_commit: CommitID | None, session_id: SessionID, upstream_branch: BranchName) -> CommitID:
        """Determine if a session can cleanly be committed to a target branch HEAD.

        Clean update means that there are no conflicting path updates in intermediate commits between
        base_commit and the HEAD commit of the upstream_branch. If the update can be performed cleanly,
        return the target branch commit_id to the caller, else raise an exception.

        Note: This is a read-only operations, it should not create or modify commits or branch states.

        Returns
        -------
        CommitID: the id of the commit at the tip of upstream_branch

        Raises
        ------
        ValueError
            if clean update is not possible
        """
        ...

    @abstractmethod
    async def update_branch(
        self, branch: BranchName, *, session_id: SessionID, base_commit: CommitID | None, new_commit: CommitID, new_branch: bool = False
    ) -> None:
        """Update a branch reference in an atomic transaction.

        Parameters
        ----------
        branch : str
            Name of branch to update
        base_commit : CommitID, optional
            Parent commit ID, None signals no parent
        new_commit : CommitID
            New commit ID
        new_branch : bool, default=False
            If True, create a new branch
        """
        ...

    @abstractmethod
    async def delete_branch(self, branch: BranchName) -> bool:
        """Delete the named branch.

        Returns: True if the branch was deleted.
        """
        ...

    @abstractmethod
    async def delete_tag(self, branch: TagName) -> bool:
        """Delete the named tag.

        Returns: True if the tag was deleted.
        """
        ...

    # Confusingly, these generator methods cannot be declared async for typing to work properly
    # https://stackoverflow.com/a/56947440
    # https://github.com/python/mypy/issues/5385#issuecomment-407281656

    @abstractmethod
    def get_all_paths_for_session(
        self, session_id: SessionID, base_commit: CommitID | None, *, collection: CollectionName, limit: int = 0
    ) -> AsyncGenerator[SessionPathsResponse, None]:
        """Get all paths that have been modified in the current session.

        Parameters
        ----------
        session_id: SessionID
            The session in which files are being modified.
        base_commit: Optional[CommitID]
            The parent commit for the session. If and only if this is the first session in the repo, pass None.
        collection : CollectionName
        limit: int
            Optimize the operation by yielding no more than limit results. 0 means no limit.
        """
        ...

    @abstractmethod
    def get_all_paths_for_commit(
        self, commit_id: CommitID, *, collection: CollectionName, limit: int = 0
    ) -> AsyncGenerator[SessionPathsResponse, None]:
        """Get all paths that have been modified in a given commit.

        Parameters
        ----------
        commit_id: CommitID
            The commit_id in which files were modified
        collection : CollectionName
        limit: int
            Optimize the operation by yielding no more than limit results. 0 means no limit.
        """
        ...

    @abstractmethod
    async def list_active_sessions(self) -> Sequence[SessionInfo]:
        """Obtain a time-ordered list of active sessions

        Parameters
        ----------
        """
        ...

    @abstractmethod
    async def create_session(self, session_request: NewSession) -> SessionInfo:
        """Lease a new server-managed session

        Parameters
        ----------
        session_request : NewSession
            A new session request object"""
        ...

    @abstractmethod
    async def get_session(self, session_id: SessionID) -> SessionInfo:
        """Retrieve an existing server-managed session

        Parameters
        ----------
        session_id : SessionID
            The SessionID corresponding to the desired session"""
        ...

    @abstractmethod
    async def update_session_expiration(self, update_request: SessionExpirationUpdate) -> SessionInfo:
        """Update an active session with new parameters

        Parameters
        ----------
        update_request : SessionExpirationUpdate
            A session expiry update request object that includes the session ID
            and a timedelta representing the offset from the moment the request
            is received server-side"""
        ...

    @abstractmethod
    async def expire_session(self, session_id: SessionID) -> SessionInfo:
        """Expire the active session, rendering it unusable for subsequent
        writes

        Parameters
        ----------
        session_id : SessionID
            The SessionID corresponding to the desired session"""
        ...

    @abstractmethod
    async def add_docs(
        self, items: Mapping[Path, Mapping[str, Any]], *, collection: CollectionName, session_id: SessionID, base_commit: CommitID | None
    ) -> None:
        """Add documents to the specified collection.

        Parameters
        ----------
        items : dict
            Mapping where keys are paths and values are documents in the form of dictionaries.
        collection : CollectionName
        session_id: SessionID
            The session in which files are being modified.
        base_commit: Optional[CommitID]
            The parent commit for the session. If and only if this is the first session in the repo, pass None.
        """
        ...

    @abstractmethod
    async def del_docs(
        self, paths: Sequence[Path], *, collection: CollectionName, session_id: SessionID, base_commit: CommitID | None
    ) -> None:
        """Remove documents from the specified collection.

        Parameters
        ----------
        paths : sequence
            Sequence of paths to delete
        collection : CollectionName
        session_id: SessionID
            The session in which files are being modified.
        base_commit: Optional[CommitID]
            The parent commit for the session. If and only if this is the first session in the repo, pass None.
        """
        ...

    @abstractmethod
    async def del_prefix(self, prefix: Path, *, collection: CollectionName, session_id: SessionID, base_commit: CommitID | None) -> None:
        """Remove documents matching a prefix from the specified collection.

        Parameters
        ----------
        prefix : sequence
            Prefix to delete
        collection : CollectionName
        session_id: SessionID
            The session in which files are being modified.
        base_commit: Optional[CommitID]
            The parent commit for the session. If and only if this is the first session in the repo, pass None.
        """
        ...

    @abstractmethod
    def get_docs(
        self, paths: Sequence[Path], *, collection: CollectionName, session_id: SessionID, base_commit: CommitID | None
    ) -> AsyncGenerator[DocResponse, None]:
        """Fetch documents from the specified collection.

        Parameters
        ----------
        paths : sequence
            Sequence of paths to fetch
        collection : str
            Which collection to search
        session_id: SessionID
            The the active session ID
        base_commit: Optional[CommitID]
            The parent commit for the session. If and only if this is the first session in the repo, pass None.

        Yields
        ------
        DocResponse

        Raises
        ------
        MultipleNodesInChunksRequest: when chunk docs for more than one array are requested
        """
        ...

    @abstractmethod
    def list(
        self,
        prefix: str,
        *,
        collection: CollectionName,
        session_id: SessionID,
        base_commit: CommitID | None,
        all_subdirs: bool = False,
    ) -> AsyncGenerator[Path, None]:
        """List documents from the specified collection matching a prefix.

        Parameters
        ----------
        prefix : str
            Path prefix to match
        collection : str
            Which collection to search
        session_id: SessionID
            The the active session ID
        base_commit: Optional[CommitID]
            The parent commit for the session. If and only if this is the first session in the repo, pass None.
        all_subdirs : bool, default=False
            If True, recursively include all sub directories

        Yields
        ------
        ListResponse
        """
        ...

    @abstractmethod
    async def getsize(
        self,
        prefix: str,
        *,
        session_id: SessionID,
        base_commit: CommitID | None,
    ) -> PathSizeResponse:
        """Get the total size of documents in a collection matching a prefix.

        Parameters
        ----------
        prefix : str
            The prefix to list documents for
        session_id: SessionID
            The the active session ID
        base_commit: Optional[CommitID]
            The parent commit for the session. If and only if this is the first session in the repo, pass None.
        all_subdirs : bool, default=False
            If True, recursively include all sub directories

        Yields
        ------
        response
            Number and size of documents (only includes chunks, not metadata)
        """
        ...

    @abstractmethod
    async def tree(
        self,
        prefix: str,
        *,
        session_id: SessionID,
        base_commit: CommitID | None,
        depth: int = 10,
        filter: str | None = None,
    ) -> Tree:
        """Create a nested dictionary representing this metastore's hierarchy.

        Parameters
        ----------
        prefix : str
            Path prefix to match
        session_id: SessionID
            The the active session ID
        base_commit: Optional[CommitID]
            The parent commit for the session. If and only if this is the first session in the repo, pass None.
        depth: int
            The maximum depth to descend into the hierarchy
        filter: str, optional
            A JMESPath filter expression

        Returns
        -------
        Tree
        """
        ...

    @abstractmethod
    async def rename(
        self,
        src_path: Path,
        dst_path: Path,
        *,
        session_id: SessionID,
        base_commit: CommitID | None,
    ) -> None:
        """Rename src_path to dst_path.

        Parameters
        ----------
        session_id: SessionID
            The the active session ID
        base_commit: Optional[CommitID]
            The parent commit for the session. If and only if this is the first session in the repo, pass None.
        """
        ...
