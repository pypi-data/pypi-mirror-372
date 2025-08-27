import datetime
from uuid import UUID, uuid4

import icechunk
import pytest
import zarr
from icechunk import IcechunkError, Repository, S3Credentials, Storage

from arraylake import AsyncClient, Client
from arraylake.config import config
from arraylake.types import DBID
from arraylake.types import Repo as RepoModel
from arraylake.types import RepoKind, RepoOperationMode, RepoOperationStatusResponse


@pytest.mark.asyncio
async def test_async_client(isolated_org_with_bucket, token):
    """Integration-style test for the async client."""
    org_name, _ = isolated_org_with_bucket

    aclient = AsyncClient(token=token)
    assert not await aclient.list_repos(org_name)

    # Create two new Icechunk repos
    # The repo name must be unique for subsequent runs
    for repo_name in ["foo", "bar"]:
        name = f"{org_name}/{repo_name}"
        repo = await aclient.create_repo(name, kind=RepoKind.Icechunk, prefix=str(uuid4())[:8])
        assert isinstance(repo, Repository)
        # TODO: earth-mover/icechunk#414: expose storage config so we can check more things

        repo = await aclient.get_repo(name)
        assert isinstance(repo, Repository)
        # TODO: earth-mover/icechunk#414: expose storage config so we can check more things

    # Check that duplicate repos are not allowed
    with pytest.raises(ValueError):
        await aclient.create_repo(name, kind=RepoKind.Icechunk)

    # List the repos
    repo_listing = await aclient.list_repos(org_name)
    all_repo_names = {repo.name for repo in repo_listing}
    assert all_repo_names == {"foo", "bar"}

    # Delete the repos
    for repo_name in ["foo", "bar"]:
        name = f"{org_name}/{repo_name}"
        await aclient.delete_repo(name, imsure=True, imreallysure=True)

    # Check that the repos are gone
    with pytest.raises(ValueError):
        # can't get nonexistent repo
        await aclient.get_repo("doesnt/exist")

    with pytest.raises(ValueError):
        # can't delete nonexistent repo
        await aclient.delete_repo("doesnt/exist", imsure=True, imreallysure=True)


def test_client(isolated_org_with_bucket, token):
    """Integration-style test for the sync client."""
    org_name, _ = isolated_org_with_bucket

    client = Client(token=token)
    assert client.list_repos(org_name) == []

    for repo_name in ["foo", "bar"]:
        name = f"{org_name}/{repo_name}"
        repo = client.create_repo(name, kind=RepoKind.Icechunk, prefix=str(uuid4())[:8])
        assert isinstance(repo, Repository)
        # TODO: earth-mover/icechunk#414: expose storage config so we can check more things

        repo = client.get_repo(name)
        assert isinstance(repo, Repository)
        # TODO: earth-mover/icechunk#414: expose storage config so we can check more things

    with pytest.raises(ValueError):
        # no duplicate repos allowed
        client.create_repo(name, kind=RepoKind.Icechunk)

    repo_listing = client.list_repos(org_name)
    assert len(repo_listing) == 2
    all_repo_names = {repo.name for repo in repo_listing}
    assert all_repo_names == {"foo", "bar"}

    for repo_name in ["foo", "bar"]:
        name = f"{org_name}/{repo_name}"
        client.delete_repo(name, imsure=True, imreallysure=True)

    with pytest.raises(ValueError):
        # can't get nonexistent repo
        client.get_repo("doesnt/exist")

    with pytest.raises(ValueError):
        # can't delete nonexistent repo
        client.delete_repo("doesnt/exist", imsure=True, imreallysure=True)


