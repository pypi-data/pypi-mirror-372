import importlib
import os
import time
from datetime import time as dt_time
from datetime import timedelta
from unittest.mock import patch
from uuid import UUID, uuid4

import httpx
import pytest
import zarr
from httpx import Response
from packaging.version import Version

from . import has_icechunk, has_zarr_v3

from arraylake import AsyncClient, Client, config
from arraylake.repos.v1.types import ChunkstoreSchemaVersion
from arraylake.token import Auth0UrlCode, AuthException, TokenHandler
from arraylake.types import (
    DBID,
    AuthProviderConfig,
    BucketResponse,
    ExpirationConfig,
    GCConfig,
    GCDeleteOlderThan,
    GCKeep,
    OptimizationConfig,
    OptimizationWindow,
    RepoKind,
    UserInfo,
)

# toggle this value if we change how many commits are created on repo init
NUM_BASE_COMMITS = 0


@pytest.fixture()
def repo_kind_to_test() -> RepoKind:
    if importlib.util.find_spec("icechunk") is not None:
        # Use V2 repo in test if icechunk is in the env
        return RepoKind.Icechunk
    elif Version(zarr.__version__) < Version("3.0.0.a0"):
        # DEPRECATED: V1 repo fallback - pending removal
        # Use V1 repo if zarr v2 is in env
        return RepoKind.V1
    else:
        # Skip in the case where icechunk not in the env but zarr v3 is
        pytest.skip("Skipping client test because zarr >= v3.0, but icechunk is not installed")


@pytest.mark.asyncio
async def test_client_raises_when_not_logged_in(isolated_org_name, test_token_file, repo_kind_to_test: RepoKind) -> None:
    org_name = isolated_org_name
    test_token_file.unlink()
    aclient = AsyncClient()
    with pytest.raises(AuthException, match=r"Not logged in, please log in .*"):
        await aclient.create_repo(f"{org_name}/foo", kind=repo_kind_to_test)


@pytest.mark.parametrize("ClientClass", [Client, AsyncClient])
def test_client_repr_does_not_show_token(ClientClass, test_token):
    client = ClientClass(token=test_token)
    assert test_token not in repr(client)


@pytest.mark.parametrize("ClientClass", [Client, AsyncClient])
@pytest.mark.parametrize("bad_token", ["emax", "em", "_", ""])
def test_client_raises_for_bad_token(ClientClass, bad_token):
    with pytest.raises(ValueError, match="Invalid token provided"):
        client = ClientClass(token=bad_token)


@pytest.mark.parametrize("ClientClass", [Client, AsyncClient])
def test_client_finds_env_token(ClientClass, test_token):
    with patch.dict(os.environ, {"ARRAYLAKE_TOKEN": test_token}):
        config.refresh()
        client = ClientClass()
        assert client.token is not None
        assert client.token == test_token


@pytest.mark.parametrize("ClientClass", [Client, AsyncClient])
def test_client_finds_config_token(ClientClass, test_token):
    with config.set({"token": test_token}):
        client = ClientClass()
        assert client.token is not None
        assert client.token == test_token


@pytest.mark.asyncio
async def test_create_repo_with_non_existing_bucket(token, helpers, repo_kind_to_test: RepoKind) -> None:
    aclient = AsyncClient(token=token)
    org_name = "bucketty"
    repo_name = f"{org_name}/{helpers.random_repo_id()}"

    with pytest.raises(ValueError, match="not-a-bucket does not exist") as exc_info:
        arepo = await aclient.create_repo(repo_name, bucket_config_nickname="not-a-bucket", kind=repo_kind_to_test)


def test_default_kind_repo_creation(isolated_org_with_bucket, token):
    org_name, _ = isolated_org_with_bucket

    client = Client(token=token)
    assert client.list_repos(org_name) == []

    name = f"{org_name}/zoo"
    repo = client.create_repo(name)
    if has_icechunk and has_zarr_v3:
        import icechunk

        assert isinstance(repo, icechunk.Repository)
    else:
        import arraylake

        assert isinstance(repo, arraylake.repo.Repo)


def test_warn_on_get_existing_v1_repo(isolated_org_with_bucket, token) -> None:
    org_name, _ = isolated_org_with_bucket
    client = Client(token=token)
    name = f"{org_name}/bar"
    # DEPRECATED: V1 repo test - pending removal
    client.create_repo(name, kind=RepoKind.V1)

    with pytest.warns(FutureWarning, match="V1 repos are deprecated"):
        client.get_repo(name)


