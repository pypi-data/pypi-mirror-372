import json
from datetime import datetime, timedelta
from uuid import uuid4

import httpx
import pytest
from httpx import Response

from arraylake import AsyncClient, Client, config
from arraylake.repos.v1.types import ChunkstoreSchemaVersion, SessionID, SessionType
from arraylake.types import RepoKind, RepoOperationMode, UserInfo

# toggle this value if we change how many commits are created on repo init
NUM_BASE_COMMITS = 0


@pytest.mark.asyncio
async def test_async_client_no_bucket(isolated_org_name, token) -> None:
    org_name = isolated_org_name
    """Integration-style test for client"""

    aclient = AsyncClient(token=token)
    assert not await aclient.list_repos(org_name)

    for repo_name in ["foo", "bar"]:
        name = f"{org_name}/{repo_name}"
        arepo = await aclient.create_repo(name, kind=RepoKind.V1)
        assert arepo.repo_name == name
        arepo = await aclient.get_repo(name)
        assert arepo.repo_name == name
        # TODO: remove this once initialization no longer-required by Zarr
        assert len(await arepo.commit_log()) == NUM_BASE_COMMITS

    with pytest.raises(ValueError):
        # no duplicate repos allowed
        await aclient.create_repo(name, kind=RepoKind.V1)

    repo_listing = await aclient.list_repos(org_name)
    assert len(repo_listing) == 2
    all_repo_names = {repo.name for repo in repo_listing}
    assert all_repo_names == {"foo", "bar"}

    for repo_name in ["foo", "bar"]:
        name = f"{org_name}/{repo_name}"
        await aclient.delete_repo(name, imsure=True, imreallysure=True)

    with pytest.raises(ValueError):
        # can't get nonexistent repo
        await aclient.get_repo("doesnt/exist")

    with pytest.raises(ValueError):
        # can't delete nonexistent repo
        await aclient.delete_repo("doesnt/exist", imsure=True, imreallysure=True)


def test_client_no_bucket(isolated_org_name, token) -> None:
    """Integration-style test for client"""

    org_name = isolated_org_name

    client = Client(token=token)
    assert client.list_repos(org_name) == []

    for repo_name in ["foo", "bar"]:
        name = f"{org_name}/{repo_name}"
        repo = client.create_repo(name, kind=RepoKind.V1)
        assert repo.repo_name == name

        repo = client.get_repo(name)
        assert repo.repo_name == name

    # check read-only mode
    repo = client.get_repo(f"{org_name}/foo", read_only=True)
    assert repo.session.session_type == SessionType.read_only

    with pytest.raises(ValueError):
        # no duplicate repos allowed
        client.create_repo(name, kind=RepoKind.V1)

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
async def test_get_or_create_repo_async_no_bucket(isolated_org_name, token) -> None:
    org_name = isolated_org_name
    aclient = AsyncClient(token=token)
    repo_name = "foo"
    name = f"{org_name}/{repo_name}"
    assert repo_name not in {repo.name for repo in await aclient.list_repos(org_name)}
    arepo = await aclient.get_or_create_repo(name, kind=RepoKind.V1)
    assert arepo.session.session_type == SessionType.write
    assert repo_name in {repo.name for repo in await aclient.list_repos(org_name)}
    arepo = await aclient.get_or_create_repo(name, kind=RepoKind.V1)
    assert arepo.session.session_type == SessionType.write


@pytest.mark.asyncio
async def test_get_or_create_repo_sync_no_bucket(isolated_org_name, token) -> None:
    org_name = isolated_org_name
    client = Client(token=token)
    repo_name = "foo"
    name = f"{org_name}/{repo_name}"
    assert repo_name not in {repo.name for repo in client.list_repos(org_name)}
    repo = client.get_or_create_repo(name, kind=RepoKind.V1)
    assert repo._arepo.session.session_type == SessionType.write
    assert repo_name in {repo.name for repo in client.list_repos(org_name)}
    repo = client.get_or_create_repo(name, kind=RepoKind.V1)
    assert repo._arepo.session.session_type == SessionType.write