@pytest.mark.asyncio
async def test_get_or_create_repo_async(isolated_org_with_bucket, token):
    org_name, _ = isolated_org_with_bucket
    aclient = AsyncClient(token=token)
    repo_name = "foo"
    name = f"{org_name}/{repo_name}"
    assert repo_name not in {repo.name for repo in await aclient.list_repos(org_name)}
    # Create the repo
    await aclient.get_or_create_repo(name, kind=RepoKind.Icechunk, prefix=str(uuid4())[:8])
    assert repo_name in {repo.name for repo in await aclient.list_repos(org_name)}
    # Get the repo
    await aclient.get_or_create_repo(name, kind=RepoKind.Icechunk)
    # TODO: earth-mover/icechunk#414: expose storage config so we can check more things
    # Delete the repo
    await aclient.delete_repo(name, imsure=True, imreallysure=True)


def test_get_or_create_repo_sync(isolated_org_with_bucket, token):
    org_name, _ = isolated_org_with_bucket
    client = Client(token=token)
    repo_name = "foo"
    name = f"{org_name}/{repo_name}"
    assert repo_name not in {repo.name for repo in client.list_repos(org_name)}
    # Create the repo
    client.get_or_create_repo(name, kind=RepoKind.Icechunk, prefix=str(uuid4())[:8])
    assert repo_name in {repo.name for repo in client.list_repos(org_name)}
    # Get the repo
    client.get_or_create_repo(name, kind=RepoKind.V1)
    # TODO: earth-mover/icechunk#414: expose storage config so we can check more things
    # Delete the repo
    client.delete_repo(name, imsure=True, imreallysure=True)


def test_get_create_repo_with_repo_config(isolated_org_with_bucket, token):
    org_name, _ = isolated_org_with_bucket
    client = Client(token=token)
    repo_name = "foo"
    name = f"{org_name}/{repo_name}"
    assert repo_name not in {repo.name for repo in client.list_repos(org_name)}
    config = icechunk.RepositoryConfig.default()
    config.inline_chunk_threshold_bytes = 1024
    config.get_partial_values_concurrency = 2
    # Create the repo with the config
    repo = client.create_repo(name, kind=RepoKind.Icechunk, config=config)
    # Check that the RepositoryConfig was applied
    assert repo.config.inline_chunk_threshold_bytes == 1024
    assert repo.config.get_partial_values_concurrency == 2
    assert repo_name in {repo.name for repo in client.list_repos(org_name)}
    # Get the repo with different config values
    config.inline_chunk_threshold_bytes = 512
    config.get_partial_values_concurrency = 10
    repo = client.get_repo(name, config=config)
    # Check that the RepositoryConfig was applied
    assert repo.config.inline_chunk_threshold_bytes == 512
    assert repo.config.get_partial_values_concurrency == 10
    # Delete the repo
    client.delete_repo(name, imsure=True, imreallysure=True)


def test_set_author_on_commit(isolated_org_with_bucket, token):
    org_name, _ = isolated_org_with_bucket
    client = Client(token=token)
    repo_name = "foo"
    name = f"{org_name}/{repo_name}"
    assert repo_name not in {repo.name for repo in client.list_repos(org_name)}
    # Create the repo
    repo = client.create_repo(name, kind=RepoKind.Icechunk, prefix=str(uuid4())[:8])
    # Check that the author is set on the commit
    session = repo.writable_session(branch="main")
    # Make a small change to the repo
    zarr.create_array(store=session.store, name="foo", shape=(10,), chunks=(5,), dtype="i4")
    sid = session.commit("Initial commit")
    snap = next(repo.ancestry(snapshot_id=sid))
    assert snap.metadata == {"author_name": "None None", "author_email": "abc@earthmover.io"}

    # Get the repo and check that the author is set on the commit
    repo_again = client.get_repo(name)
    session_again = repo_again.writable_session(branch="main")
    # Make a small change to the repo
    zarr.create_array(store=session_again.store, name="bar", shape=(10,), chunks=(5,), dtype="i4")
    sid_again = session_again.commit("Second commit")
    snap_again = next(repo_again.ancestry(snapshot_id=sid_again))
    assert snap_again.metadata == {"author_name": "None None", "author_email": "abc@earthmover.io"}

    # Delete the repo
    client.delete_repo(name, imsure=True, imreallysure=True)


