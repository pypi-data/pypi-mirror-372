"""
The Client module contains the main classes used to interact with the Arraylake service.
For asyncio interaction, use the #AsyncClient. For regular, non-async interaction, use the #Client.

**Example usage:**

```python
from arraylake import Client
client = Client()
repo = client.get_repo("my-org/my-repo")
```
"""

# mypy: disable-error-code="name-defined"
from __future__ import annotations

import re
import warnings
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import timezone
from functools import partial
from typing import Any, Callable, Literal, Optional, Union
from urllib.parse import urlparse
from uuid import UUID

from packaging.version import Version

import arraylake.repos.v1.repo as repo_v1
from arraylake.asyn import asyncio_run, sync
from arraylake.compute.services import AsyncComputeClient, ComputeClient
from arraylake.config import config as arraylake_config
from arraylake.credentials import (
    _get_hmac_credentials,
    _is_r2_bucket,
    _use_delegated_credentials,
    _use_hmac_credentials,
)
from arraylake.exceptions import BucketNotFoundError
from arraylake.log_util import get_logger
from arraylake.metastore import HttpMetastore, HttpMetastoreConfig
from arraylake.repos.icechunk.storage import (
    _get_credential_type,
    _get_icechunk_storage_obj,
)
from arraylake.repos.icechunk.utils import _raise_if_no_icechunk
from arraylake.repos.icechunk.virtual import get_icechunk_container_credentials
from arraylake.repos.v1.chunkstore import (
    Chunkstore,
    mk_chunkstore_from_bucket_config,
    mk_chunkstore_from_uri,
)
from arraylake.token import get_auth_handler
from arraylake.types import (
    DBID,
    URI,
    ApiClientResponse,
    Author,
    BucketNickname,
    BucketPrefix,
    BucketResponse,
    GSCredentials,
    HmacAuth,
    NewBucket,
    OptimizationConfig,
    OrgActions,
    OrgAndRepoName,
    OrgName,
)
from arraylake.types import Repo as RepoModel
from arraylake.types import (
    RepoActions,
    RepoConfig,
    RepoKind,
    RepoMetadataT,
    RepoName,
    RepoOperationMode,
    RepoOperationStatusResponse,
    S3Credentials,
    TempCredentials,
)

logger = get_logger(__name__)

_VALID_NAME = r"(\w[\w\.\-_]+)"

try:
    import icechunk  # noqa
    import zarr

    if Version(zarr.__version__) > Version("3.0.0.a0"):
        _DEFAULT_NEW_REPO_KIND = RepoKind.Icechunk
    else:
        # DEPRECATED: V1 default fallback - pending removal
        _DEFAULT_NEW_REPO_KIND = RepoKind.V1
except ImportError:
    # DEPRECATED: V1 default fallback - pending removal
    _DEFAULT_NEW_REPO_KIND = RepoKind.V1


def _parse_org_and_repo(org_and_repo: OrgAndRepoName) -> tuple[OrgName, RepoName]:
    expr = f"{_VALID_NAME}/{_VALID_NAME}"
    res = re.fullmatch(expr, org_and_repo)
    if not res:
        raise ValueError(f"Not a valid repo identifier: `{org_and_repo}`. " "Should have the form `[ORG]/[REPO]`.")
    org, repo_name = res.groups()
    return org, repo_name


def _validate_org(org_name: OrgName):
    if not re.fullmatch(_VALID_NAME, org_name):
        raise ValueError(f"Invalid org name: `{org_name}`.")


def _default_service_uri() -> str:
    return arraylake_config.get("service.uri", "https://api.earthmover.io")


def _default_token() -> Optional[str]:
    return arraylake_config.get("token", None)


