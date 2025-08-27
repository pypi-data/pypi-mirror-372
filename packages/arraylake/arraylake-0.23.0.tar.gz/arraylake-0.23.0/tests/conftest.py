import asyncio
import contextlib
import importlib
import json
import logging
import os
import pathlib
import random
import secrets
import shutil
import string
import time
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, Literal
from unittest import mock
from uuid import UUID, uuid4

import bson
import pytest
import yaml
from packaging.version import Version

from arraylake import AsyncClient, config
from arraylake.api_utils import ArraylakeHttpClient
from arraylake.repos.v1.chunkstore import (
    GCSFSObjectStore,
    S3FSObjectStore,
    S3ObjectStore,
    mk_chunkstore_from_uri,
)
from arraylake.token import TokenHandler
from arraylake.types import (
    DBID,
    ApiTokenInfo,
    Author,
    AuthProviderConfig,
    BucketResponse,
    NewBucket,
    NewRepoOperationStatus,
    OauthTokens,
    RepoOperationMode,
    UserInfo,
)


# this is run automatically at test collection time
def pytest_ignore_collect(collection_path):
    import zarr

    path = collection_path

    if Version(zarr.__version__) < Version("3.0.0.a0"):
        # Exclude tests in the tests/icechunk directory if zarr <v3
        if "tests/icechunk" in str(path):  # TODO: make check more robust
            return True
    else:
        if importlib.util.find_spec("icechunk"):
            # Exclude tests in the tests/v1 directory if zarr is >=v3 and icechunk is installed
            if "tests/v1" in str(path):
                return True
        else:
            # Exclude tests in the tests/v1 and tests/icechunk directories if zarr is >=v3 and icechunk is not installed
            if "tests/icechunk" in str(path) or "tests/v1" in str(path):
                return True


# Configured not to run slow tests by default
# https://stackoverflow.com/questions/52246154/python-using-pytest-to-skip-test-unless-specified
def pytest_configure(config):
    config.addinivalue_line("markers", "runslow: run slow tests")


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
    # https://github.com/pytest-dev/pytest-asyncio/issues/80#issue-308383816
    # without the next line, we get a error about unable to close event loop during test teardown
    asyncio.set_event_loop(None)


@pytest.fixture()
def temp_config_file(tmp_path):
    template_file = pathlib.Path(__file__).resolve().parent / "config.yaml"
    test_file = tmp_path / "config.yaml"
    shutil.copy(template_file, test_file)
    return test_file


@pytest.fixture(autouse=True)
def clean_config():
    template_file = pathlib.Path(__file__).resolve().parent / "config.yaml"
    with template_file.open() as f:
        c = yaml.safe_load(f)
    config.update(c)


@pytest.fixture(scope="function", autouse=True)  # perhaps autouse is too aggressive here?
def test_token_file(tmp_path):
    contents = {
        "access_token": "access-123",
        "id_token": "id-456",
        "refresh_token": "refresh-789",
        "expires_in": 86400,
        "token_type": "Bearer",
    }
    fname = tmp_path / "token.json"

    with fname.open(mode="w") as f:
        json.dump(contents, f)

    with config.set({"service.token_path": str(fname)}):
        yield fname


@pytest.fixture(scope="function")
def test_user():
    return UserInfo(
        id=uuid4(),
        sub=UUID("aeeb8bfa-e8f4-4724-9427-c3d5af66190e"),
        email="abc@earthmover.io",
        first_name="TestFirst",
        family_name="TestFamily",
    )


@pytest.fixture(scope="function")
def test_api_token():
    id = uuid4()
    email = "svc-email@some-earthmover-org.service.earthmover.io"
    return ApiTokenInfo(id=id, client_id=id.hex, email=email, expiration=int(time.time() + 10000))


@pytest.fixture()
def test_token():
    return "ema_token-123456789"


@pytest.fixture(
    params=["machine", "user"],
)
def token(request, test_token, test_token_file):
    if request.param == "machine":
        return test_token
    else:
        return None


def get_platforms_to_test(request):
    platforms = ("s3",)
    mark = request.node.get_closest_marker("add_object_store")
    if mark is not None:
        platforms += mark.args
    return platforms


@pytest.fixture(params=["s3", "gs"], scope="session")
def object_store_platform(request) -> Literal["s3", "gs"]:
    return request.param


