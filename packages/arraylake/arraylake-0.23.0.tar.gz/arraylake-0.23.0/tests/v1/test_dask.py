from uuid import uuid4

import pytest

dsa = pytest.importorskip("dask.array")


@pytest.mark.add_object_store("gs")
def test_dask_array_read_write(new_sync_repo, dask_cluster):
    array_name = uuid4().hex

    # create a dask array and store it
    a = dsa.random.random(8, chunks=4)
    a.to_zarr(new_sync_repo.store, component=array_name, zarr_version=3)
    new_sync_repo.commit("wrote array")

    # read it back
    afz = dsa.from_zarr(new_sync_repo.store, component=array_name, zarr_version=3)

    # reading one chunk works fine!
    with dask_cluster.get_client():
        afz[:4].compute()
    # so does reading more than one
    # regression test for https://github.com/earth-mover/arraylake/issues/337
    with dask_cluster.get_client():
        afz[:].compute()
