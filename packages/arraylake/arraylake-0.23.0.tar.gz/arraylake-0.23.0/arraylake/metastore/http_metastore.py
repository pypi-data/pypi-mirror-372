from __future__ import annotations

import json
from collections.abc import AsyncGenerator, Generator, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, TypeVar
from uuid import UUID

from pydantic import TypeAdapter

from arraylake.api_utils import ArraylakeHttpClient, handle_response
from arraylake.asyn import async_gather
from arraylake.config import config
from arraylake.metastore.abc import Metastore, MetastoreDatabase
from arraylake.repos.v1.types import (
    Branch,
    BranchName,
    BulkCreateDocBody,
    CollectionName,
    Commit,
    CommitID,
    DocResponse,
    DocSessionsResponse,
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
    UpdateBranchBody,
)
from arraylake.types import (
    ApiClientResponse,
    BucketModifyRequest,
    BucketResponse,
    GSCredentials,
    NewBucket,
    NewRepoOperationStatus,
    OptimizationConfig,
    OrgActions,
    PermissionBody,
    PermissionCheckResponse,
    Repo,
    RepoActions,
    RepoCreateBody,
    RepoKind,
    RepoMetadataT,
    RepoModifyRequest,
    RepoOperationMode,
    RepoOperationStatusResponse,
    S3Credentials,
    TokenAuthenticateBody,
)

# from pydantic_core import from_json


# type adapters
LIST_DATABASES_ADAPTER = TypeAdapter(list[Repo])
GET_COMMITS_ADAPTER = TypeAdapter(list[Commit])
GET_TAGS_ADAPTER = TypeAdapter(list[Tag])
GET_BRANCHES_ADAPTER = TypeAdapter(list[Branch])
GET_ALL_SESSIONS_FOR_PATH_ADAPTER = TypeAdapter(list[DocSessionsResponse])
GET_ALL_PATHS_FOR_SESSION_ADAPTER = TypeAdapter(list[SessionPathsResponse])
GET_DOCS_ADAPTER = TypeAdapter(list[DocResponse])
LIST_PATHS_ADAPTER = TypeAdapter(list[Path])
ADD_DOCS_ADAPTER = TypeAdapter(list[BulkCreateDocBody])
LIST_SESSIONS_ADAPTER = TypeAdapter(list[SessionInfo])
LIST_BUCKETS_ADAPTER = TypeAdapter(list[BucketResponse])
LIST_REPOS_FOR_BUCKET_ADAPTER = TypeAdapter(list[Repo])

T = TypeVar("T")


def chunks(seq: Sequence[T], size: int) -> Generator[Sequence[T], None, None]:
    return (seq[pos : (pos + size)] for pos in range(0, len(seq), size))  # noqa: E203


@dataclass
class HttpMetastoreConfig:
    """Encapsulates the configuration for the HttpMetastore"""

    api_service_url: str
    org: str
    token: str | None = field(default=None, repr=False)  # machine token. id/access/refresh tokens are managed by CustomOauth
    managed_sessions: bool = False