# FIXME: Ensure a bucket can't be created that shares config with a bucket in another org?


@pytest.mark.asyncio
async def test_create_repo_with_description(token, isolated_org_with_bucket, repo_kind_to_test: RepoKind) -> None:
    org_name = isolated_org_with_bucket[0]
    repo_name = f"{org_name}/foo"
    description = "This is a test repo"

    aclient = AsyncClient(token=token)
    await aclient.create_repo(repo_name, description=description, kind=repo_kind_to_test)
    repo_obj = await aclient.get_repo_object(repo_name)
    assert repo_obj.description == description


async def test_forbid_creating_v1_repos(token, isolated_org_with_bucket) -> None:
    org_name = isolated_org_with_bucket[0]
    repo_name = f"{org_name}/foo"
    aclient = AsyncClient(token=token)

    # DEPRECATED: V1 repo creation test - pending removal
    with config.set({"repo.allow_v1_repo_creation": False}):
        with pytest.raises(ValueError, match="Creating V1 repos is deprecated"):
            await aclient.create_repo(repo_name, kind=RepoKind.V1)


@pytest.mark.asyncio
async def test_create_repo_with_description_too_long(token, isolated_org_with_bucket, repo_kind_to_test: RepoKind) -> None:
    org_name = isolated_org_with_bucket[0]
    repo_name = f"{org_name}/foo"
    description = "x" * 256

    aclient = AsyncClient(token=token)
    with pytest.raises(ValueError, match="Description can be at most 255 characters long"):
        await aclient.create_repo(repo_name, description=description, kind=repo_kind_to_test)


@pytest.mark.asyncio
async def test_create_repo_with_metadata(token, isolated_org_with_bucket, repo_kind_to_test: RepoKind) -> None:
    org_name = isolated_org_with_bucket[0]
    repo_name = f"{org_name}/foo"
    metadata = {"key1": "value1", "key2": 2, "key3": 3.14, "key4": True, "key5": None}

    aclient = AsyncClient(token=token)
    await aclient.create_repo(repo_name, metadata=metadata, kind=repo_kind_to_test)
    repo_obj = await aclient.get_repo_object(repo_name)
    assert repo_obj.metadata == metadata


@pytest.mark.asyncio
async def test_create_repo_with_metadata_nested_dict_raises(token, isolated_org_with_bucket, repo_kind_to_test: RepoKind) -> None:
    org_name = isolated_org_with_bucket[0]
    repo_name = f"{org_name}/foo"
    metadata = {"key1": {"key2": 2}, "key3": 3.14, "key4": True, "key5": None}

    aclient = AsyncClient(token=token)
    with pytest.raises(ValueError):
        await aclient.create_repo(repo_name, metadata=metadata, kind=repo_kind_to_test)


@pytest.mark.asyncio
async def test_create_repo_with_metadata_too_large(token, isolated_org_with_bucket, repo_kind_to_test: RepoKind) -> None:
    org_name = isolated_org_with_bucket[0]
    repo_name = f"{org_name}/foo"
    metadata = {"key1": "x" * 4096}

    aclient = AsyncClient(token=token)
    with pytest.raises(ValueError, match="Metadata can be at most 4kB"):
        await aclient.create_repo(repo_name, metadata=metadata, kind=repo_kind_to_test)


