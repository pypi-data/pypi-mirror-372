import base64
import importlib
import warnings
from collections.abc import Mapping
from functools import lru_cache
from itertools import groupby
from typing import Callable, NewType, Optional
from urllib.parse import urlparse

import cachetools
import numpy as np

from arraylake.asyn import async_gather
from arraylake.config import config
from arraylake.exceptions import ExpectedChunkNotFoundError, MissingChunkError
from arraylake.log_util import get_logger
from arraylake.repos.v1.chunkstore.abc import Chunkstore, ObjectStore
from arraylake.repos.v1.chunkstore.fsspec_compat import FSConfig
from arraylake.repos.v1.chunkstore.utils import (
    ByteRange,
    ChunkRequest,
    CoalescedRequests,
    SplitRequest,
    UnmodifiedRequest,
    optimize_requests,
)
from arraylake.repos.v1.types import (
    ChunkHash,
    ChunkstoreSchemaVersion,
    ReferenceData,
    SessionID,
)

logger = get_logger(__name__)

MAX_INLINE_THRESHOLD_BYTES = 512
KEY_CACHE_SIZE = 5000


class InlineTooLongError(ValueError):
    pass


ChunkData = NewType("ChunkData", dict[str, bytes])


def decode_inline_data(data: bytes) -> str:
    """called before writing inline data to json"""
    # matches kerchunk inline output
    try:
        dec = data.decode()
    except UnicodeDecodeError:
        dec = "base64:" + base64.b64encode(data).decode()

    if len(dec) > MAX_INLINE_THRESHOLD_BYTES:
        # if decoding pushed the length over the threshold, raise an error
        raise InlineTooLongError(f"Inline data too large: {len(dec)} > {MAX_INLINE_THRESHOLD_BYTES}")

    return f"inline://{dec}"


def encode_inline_data(data: str) -> bytes:
    """called when loading an inline chunk"""

    if data.startswith("inline://"):
        data = data[9:]

    if data.startswith("base64:"):
        enc = base64.b64decode(data[7:])
    else:
        enc = data.encode()
    return enc


def make_object_store_key(
    version: ChunkstoreSchemaVersion,
    bucket_prefix: Optional[str],
    session_id: Optional[SessionID],
    token: str,
) -> str:
    if version == ChunkstoreSchemaVersion.V0:
        name = token
    else:
        assert session_id, "Schema manifest versions > 0 require a session_id"
        name = f"chunks/{token}.{session_id}"

    if bucket_prefix:
        return f"{bucket_prefix}/{name}"
    else:
        return name


def make_object_store_key_from_reference_data(bucket_prefix: Optional[str], chunk_ref: ReferenceData) -> tuple[Optional[str], str]:
    """Return the object store key pointed by this ReferenceData.

    If the bucket name is available in the data, include it as the first
    element of result tuple. Otherwise, return only the object key.
    """

    assert not chunk_ref.is_inline()
    schema_version = chunk_ref.v

    if chunk_ref.is_virtual() or schema_version == ChunkstoreSchemaVersion.V0:
        if chunk_ref.uri is None:
            raise ValueError("Invalid chunk, it should have a uri")
        parsed_uri = urlparse(chunk_ref.uri)
        key = parsed_uri.path.strip("/")
        bucket = parsed_uri.netloc
        return (bucket, key)
    else:
        assert chunk_ref.is_materialized()
        assert schema_version > ChunkstoreSchemaVersion.V0

        hash = chunk_ref.hash
        assert hash, "Chunkstore schema > 0 manifests must have a hash"
        token = hash.get("token")
        assert token, "Chunkstore schema > 0 manifests must have a token"
        session = chunk_ref.sid
        assert token, "Chunkstore schema > 0 manifests must have a sid"
        return (
            None,
            make_object_store_key(
                version=schema_version,
                bucket_prefix=bucket_prefix,
                session_id=session,
                token=token,
            ),
        )


class HashValidationError(AssertionError):
    pass


def tokenize(data: bytes, *, hasher: Callable) -> str:
    hash_obj = hasher(data)
    return hash_obj.hexdigest()


@lru_cache(maxsize=None)
def get_hasher(method):
    try:
        mod_name, func_name = method.rsplit(".", 1)
        mod = importlib.import_module(mod_name)
        return getattr(mod, func_name)
    except (ImportError, AttributeError):
        raise ValueError(f"invalid hash method {method}")