@pytest.mark.asyncio
async def test_get_icechunk_storage_from_repo_model(isolated_org_with_bucket, token):
    aclient = AsyncClient(token=token)
    org, bucket_nickname = isolated_org_with_bucket
    bucket_config = await aclient.get_bucket_config(org=org, nickname=bucket_nickname)

    repo_model = RepoModel(
        _id=DBID(b"some_repo_id"),
        org="earthmover",
        name="repo-name",
        updated=datetime.datetime.now(),
        status=RepoOperationStatusResponse(mode=RepoOperationMode.ONLINE, initiated_by={}),
        bucket=bucket_config,
    )
    with config.set({"icechunk.scatter_initial_credentials": False}):
        storage = await aclient._get_icechunk_storage_from_repo_model(repo_model=repo_model, user_id=uuid4())
    assert isinstance(storage, Storage)


@pytest.mark.asyncio
async def test_get_icechunk_storage_from_repo_model_no_bucket_raises(token):
    aclient = AsyncClient(token=token)
    repo_model = RepoModel(
        _id=DBID(b"some_repo_id"),
        org="earthmover",
        name="repo-name",
        updated=datetime.datetime.now(),
        status=RepoOperationStatusResponse(mode=RepoOperationMode.ONLINE, initiated_by={}),
        bucket=None,
    )
    with pytest.raises(ValueError) as excinfo:
        await aclient._get_icechunk_storage_from_repo_model(repo_model=repo_model, user_id=uuid4())
    assert "The bucket on the catalog object cannot be None for Icechunk V2 repos!" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_icechunk_storage(isolated_org_with_bucket, token):
    aclient = AsyncClient(token=token)
    org, bucket_nickname = isolated_org_with_bucket
    repo_name = f"{org}/icechunk-repo"
    await aclient.create_repo(
        name=repo_name,
        bucket_config_nickname=bucket_nickname,
        kind=RepoKind.Icechunk,
        prefix=str(uuid4())[:8],
    )
    storage = await aclient.get_icechunk_storage(repo_name)
    assert isinstance(storage, Storage)

    aclient.delete_repo(name=f"{org}/icechunk-repo", imsure=True, imreallysure=True)


@pytest.mark.asyncio
async def test_get_icechunk_container_credentials_from_bucket_hmac_async(isolated_org_with_bucket, token):
    aclient = AsyncClient(token=token)
    org, bucket_nickname = isolated_org_with_bucket
    cont_creds = await aclient.get_icechunk_container_credentials_from_bucket(org, bucket_nickname)
    # Bucket uses HMAC credentials so we should get a static credentials object
    assert isinstance(cont_creds, S3Credentials.Static)
    # TODO: can we check the access key ID and secret access key?


def test_get_icechunk_container_credentials_from_bucket_hmac_sync(isolated_org_with_bucket, token):
    client = Client(token=token)
    org, bucket_nickname = isolated_org_with_bucket
    cont_creds = client.get_icechunk_container_credentials_from_bucket(org, bucket_nickname)
    # Bucket uses HMAC credentials so we should get a static credentials object
    assert isinstance(cont_creds, S3Credentials.Static)
    # TODO: can we check the access key ID and secret access key?


@pytest.mark.asyncio
async def test_get_icechunk_container_credentials_from_bucket_anon_async(isolated_org_with_anon_bucket, token):
    aclient = AsyncClient(token=token)
    org, bucket_nickname = isolated_org_with_anon_bucket
    cont_creds = await aclient.get_icechunk_container_credentials_from_bucket(org, bucket_nickname)
    # Bucket uses anonymous credentials so we should get FromEnv credentials object
    assert isinstance(cont_creds, S3Credentials.FromEnv)


def test_get_icechunk_container_credentials_from_bucket_anon_sync(isolated_org_with_anon_bucket, token):
    client = Client(token=token)
    org, bucket_nickname = isolated_org_with_anon_bucket
    cont_creds = client.get_icechunk_container_credentials_from_bucket(org, bucket_nickname)
    # Bucket uses anonymous credentials so we should get FromEnv credentials object
    assert isinstance(cont_creds, S3Credentials.FromEnv)