class HttpMetastore(ArraylakeHttpClient, Metastore):
    """ArrayLake's HTTP Metastore

    This metastore connects to ArrayLake over HTTP

    args:
        config: config for the metastore

    :::note
    Authenticated calls require an Authorization header. Run ``arraylake auth login`` to login before using this metastore.
    :::
    """

    _config: HttpMetastoreConfig

    def __init__(self, config: HttpMetastoreConfig):
        super().__init__(config.api_service_url, token=config.token, managed_sessions=config.managed_sessions)

        self._config = config
        self.api_url = config.api_service_url

    async def ping(self) -> dict[str, Any]:
        response = await self._request("GET", "user")
        handle_response(response)

        return response.json()

    async def get_database(self, name: str) -> Repo:
        response = await self._request("GET", f"/repos/{self._config.org}/{name}")
        handle_response(response)
        return Repo.model_validate_json(response.content)

    async def list_databases(self, filter_metadata: RepoMetadataT | None = None) -> list[Repo]:
        # Serialize filter_metadata to JSON string
        filter_metadata_json = json.dumps(filter_metadata) if filter_metadata else None
        response = await self._request("GET", f"/orgs/{self._config.org}/repos", params={"filter_metadata": filter_metadata_json})
        handle_response(response)
        return LIST_DATABASES_ADAPTER.validate_json(response.content)

    async def create_database(
        self,
        name: str,
        bucket_nickname: str | None = None,
        kind: RepoKind = RepoKind.Icechunk,
        prefix: str | None = None,
        import_existing: bool = False,
        description: str | None = None,
        metadata: RepoMetadataT | None = None,
    ):
        """
        Creates a repo database entry in the metastore.

        Args:
            name: Name of the repo to create
            bucket_nickname: Optional nickname of a bucket already existing in the org.
            kind: Kind of repo to create
            prefix: Optional prefix for the icechunk repo
            import_existing: Whether to import an existing icechunk repo
            description: Optional description for the repo
            metadata: Optional metadata for the repo
        """
        create_mode: Literal["create", "register", "import"] = "import" if import_existing else "register"
        body = RepoCreateBody(
            name=name,
            bucket_nickname=bucket_nickname,
            kind=kind,
            prefix=prefix,
            create_mode=create_mode,
            description=description,
            metadata=metadata,
        )
        response = await self._request("POST", f"/orgs/{self._config.org}/repos", content=body.model_dump_json())
        handle_response(response)
        repo = Repo.model_validate_json(response.content)

        if repo.kind == RepoKind.V1:
            # DEPRECATED: V1 repository metastore handling - pending removal
            # V1 repositories are legacy and this code path will be removed in a future version
            # TODO: we shouldn't need to make another request to get the repo (in open_database), the response body has everything we need
            # either stop shipping the repo body back in the POST request or bypass the GET request in open_database
            return await self.open_database(name)

        elif repo.kind == RepoKind.Icechunk:
            # TODO: should I wrap this response in an IcechunkV2Database object?
            return repo

        raise ValueError(f"Unknown repo kind: {repo.kind}")

    async def open_database(self, name: str) -> HttpMetastoreDatabase:
        # verify repo actually exists
        await self.get_database(name)

        db_config = HttpMetastoreDatabaseConfig(
            http_metastore_config=self._config,
            repo=name,
        )
        return HttpMetastoreDatabase(db_config)

    async def set_repo_status(self, name: str, mode: RepoOperationMode, message: str | None = None) -> RepoOperationStatusResponse:
        """Set repo status"""
        new_status = NewRepoOperationStatus(mode=mode, message=message)
        response = await self._request("PUT", f"/orgs/{self._config.org}/{name}/status", content=new_status.model_dump_json())
        handle_response(response)
        return RepoOperationStatusResponse.model_validate_json(response.content)

    async def modify_database(
        self,
        name: str,
        description: str | None = None,
        add_metadata: RepoMetadataT | None = None,
        remove_metadata: list[str] | None = None,
        update_metadata: RepoMetadataT | None = None,
        optimization_config: OptimizationConfig | None = None,
    ) -> None:
        repo_modify_request = RepoModifyRequest(
            description=description,
            add_metadata=add_metadata,
            remove_metadata=remove_metadata,
            update_metadata=update_metadata,
            optimization_config=optimization_config,
        )
        response = await self._request("PATCH", f"/orgs/{self._config.org}/{name}", content=repo_modify_request.model_dump_json())
        handle_response(response)

    async def delete_database(self, name: str, *, imsure: bool = False, imreallysure: bool = False) -> None:
        if not (imsure and imreallysure):
            raise ValueError("Don't do this unless you're really sure. Once the database has been deleted, it's gone forever.")

        response = await self._request("DELETE", f"/orgs/{self._config.org}/{name}")
        handle_response(response)

    async def create_bucket_config(self, bucket_config: NewBucket) -> BucketResponse:
        response = await self._request("POST", f"/orgs/{self._config.org}/buckets", content=bucket_config.model_dump_json())
        handle_response(response)
        return BucketResponse.model_validate_json(response.content)

    async def get_bucket_config(self, bucket_id: UUID) -> BucketResponse:
        response = await self._request("GET", f"/orgs/{self._config.org}/buckets/{bucket_id}")
        handle_response(response)
        return BucketResponse.model_validate_json(response.content)

    async def modify_bucket_config(self, bucket_id: UUID, bucket_config: BucketModifyRequest) -> BucketResponse:
        response = await self._request("PATCH", f"/orgs/{self._config.org}/buckets/{bucket_id}", content=bucket_config.model_dump_json())
        handle_response(response)
        return BucketResponse.model_validate_json(response.content)

    async def delete_bucket_config(self, bucket_id: UUID) -> None:
        response = await self._request("DELETE", f"/orgs/{self._config.org}/buckets/{bucket_id}")
        handle_response(response)

    async def list_bucket_configs(self) -> list[BucketResponse]:
        response = await self._request("GET", f"/orgs/{self._config.org}/buckets")
        handle_response(response)
        return LIST_BUCKETS_ADAPTER.validate_json(response.content)

    async def list_repos_for_bucket_config(self, bucket_id: UUID) -> list[Repo]:
        response = await self._request("GET", f"/orgs/{self._config.org}/buckets/{bucket_id}/repos")
        handle_response(response)
        return LIST_REPOS_FOR_BUCKET_ADAPTER.validate_json(response.content)

    async def set_default_bucket_config(self, bucket_id: UUID) -> None:
        response = await self._request("POST", f"/orgs/{self._config.org}/buckets/{bucket_id}/default")
        handle_response(response)

    async def get_s3_bucket_credentials_from_repo(self, name: str) -> S3Credentials:
        """Gets the S3 credentials for a repo."""
        response = await self._request("GET", f"/repos/{self._config.org}/{name}/bucket-credentials")
        handle_response(response)
        return S3Credentials.model_validate_json(response.content)

    async def get_gs_bucket_credentials_from_repo(self, name: str) -> GSCredentials:
        """Gets the GCS credentials for a repo."""
        response = await self._request("GET", f"/repos/{self._config.org}/{name}/bucket-credentials")
        handle_response(response)
        return GSCredentials.model_validate_json(response.content)

    async def get_s3_bucket_credentials_from_bucket(self, bucket_id: UUID) -> S3Credentials:
        """Gets the S3 credentials for a bucket. Credentials will be scoped to read-only."""
        response = await self._request("GET", f"/orgs/{self._config.org}/buckets/{bucket_id}/credentials")
        handle_response(response)
        return S3Credentials.model_validate_json(response.content)

    async def get_gs_bucket_credentials_from_bucket(self, bucket_id: UUID) -> GSCredentials:
        """Gets the GCS credentials for a bucket. Credentials will be scoped to read-only."""
        response = await self._request("GET", f"/orgs/{self._config.org}/buckets/{bucket_id}/credentials")
        handle_response(response)
        return GSCredentials.model_validate_json(response.content)

    async def get_api_client_from_token(self, token: str) -> ApiClientResponse:
        token_body = TokenAuthenticateBody(token=token)
        data = token_body.model_dump()
        response = await self._request("GET", f"/orgs/{self._config.org}/api-clients/authenticate", params=data)
        handle_response(response)
        auth_resp = ApiClientResponse.model_validate_json(response.content)
        return auth_resp

    async def get_permission_check(self, principal_id: str, resource: str, action: OrgActions | RepoActions) -> bool:
        permission_body = PermissionBody(principal_id=principal_id, resource=resource, action=action.value)
        data = permission_body.model_dump()
        response = await self._request("GET", f"/orgs/{self._config.org}/permissions/check", params=data)
        handle_response(response)
        decision = PermissionCheckResponse.model_validate_json(response.content)
        return decision.has_permission


