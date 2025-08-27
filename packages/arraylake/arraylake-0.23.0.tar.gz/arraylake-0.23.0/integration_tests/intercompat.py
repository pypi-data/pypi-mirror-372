import warnings

import boto3
import click
import numpy as np
import xarray as xr

import arraylake
from arraylake import Client, config
from arraylake.repos.v1.repo import Repo
from arraylake.types import RepoKind

warnings.filterwarnings("ignore")


def get_expected_version(version):
    parts = arraylake.__version__.split(".")
    semver, rest = [int(x) for x in parts[:3]], parts[3:]
    if semver[1] <= 8:
        if semver[2] <= 1 and not rest:
            return 0
    return 1


IS_NEW_CLIENT = get_expected_version(arraylake.__version__) == 1

client = Client(service_uri="http://localhost:8000")
session = boto3.session.Session()
s3 = session.client(service_name="s3", endpoint_url="http://localhost:9000")


@click.group()
def cli() -> None:
    pass


# def write_data(repo):
#     shape = (1000,)
#     data = np.random.randint(9999, size=shape)
#     ds = xr.Dataset({"foo": (("x",), data)})
#     encoding = {"foo": {"chunks": (1000,)}}
#     ds.to_zarr(repo.store, group="materialized/", zarr_version=3, encoding=encoding, mode="w")
#     repo.commit("write")


def write_data(repo, size, chunks, group):
    shape = (1000,)
    data = np.random.randint(9999, size=shape)
    ds = xr.Dataset({"foo": (("x",), data)})
    encoding = {"foo": {"chunks": (chunks,)}}
    ds.to_zarr(repo.store, group=f"{group}/", zarr_version=3, encoding=encoding, mode="w")


@cli.command()
@click.argument("org_repo_name")
@click.argument("bucket_prefix")
@click.option("--virtual", required=False, default=False, is_flag=True)
@click.option("--inline", required=False, default=False, is_flag=True)
def write_old_client_chunkstore_from_old(org_repo_name, bucket_prefix, virtual: bool = False, inline: bool = False):
    """
    If running the virtual version of this, load the test .nc file into minio
    AWS_ACCESS_KEY_ID=minio123 AWS_SECRET_ACCESS_KEY=minio123 aws s3 \
        --endpoint-url http://localhost:9000 \
        cp ./integration_tests/data/small.nc s3://arraylake-repo-bucket/
    """
    if IS_NEW_CLIENT:
        raise Exception("Client should be the old client")

    if virtual and inline:
        raise Exception("can not specify both virtual and inline")

    bucket_name = "arraylake-repo-bucket"
    with config.set({"chunkstore.uri": f"s3://{bucket_name}/{bucket_prefix}", "s3.endpoint_url": "http://localhost:9000"}):
        repo = client.create_repo(org_repo_name, kind=RepoKind.V1)

        if not isinstance(repo, Repo):
            raise ValueError(f"Unexpected repo type: {type(repo)}")

        if virtual:
            print("running virtual")
            url = "s3://arraylake-repo-bucket/small.nc"
            repo.add_virtual_netcdf(url, "test-virtual")
            repo.commit("wrote virtual")
        elif inline:
            write_data(repo, 1000, 100, "inline")
            repo.commit("wrote inline")
        else:
            write_data(repo, 1000, 500, "materialized")
            repo.commit("wrote materialized")