@pytest.mark.asyncio
async def test_get_icechunk_container_credentials_from_bucket_delegated_async(isolated_org_with_delegated_creds_bucket, token):
    aclient = AsyncClient(token=token)
    org, bucket_nickname = isolated_org_with_delegated_creds_bucket
    cont_creds = await aclient.get_icechunk_container_credentials_from_bucket(org, bucket_nickname)
    # Bucket uses delegated credentials so we should get a Refreshable credentials object
    assert isinstance(cont_creds, S3Credentials.Refreshable)


def test_get_icechunk_container_credentials_from_bucket_delegated_sync(isolated_org_with_delegated_creds_bucket, token):
    client = Client(token=token)
    org, bucket_nickname = isolated_org_with_delegated_creds_bucket
    cont_creds = client.get_icechunk_container_credentials_from_bucket(org, bucket_nickname)
    # Bucket uses delegated credentials so we should get a Refreshable credentials object
    assert isinstance(cont_creds, S3Credentials.Refreshable)


@pytest.mark.asyncio
async def test_containers_credentials_for_buckets_async(isolated_org_with_buckets, token):
    aclient = AsyncClient(token=token)
    org, first_bucket_nickname, second_bucket_nickname = isolated_org_with_buckets
    conts_creds = await aclient.containers_credentials_for_buckets(
        org=org,
        containers_to_buckets_map={
            "container1": first_bucket_nickname,
            "container2": second_bucket_nickname,
        },
    )
    assert set(conts_creds.keys()) == {"container1", "container2"}
    assert all(isinstance(creds, icechunk.Credentials.S3) for creds in conts_creds.values())


def test_containers_credentials_for_buckets_sync(isolated_org_with_buckets, token):
    client = Client(token=token)
    org, first_bucket_nickname, second_bucket_nickname = isolated_org_with_buckets
    conts_creds = client.containers_credentials_for_buckets(
        org=org,
        container1=first_bucket_nickname,
        container2=second_bucket_nickname,
    )
    assert set(conts_creds.keys()) == {"container1", "container2"}
    assert all(isinstance(creds, icechunk.Credentials.S3) for creds in conts_creds.values())


# def test_get_create_repo_with_chunk_containers(isolated_org_with_bucket, token):
#     client = Client(token=token)
#     org_name, bucket_nickname = isolated_org_with_bucket
#     repo_name = "foo"
#     name = f"{org_name}/{repo_name}"
#     assert repo_name not in {repo.name for repo in client.list_repos(org_name)}
#     # Create the repo with virtual chunk containers
#     client.create_repo(name, kind=RepoKind.Icechunk, virtual_container_nicknames={"container1": bucket_nickname})
#     assert repo_name in {repo.name for repo in client.list_repos(org_name)}
#     # Get the repo
#     repo = client.get_repo(name)
#     # TODO: can we check the virtual chunk contianers?