@pytest.mark.asyncio
async def test_client_token_handler_author_config_no_bucket(isolated_org_name, test_token, test_user, respx_mock):
    org_name = isolated_org_name
    mock_url = "https://test-arraylake-service.bar/"
    repo_name = "foo"
    now = datetime.utcnow()
    timeout = timedelta(days=1)
    user: UserInfo = test_user
    repo = dict(
        id="1234",
        org=org_name,
        name=repo_name,
        created=str(now),
        description="",
        status=dict(mode="online", initiated_by={"system_id": "x"}),
        kind=RepoKind.V1,
    )
    session = dict(
        _id=f"foo-{now.isoformat()}",
        start_time=now.isoformat(),
        last_modified=now.isoformat(),
        expiration=(now + timeout).isoformat(),
        branch="main",
        base_commit=None,
        author_email="foo@earthmover.io",
        session_type=SessionType.write,
        summary="foo",
    )

    # mock api routes
    user_route = respx_mock.get(mock_url + "user").mock(return_value=Response(200, json=json.loads(user.model_dump_json())))
    repo_post_route = respx_mock.post(mock_url + f"orgs/{org_name}/repos").mock(return_value=Response(201, json=repo))
    repos_get_route = respx_mock.get(mock_url + f"orgs/{org_name}/repos").mock(return_value=Response(200, json=[repo]))
    repo_get_route = respx_mock.get(mock_url + f"repos/{org_name}/{repo_name}").mock(return_value=Response(200, json=repo))
    commits_get_route = respx_mock.get(mock_url + f"repos/{org_name}/{repo_name}/commits").mock(return_value=Response(200, json=[]))
    tags_get_route = respx_mock.get(mock_url + f"repos/{org_name}/{repo_name}/tags").mock(return_value=Response(200, json=[]))
    branches_get_route = respx_mock.get(mock_url + f"repos/{org_name}/{repo_name}/branches").mock(return_value=Response(200, json=[]))
    sessions_post_route = respx_mock.post(mock_url + f"repos/{org_name}/{repo_name}/sessions").mock(
        return_value=Response(200, json=session)
    )

    aclient = AsyncClient(mock_url, token=test_token)
    arepo = await aclient.create_repo(f"{org_name}/foo")

    # assert that all calls used the test token
    for call in respx_mock.calls:
        assert call.request.headers.get("Authorization") == f"Bearer {test_token}"

    assert arepo.author.name == f"{user.first_name} {user.family_name}"
    assert arepo.author.email == user.email


@pytest.mark.asyncio
async def test_client_create_repo_raises_after_creating_db(isolated_org_name, test_token):
    org_name = isolated_org_name
    aclient = AsyncClient(token=test_token)
    with config.set({"chunkstore.uri": None}):
        with pytest.raises(ValueError, match=r"Chunkstore uri is None. Please set it using"):
            await aclient.create_repo(f"{org_name}/foo")
    repo_listing = await aclient.list_repos(org_name)
    all_repo_names = {repo.name for repo in repo_listing}
    assert "foo" in all_repo_names


@pytest.mark.asyncio
async def test_repo_with_bad_bucket_overwrite(token, helpers) -> None:
    aclient = AsyncClient(token=token)
    org_name = "bucketty"
    repo_name = f"{org_name}/{helpers.random_repo_id()}"
    arepo = await aclient.create_repo(repo_name)
    try:
        with pytest.raises(ValueError, match=r"does not have a bucket config attached") as exc_info:
            arepo = await aclient.get_or_create_repo(repo_name, bucket_config_nickname="test", kind=RepoKind.V1)
    finally:
        await aclient.delete_repo(repo_name, imsure=True, imreallysure=True)


@pytest.mark.asyncio
@pytest.mark.xfail(reason="status endpoint is currently admin only", raises=ValueError)
async def test_repo_status_changes(token, helpers):
    aclient = AsyncClient(token=token)
    org_name = "bucketty"
    _repo_name = helpers.random_repo_id()
    repo_name = f"{org_name}/{_repo_name}"
    arepo = await aclient.create_repo(repo_name, bucket_config_nickname="test")

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


pytest.mark.parametrize("wants_managed_sessions,error", [(False, r"Joining sessions not supported"), (True, r"Session invalid or expired")])


@pytest.mark.parametrize(
    "wants_managed_sessions,error", [(False, r"Joining sessions not supported"), (True, r"Session invalid or expired")]
)
@pytest.mark.asyncio
async def test_get_nonexistent_session_async(isolated_org_name, token, wants_managed_sessions, error):
    org_name = isolated_org_name
    test_config = {"server_managed_sessions": wants_managed_sessions}
    with config.set(test_config):
        aclient = AsyncClient(token=token)
        repo_name = "foo"
        name = f"{org_name}/{repo_name}"
        assert repo_name not in {repo.name for repo in await aclient.list_repos(org_name)}
        arepo = await aclient.get_or_create_repo(name)

        nonsense_session_id = "blurble"
        with pytest.raises(ValueError, match=error):
            await arepo.join_session(SessionID(nonsense_session_id))

        realistic_session_id = SessionID(str(uuid4()))
        with pytest.raises(ValueError, match=error):
            await arepo.join_session(realistic_session_id)