@pytest.mark.asyncio
async def test_modify_repo(token, isolated_org_with_bucket, repo_kind_to_test: RepoKind) -> None:
    org_name = isolated_org_with_bucket[0]
    repo_name = f"{org_name}/foo"
    metadata = {"fruits": ["banana", "apple"], "vegetable": "carrot", "grain": "rice", "dairy": "milk", "healthy": True}
    description = "This is a test repo"

    aclient = AsyncClient(token=token)
    await aclient.create_repo(repo_name, metadata=metadata, description=description, kind=repo_kind_to_test)
    current_repo_obj = await aclient.get_repo_object(repo_name)

    # Modify metadata
    new_description = "This is a modified test repo"
    optimization_window = OptimizationWindow(
        duration=3600,  # 1 hour
        start_time=dt_time(2, 0),  # 2:00 AM UTC
        day_of_week=1,  # Monday
    )
    gc_config = GCConfig(
        extra_gc_roots={"12345678910"},
        dangling_chunks=GCKeep(),
        dangling_manifests=GCDeleteOlderThan(date=timedelta(days=30)),
        dangling_attributes=GCKeep(),
        dangling_transaction_logs=GCDeleteOlderThan(date=timedelta(days=30)),
        dangling_snapshots=GCKeep(),
        gc_every=timedelta(days=7),
        enabled=False,
    )
    expiration_config = ExpirationConfig(
        expire_versions_older_than=timedelta(days=30),
        expire_every=None,
        enabled=True,
    )
    optimization_config = OptimizationConfig(
        expiration_config=expiration_config,
        gc_config=gc_config,
        window=optimization_window,
    )
    add_metadata = {"legume": "soybean", "fats": "butter"}
    remove_metadata = ["dairy"]
    update_metadata = {"fruits": ["pear", "kiwi"], "vegetable": ["broccoli", "carrot"], "healthy": False}
    expected_metadata = {
        "fruits": ["pear", "kiwi"],
        "vegetable": ["broccoli", "carrot"],
        "grain": "rice",
        "legume": "soybean",
        "fats": "butter",
        "healthy": False,
    }
    time.sleep(1)  # Ensure the updated time is different
    await aclient.modify_repo(
        repo_name,
        description=new_description,
        add_metadata=add_metadata,
        remove_metadata=remove_metadata,
        update_metadata=update_metadata,
        optimization_config=optimization_config,
    )
    updated_repo_obj = await aclient.get_repo_object(repo_name)
    assert updated_repo_obj.metadata.keys() == expected_metadata.keys()
    for key, value in expected_metadata.items():
        if isinstance(value, list):
            assert set(updated_repo_obj.metadata[key]) == set(value)
        else:
            assert updated_repo_obj.metadata[key] == value
    assert updated_repo_obj.description == new_description
    assert updated_repo_obj.updated > current_repo_obj.updated
    assert updated_repo_obj.optimization_config.window == optimization_window
    assert updated_repo_obj.optimization_config.gc_config == gc_config
    assert updated_repo_obj.optimization_config.expiration_config == expiration_config


def test_modify_repo_raises(token, isolated_org_with_bucket, repo_kind_to_test: RepoKind) -> None:
    org_name = isolated_org_with_bucket[0]
    repo_name = f"{org_name}/foo"
    metadata = {"fruit": "banana", "vegetable": "carrot", "grain": "rice", "dairy": "milk"}

    client = Client(token=token)
    client.create_repo(repo_name, metadata=metadata, kind=repo_kind_to_test)

    with pytest.raises(ValueError, match="already exists in metadata"):
        client.modify_repo(repo_name, add_metadata={"fruit": "orange"})

    with pytest.raises(ValueError, match="Common metadata keys found in request"):
        client.modify_repo(repo_name, update_metadata={"fruit": "orange"}, remove_metadata=["fruit"])

    with pytest.raises(ValueError, match="Common metadata keys found in request"):
        client.modify_repo(repo_name, add_metadata={"fruit": "orange"}, remove_metadata=["fruit"])

    with pytest.raises(ValueError, match="Common metadata keys found in request"):
        client.modify_repo(repo_name, update_metadata={"legume": "soybean"}, add_metadata={"legume": "lentil"})

    with pytest.raises(ValueError, match="Description can be at most 255 characters long"):
        new_description = "x" * 256
        client.modify_repo(repo_name, description=new_description)


@pytest.mark.asyncio
async def test_modify_repo_no_change(token, isolated_org_with_bucket, repo_kind_to_test: RepoKind) -> None:
    org_name = isolated_org_with_bucket[0]
    repo_name = f"{org_name}/foo"
    metadata = {"fruit": "banana", "vegetable": "carrot", "grain": "rice", "dairy": "milk"}

    aclient = AsyncClient(token=token)
    await aclient.create_repo(repo_name, metadata=metadata, kind=repo_kind_to_test)
    current_repo_obj = await aclient.get_repo_object(repo_name)

    await aclient.modify_repo(repo_name)

    updated_repo_obj = await aclient.get_repo_object(repo_name)
    assert updated_repo_obj.metadata == metadata
    assert updated_repo_obj.description is None
    assert updated_repo_obj.updated == current_repo_obj.updated
    assert updated_repo_obj.optimization_config.window is None
    assert updated_repo_obj.optimization_config.gc_config is None
    assert updated_repo_obj.optimization_config.expiration_config is None