@dataclass
class AsyncClient:
    """Asyncio Client for interacting with ArrayLake

    Args:
        service_uri:
            [Optional] The service URI to target.
        token:
            [Optional] API token for service account authentication.
    """

    service_uri: str = field(default_factory=_default_service_uri)
    token: Optional[str] = field(default_factory=_default_token, repr=False)

    def __post_init__(self):
        if self.token is not None and (not self.token.startswith("ema_") and not self.token.startswith("ey")):
            # Ignore telling the user they can use JWT tokens, shhhh
            raise ValueError("Invalid token provided. Tokens must start with ema_ or be a JWT token.")
        if not self.service_uri.startswith("http"):
            raise ValueError("service uri must start with http")

    def _metastore_for_org(self, org: OrgName) -> HttpMetastore:
        _validate_org(org)
        return HttpMetastore(HttpMetastoreConfig(self.service_uri, org, self.token))

    async def list_repos(self, org: OrgName, filter_metadata: RepoMetadataT | None = None) -> Sequence[RepoModel]:
        """List all repositories for the specified org

        Args:
            org: Name of the org
            filter_metadata: Optional metadata to filter the repos by.
                If provided, only repos with the specified metadata will be returned.
                Filtering is inclusive and will return repos that match all of the provided metadata.
        """

        mstore = self._metastore_for_org(org)
        repo_models = await mstore.list_databases(filter_metadata)
        return repo_models

    async def _get_s3_delegated_credentials_from_repo(self, org: OrgName, repo_name: RepoName) -> S3Credentials:
        """Get delegated credentials for a repo's S3 bucket.

        Args:
            org: Name of the organization.
            repo_name: Name of the repository.

        Returns:
            S3Credentials: Temporary credentials for the S3 bucket.
        """
        mstore = self._metastore_for_org(org)
        s3_creds = await mstore.get_s3_bucket_credentials_from_repo(repo_name)
        return s3_creds

    async def _get_gcs_delegated_credentials_from_repo(self, org: OrgName, repo_name: RepoName) -> GSCredentials:
        """Get delegated credentials for a repo's GCS bucket.

        Args:
            org: Name of the organization.
            repo_name: Name of the repository.

        Returns:
            GSCredentials: Temporary credentials for the GCS bucket.
        """
        mstore = self._metastore_for_org(org)
        gcs_creds = await mstore.get_gs_bucket_credentials_from_repo(repo_name)
        return gcs_creds

    async def _get_s3_delegated_credentials_from_bucket(self, org: OrgName, nickname: BucketNickname) -> S3Credentials:
        """Get delegated credentials for a S3 bucket. These credentials are scoped
        to read-only.

        Args:
            org: Name of the organization that the bucket belongs to.
            nickname: Nickname of the bucket.

        Returns:
            S3Credentials: Temporary credentials for the S3 bucket.
        """
        mstore = self._metastore_for_org(org)
        bucket_id = await self._bucket_id_for_nickname(mstore, nickname)
        s3_creds = await mstore.get_s3_bucket_credentials_from_bucket(bucket_id)
        return s3_creds

    async def _get_gcs_delegated_credentials_from_bucket(self, org: RepoName, nickname: BucketNickname) -> GSCredentials:
        """Get delegated credentials for a GCS bucket. These credentials are scoped
        to read-only.

        Args:
            org: Name of the organization that the bucket belongs to.
            nickname: Nickname of the bucket.

        Returns:
            GSCredentials: Temporary credentials for the GCS bucket.
        """
        mstore = self._metastore_for_org(org)
        bucket_id = await self._bucket_id_for_nickname(mstore, nickname)
        gcs_creds = await mstore.get_gs_bucket_credentials_from_bucket(bucket_id)
        return gcs_creds

    def _get_icechunk_s3_credentials_refresh_function_for_repo(self, org: OrgName, repo_name: RepoName):  # -> icechunk.S3StaticCredentials
        """Get a function that returns S3 credentials for the given org and repo
        for credential refreshes in Icechunk.

        The returned Callable may not have any args, must return a new
        S3StaticCredentials object, and must be synchronous.

        Args:
            org: Name of the org
            repo_name: Name of the repo

        Returns:
            Callable: Function that returns a S3StaticCredentials object.
        """
        _raise_if_no_icechunk()
        import icechunk  # noqa: F811

        s3_credentials = asyncio_run(self._get_s3_delegated_credentials_from_repo(org, repo_name))
        return icechunk.S3StaticCredentials(
            access_key_id=s3_credentials.aws_access_key_id,
            secret_access_key=s3_credentials.aws_secret_access_key,
            session_token=s3_credentials.aws_session_token,
            expires_after=s3_credentials.expiration,
        )

    def _get_icechunk_gcs_credentials_refresh_function_for_repo(self, org: OrgName, repo_name: RepoName):  # -> icechunk.GcsBearerCredential
        """Get a function that returns GCS credentials for the given org and repo
        for credential refreshes in Icechunk.

        The returned Callable may not have any args, must return a new
        GcsBearerCredential object, and must be synchronous.

        Args:
            org: Name of the org
            repo_name: Name of the repo

        Returns:
            Callable: Function that returns a GcsBearerCredential object.
        """
        _raise_if_no_icechunk()
        import icechunk  # noqa: F811

        gcs_credentials = asyncio_run(self._get_gcs_delegated_credentials_from_repo(org, repo_name))
        return icechunk.GcsBearerCredential(
            bearer=gcs_credentials.access_token,
            expires_after=gcs_credentials.expiration.replace(tzinfo=timezone.utc) if gcs_credentials.expiration else None,
        )

    def _get_icechunk_s3_credentials_refresh_function_for_bucket(
        self, org: OrgName, nickname: BucketNickname
    ):  # -> icechunk.S3StaticCredentials
        """Get a function that returns S3 credentials for the given org and bucket
        for credential refreshes in Icechunk.

        The returned Callable may not have any args, must return a new
        S3StaticCredentials object, and must be synchronous.

        Args:
            org: Name of the org
            nickname: Nickname of the bucket

        Returns:
            Callable: Function that returns a S3StaticCredentials object.
        """
        _raise_if_no_icechunk()
        import icechunk  # noqa: F811

        s3_credentials = asyncio_run(self._get_s3_delegated_credentials_from_bucket(org, nickname))
        return icechunk.S3StaticCredentials(
            access_key_id=s3_credentials.aws_access_key_id,
            secret_access_key=s3_credentials.aws_secret_access_key,
            session_token=s3_credentials.aws_session_token,
            expires_after=s3_credentials.expiration,
        )

    def _get_icechunk_gcs_credentials_refresh_function_for_bucket(
        self, org: OrgName, nickname: BucketNickname
    ):  # -> icechunk.GcsBearerCredential
        """Get a function that returns GCS credentials for the given org and bucket
        for credential refreshes in Icechunk.

        The returned Callable may not have any args, must return a new
        GcsBearerCredential object, and must be synchronous.

        Args:
            org: Name of the org
            nickname: Nickname of the bucket

        Returns:
            Callable: Function that returns a GcsBearerCredential object.
        """
        _raise_if_no_icechunk()
        import icechunk  # noqa: F811

        gcs_credentials = asyncio_run(self._get_gcs_delegated_credentials_from_bucket(org, nickname))
        return icechunk.GcsBearerCredential(
            bearer=gcs_credentials.access_token,
            expires_after=gcs_credentials.expiration.replace(tzinfo=timezone.utc) if gcs_credentials.expiration else None,
        )

    async def _maybe_get_credentials_for_icechunk(
        self,
        bucket: BucketResponse,
        org: OrgName,
        repo_name: RepoName | None,
    ) -> TempCredentials | None:
        """Checks if the bucket is configured for delegated or HMAC credentials and gets the
        credentials if it is configured.

        Returns None if delegated or HMAC credentials are not configured for the bucket.
        """
        if _use_delegated_credentials(bucket):
            if bucket.platform == "s3" or _is_r2_bucket(bucket):
                if repo_name:
                    return await self._get_s3_delegated_credentials_from_repo(org, repo_name)
                else:
                    return await self._get_s3_delegated_credentials_from_bucket(org, bucket.nickname)
            elif bucket.platform == "gs":
                if repo_name:
                    return await self._get_gcs_delegated_credentials_from_repo(org, repo_name)
                else:
                    return await self._get_gcs_delegated_credentials_from_bucket(org, bucket.nickname)
            else:
                raise ValueError(f"Unsupported platform for delegated credentials: {bucket.platform}")
        elif _use_hmac_credentials(bucket):
            return await _get_hmac_credentials(bucket)
        return None

    def _maybe_get_credential_refresh_func_for_icechunk(
        self, bucket: BucketResponse, org: OrgName, repo_name: RepoName | None
    ) -> Callable | None:  # Removed S3StaticCredentials output type so icechunk import is not required
        """Checks if the bucket is configured for delegated credentials and gets the
        refresh function if it is configured.

        Returns None if delegated credentials are not configured for the bucket.
        """
        # Only S3 buckets can get a refresh function
        if _use_delegated_credentials(bucket):
            if bucket.platform == "s3" or _is_r2_bucket(bucket):
                if repo_name:
                    return partial(self._get_icechunk_s3_credentials_refresh_function_for_repo, org, repo_name)
                else:
                    return partial(self._get_icechunk_s3_credentials_refresh_function_for_bucket, org, bucket.nickname)
            elif bucket.platform == "gs":
                if repo_name:
                    return partial(self._get_icechunk_gcs_credentials_refresh_function_for_repo, org, repo_name)
                else:
                    return partial(self._get_icechunk_gcs_credentials_refresh_function_for_bucket, org, bucket.nickname)
            else:
                raise ValueError(f"Unsupported platform for delegated credentials: {bucket.platform}")
        return None

    # TODO: move init_chunkstore out of client to V1 Repo
    async def _init_chunkstore(self, repo_id: DBID, bucket: Union[BucketResponse, None], org: str, repo_name: str) -> Chunkstore:
        """DEPRECATED: This entire method is V1-specific and pending removal.
        V1 repositories are legacy and will be phased out in favor of Icechunk repositories.
        This method and all its contents are scheduled for removal in a future version.
        """
        inline_threshold_bytes = int(arraylake_config.get("chunkstore.inline_threshold_bytes", 0))
        fetch_credentials_func = None
        cache_key: tuple[Any, ...] = ()
        if bucket is None:
            chunkstore_uri = arraylake_config.get("chunkstore.uri")
            if chunkstore_uri is None:
                raise ValueError("Chunkstore uri is None. Please set it using: `arraylake config set chunkstore.uri URI`.")
            if chunkstore_uri.startswith("s3"):
                client_kws = arraylake_config.get("s3", {})
            elif chunkstore_uri.startswith("gs"):
                client_kws = arraylake_config.get("gs", {})
            else:
                raise ValueError(f"Unsupported chunkstore uri: {chunkstore_uri}")
            return mk_chunkstore_from_uri(chunkstore_uri, inline_threshold_bytes, **client_kws)
        else:
            # TODO: for now, we just punt and use the s3 namespace for server-managed
            # bucket configs. This should be generalized to support GCS.
            client_kws = arraylake_config.get("s3", {})
            # Check if the bucket is using delegated credentials
            if _use_delegated_credentials(bucket):
                # We don't support GCS delegated credentials for V1 repos, even if the bucket is configured for it
                if bucket.platform == "gs":
                    raise ValueError("GCS buckets using delegated credentials are not supported for V1 repos.")
                # If it is, pass the `_get_s3_delegated_credentials` function to the chunkstore
                fetch_credentials_func = partial(self._get_s3_delegated_credentials_from_repo, org, repo_name)  # noqa
                # Add the org, repo_name, and function name to the cache key
                cache_key = (org, repo_name, fetch_credentials_func.func.__name__)
            elif _use_hmac_credentials(bucket):
                # We must check these again or else mypy freaks out
                assert isinstance(bucket, BucketResponse)
                assert isinstance(bucket.auth_config, HmacAuth)
                # Add the HMAC creds to the client kwargs
                # we must do a copy of the kwargs so we don't modify the config directly
                client_kws = client_kws.copy()
                # note that all supported platforms use the key words aws_access_key_id and aws_secret_access_key
                client_kws.update(
                    {"aws_access_key_id": bucket.auth_config.access_key_id, "aws_secret_access_key": bucket.auth_config.secret_access_key}
                )
            return mk_chunkstore_from_bucket_config(
                bucket,
                repo_id,
                inline_threshold_bytes,
                fetch_credentials_func,  # type: ignore
                cache_key,
                **client_kws,
            )

    async def get_repo_object(self, name: OrgAndRepoName) -> RepoModel:
        """Get the repo configuration object.

        See `get_repo` for an instantiated repo.

        Args:
            name: Full name of the repo (of the form [ORG]/[REPO])
        """
        org, repo_name = _parse_org_and_repo(name)
        mstore = self._metastore_for_org(org)

        repo_model = await mstore.get_database(repo_name)
        return repo_model

    async def get_repo(
        self,
        name: OrgAndRepoName,
        *,
        checkout: Optional[bool] = None,
        read_only: bool | None = None,
        config: RepoConfig = None,  # icechunk.RepositoryConfig | dict[str, Any] | None
    ) -> repo_v1.AsyncRepo | IcechunkRepository:  # noqa
        """Get a repo by name

        Args:
            name: Full name of the repo (of the form [ORG]/[REPO])
            checkout: Automatically checkout the repo after instantiation.
                Defaults to True for V1 repos and False for icechunk repos.
            read_only: Open the repo in read-only mode.
            config: Optional config for the repo.
                For Icechunk repos, this is the RepositoryConfig.
                Config settings passed here will take precedence over
                the stored repo config when opening the repo.

        Returns:
            A V1 AsyncRepo object or an IcechunkRepository object.
        """
        repo_model = await self.get_repo_object(name)
        org, repo_name = _parse_org_and_repo(name)

        mstore = HttpMetastore(HttpMetastoreConfig(self.service_uri, org, self.token))

        user = await mstore.get_user()
        author: Author = user.as_author()

        if repo_model.kind == RepoKind.V1:
            # Check if V1 repo opening is allowed
            allow_v1_get_repo = arraylake_config.get("repo.allow_v1_get_repo", False)
            if not allow_v1_get_repo:
                raise ValueError(
                    "V1 repositories can no longer be opened in the Arraylake client. "
                    "To enable V1 repo opening, set 'repo.allow_v1_get_repo: true' in your config file or "
                    "contact support@earthmover.io for assistance migrating to Icechunk."
                )

            # DEPRECATED: V1 repository handling - pending removal
            # V1 repositories are legacy and this code path will be removed in a future version
            warnings.warn(
                "V1 repos are deprecated in favor of Icechunk repos. "
                "Please contact support@earthmover.io for assistance migrating to Icechunk.",
                FutureWarning,
            )

            # Set checkout to True if it is None
            checkout = True if checkout is None else checkout

            db = await mstore.open_database(repo_name)
            cstore = await self._init_chunkstore(repo_model.id, repo_model.bucket, org, repo_name)

            arepo = repo_v1.AsyncRepo(db, cstore, name, author)
            if checkout:
                if read_only is not None:
                    await arepo.checkout(for_writing=(not read_only))
                else:
                    await arepo.checkout()
            return arepo

        elif repo_model.kind == RepoKind.Icechunk:
            _raise_if_no_icechunk()
            from icechunk import Repository as IcechunkRepository
            from icechunk import RepositoryConfig

            icechunk_storage = await self._get_icechunk_storage_from_repo_model(repo_model, user_id=user.id)
            if not isinstance(config, RepositoryConfig) and config is not None:
                raise ValueError(f"config must be an icechunk.RepositoryConfig object or None: {config}.")

            ic_repo: IcechunkRepository = IcechunkRepository.open(
                icechunk_storage,
                config=config,  # The config passed here takes precedence over the stored config
            )
            ic_repo.set_default_commit_metadata({"author_name": author.name, "author_email": author.email})
            return ic_repo

        else:
            raise ValueError(f"Invalid repo kind: {repo_model.kind}")

    async def get_or_create_repo(
        self,
        name: OrgAndRepoName,
        *,
        checkout: Optional[bool] = None,
        bucket_config_nickname: Optional[BucketNickname] = None,
        kind: Optional[RepoKind] = None,
        prefix: Optional[str] = None,
        import_existing: bool = False,
        description: Optional[str] = None,
        metadata: Optional[RepoMetadataT] = None,
        config: RepoConfig = None,  # icechunk.RepositoryConfig | dict[str, Any] | None
    ) -> repo_v1.AsyncRepo | IcechunkRepository:  # noqa
        """Get a repo by name. Create the repo if it doesn't already exist.

        Args:
            name: Full name of the repo (of the form [ORG]/[REPO])
            checkout: Whether to checkout the repo after instantiation.
                If the repo does not exist, checkout is ignored.
                Ignored if specified for a Icechunk repo.
            bucket_config_nickname: The created repo will use this bucket for its chunks.
                If the repo exists, bucket_config_nickname is ignored.
            kind: The kind of repo to get or create e.g. Arraylake V1 or Icechunk V2
            prefix: Optional prefix for Icechunk store. Only used for Icechunk V2 repos.
                If not provided, a random ID + the repo name will be used.
            import_existing: If True, the Icechunk repo will be imported if it already exists.
            description: Optional description for the repo.
            metadata: Optional dictionary of metadata to tag the repo with.
                Dictionary values can be a scalar (string, int, float, bool, or None) or a list of scalars.
            config: Optional config for the repo.
                For Icechunk repos, this is the RepositoryConfig.
                Config settings passed here will take precedence over
                the stored repo config when opening the repo.

        Returns:
            A V1 AsyncRepo object or IcechunkRepository
        """
        org, repo_name = _parse_org_and_repo(name)
        repos = [r for r in await self.list_repos(org) if r.name == repo_name]
        if repos:
            (repo,) = repos
            if bucket_config_nickname:
                if repo.bucket and bucket_config_nickname != repo.bucket.nickname:
                    raise ValueError(
                        f"This repo exists, but the provided {bucket_config_nickname=} "
                        f"does not match the configured bucket_config_nickname {repo.bucket.nickname!r}."
                    )
                elif not repo.bucket:
                    raise ValueError(
                        "This repo exists, but does not have a bucket config attached. Please remove the bucket_config_nickname argument."
                    )
                else:
                    return await self.get_repo(name, checkout=checkout)
            return await self.get_repo(
                name,
                checkout=checkout,
                config=config,
            )
        else:
            return await self.create_repo(
                name,
                bucket_config_nickname=bucket_config_nickname,
                kind=kind,
                prefix=prefix,
                import_existing=import_existing,
                description=description,
                metadata=metadata,
                config=config,
            )

    async def create_repo(
        self,
        name: OrgAndRepoName,
        *,
        bucket_config_nickname: Optional[BucketNickname] = None,
        kind: Optional[RepoKind] = None,
        prefix: Optional[str] = None,
        import_existing: bool = False,
        description: Optional[str] = None,
        metadata: Optional[RepoMetadataT] = None,
        config: RepoConfig = None,  # icechunk.RepositoryConfig | dict[str, Any] | None
    ) -> repo_v1.AsyncRepo | IcechunkRepository:  # noqa
        """Create a new repo

        Args:
            name: Full name of the repo to create (of the form [ORG]/[REPO])
            bucket_config_nickname: An optional bucket to use for the chunkstore
            kind: The kind of repo to get or create e.g. Arraylake V1 or Icechunk V2
            prefix: Optional prefix for Icechunk store. Only used for Icechunk V2 repos.
                If not provided, a random ID + the repo name will be used.
            import_existing: If True, the Icechunk repo will be imported if it already exists.
            description: Optional description for the repo.
            metadata: Optional dictionary of metadata to tag the repo with.
                Dictionary values can be a scalar (string, int, float, bool, or None) or a list of scalars.
            config: Optional config for the repo.
                For Icechunk repos, this is the RepositoryConfig, and
                the config will be saved alongside the repo upon creation.
        """
        # Check that we can import the correct repo type
        if kind is None:
            kind = _DEFAULT_NEW_REPO_KIND

        if kind == RepoKind.V1:
            # DEPRECATED: V1 repository creation - pending removal
            # V1 repositories are legacy and this code path will be removed in a future version

            allow_v1_repo_creation = arraylake_config.get("repo.allow_v1_repo_creation", False)

            if not allow_v1_repo_creation:
                raise ValueError(
                    "Creating V1 repos is deprecated in favor of Icechunk repos. "
                    "Please contact support@earthmover.io for assistance migrating to Icechunk.",
                )

            import arraylake.repos.v1.repo as repo_v1

        elif kind == RepoKind.Icechunk:
            _raise_if_no_icechunk()
        else:
            raise ValueError(f"Invalid repo kind: {kind}")

        org, repo_name = _parse_org_and_repo(name)
        mstore = self._metastore_for_org(org)

        user = await mstore.get_user()
        author: Author = user.as_author()

        if kind == RepoKind.V1 and prefix:
            # DEPRECATED: V1 repository validation - pending removal
            raise ValueError("Prefix is not supported for V1 repos.")

        repo_model = await mstore.create_database(
            repo_name,
            bucket_config_nickname,
            kind=kind,
            prefix=prefix,
            import_existing=import_existing,
            description=description,
            metadata=metadata,
        )

        if kind == RepoKind.V1:
            # DEPRECATED: V1 repository instantiation - pending removal
            # V1 repositories are legacy and this code path will be removed in a future version
            repos = [repo for repo in await mstore.list_databases() if repo.name == repo_name]
            if len(repos) != 1:
                raise ValueError(f"Error creating repository `{name}`.")
            repo = repos[0]

            cstore = await self._init_chunkstore(repo.id, repo.bucket, org, repo_name)

            arepo = repo_v1.AsyncRepo(repo_model, cstore, name, author)
            await arepo.checkout()
            return arepo

        elif kind == RepoKind.Icechunk:
            from icechunk import IcechunkError
            from icechunk import Repository as IcechunkRepository
            from icechunk import RepositoryConfig

            icechunk_storage = await self._get_icechunk_storage_from_repo_model(repo_model, user_id=user.id)

            try:
                if not isinstance(config, RepositoryConfig) and config is not None:
                    raise ValueError(f"config must be an icechunk.RepositoryConfig object or None: {config}.")

                ic_repo: IcechunkRepository = (
                    IcechunkRepository.open(icechunk_storage, config=config)
                    if import_existing
                    else IcechunkRepository.create(icechunk_storage, config=config)
                )
                ic_repo.set_default_commit_metadata({"author_name": author.name, "author_email": author.email})
                return ic_repo
            except (IcechunkError, ValueError) as e:
                # If the repo fails to create, we need to delete the repo model
                await mstore.delete_database(repo_name, imsure=True, imreallysure=True)
                raise e

    async def _get_icechunk_storage_from_repo_model(
        self,
        repo_model: RepoModel,
        user_id: UUID,
        credentials_override=None,  # icechunk.AnyCredential | None
    ):  # -> icechunk.Storage:
        """Get the icechunk storage object from a repo model.

        Args:
            repo_model: The repo model object.
            credentials_override: Optional credentials to use for the storage object.

        Returns:
            icechunk.Storage object for the repo.
        """
        from arraylake import __version__ as arraylake_version

        _raise_if_no_icechunk()

        if repo_model.bucket is None:
            raise ValueError("The bucket on the catalog object cannot be None for Icechunk V2 repos!")

        credential_refresh_func = self._maybe_get_credential_refresh_func_for_icechunk(
            bucket=repo_model.bucket, org=repo_model.org, repo_name=repo_model.name
        )
        if credential_refresh_func is None:
            # We can't pass credentials to icechunk if we have a credential refresh function
            credentials = (
                credentials_override
                if credentials_override
                else await self._maybe_get_credentials_for_icechunk(bucket=repo_model.bucket, org=repo_model.org, repo_name=repo_model.name)
            )
        else:
            credentials = None

        # If config is not set, set scatter_initial_credentials to True by default
        scatter_initial_credentials = arraylake_config.get("icechunk.scatter_initial_credentials", True)

        return _get_icechunk_storage_obj(
            bucket_config=repo_model.bucket,
            prefix=repo_model.prefix,
            credential_type=_get_credential_type(credentials, credential_refresh_func),
            credentials=credentials,
            credential_refresh_func=credential_refresh_func,
            scatter_initial_credentials=scatter_initial_credentials,
            arraylake_version=arraylake_version,
            user_id=user_id,
        )

    async def get_icechunk_storage(self, name: OrgAndRepoName, credentials_override=None):  # -> icechunk.Storage
        """Gets the icechunk storage object for the repo.

        Args:
            repo_name: Full name of the repo (of the form [ORG]/[REPO])
            credentials_override:
                Optional credentials to use for the storage object.
                If not provided, the credentials will be fetched from
                the bucket config.

        Returns:
            icechunk.Storage object for the repo.
        """
        _raise_if_no_icechunk()

        repo_model = await self.get_repo_object(name)

        # TODO: Optimize this, we create the metastore in `get_repo_object` and we don't need to do it again here maybe?
        mstore = self._metastore_for_org(repo_model.org)
        user = await mstore.get_user()
        return await self._get_icechunk_storage_from_repo_model(repo_model, user.id, credentials_override)

    async def get_icechunk_container_credentials_from_bucket(
        self, org: OrgName, bucket_config_nickname: BucketNickname
    ):  # -> icechunk.Credentials.S3
        """Get the icechunk virtual container credentials for a given bucket.

        Args:
            org: The organization the bucket belongs to.
            bucket_config_nickname: Nickname of the bucket to get credentials for.

        Returns:
            icechunk.Credentials.S3: The icechunk virtual chunk credentials for the bucket.
        """
        _raise_if_no_icechunk()

        bucket = await self.get_bucket_config(org=org, nickname=bucket_config_nickname)
        credential_refresh_func = self._maybe_get_credential_refresh_func_for_icechunk(bucket=bucket, org=org, repo_name=None)
        if credential_refresh_func is None:
            credentials = await self._maybe_get_credentials_for_icechunk(bucket=bucket, org=org, repo_name=None)
        else:
            credentials = None

        return get_icechunk_container_credentials(
            bucket_platform=bucket.platform, credentials=credentials, credential_refresh_func=credential_refresh_func
        )

    async def containers_credentials_for_buckets(
        self, org: OrgName, containers_to_buckets_map: dict[BucketPrefix, BucketNickname] = {}, **kwargs: str
    ) -> dict[BucketPrefix, Any]:  # -> dict[Url_Prefix, icechunk.AnyCredential]
        """Builds a map of credentials for icechunk virtual chunk containers
        from the provided bucket nicknames and calls icechunk.containers_credentials
        on this mapping.

        Args:
            org: The organization the buckets belong to.
            containers_to_buckets_map:
                A dictionary mapping virtual chunk container names to bucket nicknames.

        Returns:
            A dictionary mapping container names to icechunk virtual chunk credentials.
        """
        _raise_if_no_icechunk()
        import icechunk  # noqa: F811

        m = {}
        for container_name, bucket_nickname in {**containers_to_buckets_map, **kwargs}.items():
            if isinstance(bucket_nickname, str):
                m[container_name] = await self.get_icechunk_container_credentials_from_bucket(org, bucket_nickname)
            else:
                raise ValueError(f"Invalid bucket nickname {bucket_nickname} for container {container_name}.")
        return icechunk.containers_credentials(m)

    async def modify_repo(
        self,
        name: OrgAndRepoName,
        description: Optional[str] = None,
        add_metadata: Optional[RepoMetadataT] = None,
        remove_metadata: Optional[list[str]] = None,
        update_metadata: Optional[RepoMetadataT] = None,
        optimization_config: Optional[OptimizationConfig] = None,
    ) -> None:
        """Modify a repo's metadata or description.

        Args:
            name: Full name of the repo (of the form [ORG]/[REPO])
            description: Optional description for the repo.
            add_metadata: Optional dictionary of metadata to add to the repo.
                Dictionary values can be a scalar (string, int, float, bool, or None) or a list of scalars.
                Cannot use if the key already exists in the metadata.
            remove_metadata: List of metadata keys to remove from the repo.
            update_metadata: Optional dictionary of metadata to update on the repo.
                Dictionary values can be a scalar (string, int, float, bool, or None) or a list of scalars.
            optimization_config: Optional optimization configuration for the repo.
        """
        org, repo_name = _parse_org_and_repo(name)
        mstore = self._metastore_for_org(org)
        await mstore.modify_database(
            repo_name,
            description=description,
            add_metadata=add_metadata,
            remove_metadata=remove_metadata,
            update_metadata=update_metadata,
            optimization_config=optimization_config,
        )

    async def delete_repo(self, name: OrgAndRepoName, *, imsure: bool = False, imreallysure: bool = False) -> None:
        """Delete a repo

        Args:
            name: Full name of the repo to delete (of the form [ORG]/[REPO])
            imsure, imreallysure: confirm you intend to delete this bucket config
        """

        org, repo_name = _parse_org_and_repo(name)
        mstore = self._metastore_for_org(org)
        await mstore.delete_database(repo_name, imsure=imsure, imreallysure=imreallysure)

    async def _set_repo_status(
        self, qualified_repo_name: OrgAndRepoName, mode: RepoOperationMode, message: str | None = None
    ) -> RepoOperationStatusResponse:
        """Sets the repo status to the given mode.

        Args:
            qualified_repo_name: Full name of the repo (of the form [ORG]/[REPO])
            mode: The mode to set the repo to.
            message: Optional message to associate with the mode change.

        Returns:
            RepoOperationStatusResponse object containing mode change outputs.
        """
        org, repo_name = _parse_org_and_repo(qualified_repo_name)
        mstore = self._metastore_for_org(org)
        return await mstore.set_repo_status(repo_name, mode, message)

    async def _bucket_id_for_nickname(self, mstore: HttpMetastore, nickname: BucketNickname) -> UUID:
        buckets = await mstore.list_bucket_configs()
        bucket_id = next((b.id for b in buckets if b.nickname == nickname), None)
        if not bucket_id:
            raise BucketNotFoundError(nickname)
        return bucket_id

    def _make_bucket_config(self, *, nickname: BucketNickname, uri: str, extra_config: dict | None, auth_config: dict | None) -> dict:
        if not nickname:
            raise ValueError("nickname must be specified if uri is provided.")

        # unpack optionals
        if extra_config is None:
            extra_config = {}
        if auth_config is None:
            auth_config = {"method": "anonymous"}

        # parse uri and get prefix
        res = urlparse(uri)
        platform: Literal["s3", "gs", "s3-compatible"] | None = "s3" if res.scheme == "s3" else "gs" if res.scheme == "gs" else None
        if platform == "s3" and extra_config.get("endpoint_url"):
            platform = "s3-compatible"
        if platform not in ["s3", "gs", "s3-compatible"]:
            raise ValueError(f"Invalid platform {platform} for uri {uri}")
        name = res.netloc
        prefix = res.path[1:] if res.path.startswith("/") else res.path  # is an empty string if not specified

        valid_methods = [
            "customer_managed_role",
            "aws_customer_managed_role",
            "gcp_customer_managed_role",
            "r2_customer_managed_role",
            "anonymous",
            "hmac",
        ]
        if "method" not in auth_config or auth_config["method"] not in valid_methods:
            raise ValueError(f"invalid auth_config, must provide method key {valid_methods}")

        return dict(
            platform=platform,
            name=name,
            prefix=prefix,
            nickname=nickname,
            extra_config=extra_config,
            auth_config=auth_config,
        )

    async def create_bucket_config(
        self, *, org: OrgName, nickname: BucketNickname, uri: URI, extra_config: dict | None = None, auth_config: dict | None = None
    ) -> BucketResponse:
        """Create a new bucket config entry

        NOTE: This does not create any actual buckets in the object store.

        Args:
            org: Name of the org
            nickname: bucket nickname (example: ours3-bucket`)
            uri: The URI of the object store, of the form
                platform://bucket_name[/prefix].
            extra_config: dictionary of additional config to set on bucket config
            auth_config: dictionary of auth parameters, must include "method" key, default is `{"method": "anonymous"}`
        """
        validated = NewBucket(**self._make_bucket_config(nickname=nickname, uri=uri, extra_config=extra_config, auth_config=auth_config))
        mstore = self._metastore_for_org(org)
        bucket = await mstore.create_bucket_config(validated)
        return bucket

    async def set_default_bucket_config(self, *, org: OrgName, nickname: BucketNickname) -> None:
        """Set the organization's default bucket for any new repos

        Args:
            nickname: Nickname of the bucket config to set as default.
        """
        mstore = self._metastore_for_org(org)
        bucket_id = await self._bucket_id_for_nickname(mstore, nickname)
        await mstore.set_default_bucket_config(bucket_id)

    async def get_bucket_config(self, *, org: OrgName, nickname: BucketNickname) -> BucketResponse:
        """Get a bucket's configuration

        Args:
            org: Name of the org
            nickname: Nickname of the bucket config to retrieve.
        """
        mstore = self._metastore_for_org(org)
        bucket_id = await self._bucket_id_for_nickname(mstore, nickname)
        bucket = await mstore.get_bucket_config(bucket_id)
        return bucket

    async def list_bucket_configs(self, org: OrgName) -> list[BucketResponse]:
        """List all bucket config entries

        Args:
            org: Name of the organization.
        """
        mstore = self._metastore_for_org(org)
        return await mstore.list_bucket_configs()

    async def list_repos_for_bucket_config(self, *, org: OrgName, nickname: BucketNickname) -> list[RepoModel]:
        """List repos using a given bucket

        Args:
            org: Name of the org
            nickname: Nickname of the bucket configuration.
        """
        mstore = self._metastore_for_org(org)
        bucket_id = await self._bucket_id_for_nickname(mstore, nickname)
        buckets = await mstore.list_repos_for_bucket_config(bucket_id)
        return buckets

    async def delete_bucket_config(
        self, *, org: OrgName, nickname: BucketNickname, imsure: bool = False, imreallysure: bool = False
    ) -> None:
        """Delete a bucket config entry

        NOTE: If a bucket config is in use by one or more repos, it cannot be
        deleted. This does not actually delete any buckets in the object store.

        Args:
            org: Name of the org
            nickname: Nickname of the bucket config to delete.
            imsure, imreallysure: confirm you intend to delete this bucket config
        """
        if not (imsure and imreallysure):
            raise ValueError("imsure and imreallysure must be set to True")
        mstore = self._metastore_for_org(org)
        bucket_id = await self._bucket_id_for_nickname(mstore, nickname)
        await mstore.delete_bucket_config(bucket_id)

    async def login(self, *, browser: bool = False) -> None:
        """Login to ArrayLake.

        Args:
            browser: if True, open the browser to the login page
        """
        handler = get_auth_handler()
        await handler.login(browser=browser)

    async def logout(self) -> None:
        """Log out of ArrayLake."""
        handler = get_auth_handler()
        await handler.logout()

    async def get_api_client_from_token(self, org: OrgName, token: str) -> ApiClientResponse:
        """Fetch the user corresponding to the provided token"""
        mstore = self._metastore_for_org(org)
        api_client = await mstore.get_api_client_from_token(token)
        return api_client

    async def get_permission_check(self, org: OrgName, principal_id: str, resource: str, action: OrgActions | RepoActions) -> bool:
        """Verify whether the provided principal has permission to perform the
        action against the resource"""
        mstore = self._metastore_for_org(org)
        is_approved = await mstore.get_permission_check(principal_id, resource, action)
        return is_approved

    def get_services(self, org: OrgName) -> AsyncComputeClient:
        """Get the compute client services for the given org.

        Args:
            org: Name of the org
        """
        return AsyncComputeClient(service_uri=self.service_uri, token=self.token, org=org)


