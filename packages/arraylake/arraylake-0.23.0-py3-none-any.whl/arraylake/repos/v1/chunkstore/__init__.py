"""
DEPRECATED: This V1 chunkstore module is pending removal.
V1 repositories are legacy and will be phased out in favor of Icechunk repositories.
This module and all its contents are scheduled for removal in a future version.
"""

from __future__ import annotations

from collections import ChainMap
from collections.abc import Mapping
from typing import Any, Callable, Optional, TypeVar
from urllib.parse import urlparse

from arraylake.log_util import get_logger
from arraylake.repos.v1.chunkstore.abc import Chunkstore, ObjectStore
from arraylake.repos.v1.chunkstore.base_chunkstore import (
    MAX_INLINE_THRESHOLD_BYTES,
    BaseChunkstore,
)
from arraylake.repos.v1.chunkstore.fsspec_chunkstore import (
    FSSpecObjectStore,
    GCSFSObjectStore,
    S3FSObjectStore,
)
from arraylake.repos.v1.chunkstore.s3chunkstore import S3ObjectStore
from arraylake.repos.v1.types import ChunkstoreSchemaVersion
from arraylake.types import DBID, Bucket, Platform, S3Credentials

logger = get_logger(__name__)

OS = TypeVar("OS", bound=ObjectStore)

from typing import cast

# TODO: fix Any typing here
DEFAULT_STORES: Mapping[Platform, Any] = {
    "s3": S3ObjectStore,
    "s3-compatible": S3ObjectStore,
    "minio": S3ObjectStore,
    "gs": GCSFSObjectStore,
}


def get_object_store_type(platform: Platform, object_store: type[OS] | None) -> type[OS]:
    object_store_type = DEFAULT_STORES[platform] if object_store is None else object_store
    return object_store_type


# TODO: Consider making this a class method on Chunkstore
def mk_chunkstore_from_uri(
    chunkstore_uri: str, inline_threshold_bytes: int = 0, object_store: type[OS] | None = None, **kwargs
) -> BaseChunkstore:
    """Initialize a Chunkstore

    Args:
        chunkstore_uri: URI to chunkstore.
        inline_threshold_bytes: Byte size below which a chunk will be stored in the metastore database. Maximum is 512.
            Values less than or equal to 0 disable inline storage.
        chunkstore: Type of chunkstore to create
        kwargs: Additional keyword arguments to pass to the chunkstore constructor.
    Returns:
        chunkstore:
    """

    parsed_uri = urlparse(chunkstore_uri)
    # Raise also if "s3:/foo" (for which netloc='' and path='/foo')
    if parsed_uri.scheme not in DEFAULT_STORES or not parsed_uri.netloc:
        raise ValueError(f"Cannot parse chunkstore uri {chunkstore_uri}, supported prefixes are: ['s3://', 'gs://']")

    object_store_type: type[OS] = get_object_store_type(cast(Platform, parsed_uri.scheme), object_store)
    bucket_name = parsed_uri.netloc.strip("/")
    prefix = parsed_uri.path.strip("/")

    return BaseChunkstore(
        object_store=object_store_type(bucket_name=bucket_name, kwargs=kwargs),
        prefix=prefix,
        schema_version=ChunkstoreSchemaVersion.V0,
        inline_threshold_bytes=inline_threshold_bytes,
    )


def bucket_prefix(bucket: Bucket, repo_id: DBID) -> str:
    id = repo_id.hex()
    return f"{bucket.prefix}/{id}" if bucket.prefix else id


# TODO: Consider making this a class method on Chunkstore
def mk_chunkstore_from_bucket_config(
    bucket: Bucket,
    repo_id: DBID,
    inline_threshold_bytes: int = 0,
    fetch_credentials_func: Optional[Callable[..., S3Credentials]] = None,
    cache_key: tuple[Any, ...] = (),
    **kwargs,
) -> BaseChunkstore:
    bucket_name = bucket.name
    prefix = bucket_prefix(bucket, repo_id)
    bucket_config = dict(bucket.extra_config)
    object_store_type: type[ObjectStore] = get_object_store_type(bucket.platform, object_store=None)

    # We make bucket config take precedence over kwargs
    # The main conflict we care about is endpoint_url
    # The previous version was equivalent to ChainMap(kwargs, bucket_config)
    # where kwargs took precedence over bucket_config.
    # This is an issue when s3.endpoint_url is set externally through a config file or env variable
    # but the bucket_config has an endpoint_url that points to Google Cloud, for example.
    # This is probably only an issue for us.
    conflicts = set(bucket_config) & set(kwargs)
    if conflicts:
        logger.debug("Conflicting parameters %s set on bucket_config.", conflicts)
    kws = ChainMap(bucket_config, kwargs)
    return BaseChunkstore(
        object_store=object_store_type(
            bucket_name=bucket_name, fetch_credentials_func=fetch_credentials_func, cache_key=cache_key, kwargs=dict(kws)
        ),
        prefix=prefix,
        schema_version=ChunkstoreSchemaVersion.V1,
        inline_threshold_bytes=inline_threshold_bytes,
    )
