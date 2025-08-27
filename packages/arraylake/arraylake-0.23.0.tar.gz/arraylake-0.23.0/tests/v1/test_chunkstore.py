import asyncio
import math
import pickle
import socket
from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse
from uuid import uuid4

import aiobotocore
import aiohttp
import botocore
import fsspec
import pytest
import urllib3
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from hypothesis.extra import numpy as np_st

from arraylake.asyn import get_loop
from arraylake.config import config
from arraylake.repos.v1.chunkstore import (
    DEFAULT_STORES,
    GCSFSObjectStore,
    S3ObjectStore,
    mk_chunkstore_from_bucket_config,
    mk_chunkstore_from_uri,
    s3chunkstore,
)
from arraylake.repos.v1.chunkstore.base_chunkstore import (
    MAX_INLINE_THRESHOLD_BYTES,
    HashValidationError,
    InlineTooLongError,
    decode_inline_data,
    encode_inline_data,
    get_hasher,
    tokenize,
)
from arraylake.repos.v1.types import (
    ChunkHash,
    ChunkstoreSchemaVersion,
    ReferenceData,
    SessionID,
)
from arraylake.types import DBID, Bucket

repo_id = DBID(b"some_repo_id")

# We cannot simply import these from s3chunkstore becasue we need to initialize
# them with needed kwargs.
S3_RETRYABLE_ERRORS = (
    socket.timeout,
    botocore.exceptions.HTTPClientError(error="500"),
    urllib3.exceptions.IncompleteRead(10, 20),
    botocore.parsers.ResponseParserError,
    aiohttp.ClientPayloadError,
)


def make_mock_response(name: str, data) -> MagicMock:
    from aiobotocore.response import StreamingBody

    mock = MagicMock(name=name, spec=StreamingBody)
    mock.close = MagicMock()  # For fsspec
    mock.read.return_value = data
    return mock


@pytest.fixture(
    params=[ChunkstoreSchemaVersion.V0, ChunkstoreSchemaVersion.V1],
    ids=["V0", "V1"],
)
def cstore(request, object_store_url_and_kwargs):
    object_store_type, url, chunkstore_kws = object_store_url_and_kwargs
    if request.param == ChunkstoreSchemaVersion.V0:
        return mk_chunkstore_from_uri(url, object_store=object_store_type, inline_threshold_bytes=0, **chunkstore_kws)
    elif request.param == ChunkstoreSchemaVersion.V1:
        parsed_uri = urlparse(url)
        bucket_name = parsed_uri.netloc
        extra_config = {**chunkstore_kws}
        bucket = Bucket(
            id=uuid4(),
            nickname="test",
            platform="gs" if parsed_uri.scheme == "gs" else "minio",
            name=bucket_name,
            prefix="some-prefix",
            extra_config=extra_config,
        )
        return mk_chunkstore_from_bucket_config(bucket=bucket, repo_id=repo_id)
    else:
        assert False


@pytest.fixture()
def cstore_with_inline(object_store_url_and_kwargs):
    object_store_type, url, chunkstore_kws = object_store_url_and_kwargs
    return mk_chunkstore_from_uri(url, inline_threshold_bytes=8, object_store=object_store_type, **chunkstore_kws)


@pytest.mark.asyncio
@pytest.mark.add_object_store("gs")
async def test_chunkstore_repr(cstore):
    repr(cstore)
    repr(cstore.object_store)


@pytest.mark.parametrize("uri,bucket,prefix", [("s3://foo", "foo", ""), ("s3://foo/bar", "foo", "bar")])
def test_chunkstore_init_uri(uri, bucket, prefix, object_store_type):
    cstore = mk_chunkstore_from_uri(uri, object_store=object_store_type)
    assert cstore.bucket_name == bucket
    assert cstore.prefix == prefix
    assert cstore.schema_version == ChunkstoreSchemaVersion.V0


