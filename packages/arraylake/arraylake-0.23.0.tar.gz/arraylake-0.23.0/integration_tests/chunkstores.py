import inspect
import random
import re
import string

import boto3
import numpy as np
import pytest
import xarray as xr

import arraylake
from arraylake import Client, config
from arraylake.repos.v1.chunkstore import BaseChunkstore

print("\n".join([arraylake.__version__, "***"]))
try:
    from arraylake.repos.v1.types import ChunkstoreSchemaVersion
except Exception:
    print("could not import new types, probably on old AL client")


def rdms(n):
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


def get_expected_version(version):
    parts = arraylake.__version__.split(".")
    semver, rest = [int(x) for x in parts[:3]], parts[3:]
    if semver[1] <= 8:
        if semver[2] <= 1 and not rest:
            return 0
    return 1


IS_NEW_CLIENT = get_expected_version(arraylake.__version__) == 1


def get_or_create_repo_with_org_bucket_config(client, org_name, repo_name, invalid_bucket_nickname, valid_bucket_nickname):
    """QA items:
    - get_or_create_repo works both for creation and for get (with bucket_nickname argument)
    - create_repo fails in a nice way if the bucket_nickname doesn’t exist
    """
    print(inspect.stack()[0][3])

    def _assertions(chunkstore: BaseChunkstore):
        if IS_NEW_CLIENT:
            assert chunkstore.schema_version == ChunkstoreSchemaVersion.V1, "schema is correct version"
            assert chunkstore.bucket_name == "arraylake-repo-bucket"
            assert len(chunkstore.prefix) == 24
        else:
            # in the case of a bucket config existing, we'll get our prior version of a "v1" chunkstore
            # which was never utilized by clients, because it only kicked in if they had a org bucket configuration,
            # which we never did for any of them
            assert not hasattr(chunkstore, "schema_version"), "schema version not found"
            # if org bucket config is valid, we should expect to use relative addressing
            if hasattr(chunkstore, "use_relative_addressing"):
                assert chunkstore.use_relative_addressing
            assert chunkstore.bucket_name == "arraylake-repo-bucket"
            assert len(chunkstore.prefix) == 24

    # should raise if bucket is not available in bucket config
    with pytest.raises(ValueError, match=r"bucket .*"):
        client.get_or_create_repo(f"{org_name}/{repo_name}", bucket_nickname=invalid_bucket_nickname)

    with pytest.raises(ValueError, match=r"bucket .*"):
        client.create_repo(f"{org_name}/{repo_name}", bucket_nickname=invalid_bucket_nickname)

    # should complete if bucket is valid
    repo = client.get_or_create_repo(f"{org_name}/{repo_name}", bucket_nickname=valid_bucket_nickname)
    _assertions(repo._arepo.chunkstore)

    # trying to recreate the bucket but with a conflicting bucket id should raise
    # only exists in new versions
    if IS_NEW_CLIENT:
        with pytest.raises(ValueError, match=r"This repo exists.*"):
            repo = client.get_or_create_repo(f"{org_name}/{repo_name}", bucket_nickname=invalid_bucket_nickname)

    # test get_repo after repo has been created
    repo = client.get_repo(f"{org_name}/{repo_name}")
    _assertions(repo._arepo.chunkstore)

    # verify that modifying local config has no bearing on the bucket refs here
    configured_chunkstore_bucket = rdms(4)
    with config.set({"chunkstore.uri": f"s3://{configured_chunkstore_bucket}"}):
        repo = client.get_repo(f"{org_name}/{repo_name}")
        _assertions(repo._arepo.chunkstore)


