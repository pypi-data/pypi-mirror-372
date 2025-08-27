import asyncio
import socket
import weakref
from dataclasses import dataclass
from typing import Any  # noqa: F401
from typing import TYPE_CHECKING, Callable, Literal, Optional, Union

import aiobotocore.client
import aiobotocore.session
import aiohttp
import botocore
import urllib3
from aiobotocore.config import AioConfig
from boto3 import Session
from botocore import UNSIGNED
from cachetools import LRUCache

from arraylake.api_utils import retry_on_exception
from arraylake.asyn import close_async_context, get_loop, sync
from arraylake.exceptions import ExpectedChunkNotFoundError
from arraylake.log_util import get_logger
from arraylake.repos.v1.chunkstore.abc import ObjectStore
from arraylake.repos.v1.chunkstore.credential_provider import (
    AutoRefreshingCredentialProvider,
)
from arraylake.repos.v1.chunkstore.fsspec_compat import (
    GenericObjectStoreKwargs,
    GenericObjectStoreKwargs_to_S3FSConstructorKwargs,
    S3FSConfig,
    S3FSConstructorKwargs,
)
from arraylake.types import S3Credentials

if TYPE_CHECKING:
    from types_aiobotocore_s3 import S3Client


logger = get_logger(__name__)


# This is copied from fsspec
# https://github.com/fsspec/s3fs/blob/34a32198188164fd48d4d1abcb267f033d1d1ce1/s3fs/core.py#L63
S3_RETRYABLE_ERRORS = (
    socket.timeout,
    botocore.exceptions.HTTPClientError,
    urllib3.exceptions.IncompleteRead,
    botocore.parsers.ResponseParserError,
    aiohttp.ClientPayloadError,
    botocore.exceptions.ClientError,
)


# Below we set up a global cache for aiobotocore clients
# There should be one per each event loop and set of configuration parameters
# dicts aren't hashable, so we sort the keywords into key / value pairs
@dataclass(eq=True, frozen=True)
class ClientKey:
    loop: asyncio.AbstractEventLoop
    anon: bool
    client_kwargs: tuple[tuple[str, Union[str, bool]], ...]
    extra_cache_key: tuple[Any, ...]


_LOCK = asyncio.Lock()


# tried making these weakref.WeakValueDictionary(), but they were getting garbage collected too early
# TODO: investigate whether use of weakref would be more efficient here
# As is, the clients are cleaned up at the end of the python interpreter session.
_GLOBAL_CLIENTS: LRUCache[ClientKey, "S3Client"] = LRUCache(maxsize=32)

# this is a cache to use hold asyncio tasks so they are not garbage collected before finishing
background_tasks: set[asyncio.Task] = set()


async def get_client(
    loop: asyncio.AbstractEventLoop,
    constructor_kwargs: S3FSConstructorKwargs,
    fetch_credentials_func: Optional[Callable[..., S3Credentials]] = None,
    cache_key: tuple[Any, ...] = (),
) -> "S3Client":
    """
    Attempt to get an aws client for a specific event loop and set of parameters.
    If the client already exists, the global cache will be used.
    If not, a new client will be created.
    """
    client_kws = constructor_kwargs["client_kwargs"]
    anon = constructor_kwargs["anon"]
    key = ClientKey(loop, anon, tuple(sorted(client_kws.items())), tuple(sorted(cache_key)))
    async with _LOCK:
        logger.debug("%d s3 clients present in cache.", len(_GLOBAL_CLIENTS))
        if _GLOBAL_CLIENTS.get(key) is None:
            logger.debug("Creating new s3 client %s. Loop id %s.", key, id(loop))
            boto_client_kws: dict[str, Any] = client_kws.copy()
            if anon:
                boto_client_kws["config"] = AioConfig(signature_version=UNSIGNED)
            if fetch_credentials_func is not None:
                # Set up auto-refreshing credential provider for delegated credentials
                # The AutoRefreshingCredentialProvider handles refreshing credentials when they expire or are about to expire
                provider = AutoRefreshingCredentialProvider(fetch_credentials_func)
                # The load method checks and refreshes the credentials as needed,
                # using the function provided to AutoRefreshingCredentialProvider
                refreshable_credentials = await provider.load()
                # Initialize aiobotocore session with the custom credential provider
                session = aiobotocore.session.get_session()
                session._credentials = refreshable_credentials
                autorefresh_session = Session(botocore_session=session)
                client_creator: "S3Client" = autorefresh_session.client("s3", **boto_client_kws)
            else:
                session = aiobotocore.session.get_session()
                client_creator: "S3Client" = session.create_client("s3", **boto_client_kws)  # type: ignore

            new_client = await client_creator.__aenter__()
            weakref.finalize(new_client, close_client, key)
            _GLOBAL_CLIENTS.update({key: new_client})
        else:
            logger.debug("S3 client %s already present. Loop id %s.", key, id(loop))
    client = _GLOBAL_CLIENTS.get(key)
    if client is None:
        raise RuntimeError("Client was not created.")
    return client