@cli.command()
@click.argument("org_repo_name")
@click.argument("bucket_prefix")
@click.option("--virtual", required=False, default=False, is_flag=True)
@click.option("--inline", required=False, default=False, is_flag=True)
def read_old_client_chunkstore_from_old(org_repo_name, bucket_prefix, virtual: bool = False, inline: bool = False):
    if IS_NEW_CLIENT:
        raise Exception("Client should be the old client")

    if virtual and inline:
        raise Exception("can not specify both virtual and inline")

    group = "inline" if inline else "materialized"

    bucket_name = "arraylake-repo-bucket"
    with config.set({"chunkstore.uri": f"s3://{bucket_name}/{bucket_prefix}", "s3.endpoint_url": "http://localhost:9000"}):
        if not virtual:
            repo = client.get_repo(org_repo_name)
            ds = xr.open_zarr(repo.store, group=group)
            print(ds.foo.data[:5])
        else:
            repo = client.get_repo(org_repo_name)
            ds = xr.open_zarr(repo.store, group="test-virtual")
            print(ds.lon.data[:5])


@cli.command()
@click.argument("org_repo_name")
@click.argument("bucket_prefix")
@click.option("--virtual", required=False, default=False, is_flag=True)
@click.option("--inline", required=False, default=False, is_flag=True)
def read_old_client_chunkstore_from_new(org_repo_name, bucket_prefix, virtual: bool = False, inline: bool = False):
    if not IS_NEW_CLIENT:
        raise Exception("Client should be the new client")

    group = "inline" if inline else "materialized"

    bucket_name = "arraylake-repo-bucket"
    with config.set({"chunkstore.uri": f"s3://{bucket_name}/{bucket_prefix}", "s3.endpoint_url": "http://localhost:9000"}):
        if not virtual:
            repo = client.get_repo(org_repo_name)
            ds = xr.open_zarr(repo.store, group=group)
            print(ds.foo.data[:5])
        else:
            repo = client.get_repo(org_repo_name)
            ds = xr.open_zarr(repo.store, group="test-virtual")
            print(ds.lon.data[:5])


@cli.command()
@click.argument("org_repo_name")
@click.argument("bucket_prefix")
def append_old_client_chunkstore_from_new(org_repo_name, bucket_prefix):
    bucket_name = "arraylake-repo-bucket"
    if not IS_NEW_CLIENT:
        raise Exception("Client should be the new client")

    with config.set({"chunkstore.uri": f"s3://{bucket_name}/{bucket_prefix}", "s3.endpoint_url": "http://localhost:9000"}):
        repo = client.get_repo(org_repo_name)

        if not isinstance(repo, Repo):
            raise ValueError(f"Unexpected repo type: {type(repo)}")

        write_data(repo, 1000, 500, "materialized")
        repo.commit("append old chunkstore from new client")


@cli.command()
@click.argument("org_repo_name")
@click.argument("bucket_prefix")
def append_old_client_chunkstore_from_old(org_repo_name, bucket_prefix):
    bucket_name = "arraylake-repo-bucket"
    if IS_NEW_CLIENT:
        raise Exception("Client should be the old client")

    with config.set({"chunkstore.uri": f"s3://{bucket_name}/{bucket_prefix}", "s3.endpoint_url": "http://localhost:9000"}):
        repo = client.get_repo(org_repo_name)

        if not isinstance(repo, Repo):
            raise ValueError(f"Unexpected repo type: {type(repo)}")

        write_data(repo, 1000, 500, "materialized")
        repo.commit("append old chunkstore from old client")


@cli.command()
@click.argument("org_repo_name")
@click.argument("bucket_prefix")
@click.option("--virtual", required=False, default=False, is_flag=True)
def write_old_chunkstore_from_new_client(org_repo_name, bucket_prefix, virtual: bool = False):
    """
    If running the virtual version of this, load the test .nc file into minio
    AWS_ACCESS_KEY_ID=minio123 AWS_SECRET_ACCESS_KEY=minio123 aws s3 \
        --endpoint-url http://localhost:9000 \
        cp ./integration_tests/data/small.nc s3://arraylake-repo-bucket/
    """
    if not IS_NEW_CLIENT:
        raise Exception("Client should be the new client")

    bucket_name = "arraylake-repo-bucket"
    with config.set({"chunkstore.uri": f"s3://{bucket_name}/{bucket_prefix}", "s3.endpoint_url": "http://localhost:9000"}):
        repo = client.create_repo(org_repo_name)

        if not isinstance(repo, Repo):
            raise ValueError(f"Unexpected repo type: {type(repo)}")

        if not virtual:
            write_data(repo, 1000, 500, "materialized")
            repo.commit("wrote classic chunkstore from new client")

        if virtual:
            print("running virtual")
            url = "s3://arraylake-repo-bucket/small.nc"
            repo.add_virtual_netcdf(url, "test-virtual")
            repo.commit("wrote virtual")