class BaseChunkstore(Chunkstore):
    """Class implementing logic for all chunkstores. It wraps an instance of
    ObjectStore which handles all the backend-specific logic around reading/writing
    bytes.
    """

    prefix: str
    schema_version: ChunkstoreSchemaVersion
    inline_threshold_bytes: int
    _known_key_cache: cachetools.LFUCache
    object_store: ObjectStore

    # TODO: consider classmethod from_object_store instead
    def __init__(
        self,
        object_store: ObjectStore,
        prefix: str,
        schema_version: ChunkstoreSchemaVersion,
        inline_threshold_bytes: int = 0,
    ):
        """
        This base class captures core chunkstore logic, but expects to be sub-classed for specific storage
        targets (s3, GCS, etc). To use this class it is required to provide an ObjectStore subclass: pull_data, put_data.
        Args:
            object_store: Underlying ObjectStore that handles reading and writing of bytes.
            prefix: a string under which all chunk keys will be placed. Must be unique for the bucket.
            schema_version: the version number for the manifest and object store key schema
            inline_threshold_bytes: Byte size below which a chunk will be stored in the metastore database. Maximum is 512.
                Values less than or equal to 0 disable inline storage.
        """
        assert prefix or schema_version == ChunkstoreSchemaVersion.V0, "schema_version > 0 requires a bucket prefix"
        self.prefix = prefix.strip("/")
        self.schema_version = schema_version
        self.object_store = object_store

        self.inline_threshold_bytes = inline_threshold_bytes
        if self.inline_threshold_bytes > MAX_INLINE_THRESHOLD_BYTES:
            raise ValueError(f"Inline chunk threshold too large, max={MAX_INLINE_THRESHOLD_BYTES} bytes")

        self._known_key_cache = cachetools.LFUCache(maxsize=KEY_CACHE_SIZE)  # tunable

    def __getstate__(self):
        return (
            self.prefix,
            self.schema_version,
            self.inline_threshold_bytes,
            self.object_store,
        )

    def __setstate__(self, state):
        (
            self.prefix,
            self.schema_version,
            self.inline_threshold_bytes,
            self.object_store,
        ) = state
        self._known_key_cache = cachetools.LFUCache(maxsize=KEY_CACHE_SIZE)

    @property
    def bucket_name(self) -> str:
        return self.object_store.bucket_name

    @property
    def write_schema_version(self) -> ChunkstoreSchemaVersion:
        return self.schema_version

    async def ping(self):
        await self.object_store.ping()

    async def add_chunk(self, data: bytes, *, session_id: SessionID, hash_method: Optional[str] = None) -> ReferenceData:
        if isinstance(data, np.ndarray):
            # We land here if the data are not compressed by a codec. This happens for 0d arrays automatically.
            data = data.tobytes()

        if hash_method is None:
            hash_method = config.get("chunkstore.hash_method", "hashlib.sha256")

        hasher = get_hasher(hash_method)
        token = tokenize(data, hasher=hasher)
        hash = ChunkHash(method=hash_method, token=token)
        length = len(data)

        await logger.adebug("put chunk %s", token)

        inline = False
        uri: Optional[str] = None

        if length <= self.inline_threshold_bytes:
            await logger.adebug("Adding inline chunk %s", token)
            try:
                uri = decode_inline_data(data)
                inline = True
            except InlineTooLongError:
                # we failed to inline this data, so treat it like a regular chunk
                pass

        if inline is False:
            key = make_object_store_key(
                self.schema_version,
                bucket_prefix=self.prefix,
                session_id=session_id,
                token=token,
            )

            if key not in self._known_key_cache:
                await self.object_store.put_data(data=data, key=key)
                self._known_key_cache[key] = None

            if self.schema_version == ChunkstoreSchemaVersion.V0:
                uri = self.object_store.make_uri(key)
                return ReferenceData.new_materialized_v0(uri=uri, length=len(data), hash=hash)
            elif self.schema_version == ChunkstoreSchemaVersion.V1:
                return ReferenceData.new_materialized_v1(length=len(data), hash=hash, sid=session_id)
            else:
                assert False, f"Unsupported chunkstore schema version {self.schema_version}"

        else:
            assert uri
            return ReferenceData.new_inline(
                for_version=self.schema_version,
                data=uri,
                length=length,
                hash=hash,
                sid=session_id,
            )

    async def _pull_data_for_chunk_ref(self, start_byte: int, length: int, key: str, bucket: str) -> bytes:
        try:
            data = await self.object_store.pull_data(start_byte=start_byte, length=length, key=key, bucket=bucket or self.bucket_name)
        except ExpectedChunkNotFoundError as e:
            warnings.warn(f"failed to fetch chunk, key={key}, error{e}", category=UserWarning, stacklevel=3)
            if config.get("chunkstore.unsafe_use_fill_value_for_missing_chunks", False):
                # raise a MissingChunkError (a KeyError) so that Zarr can handle the missing chunk
                # (likely by inserting fill value for this chunk)
                raise MissingChunkError(key) from e
            else:
                # raise the original error
                raise e
        return data

    async def _get_chunk_unmodified(self, bucket_name: Optional[str], key: str, chunk_request: UnmodifiedRequest) -> ChunkData:
        await logger.adebug("getting unmodified chunk %s, from %s/%s", chunk_request, bucket_name, key)
        data = await self._pull_data_for_chunk_ref(
            start_byte=chunk_request.download_range.start,
            length=chunk_request.download_range.length,
            key=key,
            bucket=bucket_name or self.bucket_name,
        )
        return ChunkData({chunk_request.key: data})

    async def _get_chunk_split(self, bucket_name: Optional[str], key: str, chunk_request: SplitRequest) -> ChunkData:
        await logger.adebug("getting split chunk %s, from %s/%s", chunk_request, bucket_name, key)
        # TODO: consider explicitly setting a high concurrency limit here
        data = await async_gather(
            *(
                self._pull_data_for_chunk_ref(
                    start_byte=range.start,
                    length=range.length,
                    key=key,
                    bucket=bucket_name or self.bucket_name,
                )
                for range in chunk_request.download_ranges
            )
        )
        return ChunkData({chunk_request.key: b"".join(data)})

    async def _get_chunks_coalesced(self, bucket_name: Optional[str], key: str, request: CoalescedRequests) -> ChunkData:
        await logger.adebug("getting coalesced chunks %s, from %s/%s", request, bucket_name, key)
        download_range = request.download_range
        data = await self._pull_data_for_chunk_ref(
            start_byte=download_range.start,
            length=download_range.length,
            key=key,
            bucket=bucket_name or self.bucket_name,
        )
        # In this step, we map each chunk request (identified by chunk.key) to the correct range of the
        # the downloaded bytes. The slice includes the offset math to identify this range.
        return ChunkData(
            {
                chunk.key: data[
                    slice((chunk.range.start - download_range.start), (chunk.range.start - download_range.start + chunk.range.length))
                ]
                for chunk in request.ranges
            }
        )

    async def get_chunks(self, chunk_refs: Mapping[str, ReferenceData], *, validate: bool = False) -> ChunkData:
        chunk_data = ChunkData({})
        # TODO : Use a NamedTuple or dataclass here
        remote_refs: list[tuple[str, str | None, str, int, int]] = []  # chunk_key, bucket, key, offset, length
        for chunk_key, chunk_ref in chunk_refs.items():
            if chunk_ref.is_inline():
                assert chunk_ref.uri
                chunk_data[chunk_key] = encode_inline_data(chunk_ref.uri)
            else:
                (bucket_name, key) = make_object_store_key_from_reference_data(self.prefix, chunk_ref)
                remote_refs.append((chunk_key, bucket_name, key, chunk_ref.offset, chunk_ref.length))

        # we now need to group all the requests by bucket and key in order to discover coalescing opportunities
        def groupby_key(x):
            # bucket and key
            return x[1], x[2]

        # (list must be sorted for groupby to work)
        remote_refs.sort()
        coros = []
        for (bucket_name, key), refs in groupby(remote_refs, key=groupby_key):
            chunk_requests = [ChunkRequest(chunk_key, ByteRange(offset, length)) for chunk_key, _, _, offset, length in refs]
            for request in optimize_requests(chunk_requests):
                # dispatch to the correct method; closest thing to a Rust match statement
                if isinstance(request, UnmodifiedRequest):
                    coros.append(self._get_chunk_unmodified(bucket_name, key, request))
                elif isinstance(request, SplitRequest):
                    coros.append(self._get_chunk_split(bucket_name, key, request))
                elif isinstance(request, CoalescedRequests):
                    coros.append(self._get_chunks_coalesced(bucket_name, key, request))
                else:
                    assert False, f"Unknown request type {request}"

        results = await async_gather(*coros, return_exceptions=True)
        for item in results:
            if isinstance(item, Exception):
                if isinstance(item, MissingChunkError):
                    # omit chunks that returned a MissingChunkError
                    continue
                else:
                    raise item
            chunk_data.update(item)

        # now we have all the chunks
        if validate:
            for chunk_key, chunk_ref in chunk_refs.items():
                data = chunk_data[chunk_key]
                # TODO should this fail for virtual chunks? We never set the hash
                if chunk_ref.hash is None:
                    if chunk_ref.is_virtual():
                        logger.warning("Cannot validate: chunk hash not set, this must be a virtual chunk")
                        continue
                    else:
                        raise HashValidationError("Cannot validate: chunk hash not set")
                hasher = get_hasher(chunk_ref.hash["method"])
                h = tokenize(data, hasher=hasher)
                if h != chunk_ref.hash["token"]:
                    raise HashValidationError(f"hashes did not match for key: {key}")

        return chunk_data

    async def get_chunk(self, chunk_ref: ReferenceData, *, validate: bool = False) -> bytes:
        # here for backwards compatibility with tests
        DUMMY_KEY = "foo"
        chunk_data = await self.get_chunks({DUMMY_KEY: chunk_ref}, validate=validate)
        return chunk_data[DUMMY_KEY]

    def __repr__(self):
        return (
            f"<{type(self).__name__}, object_store={type(self.object_store).__name__}, "
            f"bucket_name={self.bucket_name!r} "
            f"schema_version='{self.schema_version}' "
            f"prefix={self.prefix!r} "
            f"status={self.object_store.status}>"
        )

    def _get_fs_config(self) -> FSConfig:
        return self.object_store._get_fs_config()