def test_list_repos_filter_metadata(token, isolated_org_with_bucket, repo_kind_to_test: RepoKind):
    org_name = isolated_org_with_bucket[0]
    repo_name = "foo"
    metadata = {"key1": "value1", "key2": 2, "key3": 3.14, "key4": True, "key5": None}

    client = Client(token=token)
    client.create_repo(f"{org_name}/bar", kind=repo_kind_to_test)
    client.create_repo(f"{org_name}/{repo_name}", kind=repo_kind_to_test, metadata=metadata)

    for key, value in metadata.items():
        repos = client.list_repos(org_name, filter_metadata={key: value})
        assert len(repos) == 1
        assert repos[0].name == repo_name


def test_list_repos_filter_metadata_fails(token, isolated_org_with_bucket):
    org_name = isolated_org_with_bucket[0]

    client = Client(token=token)
    with pytest.raises(ValueError, match="filter_metadata must be a JSON object"):
        client.list_repos(org_name, filter_metadata="not-a-dict")

    with pytest.raises(ValueError, match="filter_metadata values must be scalars or lists of scalars"):
        client.list_repos(org_name, filter_metadata={"key": {"key2": "value"}})


@pytest.mark.asyncio
async def test_hmac_bucket_config(token, helpers):
    aclient = AsyncClient(token=token)
    org_config = {
        "metastoredb_host": "mongo",
        "minimum_chunkstore_version": ChunkstoreSchemaVersion.V1,
    }
    org_name = await helpers.isolated_org(token, org_config)
    bucket_name = helpers.an_id(10)
    bucket_nickname = helpers.an_id(5)
    prefix = helpers.an_id(7)

    # Check that there are no buckets
    buckets = await aclient.list_bucket_configs(org_name)
    assert len(buckets) == 0

    # Create a bucket with hmac auth
    new_bucket = await aclient.create_bucket_config(
        org=org_name,
        nickname=bucket_nickname,
        uri=f"s3://{bucket_name}/{prefix}",
        extra_config={"region_name": "us-west-2"},
        auth_config={"method": "hmac", "access_key_id": "access-key", "secret_access_key": "secret"},
    )
    buckets = await aclient.list_bucket_configs(org_name)
    assert len(buckets) == 1
    assert new_bucket in buckets
    test_bucket_config = buckets[0]
    assert test_bucket_config.auth_config.method == "hmac"
    assert test_bucket_config.auth_config.access_key_id == "access-key"
    assert test_bucket_config.auth_config.secret_access_key == "secret"

    # Clean up the bucket
    await aclient.delete_bucket_config(org=org_name, nickname=bucket_nickname, imsure=True, imreallysure=True)
    bucket_configs = await aclient.list_bucket_configs(org_name)
    assert len(bucket_configs) == 0


def test_login_logout(monkeypatch, test_token_file, helpers, respx_mock) -> None:
    test_tokens = helpers.oauth_tokens_from_file(test_token_file)
    test_token_file.unlink()
    refreshed_tokens = test_tokens.model_copy(update={"id_token": "123456789abcdefg"})

    client = Client(service_uri="https://foo.com")

    user_code = "sample-code-12345"
    device_code = "12345"

    class MockTokenHandler(TokenHandler):
        _code = None

        @property
        def auth_provider_config(self) -> AuthProviderConfig:
            return AuthProviderConfig(domain="foo.auth0.com", client_id="bar")

        async def get_authorize_info(self) -> Auth0UrlCode:
            return Auth0UrlCode(url="https://foo.auth0.com", user_code=user_code, device_code=device_code, interval=1, expires_in=100)

        async def get_token(self, device_code: str, interval: int, expires_in: int):
            assert device_code == device_code
            self.update(test_tokens)

        async def refresh_token(self):
            self.update(refreshed_tokens)

        async def _get_user(self) -> UserInfo:
            return UserInfo(
                id=UUID("aeeb8bfa-e8f4-4724-9427-c3d5af661900"),
                email="spam@foo.com",
                first_name="TestFirst",
                family_name="TestFamily",
            )

    def get_auth_handler(org: str = None):
        return MockTokenHandler(api_endpoint="https://foo.com")

    def _input():
        return test_code

    monkeypatch.setattr("builtins.input", _input)

    logout_route = respx_mock.get(f"https://foo.auth0.com/v2/logout").mock(return_value=Response(200))

    with patch("arraylake.client.get_auth_handler", get_auth_handler), patch("arraylake.token.open_new") as mock_open_new:
        client.login(browser=False)
        assert mock_open_new.call_count == 0  # check that browser was not opened
        assert test_token_file.is_file()

    with patch("arraylake.client.get_auth_handler", get_auth_handler):
        client.logout()
        assert not test_token_file.is_file()


