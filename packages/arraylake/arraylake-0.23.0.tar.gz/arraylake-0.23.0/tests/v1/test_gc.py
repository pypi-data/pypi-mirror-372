import datetime
import secrets
import time

import aiobotocore
import arraylake_mongo_metastore.expiration.collect as collect
import arraylake_mongo_metastore.expiration.generate as squash
import pytest
from tests.v1.helpers.test_utils import metastore_params_only_mongo_27018

from arraylake import Client, config

shape = (10, 300, 300)
chunks = (10, 30, 30)


async def mk_repo(num_commits):
    al_client = Client()
    org = "bucketty"
    repo_name = secrets.token_hex(10)
    full_repo_name = f"{org}/{repo_name}"
    repo = al_client.get_or_create_repo(full_repo_name, bucket_nickname="test")
    repo_data = next(repo for repo in al_client.list_repos(org) if repo.name == repo_name)

    import numpy as np
    from numpy.random import rand

    commits = []

    array = repo.root_group.create("array", shape=shape, chunks=chunks, dtype="f4", fill_value=np.nan)
    commits.append(repo.commit("empty array created"))

    for time in range(num_commits):
        array = repo.root_group["array"]
        array[time % shape[0], :, :] = rand(*shape[1:])[:]
        commits.append(repo.commit(f"time={time}"))

    return (repo, repo_data, commits)


async def calculate_s3_space(client, bucket_name, repo_id):
    total_size = 0
    total_keys = 0
    async for obj in collect.bucket_objects(client, bucket_name, repo_id.hex()):
        total_size += obj["Size"]
        total_keys += 1
    return (total_keys, total_size)


