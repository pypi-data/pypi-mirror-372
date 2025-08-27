import asyncio
from typing import Any, Callable, Literal, Optional

import fsspec
from fsspec import AbstractFileSystem

from arraylake.exceptions import ExpectedChunkNotFoundError
from arraylake.log_util import get_logger
from arraylake.repos.v1.chunkstore.abc import ObjectStore
from arraylake.repos.v1.chunkstore.fsspec_compat import (
    FSSpecConstructorKwargs,
    GCSFSConfig,
    GCSFSConstructorKwargs,
    GenericObjectStoreKwargs,
    GenericObjectStoreKwargs_to_S3FSConstructorKwargs,
    Platform,
    S3FSConfig,
    S3FSConstructorKwargs,
)
from arraylake.types import S3Credentials

logger = get_logger(__name__)


class FSSpecObjectStore(ObjectStore):
    _OPEN: bool
    _fs: Optional[AbstractFileSystem]
    _bucket_name: str
    protocol: Literal["gs", "s3"]

    def __init__(self, bucket_name: str, constructor_kwargs: FSSpecConstructorKwargs, platform: Platform):
        self._bucket_name = bucket_name
        # for the filesystem constructor
        self.constructor_kwargs = constructor_kwargs
        if platform == Platform.S3:
            self.protocol = "s3"
        elif platform == Platform.GS:
            self.protocol = "gs"
        self._fs = None

    @property
    def bucket_name(self) -> str:
        return self._bucket_name

    async def _open(self):
        """
        We need to do something to actually open a session.
        This is important. We need to create the connection in the current loop.
        Otherwise all hell breaks loose. This also means we need to call ._open() on
        every op.
        """
        loop = asyncio.get_running_loop()
        if self._fs is None:
            self._fs = fsspec.get_filesystem_class(self.protocol)(loop=loop, **self.constructor_kwargs)
        assert self._fs.loop is loop

    def __getstate__(self):
        return self._bucket_name, self.protocol, self.constructor_kwargs

    def __setstate__(self, state):
        self._bucket_name, self.protocol, self.constructor_kwargs = state
        # TODO: figure out how to pickle *async* fsspec filesystem objects
        # TypeError: no default __reduce__ due to non-trivial __cinit__
        self._fs = None

    def make_uri(self, key: str):
        return f"{self.protocol}://{self.bucket_name}/{key}"

    @property
    def status(self) -> Literal["OPEN", "CLOSED"]:
        raise NotImplementedError

    async def ping(self):
        raise NotImplementedError

    async def pull_data(self, start_byte: int, length: int, key: str, bucket: str) -> bytes:
        await self._open()
        assert self._fs is not None  # for mypy
        # stop_byte is inclusive, in contrast to python indexing conventions
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Range
        stop_byte = start_byte + length  # - 1
        try:
            data = await self._fs._cat_file(f"{bucket}/{key}", start=start_byte, end=stop_byte)
        except FileNotFoundError as e:
            raise ExpectedChunkNotFoundError(key) from e
        return data

    async def put_data(self, *, data: bytes, key: str) -> None:
        await self._open()
        assert self._fs is not None  # for mypy
        resp = await self._fs._pipe_file(path=f"{self.bucket_name}/{key}", data=data)
        await logger.adebug("put_data received response: %s", resp)

    @property
    async def is_anonymous_session(self):
        raise NotImplementedError


class S3FSObjectStore(FSSpecObjectStore):
    constructor_kwargs: S3FSConstructorKwargs

    """This is a reference implementation."""

    def __init__(self, bucket_name: str, kwargs: GenericObjectStoreKwargs):
        constructor_kws = GenericObjectStoreKwargs_to_S3FSConstructorKwargs(kwargs)
        super().__init__(bucket_name=bucket_name, constructor_kwargs=constructor_kws, platform=Platform.S3)

    async def _open(self):
        await super()._open()
        assert self._fs is not None
        # s3fs interface is not consistent with gcsfs (╯°益°)╯彡┻━┻
        await self._fs.set_session()
        assert self._fs._s3 is not None

    async def ping(self):
        """Check if the chunk store bucket exists."""
        await self._open()
        assert self._fs is not None
        # TODO: Should raise an exception if the bucket does not exist
        await self._fs._s3.head_bucket(Bucket=self.bucket_name)

    @property
    async def is_anonymous_session(self) -> bool:
        self._open()
        assert self._fs is not None
        return self._fs._s3.anon is True

    @property
    def status(self) -> Literal["OPEN", "CLOSED"]:
        return "OPEN" if self._fs is not None and self._fs._s3 is not None else "CLOSED"

    def __repr__(self):
        status = self.status
        disp = f"{type(self).__name__}, bucket: {self.bucket_name}, status: {status}"
        if status == "OPEN":
            assert self._fs is not None
            disp += f", endpoint: {self._fs._s3._endpoint}, anonymous?: {self._fs.anon}"
        return disp

    def _get_fs_config(self) -> S3FSConfig:
        fs = fsspec.get_filesystem_class(self.protocol)(**self.constructor_kwargs)
        return S3FSConfig(
            fs=fs,
            constructor_kwargs=self.constructor_kwargs,
        )


class GCSFSObjectStore(FSSpecObjectStore):
    constructor_kwargs: GCSFSConstructorKwargs

    def __init__(
        self,
        bucket_name: str,
        kwargs: GCSFSConstructorKwargs,
        fetch_credentials_func: Optional[Callable[..., S3Credentials]] = None,
        cache_key: tuple[Any, ...] = (),
    ):
        if fetch_credentials_func is not None:
            raise ValueError("fetch_credentials_func is not supported for GCSFSObjectStore")
        if cache_key:
            raise ValueError("cache_key is not supported for GCSFSObjectStore")
        super().__init__(bucket_name=bucket_name, constructor_kwargs=kwargs, platform=Platform.GS)

    @property
    def status(self) -> Literal["OPEN", "CLOSED"]:
        return "OPEN" if self._fs is not None and self._fs._session is not None else "CLOSED"

    async def _open(self):
        await super()._open()
        assert self._fs is not None
        # s3fs interface is not consistent with gcsfs (╯°益°)╯彡┻━┻
        await self._fs._set_session()
        assert self._fs._session is not None

    async def ping(self):
        """Check if the chunk store bucket exists."""
        await self._open()
        assert self._fs is not None
        assert await self._fs._exists(self.bucket_name)

    def __repr__(self):
        status = self.status
        disp = f"{type(self).__name__}, bucket: {self.bucket_name}, status: {status}"
        if status == "OPEN":
            assert self._fs is not None
            disp += f", endpoint: {self._fs._endpoint}, auth_method: {self._fs.credentials.method!r}"
        return disp

    @property
    async def is_anonymous_session(self) -> bool:
        await self._open()
        assert self._fs is not None
        credentials = self._fs.credentials
        return credentials.method == "anon"

    def _get_fs_config(self) -> GCSFSConfig:
        fs = fsspec.get_filesystem_class(self.protocol)(**self.constructor_kwargs)
        return GCSFSConfig(
            fs=fs,
            constructor_kwargs=GCSFSConstructorKwargs(self.constructor_kwargs),
        )