def test_get_database(respx_mock, test_user) -> None:
    mock_url = "https://foo.com"
    org = "foo"
    repo = "bar"
    client = Client(service_uri=mock_url)

    respx_mock.get(f"{mock_url}/user").mock(return_value=Response(200, json=json.loads(test_user.model_dump_json())))

    route = respx_mock.get(f"{mock_url}/repos/{org}/{repo}").mock(
        return_value=httpx.Response(
            httpx.codes.OK,
            json={
                "id": "123456",
                "org": "foo",
                "name": "bar",
                "updated": "2024-01-01T00:00:00+00:00",
                "description": None,
                "created_by": "11111111-2222-3333-4444-555555555555",
                "visibility": "PRIVATE",
                "kind": str(RepoKind.V1.value),
                "bucket": None,
                "status": {
                    "mode": "online",
                    "message": "new repo creation",
                    "initiated_by": {"principal_id": "11111111-2222-3333-4444-555555555555", "system_id": None},
                    "estimated_end_time": None,
                },
            },
        )
    )

    repo_obj = client.get_repo(f"{org}/{repo}", checkout=False)
    assert route.called
    assert repo_obj.repo_name == f"{org}/{repo}"
    from arraylake.repos.v1 import repo as repo_v1

    assert isinstance(repo_obj, repo_v1.Repo)


@pytest.mark.asyncio
async def test_repo_with_bucket(token, helpers) -> None:
    aclient = AsyncClient(token=token)
    org_name = "bucketty"
    _repo_name = helpers.random_repo_id()
    repo_name = f"{org_name}/{_repo_name}"
    arepo = await aclient.create_repo(repo_name, bucket_config_nickname="test", kind=RepoKind.V1)
    try:
        (res_repo,) = [repo for repo in await aclient.list_repos(org_name) if repo.name == _repo_name]
        assert res_repo.bucket.nickname == "test"

    finally:
        await aclient.delete_repo(repo_name, imsure=True, imreallysure=True)


@pytest.mark.asyncio
async def test_repo_with_inconsistent_bucket(token, helpers) -> None:
    aclient = AsyncClient(token=token)
    org_name = "bucketty"
    repo_name = f"{org_name}/{helpers.random_repo_id()}"
    arepo = await aclient.create_repo(repo_name, bucket_config_nickname="test", kind=RepoKind.V1)
    try:
        with pytest.raises(ValueError, match=r"does not match the configured bucket_config_nickname") as exc_info:
            arepo = await aclient.get_or_create_repo(repo_name, bucket_config_nickname="bad-nickname")
    finally:
        await aclient.delete_repo(repo_name, imsure=True, imreallysure=True)