@pytest.mark.parametrize("platform", ["s3", "gs"])
def test_chunkstore_init_bucket(platform):
    bucket_id = uuid4()
    repo_id = DBID(b"hello")
    bucket = Bucket(
        id=bucket_id,
        nickname="nickname",
        platform=platform,
        name="the-bucket",
        prefix="the-prefix",
        extra_config={"foo": "bar", "endpoint_url": "https://example.com"},
    )
    cstore = mk_chunkstore_from_bucket_config(bucket, repo_id, inline_threshold_bytes=5, bar=42)
    assert isinstance(cstore.object_store, DEFAULT_STORES[platform])
    assert cstore.bucket_name == "the-bucket"
    assert cstore.prefix == f"the-prefix/{repo_id.hex()}"
    assert cstore.schema_version == ChunkstoreSchemaVersion.V1
    assert cstore.inline_threshold_bytes == 5
    client_kws = {"foo": "bar", "bar": 42, "endpoint_url": "https://example.com"}
    # S3 and GCS have to handle config differently
    if platform == "s3":
        expected = {"anon": False, "client_kwargs": client_kws}
    else:
        expected = client_kws
    assert cstore.object_store.constructor_kwargs == expected


@pytest.mark.asyncio
async def test_chunkstore_anon_config(object_store_type):
    if "s3" in object_store_type.__name__.lower():
        cstore = mk_chunkstore_from_uri("s3://foo", anon=True, object_store=object_store_type)
    else:
        cstore = mk_chunkstore_from_uri("gs://arraylake-test", token="anon", object_store=object_store_type)
    assert await cstore.object_store.is_anonymous_session


@pytest.mark.parametrize("uri", ["", "/foo", "https://foo", "gcs://foo", "s3:/foo"])
def test_chunkstore_init_parse_uri_raises(uri, object_store_type):
    if uri is None:
        with pytest.raises(ValueError, match=rf"Chunkstore uri is None. Please set your using"):
            mk_chunkstore_from_uri(uri, object_store=object_store_type, client_kws={})
    else:
        with pytest.raises(ValueError, match=rf"Cannot parse chunkstore uri {uri}.*"):
            mk_chunkstore_from_uri(uri, object_store=object_store_type, client_kws={})


def test_chunkstore_init_raises_for_too_large_inline_threshold(object_store_url_and_kwargs):
    object_store_type, url, chunkstore_kws = object_store_url_and_kwargs
    with pytest.raises(ValueError, match=r"Inline chunk threshold too large, max="):
        mk_chunkstore_from_uri(url, object_store=object_store_type, inline_threshold_bytes=1e6, **chunkstore_kws)


@pytest.mark.add_object_store("gs")
def test_chunkstore_serialization(cstore):
    serialized = pickle.dumps(cstore)
    pickle.loads(serialized)


async def test_relative_chunkstore_with_virtual_array():
    """We check if relative chunkstores can read virtual datasets"""
    bucket_id = uuid4()
    repo_id = DBID(b"hello")  # fixme
    bucket = Bucket(id=bucket_id, nickname="test", platform="minio", name="the-bucket", extra_config={"use_ssl": False})
    cstore = mk_chunkstore_from_bucket_config(bucket, repo_id, inline_threshold_bytes=0)
    virtual_ref = ReferenceData.new_virtual(
        for_version=ChunkstoreSchemaVersion.V1, uri="s3://some-other-bucket/some/prefix/foo.nc", offset=42, length=500, sid=SessionID("abc")
    )

    with patch("aiobotocore.client.AioBaseClient._make_api_call") as mock_method:
        # Mock the Body of response from S3's GetObject.
        read_mock = make_mock_response(name="ReadMock", data="foo")
        # Mock the get_object method
        mock_method.return_value = {"Body": read_mock}
        await cstore.get_chunk(virtual_ref)
        assert mock_method.call_count == 1
        mock_method.assert_called_with("GetObject", {"Bucket": "some-other-bucket", "Key": "some/prefix/foo.nc", "Range": "bytes=42-541"})


@pytest.mark.parametrize("method,length", [("hashlib.md5", 32), ("hashlib.sha256", 64), ("xxhash.xxh128", 32)])
def test_chunk_tokenize(method, length):
    if "xxhash" in method:
        pytest.importorskip("xxhash")

    data = b"\x00\x01\x02"

    hasher = get_hasher(method)
    digest = tokenize(data, hasher=hasher)
    assert isinstance(digest, str)
    assert len(digest) == length