@dataclass
class Client:
    """Client for interacting with ArrayLake.

    Args:
        service_uri (str): [Optional] The service URI to target.
        token (str): [Optional] API token for service account authentication.
    """

    service_uri: Optional[str] = None
    token: Optional[str] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.token is None:
            self.token = arraylake_config.get("token", None)
        if self.service_uri is None:
            self.service_uri = arraylake_config.get("service.uri")

        self.aclient = AsyncClient(self.service_uri, token=self.token)

    def list_repos(self, org: OrgName, filter_metadata: RepoMetadataT | None = None) -> Sequence[RepoModel]:
        """List all repositories for the specified org

        Args:
            org: Name of the org
            filter_metadata: Optional metadata to filter the repos by.
                If provided, only repos with the specified metadata will be returned.
                Filtering is inclusive and will return repos that match all of the provided metadata.
        """

        repo_list = sync(self.aclient.list_repos, org, filter_metadata=filter_metadata)
        return repo_list

    def get_repo(
        self,
        name: OrgAndRepoName,
        *,
        checkout: Optional[bool] = None,
        read_only: bool | None = None,
        config: RepoConfig = None,  # icechunk.RepositoryConfig | dict[str, Any] | None
    ) -> repo_v1.Repo | IcechunkRepository:  # noqa
        """Get a repo by name

        Args:
            name: Full name of the repo (of the form [ORG]/[REPO])
            checkout: Automatically checkout the repo after instantiation. Ignored if specified for a Icechunk repo.
            read_only: Open the repo in read-only mode.
            config: Optional config for the repo. For Icechunk repos, this is the RepositoryConfig.
                Config settings passed here will take precedence over
                the stored repo config when opening the repo.
        """

        arepo = sync(
            self.aclient.get_repo,
            name,
            checkout=checkout,
            read_only=read_only,
            config=config,
        )
        # We don't have access to the repo kind and we must be environment agnostic
        try:
            from icechunk import Repository as IcechunkRepository

            if isinstance(arepo, IcechunkRepository):
                return arepo
        except ImportError:
            pass
        return arepo.to_sync_repo()

    def get_or_create_repo(
        self,
        name: OrgAndRepoName,
        *,
        checkout: Optional[bool] = None,
        bucket_config_nickname: Optional[BucketNickname] = None,
        kind: Optional[RepoKind] = None,
        prefix: Optional[str] = None,
        import_existing: bool = False,
        description: Optional[str] = None,
        metadata: Optional[RepoMetadataT] = None,
        config: RepoConfig = None,  # icechunk.RepositoryConfig | dict[str, Any] | None
    ) -> repo_v1.Repo | IcechunkRepository:  # noqa
        """Get a repo by name. Create the repo if it doesn't already exist.

        Args:
            name: Full name of the repo (of the form [ORG]/[REPO])
            checkout: Whether to checkout the repo after instantiation.
                If the repo does not exist, checkout is ignored.
                Ignored if specified for a Icechunk repo.
            bucket_config_nickname: The created repo will use this bucket for its chunks.
                If the repo exists, bucket_config_nickname is ignored.
            kind: The kind of repo to get or create e.g. Arraylake V1 or Icechunk V2
            prefix: Optional prefix for Icechunk store. Only used for Icechunk repos.
                If not provided, a random ID + the repo name will be used.
            import_existing: If True, the Icechunk repo will be imported if it already exists.
            description: Optional description for the repo.
            metadata: Optional dictionary of metadata to tag the repo with.
                Dictionary values can be a scalar (string, int, float, bool, or None) or a list of scalars.
            config: Optional config for the repo.
                For Icechunk repos, this is the RepositoryConfig.
                Config settings passed here will take precedence over
                the stored repo config when opening the repo. When creating
                a new repo, the config will be saved alongside the repo.
        """
        arepo = sync(
            self.aclient.get_or_create_repo,
            name,
            bucket_config_nickname=bucket_config_nickname,
            checkout=checkout,
            kind=kind,
            prefix=prefix,
            import_existing=import_existing,
            description=description,
            metadata=metadata,
            config=config,
        )
        # We don't have access to the repo kind and we must be environment agnostic
        try:
            from icechunk import Repository as IcechunkRepository

            if isinstance(arepo, IcechunkRepository):
                return arepo
        except ImportError:
            pass
        return arepo.to_sync_repo()

    def create_repo(
        self,
        name: OrgAndRepoName,
        *,
        bucket_config_nickname: Optional[BucketNickname] = None,
        kind: Optional[RepoKind] = None,
        prefix: Optional[str] = None,
        import_existing: bool = False,
        description: Optional[str] = None,
        metadata: Optional[RepoMetadataT] = None,
        config: RepoConfig = None,  # icechunk.RepositoryConfig | dict[str, Any] | None
    ) -> repo_v1.Repo | IcechunkRepository:  # noqa
        """Create a new repo

        Args:
            name: Full name of the repo to create (of the form [ORG]/[REPO])
            bucket_config_nickname: An optional bucket to use for the chunkstore
            kind: the kind of repo to create (`v1` or `icechunk`)
            prefix: Optional prefix for Icechunk store. Only used for Icechunk V2 repos.
                If not provided, a random ID + the repo name will be used.
            import_existing: If True, the Icechunk repo will be imported if it already exists.
            description: Optional description for the repo.
            metadata: Optional dictionary of metadata to tag the repo with.
                Dictionary values can be a scalar (string, int, float, bool, or None) or a list of scalars.
            config: Optional config for the repo.
                For Icechunk repos, this is the RepositoryConfig, and
                the config will be saved alongside the repo upon creation.
        """
        # Check that we can import the correct repo type
        if kind is None:
            kind = _DEFAULT_NEW_REPO_KIND

        arepo = sync(
            self.aclient.create_repo,
            name,
            bucket_config_nickname=bucket_config_nickname,
            kind=kind,
            prefix=prefix,
            import_existing=import_existing,
            description=description,
            metadata=metadata,
            config=config,
        )
        if kind == RepoKind.Icechunk:
            return arepo
        return arepo.to_sync_repo()

    def get_icechunk_storage(
        self, name: OrgAndRepoName, *, credentials_override=None  # icechunk.AnyCredential | None
    ):  # Returns a icechunk.Storage object
        """Gets the icechunk storage object for the repo.

        Example usage:

            ```python
            from arraylake import Client
            client = Client()
            storage = client.get_icechunk_storage("my-org/my-repo")
            icechunk.Repository.exists(storage)
            icechunk.Repository.fetch_config(storage)
            repo = icechunk.Repository.open(storage)
            ```

        Args:
            repo_name: Full name of the repo (of the form [ORG]/[REPO])
            credentials_override: Optional credentials to use for the storage object.
                If not provided, the credentials will be fetched from
                the bucket config.

        Returns:
            icechunk.Storage object for the repo.
        """
        return sync(self.aclient.get_icechunk_storage, name, credentials_override=credentials_override)

    def get_icechunk_container_credentials_from_bucket(
        self, org: OrgName, bucket_config_nickname: BucketNickname
    ):  # -> icechunk.Credentials.S3
        """Get the icechunk virtual chunk credentials for a given bucket.

        Args:
            org: The organization the bucket belongs to.
            bucket_config_nickname: Nickname of the bucket to get credentials for.

        Returns:
            icechunk.Credentials.S3: The icechunk virtual chunk credentials for the bucket.
        """
        return sync(self.aclient.get_icechunk_container_credentials_from_bucket, org, bucket_config_nickname)

    def containers_credentials_for_buckets(
        self, org: OrgName, containers_to_buckets_map: dict[BucketPrefix, BucketNickname] = {}, **kwargs: str
    ) -> dict[BucketPrefix, S3Credentials]:
        """Builds a map of credentials for icechunk virtual chunk containers
        from the provided bucket nicknames and calls icechunk.containers_credentials
        on this mapping.

        Example usage:
        ```python
        import icechunk as ic
        from arraylake import Client

        client = Client()
        storage = client.get_icechunk_storage("my-org/my-repo")
        config = ic.Repository.fetch_config(storage)
        container_names = [container.name for container in config.virtual_chunk_containers()]
        container_creds = client.containers_credentials_for_buckets("my-org", conatiner_name="my-bucket")
        repo = ic.Repository.open(storage, config=config, virtual_chunk_credentials=container_creds)
        ```

        Args:
            org: The organization the bucket belongs to.
            containers_to_buckets_map:
                A dictionary mapping virtual chunk container names to bucket nicknames.

        Returns:
            A dictionary mapping container names to icechunk virtual chunk credentials.
        """
        return sync(
            self.aclient.containers_credentials_for_buckets,
            org=org,
            containers_to_buckets_map=containers_to_buckets_map,
            **kwargs,  # type: ignore
        )

    def modify_repo(
        self,
        name: OrgAndRepoName,
        description: Optional[str] = None,
        add_metadata: Optional[RepoMetadataT] = None,
        remove_metadata: Optional[list[str]] = None,
        update_metadata: Optional[RepoMetadataT] = None,
        optimization_config: Optional[OptimizationConfig] = None,
    ) -> None:
        """Modify a repo's metadata or description.

        Args:
            name: Full name of the repo (of the form [ORG]/[REPO])
            description: Optional description for the repo.
            add_metadata: Optional dictionary of metadata to add to the repo.
                Dictionary values can be a scalar (string, int, float, bool, or None) or a list of scalars.
                Cannot use if the key already exists in the metadata.
            remove_metadata: List of metadata keys to remove from the repo.
            update_metadata: Optional dictionary of metadata to update on the repo.
                Dictionary values can be a scalar (string, int, float, bool, or None) or a list of scalars.
            optimization_config: Optional optimization configurations for the repo.
        """
        return sync(
            self.aclient.modify_repo,
            name,
            description=description,
            add_metadata=add_metadata,
            remove_metadata=remove_metadata,
            update_metadata=update_metadata,
            optimization_config=optimization_config,
        )

    def delete_repo(self, name: OrgAndRepoName, *, imsure: bool = False, imreallysure: bool = False) -> None:
        """Delete a repo

        Args:
            name: Full name of the repo to delete (of the form [ORG]/[REPO])
        """

        return sync(self.aclient.delete_repo, name, imsure=imsure, imreallysure=imreallysure)

    def create_bucket_config(
        self, *, org: OrgName, nickname: BucketNickname, uri: URI, extra_config: dict | None = None, auth_config: dict | None = None
    ) -> BucketResponse:
        """Create a new bucket config entry

        NOTE: This does not create any actual buckets in the object store.

        Args:
            org: Name of the org
            nickname: bucket nickname (example: our-s3-bucket)
            uri: The URI of the object store, of the form
                platform://bucket_name[/prefix].
            extra_config: dictionary of additional config to set on bucket config
            auth_config: dictionary of auth parameters, must include "method" key, default is `{"method": "anonymous"}`
        """
        return sync(
            self.aclient.create_bucket_config, org=org, nickname=nickname, uri=uri, extra_config=extra_config, auth_config=auth_config
        )

    def set_default_bucket_config(self, *, org: OrgName, nickname: BucketNickname) -> None:
        """Set the organization's default bucket config for any new repos

        Args:
            org: Name of the org
            nickname: Nickname of the bucket config to set as default.
        """
        return sync(self.aclient.set_default_bucket_config, org=org, nickname=nickname)

    def get_bucket_config(self, *, org: OrgName, nickname: BucketNickname) -> BucketResponse:
        """Get a bucket's configuration

        Args:
            org: Name of the org
            nickname: Nickname of the bucket config to retrieve.
        """
        return sync(self.aclient.get_bucket_config, org=org, nickname=nickname)

    def list_bucket_configs(self, org: OrgName) -> list[BucketResponse]:
        """List all buckets for the specified org

        Args:
            org: Name of the org
        """
        return sync(self.aclient.list_bucket_configs, org)

    def list_repos_for_bucket_config(self, *, org: OrgName, nickname: BucketNickname) -> list[repo_v1.Repo | IcechunkRepository]:  # noqa
        """List repos using a given bucket config

        Args:
            org: Name of the org
            nickname: Nickname of the bucket.
        """
        return sync(self.aclient.list_repos_for_bucket_config, org=org, nickname=nickname)

    def delete_bucket_config(self, *, org: OrgName, nickname: BucketNickname, imsure: bool = False, imreallysure: bool = False) -> None:
        """Delete a bucket config entry

        NOTE: If a bucket config is in use by one or more repos, it cannot be
        deleted. This does not actually delete any buckets in the object store.

        Args:
            org: Name of the org
            nickname: Nickname of the bucket config to delete.
            imsure, imreallysure: confirm you intend to delete this bucket config
        """
        return sync(self.aclient.delete_bucket_config, org=org, nickname=nickname, imsure=imsure, imreallysure=imreallysure)

    def login(self, *, browser: bool = False) -> None:
        """Login to ArrayLake.

        Args:
            browser: if True, open the browser to the login page
        """
        return sync(self.aclient.login, browser=browser)

    def logout(self) -> None:
        """Log out of ArrayLake."""
        return sync(self.aclient.logout)

    def get_services(self, org: OrgName) -> ComputeClient:
        """Get the compute client services for the given org.

        Args:
            org: Name of the org
        """
        return self.aclient.get_services(org).to_sync_client()