@pytest.mark.asyncio
async def test_chunkstore_init_s3_bucket_delegated(isolated_org_name, token, respx_mock):
    """DEPRECATED: V1 chunkstore test - pending removal.
    V1 repositories are legacy and this test will be removed in a future version."""
    bucket_id = uuid4()
    repo_id = DBID(b"hello")
    org_name = isolated_org_name
    mock_url = "https://test-arraylake-service.bar/"
    repo_name = "foo"

    auth_config = {
        "method": "aws_customer_managed_role",
        "external_customer_id": "12345678",
        "external_role_name": "my_external_role",
        "shared_secret": "our-shared-secret",
    }

    aws_creds = {"aws_access_key_id": "12345678", "aws_secret_access_key": "abcdefgh", "aws_session_token": "a_token_string"}

    bucket = BucketResponse(
        id=bucket_id,
        nickname="nickname",
        platform="s3",
        name="the-bucket",
        auth_config=auth_config,
        extra_config={},
        is_default=False,
    )

    respx_mock.get(mock_url + f"repos/{org_name}/{repo_name}/bucket-credentials").mock(return_value=httpx.Response(200, json=aws_creds))

    aclient = AsyncClient(mock_url, token=token)

    with config.set({"chunkstore.use_delegated_credentials": True}):
        cstore = await aclient._init_chunkstore(repo_id, bucket, org_name, repo_name)

    assert cstore.object_store._fetch_credentials_func is not None

    cstore_kwargs = cstore.object_store.constructor_kwargs
    assert set(cstore_kwargs.keys()) == {"client_kwargs", "anon"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "auth_params",
    (
        ({"method": "anonymous"}, False),
        ({"method": "anonymous"}, True),
        (
            {
                "method": "aws_customer_managed_role",
                "external_customer_id": "123456",
                "external_role_name": "myrolename",
                "shared_secret": "our-shared-secret",
            },
            False,
        ),
    ),
)
async def test_chunkstore_init_s3_bucket_not_delegated(isolated_org_name, token, auth_params):
    """DEPRECATED: V1 chunkstore test - pending removal.
    V1 repositories are legacy and this test will be removed in a future version."""
    auth_config, use_delegated_credentials = auth_params

    bucket_id = uuid4()
    repo_id = DBID(b"hello")
    org_name = isolated_org_name
    mock_url = "https://test-arraylake-service.foo/"
    repo_name = "foo"

    bucket = BucketResponse(
        id=bucket_id,
        nickname="nickname",
        platform="s3",
        name="the-bucket",
        extra_config={},
        auth_config=auth_config,
        is_default=False,
    )

    aclient = AsyncClient(mock_url, token=token)

    with config.set({"chunkstore.use_delegated_credentials": use_delegated_credentials}):
        cstore = await aclient._init_chunkstore(repo_id, bucket, org_name, repo_name)

    cstore_client_kwargs = cstore.object_store.constructor_kwargs["client_kwargs"]

    # check that AWS creds are not in client kwargs
    assert cstore_client_kwargs.keys() == {"endpoint_url"}


@pytest.mark.asyncio
@pytest.mark.parametrize("platform", ("s3", "s3-compatible", "minio", "gs"))
async def test_chunkstore_init_hmac(isolated_org_name, token, platform):
    """DEPRECATED: V1 chunkstore test - pending removal.
    V1 repositories are legacy and this test will be removed in a future version."""
    hmac_inputs = {"access_key_id": "access-key", "secret_access_key": "secret-key"}
    expected_keys = ("aws_access_key_id", "aws_secret_access_key")
    auth_config = {"method": "hmac", **hmac_inputs}

    bucket_id = uuid4()
    repo_id = DBID(b"hello")
    repo_name = "bucketty"

    bucket = BucketResponse(
        id=bucket_id,
        nickname="nickname",
        platform=platform,
        name="bucketty",
        extra_config={},
        auth_config=auth_config,
        is_default=False,
    )

    aclient = AsyncClient("https://test-arraylake-service.foo/", token=token)
    cstore = await aclient._init_chunkstore(repo_id, bucket, isolated_org_name, repo_name)

    if platform == "gs":
        for key in expected_keys:
            assert key not in cstore.object_store.constructor_kwargs
    else:
        cstore_client_kwargs = cstore.object_store.constructor_kwargs["client_kwargs"]
        for key, expected_key in zip(hmac_inputs, expected_keys):
            assert expected_key in cstore_client_kwargs
            assert cstore_client_kwargs[expected_key] == hmac_inputs[key]