@pytest.mark.skip(reason="some of this code is unmantained as we are moving it to Rust")
@pytest.mark.parametrize("metastore_class_and_config", metastore_params_only_mongo_27018)
@pytest.mark.slow
@pytest.mark.asyncio
async def test_gc(metastore):
    """
    Create a repository with 5 commits that overwrite the same chunks. The chunks are shaped
    as pancakes but with a time chunk size != 1. Every commit writes to one time dimensions 0 <= t < 5.
    Then we squash all 5 commits into 1, and run garbage collection.
    We check the result of GC and the number and size of keys in S3.
    This test uses minio for the chunkstore and "bucketty", the seeded org with bucket information.
    """
    bucket_name = "arraylake-repo-bucket"  # this comes from orgs-config.yaml
    num_commits = 5
    repo, repo_data, commits = await mk_repo(num_commits)
    try:
        async with aiobotocore.session.get_session().create_client(
            "s3", endpoint_url="http://localhost:9000", aws_secret_access_key="minio123", aws_access_key_id="minio123"
        ) as client:
            database = await metastore.open_database(repo_data.id.hex())

            keys_before, size_before = await calculate_s3_space(client, bucket_name, repo_data.id)
            assert keys_before == num_commits * pow(shape[1], 2) / pow(chunks[1], 2)

            database = await metastore.open_database(repo_data.id.hex())
            await squash.squash_commits(database, commits[-1], list(reversed(commits[:-1])))

            database = await metastore.open_database(repo_data.id.hex())
            gc_notifier = collect.GCReportNotifier()
            gc_settings = collect.GCSettings(
                bucket_name=bucket_name,
                repo_prefix=repo_data.id.hex(),
                dry_run=True,
                dont_delete_after=datetime.datetime.now(datetime.timezone.utc),
                notifier=gc_notifier,
            )

            # We do a dry_run GC first
            await collect.gc(client, database, gc_settings)
            report = gc_notifier.report

            keys_after, size_after = await calculate_s3_space(client, bucket_name, repo_data.id)

            assert size_after == size_before
            assert keys_after == keys_before

            assert report.repository_retained_keys == pow(shape[1], 2) / pow(chunks[1], 2)
            assert report.repository_retained_virtual_keys == 0
            assert report.manifest_key_errors == 0
            assert report.deleted_keys == (num_commits - 1) * pow(shape[1], 2) / pow(chunks[1], 2)
            assert report.deleted_bytes > 0
            assert report.time_taken.total_seconds() > 0
            assert report.deletion_errors == 0
            assert report.ignored_virtual_keys == 0
            assert report.ignored_inline_keys == 0
            assert report.ignored_absolute_keys == 0
            assert report.ignored_recent_keys == 0
            assert report.manifest_key_errors == 0
            assert report.required_keys_not_found == set()

            # now we do a real GC, but setup so it doesn't delete recent keys,
            # it should delete nothing
            gc_notifier = collect.GCReportNotifier()
            gc_settings.dry_run = False
            gc_settings.dont_delete_after = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
            gc_settings.notifier = gc_notifier

            await collect.gc(client, database, gc_settings)
            report = gc_notifier.report

            keys_after, size_after = await calculate_s3_space(client, bucket_name, repo_data.id)

            assert size_after == size_before
            assert keys_after == keys_before

            assert report.ignored_recent_keys == (num_commits - 1) * pow(shape[1], 2) / pow(chunks[1], 2)
            assert report.repository_retained_keys == pow(shape[1], 2) / pow(chunks[1], 2)
            assert report.repository_retained_virtual_keys == 0
            assert report.manifest_key_errors == 0
            assert report.deleted_keys == 0
            assert report.deleted_bytes == 0
            assert report.time_taken.total_seconds() > 0
            assert report.deletion_errors == 0
            assert report.ignored_virtual_keys == 0
            assert report.ignored_inline_keys == 0
            assert report.ignored_absolute_keys == 0
            assert report.manifest_key_errors == 0
            assert report.required_keys_not_found == set()

            # and now we do a real GC, deleting objects
            gc_notifier = collect.GCReportNotifier()
            gc_settings.dont_delete_after = datetime.datetime.now(datetime.timezone.utc)
            gc_settings.notifier = gc_notifier

            # But we manually delete a random retained key from S3 to check that it's reported missing
            hash = repo._get_chunk_ref("data/root/array/c0/0/0").hash["token"]
            missing_key = f"{repo_data.id.hex()}/{hash}"
            delete_res = await client.delete_object(Bucket=bucket_name, Key=missing_key)
            assert delete_res["ResponseMetadata"]["HTTPStatusCode"] == 204

            # we need to recompute this now that we deleted one key
            keys_before, size_before = await calculate_s3_space(client, bucket_name, repo_data.id)

            await collect.gc(client, database, gc_settings)
            report = gc_notifier.report

            keys_after, size_after = await calculate_s3_space(client, bucket_name, repo_data.id)
            assert size_after < 0.5 * size_before
            assert keys_after == 1 * pow(shape[1], 2) / pow(chunks[1], 2) - 1

            assert report.repository_retained_keys == pow(shape[1], 2) / pow(chunks[1], 2)
            assert report.repository_retained_virtual_keys == 0
            assert report.manifest_key_errors == 0
            assert report.deleted_keys == (num_commits - 1) * pow(shape[1], 2) / pow(chunks[1], 2)
            assert report.deleted_bytes > 0
            assert report.time_taken.total_seconds() > 0
            assert report.deletion_errors == 0
            assert report.ignored_virtual_keys == 0
            assert report.ignored_inline_keys == 0
            assert report.ignored_absolute_keys == 0
            assert report.ignored_recent_keys == 0
            assert report.manifest_key_errors == 0
            assert report.required_keys_not_found == {missing_key}

            assert size_before - report.deleted_bytes == size_after

            # if we do GC again, it shouldn't find any of the retained keys
            gc_notifier = collect.GCReportNotifier()
            gc_settings.notifier = gc_notifier
            await collect.gc(client, database, gc_settings)
            report = gc_notifier.report

            assert report.repository_retained_keys == pow(shape[1], 2) / pow(chunks[1], 2)
            assert report.repository_retained_virtual_keys == 0
            assert report.manifest_key_errors == 0
            assert report.deleted_keys == 0
            assert report.deleted_bytes == 0
            assert report.time_taken.total_seconds() > 0
            assert report.deletion_errors == 0
            assert report.ignored_virtual_keys == 0
            assert report.ignored_inline_keys == 0
            assert report.ignored_absolute_keys == 0
            assert report.ignored_recent_keys == 0
            assert report.manifest_key_errors == 0
            assert report.required_keys_not_found == {missing_key}

    finally:
        await metastore.delete_database(repo_data.id.hex(), imsure=True, imreallysure=True)