def close_client(key: ClientKey) -> None:
    """
    This is a finalizer function that is called when a global client is
    garbage collected. It cleanly closes the client for the specified key.

    If the event loop associated with this client is already closed, we can't
    call __aexit__. So we attempt to directly close the TCP Socket associated
    with the aiohttp session.

    If the event loop associated with this client is determined to be the
    dedicated io loop, we call `sync` to on __aexit__.

    If the event loop associated with this client is determined to be the currently
    running event loop, we schedule the __aexit__ coroutine for execution.

    If the event loop doesn't match any of these scenarios, we have no way to call
    the closer function and issue a RuntimeWarning

    Note: logging in this function runs the risk of conflicting with pytest#5502. For
    this reason, we have removed debug log statements.
    """
    client = _GLOBAL_CLIENTS.pop(key, None)

    client_loop = key.loop  # the loop this client was created from

    if not hasattr(client, "_endpoint"):
        return  # this makes mypy happy

    # this is the underlying thing we have to close
    if client is None:
        return  # this makes mypy happy
    elif hasattr(client._endpoint.http_session, "_session"):
        aio_http_session = client._endpoint.http_session._session
    elif hasattr(client._endpoint.http_session, "_sessions"):
        # aiobotocore 2.12.1 and later
        if not client._endpoint.http_session._sessions:
            return
        if len(client._endpoint.http_session._sessions) > 1:
            logger.warn("More than one aiohttp session present.")
        key = next(iter(client._endpoint.http_session._sessions))
        aio_http_session = client._endpoint.http_session._sessions[key]
    else:
        return  # this makes mypy happy
    # sanity checks
    # assert aio_http_session._loop is client_loop
    # assert aio_http_session._connector._loop is client_loop

    if aio_http_session.closed:
        return

    sync_loop = get_loop()  # the loop associated with the synchronizer thread

    try:
        running_loop = asyncio.get_running_loop()
    except RuntimeError:
        running_loop = None

    if client_loop.is_closed():
        # we can never talk to this client again because its loop is closed;
        # just close the sockets directly
        aio_http_session._connector._close()
        assert aio_http_session.closed
    else:
        # client loop is still open -- how can we talk to it?
        if client_loop is sync_loop:
            sync(close_async_context, client, "calling from sync", timeout=1)
        elif client_loop is running_loop:
            coro = close_async_context(client, f"closing from loop {id(client_loop)}")
            if client_loop.is_running():
                task = client_loop.create_task(coro)
                # try to prevent this task from being garbage collected before it finishes
                background_tasks.add(task)
            else:
                client_loop.run_until_complete(coro)


class S3ObjectStore(ObjectStore):
    _bucket_name: str
    constructor_kwargs: S3FSConstructorKwargs

    def __init__(
        self,
        bucket_name: str,
        kwargs: GenericObjectStoreKwargs,
        fetch_credentials_func: Optional[Callable[..., S3Credentials]] = None,
        cache_key: tuple[Any, ...] = (),
    ):
        self._bucket_name = bucket_name.strip("/")
        self._fetch_credentials_func = fetch_credentials_func
        self._cache_key = cache_key
        # this parses `anon` into a special field
        self.constructor_kwargs = GenericObjectStoreKwargs_to_S3FSConstructorKwargs(kwargs)

    @property
    def bucket_name(self) -> str:
        return self._bucket_name

    def __getstate__(self):
        return self._bucket_name, self._fetch_credentials_func, self._cache_key, self.constructor_kwargs

    def __setstate__(self, state):
        self._bucket_name, self._fetch_credentials_func, self._cache_key, self.constructor_kwargs = state

    async def get_session_client(self) -> "S3Client":
        loop = asyncio.get_running_loop()
        return await get_client(loop, self.constructor_kwargs, self._fetch_credentials_func, self._cache_key)

    def make_uri(self, key: str) -> str:
        return f"s3://{self.bucket_name}/{key}"

    @property
    def status(self) -> Literal["OPEN", "CLOSED"]:
        return "OPEN"

    async def ping(self):
        """Check if the chunk store bucket exists."""
        client = await self.get_session_client()
        await client.head_bucket(Bucket=self.bucket_name)

    @retry_on_exception(S3_RETRYABLE_ERRORS, n=20)
    async def put_data(self, *, data: bytes, key: str) -> None:
        client = await self.get_session_client()
        resp = await client.put_object(Bucket=self.bucket_name, Key=key, Body=data)
        await logger.adebug("put_data received response: %s", resp)

    @retry_on_exception(S3_RETRYABLE_ERRORS, n=5)
    async def pull_data(self, start_byte: int, length: int, key: str, bucket: str) -> bytes:
        client = await self.get_session_client()
        # stop_byte is inclusive, in contrast to python indexing conventions
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Range
        stop_byte = start_byte + length - 1
        byte_range = f"bytes={start_byte}-{stop_byte}"
        try:
            response = await client.get_object(Bucket=bucket, Key=key, Range=byte_range)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise ExpectedChunkNotFoundError(key) from e
            else:
                raise e
        await logger.adebug("pull_data received response: %s", response)
        async with response["Body"] as stream:
            data = await stream.read()
        return data

    @property
    async def is_anonymous_session(self) -> bool:
        client = await self.get_session_client()
        # TODO: Does _client_config always exist
        assert hasattr(client, "_client_config"), "session client does not have _client_config"
        return client._client_config.signature_version == botocore.UNSIGNED

    def __repr__(self):
        disp = f"{type(self).__name__}, bucket: {self.bucket_name}, "
        disp += f", constructor_kwargs: {self.constructor_kwargs}"
        return disp

    def _get_fs_config(self) -> S3FSConfig:
        import fsspec

        fs = fsspec.get_filesystem_class("s3")(**self.constructor_kwargs)
        return S3FSConfig(
            fs=fs,
            constructor_kwargs=self.constructor_kwargs,
        )