@dataclass
class HttpMetastoreDatabaseConfig:
    """Encapsulates the configuration for an HttpMetastoreDatabase"""

    http_metastore_config: HttpMetastoreConfig
    repo: str


class HttpMetastoreDatabase(ArraylakeHttpClient, MetastoreDatabase):
    _config: HttpMetastoreDatabaseConfig

    def __init__(self, config: HttpMetastoreDatabaseConfig):
        """ArrayLake's HTTP Metastore Database

        This metastore database connects to ArrayLake over HTTP

        args:
            config: config for the metastore database

        :::note
        Authenticated calls require an Authorization header. Run ``arraylake auth login`` to login before using this metastore.
        :::
        """
        super().__init__(
            config.http_metastore_config.api_service_url,
            token=config.http_metastore_config.token,
        )

        self._config = config
        self._setup()

    def _setup(self):
        self._repo_path = f"/repos/{self._config.http_metastore_config.org}/{self._config.repo}"

    def __getstate__(self):
        return self._config

    def __setstate__(self, state):
        super().__init__(state.http_metastore_config.api_service_url, token=state.http_metastore_config.token)
        self._config = state
        self._setup()

    def __repr__(self):
        status = "OPEN" if self._get_client() is not None else "CLOSED"
        full_name = f"{self._config.http_metastore_config.org}/{self._config.repo}"
        return f"<arraylake.http_metastore.HttpMetastoreDatabase repo_name='{full_name}' status={status}>"

    async def get_commits(self, *, last_seen_commit: CommitID | None = None, limit: int = 0) -> AsyncGenerator[Commit, None]:
        # TODO: We would like to remove optional `limit=0` when min supported client version >= 0.9.1
        params: dict[str, int | CommitID | None] = {"limit": limit}
        if last_seen_commit is not None:
            params["last_seen_commit"] = last_seen_commit
        response = await self._request("GET", f"{self._repo_path}/commits", params=params)
        handle_response(response)
        commits = GET_COMMITS_ADAPTER.validate_json(response.content)
        for commit in commits:
            yield commit

    async def get_commit_by_id(self, commit_id: CommitID) -> Commit:
        response = await self._request("GET", f"{self._repo_path}/commits/{commit_id}")
        handle_response(response)
        return Commit.model_validate_json(response.content)

    async def get_tags(self, names: Sequence[TagName] | None = None) -> tuple[Tag, ...]:
        params = {"names": names} if names else {}
        response = await self._request("GET", f"{self._repo_path}/tags", params=params)
        handle_response(response)
        return tuple(GET_TAGS_ADAPTER.validate_json(response.content))

    async def get_branches(self, names: Sequence[BranchName] = []) -> tuple[Branch, ...]:
        params = {"names": names} if names else {}
        response = await self._request("GET", f"{self._repo_path}/branches", params=params)
        handle_response(response)
        return tuple(GET_BRANCHES_ADAPTER.validate_json(response.content))

    async def get_refs(self) -> tuple[tuple[Tag, ...], tuple[Branch, ...]]:
        return tuple(await async_gather(self.get_tags(), self.get_branches()))

    async def new_tag(self, tag: NewTag) -> Tag:
        response = await self._request("PUT", f"{self._repo_path}/tags", content=tag.model_dump_json())
        handle_response(response)
        return Tag.model_validate(response.json())

    async def delete_tag(self, tag_name: TagName) -> bool:
        response = await self._request("DELETE", f"{self._repo_path}/tags", params={"name": tag_name})
        handle_response(response)
        # Note: any possible errors are re-raised from handle_response,
        # so if we get here, we have succeeded adding a tag.
        # and "acknowledged" is always True
        return response.json()["acknowledged"]

    async def new_commit(self, commit_info: NewCommit) -> CommitID:
        response = await self._request("PUT", f"{self._repo_path}/commits", content=commit_info.model_dump_json())
        handle_response(response)
        return CommitID.fromhex(response.json()["_id"])

    async def old_style_rebase(self, commit_id: CommitID, upstream_branch: BranchName) -> CommitID:
        """Old method, needed for tests and compatibility with clients <= 0.7.6

        Delete this method once arraylake 0.7.6 is no longer supported
        """
        body = {"commit_id": str(commit_id) if commit_id else None, "branch_name": upstream_branch}
        response = await self._request("POST", f"{self._repo_path}/rebase", params=body)
        handle_response(response)
        return CommitID.fromhex(response.json()["commit_id"])

    async def rebase(self, base_commit: CommitID | None, session_id: SessionID, upstream_branch: BranchName) -> CommitID:
        body = {"session_id": str(session_id), "branch_name": upstream_branch}
        # passing base_commit=& as query parameter doesn't work, it gets parsed as an empty DBID
        if base_commit is not None:
            body["base_commit"] = str(base_commit)

        response = await self._request("POST", f"{self._repo_path}/rebase", params=body)
        handle_response(response)
        return CommitID.fromhex(response.json()["commit_id"])

    # TODO: Make session_id mandatory once all clients are using
    # managed_sessions by default.
    async def update_branch(
        self,
        branch: BranchName,
        *,
        session_id: SessionID | None,
        base_commit: CommitID | None,
        new_commit: CommitID,
        new_branch: bool = False,
    ) -> None:
        body = UpdateBranchBody(branch=branch, session_id=session_id, new_commit=new_commit, base_commit=base_commit, new_branch=new_branch)
        response = await self._request("PUT", f"{self._repo_path}/branches", content=body.model_dump_json())
        handle_response(response)

    async def delete_branch(self, branch_name: BranchName) -> bool:
        response = await self._request("DELETE", f"{self._repo_path}/branches", params={"name": branch_name})
        handle_response(response)
        # Note: any possible errors are re-raised from handle_response,
        # so if we get here, we have succeeded adding a tag.
        # and "acknowledged" is always True
        return response.json()["acknowledged"]

    # FIXME: Do we need to re-home this, since it collides with the /sessions
    # path prefix?
    async def get_all_sessions_for_path(self, path: Path, *, collection: CollectionName) -> AsyncGenerator[DocSessionsResponse, None]:
        # keys are sids, values are deleted or not
        response = await self._request("GET", f"{self._repo_path}/sessions/{collection}/{path}")
        handle_response(response)

        # TODO: stream/paginate here
        docs = GET_ALL_SESSIONS_FOR_PATH_ADAPTER.validate_json(response.content)
        for doc in docs:
            yield doc

    async def get_all_paths_for_session(
        self,
        session_id: SessionID,
        base_commit: CommitID | None,
        *,
        collection: CollectionName,
        limit: int = 0,
    ) -> AsyncGenerator[SessionPathsResponse, None]:
        """Get all paths that have been modified in the current session."""

        # /repos/{org}/{repo}/sessions/{collection}/{session_id}
        params = {"limit": limit, "session_id": session_id, "base_commit": base_commit}
        response = await self._request("GET", f"{self._repo_path}/modified_paths/{collection}", params=params)
        handle_response(response)

        # TODO: stream/paginate here
        docs = GET_ALL_PATHS_FOR_SESSION_ADAPTER.validate_json(response.content)
        for doc in docs:
            yield doc

    async def get_all_paths_for_commit(
        self,
        commit_id: CommitID,
        *,
        collection: CollectionName,
        limit: int = 0,
    ) -> AsyncGenerator[SessionPathsResponse, None]:
        params = {"limit": limit, "commit_id": commit_id}
        response = await self._request("GET", f"{self._repo_path}/modified_paths_commit/{collection}", params=params)
        handle_response(response)

        # TODO: stream/paginate here
        docs = GET_ALL_PATHS_FOR_SESSION_ADAPTER.validate_json(response.content)
        for doc in docs:
            yield doc

    async def list_active_sessions(self) -> Sequence[SessionInfo]:
        response = await self._request("GET", f"{self._repo_path}/sessions")
        handle_response(response)

        return LIST_SESSIONS_ADAPTER.validate_json(response.content)

    async def create_session(self, session_request: NewSession) -> SessionInfo:
        response = await self._request("POST", f"{self._repo_path}/sessions", content=session_request.model_dump_json())
        handle_response(response)

        return SessionInfo.model_validate_json(response.content)

    async def get_session(self, session_id: SessionID) -> SessionInfo:
        response = await self._request("GET", f"{self._repo_path}/sessions/{session_id}")
        handle_response(response)

        return SessionInfo.model_validate_json(response.content)

    async def update_session_expiration(self, update_request: SessionExpirationUpdate) -> SessionInfo:
        response = await self._request(
            "PUT", f"{self._repo_path}/sessions/{update_request.session_id}", content=update_request.model_dump_json()
        )
        handle_response(response)

        return SessionInfo.model_validate_json(response.content)

    async def expire_session(self, session_id: SessionID) -> SessionInfo:
        response = await self._request("DELETE", f"{self._repo_path}/sessions/{session_id}")
        handle_response(response)

        return SessionInfo.model_validate_json(response.content)

    async def _add_docs(
        self, docs: Sequence[BulkCreateDocBody], collection: CollectionName, session_id: SessionID, base_commit: CommitID | None
    ) -> None:
        """Submits a list of docs to the server to be added in bulk."""
        params = {"session_id": session_id, "base_commit": str(base_commit) if base_commit else None}
        content = ADD_DOCS_ADAPTER.dump_json(list(docs))
        response = await self._request("PUT", f"{self._repo_path}/contents/{collection}/_bulk_set", content=content, params=params)
        handle_response(response)

    async def add_docs(
        self, items: Mapping[Path, Mapping[str, Any]], *, collection: CollectionName, session_id: SessionID, base_commit: CommitID | None
    ) -> None:
        docs = [BulkCreateDocBody(session_id=session_id, content=content, path=path) for path, content in items.items()]
        await async_gather(
            *[
                self._add_docs(docs=batch, collection=collection, session_id=session_id, base_commit=base_commit)
                for batch in chunks(docs, int(config.get("async.batch_size")))
            ]
        )

    async def del_docs(
        self, paths: Sequence[Path], *, collection: CollectionName, session_id: SessionID, base_commit: CommitID | None
    ) -> None:
        params = {"session_id": session_id, "base_commit": base_commit}
        content = LIST_PATHS_ADAPTER.dump_json(list(paths))
        response = await self._request("PUT", f"{self._repo_path}/contents/{collection}/_bulk_delete", content=content, params=params)
        handle_response(response)

    async def _get_docs(
        self, paths: Sequence[Path], collection: CollectionName, session_id: SessionID, base_commit: CommitID | None
    ) -> list[DocResponse]:
        """Submits a list of paths to the server to be retrieved in bulk."""
        params = {"session_id": session_id, "base_commit": str(base_commit) if base_commit else None}
        content = LIST_PATHS_ADAPTER.dump_json(list(paths))
        response = await self._request("POST", f"{self._repo_path}/contents/{collection}/_bulk_get", content=content, params=params)
        handle_response(response)
        return GET_DOCS_ADAPTER.validate_json(response.content)

    async def get_docs(
        self, paths: Sequence[Path], *, collection: CollectionName, session_id: SessionID, base_commit: CommitID | None
    ) -> AsyncGenerator[DocResponse, None]:
        # remove dupes from request; is there a cheaper way of doing this? seems like a lot of overhead for every call
        paths = list(set(paths))

        results = await async_gather(
            *(
                self._get_docs(paths_batch, collection, session_id=session_id, base_commit=base_commit)
                for paths_batch in chunks(paths, int(config.get("async.batch_size")))
            ),
        )

        for result in results:
            for doc in result:
                yield doc

    # TODO: could make list cacheable if we can bound it on a specific commit
    async def list(
        self,
        prefix: str,
        *,
        collection: CollectionName,
        session_id: SessionID,
        base_commit: CommitID | None,
        all_subdirs: bool = False,
        filter: str | None = None,
    ) -> AsyncGenerator[Path, None]:
        # TODO: implement pagination for this API call
        response = await self._request(
            "GET",
            f"{self._repo_path}/contents/{collection}/",
            params={
                "prefix": prefix,
                "session_id": session_id,
                "base_commit": str(base_commit) if base_commit else None,
                "all_subdirs": all_subdirs,
                "filter": filter,
            },
        )
        handle_response(response)

        # TODO: stream or paginate this
        paths = LIST_PATHS_ADAPTER.validate_json(response.content)
        for path in paths:
            yield path

    async def getsize(
        self,
        prefix: str,
        *,
        session_id: SessionID,
        base_commit: CommitID | None,
    ) -> PathSizeResponse:
        response = await self._request(
            "GET",
            f"{self._repo_path}/size/",
            params={"prefix": prefix, "session_id": session_id, "base_commit": str(base_commit) if base_commit else None},
        )
        handle_response(response)
        return PathSizeResponse.model_validate_json(response.content)

    async def del_prefix(self, prefix: str, *, collection: CollectionName, session_id: SessionID, base_commit: CommitID | None) -> None:
        response = await self._request(
            "DELETE",
            f"{self._repo_path}/contents/{collection}/{prefix}",
            params={"session_id": session_id, "base_commit": str(base_commit) if base_commit else None},
        )
        handle_response(response)

    async def tree(
        self,
        prefix: str,
        *,
        session_id: SessionID,
        base_commit: CommitID | None,
        depth: int = 10,
        filter: str | None = None,
    ) -> Tree:
        response = await self._request(
            "GET",
            f"{self._repo_path}/tree",
            params={
                "prefix": prefix,
                "session_id": session_id,
                "base_commit": str(base_commit) if base_commit else None,
                "depth": depth,
                "filter": filter,
            },
        )
        handle_response(response)
        return Tree.model_validate_json(response.content)

    async def rename(
        self,
        src_path: Path,
        dst_path: Path,
        *,
        session_id: SessionID,
        base_commit: CommitID | None,
    ) -> None:
        params = {
            "src_path": src_path,
            "dst_path": dst_path,
            "session_id": session_id,
            "base_commit": str(base_commit) if base_commit else None,
        }
        response = await self._request(
            "PUT",
            f"{self._repo_path}/contents/nodes/rename",
            params=params,
        )
        handle_response(response)