@pytest.mark.asyncio
async def test_raises_invalid_hash_method(cstore):
    data = b"\x00\x01\x02"
    with pytest.raises(ValueError):
        await cstore.add_chunk(data, session_id=SessionID("abc"), hash_method="foo")

    with pytest.raises(ValueError):
        await cstore.add_chunk(data, session_id=SessionID("abc"), hash_method="foo.bar")


@pytest.mark.asyncio
@pytest.mark.add_object_store("gs")
async def test_chunkstore_roundtrip(cstore):
    data = b"\x00\x01\x02"
    chunk_ref = await cstore.add_chunk(data, session_id=SessionID("abc"))
    assert chunk_ref.length == len(data)
    assert chunk_ref.offset == 0
    if cstore.schema_version == ChunkstoreSchemaVersion.V0:
        assert chunk_ref.v is None or chunk_ref.v == ChunkstoreSchemaVersion.V0
        assert chunk_ref.sid == None
    else:
        assert chunk_ref.v == ChunkstoreSchemaVersion.V1
        assert chunk_ref.sid == SessionID("abc")

    actual = await cstore.get_chunk(chunk_ref, validate=True)
    assert actual == data

    # with hash_method
    chunk_ref = await cstore.add_chunk(data, session_id=SessionID("abc"), hash_method="hashlib.md5")
    actual = await cstore.get_chunk(chunk_ref, validate=True)
    assert actual == data

    # with hash_method in config
    with config.set({"chunkstore.hash_method": "hashlib.md5"}):
        chunk_ref = await cstore.add_chunk(data, session_id=SessionID("abc"))
    assert chunk_ref.hash["method"] == "hashlib.md5"
    actual = await cstore.get_chunk(chunk_ref, validate=True)
    assert actual == data

    if cstore.schema_version == ChunkstoreSchemaVersion.V0:
        # raise when token != hash
        # we cannot change the token for relative chunkstores because that changes the key
        chunk_ref.hash["token"] = "123456foobar"
        with pytest.raises(HashValidationError):
            actual = await cstore.get_chunk(chunk_ref, validate=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("exception", S3_RETRYABLE_ERRORS)
async def test_chunkstore_retries(cstore, exception):
    data = b"\x00\x01\x02"
    # bizarrely, this is enough for add_chunk
    write_mock = make_mock_response(name="WriteMock", data=None)
    with patch("aiobotocore.client.AioBaseClient._make_api_call") as mock_method:
        mock_method.side_effect = [exception, {"Body": write_mock}]
        chunk_ref = await cstore.add_chunk(data, session_id=SessionID("abc"))
        assert mock_method.call_count == 2

    read_mock = make_mock_response(name="ReadMock", data=data)
    # necessary otherwise a new mock is created for the context.
    # We do not control the return value then.
    # I guess we could patch the mock, but this works.
    read_mock.__aenter__.return_value = read_mock
    with patch("aiobotocore.client.AioBaseClient._make_api_call") as mock_method:
        mock_method.side_effect = [exception, {"Body": read_mock}]
        actual = await cstore.get_chunk(chunk_ref)
        assert mock_method.call_count == 2
        # make sure mocks are working as expected
        read_mock.read.assert_awaited_once()
        assert actual == data


@pytest.mark.asyncio
async def test_chunkstore_key_cache(cstore):
    with patch("arraylake.repos.v1.chunkstore." + cstore.object_store.put_data.__qualname__) as mock_method:
        with config.set({"chunkstore.inline_threshold_bytes": 0}):
            data = b"\x00\x01\x02"
            chunk_ref1 = await cstore.add_chunk(data, session_id=SessionID("abc"))
            assert chunk_ref1.length == len(data)
            assert chunk_ref1.offset == 0

            assert mock_method.call_count == 1
            key = f"{cstore.prefix}/chunks/{chunk_ref1.hash['token']}.{chunk_ref1.sid}"
            if cstore.schema_version == ChunkstoreSchemaVersion.V0:
                key = f"{chunk_ref1.hash['token']}"
            mock_method.assert_called_with(key=key, data=data)

            # write the same chunk again, this should be a noop on the s3 side
            chunk_ref2 = await cstore.add_chunk(data, session_id=SessionID("abc"))
            assert chunk_ref2 == chunk_ref1
            assert mock_method.call_count == 1

            data3 = b"\x00\x01\x02\x03"
            chunk_ref3 = await cstore.add_chunk(data3, session_id=SessionID("abc"))
            assert chunk_ref3.length == len(data3)
            assert chunk_ref3.offset == 0

            key = f"{cstore.prefix}/chunks/{chunk_ref3.hash['token']}.{chunk_ref3.sid}"
            if cstore.schema_version == ChunkstoreSchemaVersion.V0:
                key = f"{chunk_ref3.hash['token']}"
            mock_method.assert_called_with(key=key, data=data3)
            assert mock_method.call_count == 2


@given(st.binary(max_size=512))
def test_inline_data_roundtrips(data):
    dec = decode_inline_data(data)
    assert dec.startswith("inline://")
    enc = encode_inline_data(dec)
    assert b"inline" not in enc
    assert enc == data


def test_inline_decode_raises():
    data = b'\x02\x01!\x04\xa0\x05\x00\x00\xa0\x05\x00\x00\xcf\x01\x00\x00\x14\x00\x00\x00\x0c\x00\x00\x00\x1f\x00\x01\x00\xffPP\x00\x00\x00\x00\x00\x16\x00\x00\x00\x1f\x00\x01\x00l\x1f\x80\x01\x00l/@\xc0\x02\x00NP\xc0@\xc0@\xc0h\x01\x00\x00\x00\xc0 `\x90\xb0\xd0\xf0\x08\x18(8HXhx\x84\x8c\x94\x9c\xa4\xac\xb4\xbc\xc4\xcc\xd4\xdc\xe4\xec\xf4\xfc\x02\x06\n\x0e\x12\x16\x1a\x1e"&*.26:>BFJNRVZ^bfjnrvz~\x81\x83\x85\x87\x89\x8b\x8d\x8f\x91\x93\x95\x97\x99\x9b\x9d\x9f\xa1\xa3\xa5\xa7\xa9\xab\xad\xaf\xb1\xb3\xb5\xb7\xb9\xbb\xbd\xbf\xc1\xc3\xc5\xc7\xc9\xcb\xcd\xcf\xd1\xd3\xd5\xd7\xd9\xdb\xdd\xdf\xe1\xe3\xe5\xe7\xe9\xeb\xed\xef\xf1\xf3\xf5\xf7\xf9\xfb\xfd\xff\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x80\x81\x81\x82\x82\x83\x83\x84\x84\x85\x85\x86\x86\x87\x87\x88\x88\x89\x89\x8a\x8a\x8b\x8b\x8c\x8c\x8d\x8d\x8e\x8e\x8f\x8f\x90\x90\x91\x91\x92\x92\x93\x93\x94\x94\x95\x95\x96\x96\x97\x97\x98\x98\x99\x99\x9a\x9a\x9b\x9b\x9c\x9c\x9d\x9d\x9e\x9e\x9f\x9f\xa0\xa0\xa1\xa1\xa2\xa2\xa3\xa3\xa4\xa4\xa5\xa5\xa6\xa6\xa7\xa7\xa8\xa8\xa9\xa9\xaa\xaa\xab\xab\xac\xac\xad\xad\xae\xae\xaf\xaf\xb0\xb0\xb1\xb1\xb2\xb2\xb3\xb3!\x00\x00\x00\xdf??@@@@@@AAAAA\x05\x00\x00\x1fB\x01\x00L\x1fC\x01\x00\xcfPCCCCC'
    with pytest.raises(InlineTooLongError):
        decode_inline_data(data)


@pytest.mark.asyncio
async def test_chunkstore_inline_data(cstore_with_inline):
    cstore = cstore_with_inline
    data = b"\x00\x01\x02"
    chunk_ref = await cstore.add_chunk(data, hash_method="hashlib.md5", session_id=SessionID("abc"))
    assert chunk_ref.uri == f"inline://{data.decode()}"
    assert chunk_ref.length == len(data)
    actual = await cstore.get_chunk(chunk_ref, validate=False)
    assert actual == data

    # with validate
    actual = await cstore.get_chunk(chunk_ref, validate=True)
    assert actual == data

    # chunks exceeding inline threshold should go to s3
    data = b"\x00\x01\x02\x02\x02\x02\x02\x02\x02\x02\x02"
    chunk_ref = await cstore.add_chunk(data, hash_method="hashlib.md5", session_id=SessionID("abc"))
    assert chunk_ref.length == len(data)
    if isinstance(cstore_with_inline.object_store, GCSFSObjectStore):
        assert chunk_ref.uri.startswith("gs://")
    else:
        assert chunk_ref.uri.startswith("s3://")


@pytest.mark.asyncio
@given(array=np_st.arrays(np_st.scalar_dtypes(), shape=np_st.array_shapes()))
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.add_object_store("gs")
async def test_chunkstore_hypothesis(array, cstore_with_inline):
    data = array.tobytes()
    cstore = cstore_with_inline
    chunk_ref = await cstore.add_chunk(data, session_id=SessionID("abc"))
    assert chunk_ref.length == len(data)
    assert chunk_ref.offset == 0
    assert chunk_ref.hash["token"] is not None
    if chunk_ref.uri.startswith("inline://"):
        assert chunk_ref.uri != "inline://"
        assert len(chunk_ref.uri) <= MAX_INLINE_THRESHOLD_BYTES + len("inline://")


def test_v0_reference_data_loading():
    uri = "s3://foo"
    offset = 5
    length = 42
    hash = ChunkHash(method="sha256", token="abcdef")
    v = ChunkstoreSchemaVersion.V1
    fields = {
        "uri": uri,
        "offset": offset,
        "length": length,
        "hash": {"method": hash["method"], "token": hash["token"]},
    }
    rd = ReferenceData(**fields)
    assert rd.uri == uri
    assert rd.offset == offset
    assert rd.length == length
    assert rd.hash == hash
    assert rd.v == ChunkstoreSchemaVersion.V0


def test_v1_reference_data_loading():
    uri = None
    offset = 5
    length = 42
    hash = ChunkHash(method="sha256", token="abcdef")
    v = ChunkstoreSchemaVersion.V1
    sid = SessionID("abc")

    fields = {
        "uri": uri,
        "offset": offset,
        "length": length,
        "hash": {"method": hash["method"], "token": hash["token"]},
        "v": v,
        "sid": sid,
    }
    rd = ReferenceData(**fields)
    assert rd.uri == uri
    assert rd.offset == offset
    assert rd.length == length
    assert rd.hash == hash
    assert rd.v == v
    assert rd.sid == sid


schema_version_st = st.sampled_from([ChunkstoreSchemaVersion.V0, ChunkstoreSchemaVersion.V1])
chunk_hash_st = st.builds(lambda method, token: ChunkHash(method=method, token=token), st.text(min_size=1), st.text(min_size=1))


@pytest.mark.asyncio
@given(
    sid=st.uuids(version=4).map(lambda u: str(u)),
    offset=st.integers(min_value=0),
    length=st.integers(min_value=0),
    uri=st.text(min_size=1).map(lambda s: f"s3://{s}"),
    version=schema_version_st,
)
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
async def test_virtual_reference_data_creation(sid, offset, length, uri, version):
    rd = ReferenceData.new_virtual(for_version=version, uri=uri, offset=offset, length=length, sid=sid)
    assert rd.is_virtual()
    parsed = ReferenceData(**dict(rd))
    assert parsed == rd
    assert parsed.v == version
    if version == ChunkstoreSchemaVersion.V1:
        assert parsed.sid == sid
    else:
        assert parsed.sid is None
    assert parsed.length == length
    assert parsed.offset == offset
    assert parsed.hash is None
    assert parsed.uri == uri


@pytest.mark.asyncio
@given(
    sid=st.uuids(version=4).map(lambda u: str(u)),
    length=st.integers(min_value=0),
    hash=chunk_hash_st,
    data=st.text(min_size=1).map(lambda s: f"inline://{s}"),
    version=schema_version_st,
)
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
async def test_inline_reference_data_creation(sid, length, hash, data, version):
    rd = ReferenceData.new_inline(for_version=version, data=data, length=length, hash=hash, sid=sid)
    assert rd.is_inline()
    parsed = ReferenceData(**dict(rd))
    assert parsed == rd
    assert parsed.v == version
    if version == ChunkstoreSchemaVersion.V1:
        assert parsed.sid == sid
    else:
        assert parsed.sid is None
    assert parsed.length == length
    assert parsed.offset == 0
    assert parsed.hash == hash
    assert parsed.uri == data


@pytest.mark.asyncio
@given(
    uri=st.text(min_size=1).map(lambda s: f"s3://{s}"),
    length=st.integers(min_value=0),
    hash=chunk_hash_st,
)
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
async def test_materialized_v0_reference_data_creation(uri, length, hash):
    rd = ReferenceData.new_materialized_v0(uri=uri, length=length, hash=hash)
    assert rd.is_materialized()
    parsed = ReferenceData(**dict(rd))
    assert parsed == rd
    assert parsed.v == ChunkstoreSchemaVersion.V0
    assert parsed.sid is None
    assert parsed.length == length
    assert parsed.offset == 0
    assert parsed.hash == hash
    assert parsed.uri == uri


@pytest.mark.asyncio
@given(
    length=st.integers(min_value=0),
    hash=chunk_hash_st,
    sid=st.uuids(version=4).map(lambda u: str(u)),
)
@settings(deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
async def test_materialized_v1_reference_data_creation(length, hash, sid):
    rd = ReferenceData.new_materialized_v1(sid=sid, length=length, hash=hash)
    assert rd.is_materialized()
    parsed = ReferenceData(**dict(rd))
    assert parsed == rd
    assert parsed.v == ChunkstoreSchemaVersion.V1
    assert parsed.sid == sid
    assert parsed.length == length
    assert parsed.offset == 0
    assert parsed.hash == hash
    assert parsed.uri is None


@pytest.mark.asyncio
@pytest.mark.add_object_store("gs")
async def test_fsspec_object_store_resuses_fs_instance(cstore):
    object_store = cstore.object_store
    if isinstance(object_store, S3ObjectStore):
        pytest.skip()

    assert object_store._fs is None
    await object_store._open()
    fsid = id(object_store._fs)
    # forcefully invalidate the cache
    object_store._fs = None
    await object_store._open()
    assert id(object_store._fs) == fsid


@pytest.mark.add_object_store("gs")
def test_chunk_store_get_fsconfig(object_store_platform, cstore):
    fs_config = cstore._get_fs_config()
    assert isinstance(fs_config.fs, fsspec.AbstractFileSystem)
    assert fs_config.constructor_kwargs == cstore.object_store.constructor_kwargs
    assert fs_config.protocol == object_store_platform


@pytest.mark.asyncio
async def test_s3chunkstore_client_lifecycle():
    loop = get_loop()
    constructor_kwargs = {"anon": False, "client_kwargs": {}}
    client = await s3chunkstore.get_client(loop, constructor_kwargs)
    assert hasattr(client, "_endpoint")
    key = s3chunkstore.ClientKey(loop, False, tuple({}), tuple())
    assert s3chunkstore._GLOBAL_CLIENTS.get(key) is not None

    s3chunkstore.close_client(key)
    assert s3chunkstore._GLOBAL_CLIENTS.get(key) is None


def test_S3ObjectStore_multiple_loops(cstore):
    object_store = cstore.object_store
    assert isinstance(object_store, S3ObjectStore)
    loop1 = asyncio.new_event_loop()
    loop2 = asyncio.new_event_loop()

    loop1.run_until_complete(object_store.ping())
    loop1.close()
    loop2.run_until_complete(object_store.ping())
    loop2.close()


def test_S3ObjectStore_multiple_loops(cstore):
    object_store = cstore.object_store
    assert isinstance(object_store, S3ObjectStore)
    loop1 = asyncio.new_event_loop()
    loop2 = asyncio.new_event_loop()

    loop1.run_until_complete(object_store.ping())
    loop1.close()
    loop2.run_until_complete(object_store.ping())
    loop2.close()


@settings(
    # It is fine to not reset the chunkstore fixture here.
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None,
)
@given(data=st.binary(min_size=1, max_size=200), max_request_size=st.none() | st.integers(min_value=0))
@pytest.mark.asyncio
async def test_get_chunk_split(cstore, data, max_request_size):
    nbytes = len(data)
    expected_chunks = 1 if max_request_size in [None, 0] else int(math.ceil(nbytes / max_request_size))

    with config.set({"chunkstore.inline_threshold_bytes": 0}):
        chunk_ref = await cstore.add_chunk(data, session_id=SessionID("abc"))

    # now check the splitting is happening correctly by patching the object store
    with patch.object(
        type(cstore.object_store),
        "pull_data",
        side_effect=type(cstore.object_store).pull_data,
        autospec=True,
    ) as mock_method:
        with config.set({"chunkstore.max_request_size": max_request_size}):
            actual = await cstore.get_chunk(chunk_ref, validate=True)
            assert actual == data
            assert mock_method.call_count == expected_chunks


@pytest.mark.parametrize(
    "num_chunks,chunk_spacing,coalesce_size,expected_requests",
    [
        (2, 10, None, 1),  # default will coalesce
        (2, 10, 20, 1),  # will coalesce
        (2, 10, 5, 2),  # won't coalesce
    ],
)
@pytest.mark.add_object_store("gs")
@pytest.mark.asyncio
async def test_get_chunk_coalesce(cstore, num_chunks, chunk_spacing, coalesce_size, expected_requests):
    # need to artificially create a single object with multiple chunks in it (a.k.a. a shard)
    chunk_len = 5
    full_data = bytes(range(2 * chunk_len + chunk_spacing * (num_chunks - 1)))
    raw_chunk_ref = await cstore.add_chunk(full_data, session_id=SessionID("abc"))
    refs = {}
    expected = {}
    for i in range(num_chunks):
        offset = i * (chunk_len + chunk_spacing)
        ref = raw_chunk_ref.model_copy(update=dict(offset=offset, length=chunk_len))
        refs[str(i)] = ref
        expected[str(i)] = full_data[offset : offset + chunk_len]

    with patch.object(
        type(cstore.object_store),
        "pull_data",
        side_effect=type(cstore.object_store).pull_data,
        autospec=True,
    ) as mock_method:
        with config.set({"chunkstore.coalesce_size": coalesce_size}):
            actual = await cstore.get_chunks(refs)
        assert actual == expected
        assert mock_method.call_count == expected_requests


@pytest.mark.asyncio
async def test_s3chunkstore_client_creds():
    loop = get_loop()
    client_kwargs = {"aws_access_key_id": "12345678", "aws_secret_access_key": "abcdefgh", "aws_session_token": "a_token_string"}
    constructor_kwargs = {"anon": False, "client_kwargs": client_kwargs}
    client = await s3chunkstore.get_client(loop, constructor_kwargs)
    assert client._request_signer._credentials.access_key == client_kwargs["aws_access_key_id"]
    assert client._request_signer._credentials.secret_key == client_kwargs["aws_secret_access_key"]
    assert client._request_signer._credentials.token == client_kwargs["aws_session_token"]


def test_chunkstore_init_bucket_cred_conflicts_s3(object_store_url_and_kwargs):
    _, url, chunkstore_kws = object_store_url_and_kwargs
    client_kwargs = {"aws_access_key_id": "12345678", "aws_secret_access_key": "abcdefgh", "aws_session_token": "a_token_string"}
    chunkstore_kws["aws_access_key_id"] = "87654321"

    parsed_uri = urlparse(url)
    bucket_name = parsed_uri.netloc
    extra_config = {**chunkstore_kws}
    bucket = Bucket(
        id=uuid4(),
        nickname="test",
        platform="s3",
        name=bucket_name,
        prefix="some-prefix",
        extra_config=extra_config,
    )
    cstore = mk_chunkstore_from_bucket_config(bucket=bucket, repo_id=repo_id, **client_kwargs)

    cstore_client_kwargs = cstore.object_store.constructor_kwargs["client_kwargs"]
    assert cstore_client_kwargs["aws_access_key_id"] == chunkstore_kws["aws_access_key_id"]
    assert cstore_client_kwargs["aws_secret_access_key"] == client_kwargs["aws_secret_access_key"]
    assert cstore_client_kwargs["aws_session_token"] == client_kwargs["aws_session_token"]