@pytest.fixture(scope="session")
def object_store_config(object_store_platform):
    if object_store_platform == "s3":
        config_params = {
            "service.uri": "http://0.0.0.0:8000",
            "chunkstore.uri": "s3://testbucket",
            "s3.endpoint_url": "http://localhost:9000",
        }
    elif object_store_platform == "gs":
        config_params = {
            "service.uri": "http://0.0.0.0:8000",
            "chunkstore.uri": "gs://arraylake-test",
            "gs.endpoint_url": "http://127.0.0.1:4443",
            "gs.token": "anon",
            "gs.project": "test",
        }
    return config_params


@pytest.fixture
def client_config(object_store_platform, object_store_config, request):
    if object_store_platform not in get_platforms_to_test(request):
        pytest.skip()
    with config.set(object_store_config):
        yield


@pytest.fixture
def user():
    return Author(name="Test User", email="foo@icechunk.io")


@pytest.fixture(scope="session", autouse=True)
def aws_config():
    credentials_env = {
        "AWS_ACCESS_KEY_ID": "minio123",
        "AWS_SECRET_ACCESS_KEY": "minio123",
    }
    with mock.patch.dict(os.environ, credentials_env):
        yield


@pytest.fixture(scope="session")
def all_object_store_url_and_kwargs(object_store_platform, object_store_config):
    """DEPRECATED: V1 chunkstore fixture - pending removal.
    V1 repositories are legacy and this fixture will be removed in a future version."""
    chunkstore_uri = object_store_config["chunkstore.uri"]

    if object_store_platform == "s3":
        chunkstore_kws = {"endpoint_url": object_store_config["s3.endpoint_url"]}
        return S3ObjectStore, chunkstore_uri, chunkstore_kws
    # not currently testing s3fs path
    elif object_store_platform == "s3fs":
        raise NotImplementedError
        # return S3FSObjectStore, S3_URL, chunkstore_kws
    elif object_store_platform == "gs":
        chunkstore_kws = {
            "endpoint_url": object_store_config["gs.endpoint_url"],
            "token": object_store_config["gs.token"],
            "project": object_store_config["gs.project"],
        }
        return GCSFSObjectStore, chunkstore_uri, chunkstore_kws


@pytest.fixture
def object_store_url_and_kwargs(all_object_store_url_and_kwargs, object_store_platform, request):
    platforms = get_platforms_to_test(request)
    if object_store_platform not in platforms:
        pytest.skip()
    return all_object_store_url_and_kwargs


@pytest.fixture(params=[True, False], ids=["with_Dask", "no_Dask"])
def use_dask(request):
    return request.param


@pytest.fixture(params=["s3", "gs"])  # can also do "s3fs"
def object_store_type(request):
    if request.param == "s3":
        return S3ObjectStore
    elif request.param == "s3fs":
        return S3FSObjectStore
    elif request.param == "gs":
        return GCSFSObjectStore


# adapted from https://github.com/pangeo-forge/pangeo-forge-recipes/blob/bd90598a7fca03272f811553521dd239b53a31ae/tests/conftest.py#L414
@pytest.fixture
def dask_cluster(event_loop):
    distributed = pytest.importorskip("distributed")

    # asynchronous:
    # Set to True if using this cluster within async/await functions or within Tornado gen.coroutines.
    # This should remain False for normal use.
    cluster = distributed.LocalCluster(n_workers=2, threads_per_worker=1, silence_logs=logging.INFO + 1, asynchronous=False)

    def set_blosc_threads():
        try:
            from numcodecs import blosc

            blosc.use_threads = False
        except ImportError:
            pass

    with cluster.get_client() as client:
        client.run(set_blosc_threads)

    yield cluster

    cluster.close()


@pytest.fixture(scope="function")
def dask_client(dask_cluster, use_dask):
    if use_dask:
        client = dask_cluster.get_client()
        yield client
        client.close()
    else:
        yield contextlib.nullcontext()


@pytest.fixture()
def metastore(metastore_class_and_config):
    MetastoreClass, metastore_config = metastore_class_and_config
    with config.set({"server_managed_sessions": metastore_config.managed_sessions}):
        yield MetastoreClass(metastore_config)


