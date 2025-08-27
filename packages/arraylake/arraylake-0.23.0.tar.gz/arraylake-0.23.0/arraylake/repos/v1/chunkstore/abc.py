from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, Callable, Literal, Optional

from arraylake.repos.v1.chunkstore.fsspec_compat import (
    FSConfig,
    GenericObjectStoreKwargs,
)
from arraylake.repos.v1.types import ChunkstoreSchemaVersion, ReferenceData, SessionID
from arraylake.types import S3Credentials


class Chunkstore(ABC):  # pragma: no cover
    @property
    @abstractmethod
    def bucket_name(self) -> str: ...

    @abstractmethod
    async def ping(self):
        """Ping the underlying object store to check connectivity"""
        ...

    @abstractmethod
    async def add_chunk(self, data: bytes, *, session_id: SessionID, hash_method: str | None = None) -> ReferenceData:
        """Add a chunk to the chunkstore

        Args:
            data: Bytestring to add to the chunkstore
            session_id: session identifier used to setup the object store key
            hash_method: Key generation method. May be any hash function that returns an object with the
                ``hexdigest()`` method. Valid examples are ``{'hashlib.sha256', 'hashlib.md5', 'xxhash.xxh128'}``.
                 Default can be set in the ``chunkstore.hash_method`` config key.

        Returns:
            chunk_ref: Dict of reference metadata about written chunk
        """
        ...

    @abstractmethod
    async def get_chunks(self, chunk_refs: Mapping[str, ReferenceData], *, validate: bool = False) -> dict[str, bytes]:
        """Get chunks from the chunkstore

        Args:
            chunk_refs: Mapping of keys to reference metadata about written chunk
            validate: If True, then validate the chunks data with its reference hash.

        Returns:
            data: Chunk bytes for each key in chunk_refs
        """
        ...

    @property
    @abstractmethod
    def write_schema_version(self) -> ChunkstoreSchemaVersion:
        """The latest version of the schema this Chunkstore can write"""
        ...

    @abstractmethod
    def _get_fs_config(self) -> FSConfig:
        """Return an FSConfig object for the underlying object store."""
        ...


class ObjectStore(ABC):  # pragma: no cover
    """This ABC defines an interface that should be implemented by new object stores."""

    @abstractmethod
    def __init__(
        self,
        bucket_name: str,
        kwargs: GenericObjectStoreKwargs,
        fetch_credentials_func: Optional[Callable[..., S3Credentials]] = None,
        cache_key: tuple[Any, ...] = (),
    ): ...

    @property
    @abstractmethod
    def bucket_name(self) -> str: ...

    @property
    @abstractmethod
    async def is_anonymous_session(self) -> bool:
        """Returns True is anonymously logged in"""
        # TODO: Consider returning enum-like that specifies different types of login,
        # and return that instead of a boolean. Examples: NOT_LOGGED, ANONYMOUS, LOCAL_CREDENTIALS, etc
        ...

    @abstractmethod
    async def ping(self):
        """Ping the object store to check connectivity"""
        ...

    @abstractmethod
    def make_uri(self, key: str) -> str:
        """Make a URI for V0 chunkstores only.
        TODO: Delete when we migrate away from V0."""
        ...

    @property
    @abstractmethod
    def status(self) -> Literal["OPEN", "CLOSED"]:
        """Return either 'OPEN' or 'CLOSED' if a
        connection to the object store is open."""
        ...

    @abstractmethod
    async def put_data(self, *, data: bytes, key: str) -> None:
        """Write bytes to chunk store

        Args:
            data: Bytestring to add to the chunkstore
            key: ...
        """
        ...

    @abstractmethod
    async def pull_data(self, start_byte: int, length: int, key: str, bucket: str) -> bytes:
        """Get a chunk from the chunkstore

        Args:
            start_byte: Offset to start from
            length: number of bytes to read
            key: ...
            bucket: bucket name

        Returns:
            data: Chunk byte string
        """
        ...

    @abstractmethod
    def _get_fs_config(self) -> FSConfig:
        """Return an FSConfig object which encapsulates an fsspec filesystem
        and is used for indexing virtual files in a way that is consistent with
        the underlying object store.
        """
        ...
