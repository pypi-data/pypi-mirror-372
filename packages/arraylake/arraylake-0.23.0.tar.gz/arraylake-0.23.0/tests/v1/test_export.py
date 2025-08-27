from uuid import uuid4

import pytest
import yaml

from .test_cli import invoke
from .test_xarray import all_dsets, requires_xarray

from arraylake import Client
from arraylake.cli.export import ExportManager, ExportTarget


@pytest.fixture(params=[True, False])
def object_store_destination_and_extra_config(object_store_config, tmp_path, request):
    as_yaml = request.param
    base_uri = object_store_config["chunkstore.uri"]
    if not base_uri.startswith("s3://"):
        pytest.skip("Test requires S3-compatible object store")
    destination_uri = base_uri + "/export-" + uuid4().hex
    extra_config = {"endpoint_url": object_store_config["s3.endpoint_url"]}
    if as_yaml:
        # TODO: random file name?
        config_file = tmp_path / "export_config.yaml"
        config_file.write_text(yaml.safe_dump(extra_config))
        yield destination_uri, str(config_file)
    else:
        yield destination_uri, extra_config


@pytest.mark.parametrize(param=["a", "b"])
@pytest.fixture
def tmp_path_destination_and_extra_config(tmp_path, request):
    return tmp_path, None


@pytest.fixture(params=["zarr2", "zarr3alpha"])
def format(request):
    return request.param


@pytest.fixture
def src_dst_path(format):
    if format == "zarr2":
        return "data/root/foo/bar/c0/1/2", "foo/bar/0.1.2"
    elif format == "zarr3alpha":
        return "data/root/foo/bar/c0/1/2", "data/root/foo/bar/c0/1/2"
    else:
        raise ValueError(f"unknown format {format}")


@pytest.fixture(
    params=[pytest.lazy_fixture("tmp_path_destination_and_extra_config"), pytest.lazy_fixture("object_store_destination_and_extra_config")]
)
def export_target(request, format):
    destination, extra_config = request.param
    export_target = ExportTarget(
        destination=destination,
        format=format,
        extra_config=extra_config,
    )
    return export_target


@pytest.mark.asyncio
async def test_export_target(export_target, src_dst_path):
    src_path, dst_path = src_dst_path
    await export_target.setup()

    assert export_target.group is not None

    # bare bones test of write - does not exercise edge cases
    source_bytes = b"bar"
    nbytes = export_target.write(src_path, source_bytes)
    assert nbytes == len(source_bytes)
    assert export_target.group.store[dst_path] == source_bytes

    assert dst_path == export_target.transform_path(src_path)
    # test delete
    assert dst_path in export_target.group.store
    export_target.delete(src_path)
    assert dst_path not in export_target.group.store


@pytest.fixture(params=all_dsets)
def xarray_dset(request):
    xr = pytest.importorskip("xarray")

    # not decoding simplifies round trip consistency tests
    ds = xr.tutorial.open_dataset(request.param, decode_cf=False)
    return ds


@pytest.fixture
def repo_name(isolated_org_name):
    repo_name = f"{isolated_org_name}/{uuid4().hex}"

    client = Client()
    client.create_repo(repo_name)
    return repo_name


@pytest.fixture
def export_manager(repo_name, export_target):
    return ExportManager(
        repo=repo_name,
        target=export_target,
    )


@requires_xarray
@pytest.mark.asyncio
async def test_export(xarray_dset, repo_name, export_manager):
    xr = pytest.importorskip("xarray")

    ds = xarray_dset
    ds = ds.chunk("2MB")

    client = Client()
    repo = client.get_repo(repo_name)

    ds.to_zarr(repo.store, zarr_version=3)
    repo.commit("stored dataset")
    ds_source = repo.to_xarray("", decode_cf=False)

    async with export_manager as manager:
        await manager.copy_data()

    ds_target = xr.open_zarr(export_manager.target.group.store, decode_cf=False).load()
    ds_source.load()
    xr.testing.assert_identical(ds_source, ds_target)


@requires_xarray
@pytest.mark.asyncio
async def test_export_between_refs(xarray_dset, repo_name, export_target):
    xr = pytest.importorskip("xarray")

    ds = xarray_dset
    ds = ds.chunk("2MB")

    client = Client()
    repo = client.get_repo(repo_name)

    ds.to_zarr(repo.store, zarr_version=3)
    first_commit = repo.commit("stored dataset")

    first_array_name = [k for (k, v) in repo.root_group.arrays()][0]
    repo.root_group[first_array_name].attrs["foo"] = "bar"
    second_commit = repo.commit("modified attrs")

    repo.root_group[first_array_name][:] *= -1
    third_commit = repo.commit("inverted first array values")

    # For each commit:
    # - perform an incremental copy
    # - checkout the repo as of that commit
    # - compare the repo and the exported copy
    commits = [first_commit, second_commit, third_commit]

    for idx, commit in enumerate(commits):
        from_ref = None

        if idx > 0:
            from_ref = commits[idx - 1]

        mgr = ExportManager(repo_name, export_target, from_ref=from_ref, ref=commit)

        async with mgr as manager:
            await manager.copy_data()

            repo.checkout(commit)
            ds_source = repo.to_xarray("", decode_cf=False).load()

            ds_target = xr.open_zarr(manager.target.group.store, decode_cf=False).load()
            xr.testing.assert_identical(ds_source, ds_target)