@pytest.fixture()
def chunkstore_bucket(client_config):
    """DEPRECATED: V1 chunkstore fixture - pending removal.
    V1 repositories are legacy and this fixture will be removed in a future version."""
    uri = config.get("chunkstore.uri")
    if uri.startswith("s3"):
        client_kws = config.get("s3", {})
    elif uri.startswith("gs"):
        client_kws = config.get("gs", {})
    cstore = mk_chunkstore_from_uri(uri, **client_kws)
    return cstore


@pytest.fixture
async def org_name(client_config, test_token):
    # This fixture should be used by all client-level tests.
    # It makes things more resilient by making sure there are no repos
    # under the specified org and cleaning up any repos that might be left over.
    # But warning: if there are errors in the list / delete logic, they
    # will show up here first!
    org = "my-org"
    async_client = AsyncClient(token=test_token)
    for repo in await async_client.list_repos(org):
        await async_client.delete_repo(f"{org}/{repo.name}", imsure=True, imreallysure=True)
    yield org
    for repo in await async_client.list_repos(org):
        await async_client.delete_repo(f"{org}/{repo.name}", imsure=True, imreallysure=True)


@pytest.fixture
async def isolated_org_name(client_config, test_token):
    # This fixture should be used by all client-level tests.
    # It makes things more resilient by making sure there are no repos
    # under the specified org and cleaning up any repos that might be left over.
    # But warning: if there are errors in the list / delete logic, they
    # will show up here first!
    org_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    body = {
        "name": org_name,
        "feature_flags": ["v1-write"],
    }
    client = ArraylakeHttpClient("http://localhost:8000", token=test_token)
    resp = await client._request("POST", "/orgs_test_create", content=json.dumps(body))
    yield org_name


@pytest.fixture
def new_bucket_obj():
    return NewBucket(
        org=isolated_org_name,
        nickname="test_bucket",
        platform="minio",
        name="testbucket",
        extra_config={
            "use_ssl": False,
            "endpoint_url": "http://localhost:9000",
        },
        auth_config={"method": "hmac", "access_key_id": "minio123", "secret_access_key": "minio123"},
    )


@pytest.fixture
def new_bucket_obj_with_prefix(new_bucket_obj):
    new_bucket_obj.prefix = "prefix"
    return new_bucket_obj


@pytest.fixture
async def isolated_org_with_bucket(isolated_org_name, new_bucket_obj, test_token):
    # we cannot use async_client.create_bucket_config because it does not support minio as a platform
    client = ArraylakeHttpClient("http://localhost:8000", token=test_token)
    resp = await client._request("POST", f"/orgs/{isolated_org_name}/buckets", content=new_bucket_obj.model_dump_json())
    bucket_id = BucketResponse.model_validate_json(resp.content).id
    yield isolated_org_name, new_bucket_obj.nickname
    await client._request("DELETE", f"/orgs/{isolated_org_name}/buckets/{bucket_id}")


@pytest.fixture
async def isolated_org_with_bucket_with_prefix(isolated_org_name, new_bucket_obj_with_prefix, test_token):
    # we cannot use async_client.create_bucket_config because it does not support minio as a platform
    client = ArraylakeHttpClient("http://localhost:8000", token=test_token)
    resp = await client._request("POST", f"/orgs/{isolated_org_name}/buckets", content=new_bucket_obj_with_prefix.model_dump_json())
    bucket_id = BucketResponse.model_validate_json(resp.content).id
    yield isolated_org_name, new_bucket_obj_with_prefix.nickname
    await client._request("DELETE", f"/orgs/{isolated_org_name}/buckets/{bucket_id}")


@pytest.fixture
async def isolated_org_with_buckets(isolated_org_with_bucket, test_token):
    isolated_org_name, first_bucket_nickname = isolated_org_with_bucket
    async_client = AsyncClient(token=test_token)
    second_bucket_nickname = "another_test_bucket"
    await async_client.create_bucket_config(
        org=isolated_org_name,
        nickname=second_bucket_nickname,
        auth_config={"method": "anonymous"},
        uri="s3://name/prefix",
        extra_config={"use_ssl": False, "endpoint_url": "http://localhost:9000"},
    )
    yield isolated_org_name, first_bucket_nickname, second_bucket_nickname
    async_client.delete_bucket_config(org=isolated_org_name, nickname=second_bucket_nickname, imsure=True, imreallysure=True)