def get_or_create_repo_no_org_bucket_config(client, org_name, repo_name):
    """The org passed to this test should not have a bucket config.

    In this case we expect repo instantiation to succeeed, using the users locally configured
    bucket information.

    QA items:
    - get_or_create_repo works both for creation and for get (without bucket_nickname argument)
    """
    print(inspect.stack()[0][3])

    # if the org has no bucket config, attempting to use one should fail in all cases
    with pytest.raises(ValueError, match=r"bucket .*"):
        client.get_or_create_repo(f"{org_name}/{repo_name}", bucket_nickname="some-name")

    def _assertions(chunkstore: BaseChunkstore, bucket_name: str):
        if IS_NEW_CLIENT:
            # no bucket config should see us create an old style repo
            assert chunkstore.schema_version == ChunkstoreSchemaVersion.V0, "schema is correct version"
            assert chunkstore.bucket_name == bucket_name
            assert chunkstore.prefix == ""
        else:
            assert not hasattr(chunkstore, "schema_version"), "schema version not found"
            if hasattr(chunkstore, "use_relative_addressing"):
                assert chunkstore.use_relative_addressing is False
            assert chunkstore.bucket_name == bucket_name
            assert chunkstore.prefix == ""

    configured_chunkstore_bucket = rdms(4)
    with config.set({"chunkstore.uri": f"s3://{configured_chunkstore_bucket}"}):
        repo = client.get_or_create_repo(f"{org_name}/{repo_name}")
        _assertions(repo._arepo.chunkstore, configured_chunkstore_bucket)

    # create a new local config and ensure we don't have a dupe
    new_configured_chunkstore_bucket = rdms(4)
    assert configured_chunkstore_bucket != new_configured_chunkstore_bucket

    # perform get_repo, but with a new local config
    with config.set({"chunkstore.uri": f"s3://{new_configured_chunkstore_bucket}"}):
        repo = client.get_repo(f"{org_name}/{repo_name}")
        _assertions(repo._arepo.chunkstore, new_configured_chunkstore_bucket)


def write_data(repo, size, chunks, group):
    shape = (1000,)
    data = np.random.randint(9999, size=shape)
    ds = xr.Dataset({"foo": (("x",), data)})
    encoding = {"foo": {"chunks": (chunks,)}}
    ds.to_zarr(repo.store, group=f"{group}/", zarr_version=3, encoding=encoding, mode="w")


def create_and_write_to_repo_with_no_org_bucket_config(client, org_name, repo_name, s3client):
    """QA items:

    - Latest version of the client can:
        - write and commit to old style repos (no bucket)
        - Manifests are written with V0 and absolute URIs
        - Chunks are written to the bucket in the local configuratio
    """
    print(inspect.stack()[0][3])

    bucket_name = "arraylake-repo-bucket"
    bucket_prefix = f"{rdms(4)}"

    # specify a config bucket to be used for old style creation
    with config.set({"chunkstore.uri": f"s3://{bucket_name}/{bucket_prefix}", "s3.endpoint_url": "http://localhost:9000"}):
        repo = client.get_or_create_repo(f"{org_name}/{repo_name}")

        size, chunks = 1000, 100
        write_data(repo, size, chunks, "inline")
        if IS_NEW_CLIENT:
            reference_datas = [repo._get_chunk_ref(c) for c in repo.store.list_prefix("data/root/inline")]
            assert len(reference_datas) == size / chunks
            for rd in reference_datas:
                assert rd.is_inline()
            objects = s3client.list_objects(Bucket=bucket_name, Prefix=bucket_prefix)
            assert not objects.get("Contents")

        def assert_materialized_v0_bucket_contents(s3, bucket_name, bucket_prefix, length):
            # note: bucket_prefix in this case is something different than a new, official, 'prefix' which
            # is the repo.id. in this case, it's just a prefix we're using for testing to help give some
            # isolation during testing. i.e. the "bucket" configured for this old style repo looks like this:
            # s3://{bucket_name}/{bucket_prefix}
            objects = s3client.list_objects(Bucket=bucket_name, Prefix=bucket_prefix)["Contents"]
            keys = [o["Key"].replace(f"{bucket_prefix}/", "") for o in objects]
            assert len(keys) == 2
            for k in keys:
                assert re.match(r"[a-zA-Z0-9]{64}$", k)

        # write materialized
        size, chunks = 1000, 500
        write_data(repo, size, chunks, "materialized")
        repo.commit("new client writing old style")
        if IS_NEW_CLIENT:
            reference_datas = [repo._get_chunk_ref(c) for c in repo.store.list_prefix("data/root/materialized")]
            assert len(reference_datas) == size / chunks
            for rd in reference_datas:
                # Manifests are written with V0 and absolute URIs
                assert rd._is_materialized_v0()

            # Chunks are written to the bucket in the local configuration
            assert_materialized_v0_bucket_contents(s3client, bucket_name, bucket_prefix, 2)


def assert_materialized_v1_bucket_contents(s3client, bucket_name, prefix, length):
    objects = s3client.list_objects(Bucket=bucket_name, Prefix=prefix)["Contents"]
    keys = [o["Key"] for o in objects]
    assert len(keys) == 2
    for k in keys:
        assert re.match(prefix + r"\/chunks\/[a-zA-Z0-9]{64}\.[a-zA-Z0-9]{32}$", k)