@pytest.mark.asyncio
async def test_bucket_lifecycle(token, helpers):
    # TODO: Ensure that can_write_org_repos permissions are enforced
    aclient = AsyncClient(token=token)
    org_config = {"metastoredb_host": "mongo", "minimum_chunkstore_version": ChunkstoreSchemaVersion.V1, "feature_flags": ["v1-write"]}
    org_name = await helpers.isolated_org(token, org_config)
    repo_name = f"{org_name}/{helpers.random_repo_id()}"
    bucket_name = helpers.an_id(10)
    bucket_nickname = helpers.an_id(5)
    second_bucket_nickname = helpers.an_id(6)
    prefix = helpers.an_id(7)

    buckets = await aclient.list_bucket_configs(org_name)
    assert len(buckets) == 0
    new_bucket = await aclient.create_bucket_config(
        org=org_name, nickname=bucket_nickname, uri=f"s3://{bucket_name}/{prefix}", extra_config={"region_name": "us-west-2"}
    )
    buckets = await aclient.list_bucket_configs(org_name)
    assert len(buckets) == 1
    assert new_bucket in buckets

    # Make this bucket the default.
    await aclient.set_default_bucket_config(org=org_name, nickname=bucket_nickname)
    new_bucket = await aclient.get_bucket_config(org=org_name, nickname=bucket_nickname)
    assert new_bucket.is_default is True

    bucket_kws = {
        "nickname": bucket_nickname,
        "uri": f"s3://{bucket_name}/{prefix}",
        "extra_config": {"region_name": "us-west-2"},
    }

    # Repeated requests to create the same bucket should fail.
    with pytest.raises(ValueError, match="already exists"):
        _ = await aclient.create_bucket_config(org=org_name, **bucket_kws)

    # No two buckets should have the same (platform, name, prefix, endpoint_url) set, as
    # they would point to the same location.
    diff_bucket_kws = {
        "nickname": second_bucket_nickname,
        "uri": f"s3://{bucket_name}/{prefix}",
        "extra_config": {"region_name": "us-west-2"},
    }
    with pytest.raises(ValueError, match="already exists"):
        _ = await aclient.create_bucket_config(org=org_name, **diff_bucket_kws)

    # However, if the endpoint URL differs between two otherwise identical
    # buckets, that's cool.
    diff_bucket_kws = {
        "nickname": second_bucket_nickname,
        "uri": f"s3://{bucket_name}/{prefix}",
        "extra_config": {"endpoint_url": "http://some-other-url:1234"},
    }
    valid_bucket = await aclient.create_bucket_config(org=org_name, **diff_bucket_kws)
    buckets = await aclient.list_bucket_configs(org_name)
    assert len(buckets) == 2
    assert valid_bucket in buckets
    assert valid_bucket.extra_config["endpoint_url"] == "http://some-other-url:1234"

    # No two buckets can share the same nickname.
    diff_bucket_kws = {
        "nickname": bucket_nickname,
        "uri": f"s3://{helpers.an_id(11)}",
        "extra_config": {"endpoint_url": "http://some-other-url:1234"},
    }
    with pytest.raises(ValueError, match="already exists"):
        _ = await aclient.create_bucket_config(org=org_name, **diff_bucket_kws)

    with pytest.raises(ValueError, match="Invalid platform"):
        _ = await aclient.create_bucket_config(org=org_name, nickname=bucket_nickname, uri="s4://my-bucket")

    with pytest.raises(ValueError, match="invalid auth_config"):
        _ = await aclient.create_bucket_config(org=org_name, nickname=bucket_nickname, uri="s3://my-bucket", auth_config={"method": "foo"})

    # Buckets can be modified after creation as long as they haven't been
    # assigned to a repo. After assignment to a repo, only the nickname
    # and/or auth_config can be modified.
    # modified_bucket = dict(auth_config=AnonymousAuth(method="anonymous"), extra_config={"foo": "bar"})
    # newer_bucket = await aclient.modify_bucket_config(org=org_name, nickname=bucket_nickname, **modified_bucket)
    # assert newer_bucket in await aclient.list_bucket_configs(org_name)
    # assert newer_bucket.extra_config == {"foo": "bar"}

    arepo = await aclient.create_repo(repo_name, bucket_config_nickname=bucket_nickname, kind=RepoKind.V1)
    repos = [f"{org_name}/{r.name}" for r in await aclient.list_repos_for_bucket_config(org=org_name, nickname=bucket_nickname)]
    assert repos == [arepo.repo_name]

    # remodified_bucket = BucketModifyRequest(auth_config=AnonymousAuth(method="anonymous"))
    # newer_bucket = await aclient.modify_bucket_config(org=org_name, nickname=bucket_nickname, bucket_config=remodified_bucket)
    # assert newer_bucket.auth_method == "anonymous"

    # new_nickname = helpers.an_id(5)
    # remodified_bucket = BucketModifyRequest(nickname=new_nickname)
    # newer_bucket = await aclient.modify_bucket_config(org=org_name, nickname=bucket_nickname, bucket_config=remodified_bucket)
    # assert newer_bucket.nickname == new_nickname
    # bucket_nickname = new_nickname

    # disabled_modifications = {
    #     "name": f"{bucket_name}_1",
    #     "prefix": f"{prefix}_1",
    #     "platform": "minio",
    #     "extra_config": {"foo": "blarg"},
    # }

    # for k, v in disabled_modifications.items():
    #     remodified_bucket = BucketModifyRequest()
    #     setattr(remodified_bucket, k, v)
    #     with pytest.raises(ValueError, match="in use by a repo and cannot be modified") as exc_info:
    #         newer_bucket = await aclient.modify_bucket_config(org=org_name, nickname=bucket_nickname, bucket_config=remodified_bucket)

    # Buckets cannot be deleted if they are assigned to a repo.
    with pytest.raises(ValueError, match="in use by a repo and cannot be modified") as exc_info:
        await aclient.delete_bucket_config(org=org_name, nickname=bucket_nickname, imsure=True, imreallysure=True)

    # Buckets can be modified and deleted if they are not assigned to a repo.
    await aclient.delete_repo(repo_name, imsure=True, imreallysure=True)
    assert await aclient.list_repos_for_bucket_config(org=org_name, nickname=bucket_nickname) == []

    # Now that the bucket is no longer assigned to a repo, it can be modified.
    # remodified_bucket = BucketModifyRequest(extra_config={"foo": "baz"})
    # newer_bucket = await aclient.modify_bucket_config(org=org_name, nickname=bucket_nickname, bucket_config=remodified_bucket)
    # assert newer_bucket.extra_config == {"foo": "baz"}poe

    # set up one more bucket before deleting the default one
    diff_bucket_kws = {
        "nickname": second_bucket_nickname + "-bonus",
        "uri": f"s3://{bucket_name}/bonus",
        "extra_config": {"region_name": "us-west-2"},
    }
    await aclient.create_bucket_config(org=org_name, **diff_bucket_kws)

    # Ensure that deleting the pre-existing default bucket will
    # promote the oldest existing bucket to default.
    await aclient.delete_bucket_config(org=org_name, nickname=bucket_nickname, imsure=True, imreallysure=True)
    num_default = 0
    bucket_configs = await aclient.list_bucket_configs(org_name)
    for b in bucket_configs:
        assert b.nickname != bucket_nickname
        if b.is_default:
            num_default += 1
    assert num_default == 1