@pytest.fixture
async def isolated_org_with_anon_bucket(isolated_org_name, test_token):
    async_client = AsyncClient(token=test_token)
    bucket_nickname = "anon_bucket"
    await async_client.create_bucket_config(
        org=isolated_org_name,
        nickname=bucket_nickname,
        auth_config={"method": "anonymous"},
        uri="s3://name/prefix",
        extra_config={"region_name": "us-west-2"},
    )
    yield isolated_org_name, bucket_nickname
    async_client.delete_bucket_config(org=isolated_org_name, nickname=bucket_nickname, imsure=True, imreallysure=True)


@pytest.fixture
async def isolated_org_with_delegated_creds_bucket(isolated_org_name, test_token):
    async_client = AsyncClient(token=test_token)
    bucket_nickname = "delegated_creds_bucket"
    await async_client.create_bucket_config(
        org=isolated_org_name,
        nickname=bucket_nickname,
        auth_config={
            "method": "aws_customer_managed_role",
            "external_customer_id": "12345678",
            "external_role_name": "my_external_role",
            "shared_secret": "our-shared-secret",
        },
        uri="s3://name/prefix",
        extra_config={"region_name": "us-west-2"},
    )
    yield isolated_org_name, bucket_nickname
    async_client.delete_bucket_config(org=isolated_org_name, nickname=bucket_nickname, imsure=True, imreallysure=True)


class Helpers:
    """Helper functions for tests.

    This class is made available to tests using the helpers fixture.
    """

    @staticmethod
    def new_random_dbid() -> DBID:
        """Generate a random, 12 bytes database id"""
        return DBID(secrets.token_bytes(12))

    # __func__ is needed here for compatibility with Python < 3.10
    random_dbids: Iterator[DBID] = iter(new_random_dbid.__func__, None)
    """A fresh, infinite stream of random DBIDs"""

    @staticmethod
    def random_repo_id() -> str:
        return str(bson.ObjectId())

    @staticmethod
    def gen_docs(n, prefix="/some/path-") -> Mapping[Path, Mapping[str, Any]]:
        # make the generated items unique in some way
        rdm = str(uuid4())
        return {f"{prefix}{rdm}-{i}.json": {"i": i, "data": rdm} for i in range(n)}

    @staticmethod
    def gen_chunks(n, path="/some/path") -> Mapping[Path, Mapping[str, Any]]:
        # make the generated items unique in some way
        def coords():
            c0 = random.randint(0, 99999)
            c1 = random.randint(0, 99999)
            return f"c{c0}/{c1}"

        path = path.rstrip("/")
        return {f"{path}/{coords()}": {"uri": f"s3://testbucket/{uuid4()}"} for i in range(n)}

    @staticmethod
    def an_id(n: int) -> str:
        return "".join(random.choices(string.hexdigits, k=n))

    @staticmethod
    def oauth_tokens_from_file(file: Path) -> OauthTokens:
        """Utility to read an oauth tokens file"""
        with file.open() as f:
            return OauthTokens.model_validate_json(f.read())

    @staticmethod
    async def isolated_org(token, org_config):
        org_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        org_config["name"] = org_name
        client = ArraylakeHttpClient("http://localhost:8000", token=token)
        resp = await client._request("POST", "/orgs_test_create", content=json.dumps(org_config))
        return org_name

    @staticmethod
    async def set_repo_system_status(token, org_name, repo_name, mode: RepoOperationMode, message: str, is_user_modifiable: bool):
        """Util to set a system status for client tests.

        System statuses and the user modifiable status are not available in the public API.
        """
        client = ArraylakeHttpClient("http://localhost:8000", token=token)
        body = dict(NewRepoOperationStatus(mode=mode, message=message))
        resp = await client._request(
            "POST",
            "/repo_status_system",
            content=json.dumps(body),
            params={"org_name": org_name, "repo_name": repo_name, "is_user_modifiable": is_user_modifiable},
        )


@pytest.fixture(scope="session")
def helpers():
    """Provide the helpers found in the Helpers class"""
    return Helpers


@pytest.fixture
def mock_auth_provider_config():
    mock_config = AuthProviderConfig(client_id="123456789", domain="auth.foo.com")

    with mock.patch.object(TokenHandler, "auth_provider_config", return_value=mock_config, new_callable=mock.PropertyMock):
        yield mock_config