@pytest.mark.asyncio
@pytest.mark.xfail(reason="status endpoint is currently admin only", raises=ValueError)
async def test_repo_status_changes(isolated_org_with_bucket, token, helpers):
    aclient = AsyncClient(token=token)
    org_name, _ = isolated_org_with_bucket
    _repo_name = helpers.random_repo_id()
    repo_name = f"{org_name}/{_repo_name}"
    await aclient.create_repo(repo_name, kind=RepoKind.Icechunk)

    # assert repo is initialized with the right status
    repo_obj = await aclient.get_repo_object(repo_name)
    assert repo_obj.status.mode == RepoOperationMode.ONLINE
    assert repo_obj.status.message == "new repo creation"
    assert repo_obj.status.initiated_by.get("principal_id") is not None
    assert repo_obj.status.initiated_by.get("system_id") is None

    # assert update operates correctly
    await aclient._set_repo_status(repo_name, RepoOperationMode.OFFLINE, message="foo")
    repo_obj = await aclient.get_repo_object(repo_name)
    assert repo_obj.status.mode == RepoOperationMode.OFFLINE
    assert repo_obj.status.message == "foo"
    assert repo_obj.status.initiated_by.get("principal_id") is not None

    # assert system update is visible
    _on, _rn = repo_name.split("/")
    await helpers.set_repo_system_status(token, _on, _rn, RepoOperationMode.MAINTENANCE, "system message", False)
    repo_obj = await aclient.get_repo_object(repo_name)
    assert repo_obj.status.mode == RepoOperationMode.MAINTENANCE
    assert repo_obj.status.message == "system message"
    assert repo_obj.status.initiated_by.get("principal_id") is None
    assert repo_obj.status.initiated_by.get("system_id") is not None

    # is_user_modifiable is false, verify request is blocked
    with pytest.raises(ValueError, match="Repo status is not modifiable") as exc_info:
        await aclient._set_repo_status(repo_name, RepoOperationMode.ONLINE, message="foo")

    # and state is still what it was prior to the attempt
    repo_obj = await aclient.get_repo_object(repo_name)
    assert repo_obj.status.mode == RepoOperationMode.MAINTENANCE
    assert repo_obj.status.message == "system message"
    assert repo_obj.status.initiated_by.get("principal_id") is None

    await aclient.delete_repo(repo_name, imsure=True, imreallysure=True)


@pytest.mark.asyncio
async def test_repo_with_inconsistent_bucket(isolated_org_with_bucket, token, helpers) -> None:
    aclient = AsyncClient(token=token)
    org_name, _ = isolated_org_with_bucket
    repo_name = f"{org_name}/{helpers.random_repo_id()}"
    await aclient.create_repo(repo_name, kind=RepoKind.Icechunk)
    try:
        with pytest.raises(ValueError, match=r"does not match the configured bucket_config_nickname") as exc_info:
            await aclient.get_or_create_repo(repo_name, bucket_config_nickname="bad-nickname")
    finally:
        await aclient.delete_repo(repo_name, imsure=True, imreallysure=True)


@pytest.mark.asyncio
async def test_create_repo_with_duplicate_prefix(isolated_org_with_bucket, token, helpers):
    aclient = AsyncClient(token=token)
    org_name, _ = isolated_org_with_bucket
    repo_name = f"{org_name}/{helpers.random_repo_id()}"
    duplicate_repo_name = f"{org_name}/{helpers.random_repo_id()}2"
    prefix = str(uuid4())[:8]
    await aclient.create_repo(repo_name, kind=RepoKind.Icechunk, prefix=prefix)
    with pytest.raises(IcechunkError, match="repositories can only be created in clean prefixes"):
        await aclient.create_repo(duplicate_repo_name, kind=RepoKind.Icechunk, prefix=prefix)

    # make sure the duplicated prefix repo is deleted
    repos = await aclient.list_repos(org_name)
    assert duplicate_repo_name not in {repo.name for repo in repos}

    await aclient.delete_repo(repo_name, imsure=True, imreallysure=True)


@pytest.mark.asyncio
async def test_create_repo_with_bucket_prefix(isolated_org_with_bucket_with_prefix, token, helpers):
    aclient = AsyncClient(token=token)
    org_name, bucket_with_prefix_nickname = isolated_org_with_bucket_with_prefix
    repo_name = f"{org_name}/{helpers.random_repo_id()}"
    ic_prefix = str(uuid4())[:8]
    await aclient.create_repo(repo_name, kind="icechunk", bucket_config_nickname=bucket_with_prefix_nickname, prefix=ic_prefix)

    repo_obj = await aclient.get_repo_object(repo_name)
    bucket = await aclient.get_bucket_config(org=org_name, nickname=bucket_with_prefix_nickname)
    assert repo_obj.prefix == f"{bucket.prefix}/{ic_prefix}"

    await aclient.delete_repo(repo_name, imsure=True, imreallysure=True)