@pytest.mark.parametrize(
    "wants_managed_sessions,checkout_flag,created_server_session",
    [(False, False, False), (False, True, False), (True, False, False), (True, True, True)],
)
@pytest.mark.asyncio
async def test_get_repo_obeys_checkout_flag(
    org_name, test_user, token, respx_mock, wants_managed_sessions, checkout_flag, created_server_session
):
    mock_url = "https://test-arraylake-client.foo/"
    now = datetime.utcnow()
    timeout = timedelta(days=1)
    repo_name = "foo"
    user: UserInfo = test_user
    repo = dict(
        id="1234",
        org=org_name,
        name=repo_name,
        created=str(now),
        description="",
        status=dict(mode="online", initiated_by={"system_id": "x"}),
    )
    session = dict(
        _id=f"foo-{now.isoformat()}",
        start_time=now.isoformat(),
        expiration=(now + timeout).isoformat(),
        author_email="foo@earthmover.io",
        branch="main",
        base_commit=None,
        session_type=SessionType.write,
        summary="foo",
    )

    # mock api routes
    user_route = respx_mock.get(mock_url + "user").mock(return_value=Response(200, json=json.loads(user.model_dump_json())))
    repos_get_route = respx_mock.get(mock_url + f"orgs/{org_name}/repos").mock(return_value=Response(200, json=[repo]))
    repo_get_route = respx_mock.get(mock_url + f"repos/{org_name}/{repo_name}").mock(return_value=Response(200, json=repo))
    commits_get_route = respx_mock.get(mock_url + f"repos/{org_name}/{repo_name}/commits").mock(return_value=Response(200, json=[]))
    tags_get_route = respx_mock.get(mock_url + f"repos/{org_name}/{repo_name}/tags").mock(return_value=Response(200, json=[]))
    branches_get_route = respx_mock.get(mock_url + f"repos/{org_name}/{repo_name}/branches").mock(return_value=Response(200, json=[]))
    session_post_route = respx_mock.post(mock_url + f"repos/{org_name}/{repo_name}/sessions").mock(return_value=Response(200, json=session))
    test_config = {"server_managed_sessions": wants_managed_sessions}
    with config.set(test_config):
        client = Client(service_uri=mock_url, token=token)

        _ = client.get_repo(f"{org_name}/{repo_name}", checkout=checkout_flag)
        assert created_server_session == any(
            [call.request.method == "POST" and call.request.url.path.endswith("/sessions") for call in respx_mock.calls]
        )

        _ = client.get_or_create_repo(f"{org_name}/{repo_name}", checkout=checkout_flag)
        assert created_server_session == any(
            [call.request.method == "POST" and call.request.url.path.endswith("/sessions") for call in respx_mock.calls]
        )