@cli.command()
@click.argument("org_repo_name")
@click.argument("bucket_nickname")
@click.option("--virtual", required=False, default=False, is_flag=True)
def write_new_client_chunkstore_from_new(org_repo_name, bucket_nickname, virtual: bool = False, inline: bool = False):
    """
    If running the virtual version of this, load the test .nc file into minio
    AWS_ACCESS_KEY_ID=minio123 AWS_SECRET_ACCESS_KEY=minio123 aws s3 \
        --endpoint-url http://localhost:9000 \
        cp ./integration_tests/data/small.nc s3://arraylake-repo-bucket/
    """
    if not IS_NEW_CLIENT:
        raise Exception("Client should be the new client")

    if all([virtual, inline]):
        raise Exception("can not specify both virtual and inline")

    with config.set({"s3.endpoint_url": "http://localhost:9000"}):
        repo = client.create_repo(org_repo_name, bucket_config_nickname=bucket_nickname)

        if not isinstance(repo, Repo):
            raise ValueError(f"Unexpected repo type: {type(repo)}")

        if virtual:
            print("running virtual")
            url = "s3://arraylake-repo-bucket/small.nc"
            repo.add_virtual_netcdf(url, "test-virtual")
            repo.commit("wrote virtual")
        elif inline:
            write_data(repo, 1000, 100, "inline")
            repo.commit("wrote inline")
        else:
            write_data(repo, 1000, 500, "materialized")
            repo.commit("wrote materialized")


@cli.command()
@click.argument("org_repo_name")
@click.option("--virtual", required=False, default=False, is_flag=True)
def read_new_client_chunkstore_from_new(org_repo_name, virtual: bool = False):
    if not IS_NEW_CLIENT:
        raise Exception("Client should be the new client")

    repo = client.get_repo(org_repo_name)

    if not virtual:
        ds = xr.open_zarr(repo.store, group="materialized")
        print(ds.foo.data[:5])
    else:
        ds = xr.open_zarr(repo.store, group="test-virtual")
        print(ds.lon.data[:5])


@cli.command()
@click.argument("org_repo_name")
@click.option("--virtual", required=False, default=False, is_flag=True)
def read_new_client_chunkstore_from_old(org_repo_name, virtual: bool = False):
    if IS_NEW_CLIENT:
        raise Exception("Client should be the old client")

    with config.set({"s3.endpoint_url": "http://localhost:9000"}):
        repo = client.get_repo(org_repo_name)

        if not virtual:
            try:
                ds = xr.open_zarr(repo.store, group="materialized")
                print(ds.foo.data[:5])
            except Exception as e:
                if "NoSuchKey" in str(e):
                    print("boto NoSuchKey: could not open repo for read, as expected")
                else:
                    raise e
        else:
            ds = xr.open_zarr(repo.store, group="test-virtual")
            print(ds.lon.data[:5])


@cli.command()
@click.argument("org_repo_name")
def append_new_client_chunkstore_from_old(org_repo_name):
    if IS_NEW_CLIENT:
        raise Exception("Client should be the old client")
    repo = client.get_repo(org_repo_name)
    try:
        write_data(repo, 1000, 500, "materialized")
    except ValueError as e:
        if "Invalid chunk manifest version" in str(e):
            print("Invalid chunk manifest version, as expected")
        else:
            raise e


if __name__ == "__main__":
    cli()