def create_and_write_to_repo_with_org_bucket_config(client, org_name, repo_name, bucket_name, s3client):
    """QA items:
    - Writing chunks with a new style repo writes manifests with V1 and no URI
    - Writing chunks with a new style repo writes chunks to s3://bucket/repo_id/chunks/hash.session_id
    - Inline chunks can be written and read by the new client
    """
    print(inspect.stack()[0][3])

    repo = client.get_or_create_repo(f"{org_name}/{repo_name}", bucket_nickname=bucket_name)

    bucket_name = "arraylake-repo-bucket"

    size, chunks = 1000, 100

    if not IS_NEW_CLIENT:
        with pytest.raises(ValueError, match=r"chunk manifest"):
            write_data(repo, size, chunks, "inline")
    else:
        # - Inline chunks can be written and read by the new client
        write_data(repo, size, chunks, "inline")
        if IS_NEW_CLIENT:
            reference_datas = [repo._get_chunk_ref(c) for c in repo.store.list_prefix("data/root/inline")]
            assert len(reference_datas) == size / chunks
            for rd in reference_datas:
                assert rd.is_inline()

    size, chunks = 1000, 500
    if not IS_NEW_CLIENT:
        with pytest.raises(ValueError, match=r"chunk manifest"):
            write_data(repo, size, chunks, "materialized")

    else:
        write_data(repo, size, chunks, "materialized")
        if IS_NEW_CLIENT:
            reference_datas = [repo._get_chunk_ref(c) for c in repo.store.list_prefix("data/root/materialized")]
            assert len(reference_datas) == size / chunks
            for rd in reference_datas:
                # Writing chunks with a new style repo writes manifests with V1 and no URI
                assert rd._is_materialized_v1()

            # Writing chunks with a new style repo writes chunks to s3://bucket/repo_id/chunks/hash.session_id
            assert_materialized_v1_bucket_contents(s3client, bucket_name, repo._arepo.chunkstore.prefix, 2)


def create_and_get_repo_for_old_and_new_style_repos(client, org_name, repo_name, bucket_nickname):
    """QA items:
    -  get_repo works both for old style and new style repos (with or without associated bucket)
    """

    if IS_NEW_CLIENT:
        # create and get old style repo
        configured_chunkstore_bucket = rdms(4)
        with config.set({"chunkstore.uri": f"s3://{configured_chunkstore_bucket}"}):
            client.create_repo(f"{org_name}/{repo_name}-old")
            opened_old_style_repo = client.get_repo(f"{org_name}/{repo_name}-old")
            assert opened_old_style_repo._arepo.chunkstore.bucket_name == configured_chunkstore_bucket

        # create and get new style repo
        client.create_repo(f"{org_name}/{repo_name}-new", bucket_nickname=bucket_nickname)
        opened_new_style_repo = client.get_repo(f"{org_name}/{repo_name}-new")
        assert opened_new_style_repo._arepo.chunkstore.bucket_name == "arraylake-repo-bucket"


# TODO: add combination test, where we write with the old, and read with the new
# TODO: If new client writes an old repo, old client must be able to read & write it.
# TODO: If old client writes a repo, the new client must be albe to r/w
# TODO: YOu create a new style repo with new client. Then try to write with old client
# - server check will pass, as manifest is the same
# - we probably need to add check in service
# - try to write from old client to new style repo


@pytest.mark.asyncio
async def test_main():
    client = Client(service_uri="http://localhost:8000")
    org_name = "bucketty"  # this org is set up with buckets in yaml file
    org_name_no_bucket_config = "earthmover"

    def r():
        return f"test-chunkstore-{rdms(4)}"

    session = boto3.session.Session()

    s3 = session.client(service_name="s3", endpoint_url="http://localhost:9000")

    bucket_nickname = "test"
    get_or_create_repo_with_org_bucket_config(client, org_name, r(), f"{bucket_nickname}-invalid", bucket_nickname)

    get_or_create_repo_no_org_bucket_config(client, org_name_no_bucket_config, r())

    create_and_write_to_repo_with_no_org_bucket_config(client, org_name_no_bucket_config, r(), s3)

    create_and_write_to_repo_with_org_bucket_config(client, org_name, r(), bucket_nickname, s3)

    create_and_get_repo_for_old_and_new_style_repos(client, org_name, r(), bucket_nickname)


# if __name__ == '__main__':
#     asyncio.run(test_main())
