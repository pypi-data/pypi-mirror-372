import os
from uuid import uuid4

import pytest
from tests.v1.helpers.test_utils import get_sync_repo

from .. import requires_distributed

from arraylake import Client


@pytest.fixture(scope="module")
def data():
    dsa = pytest.importorskip("dask.array")
    seed = 993
    shape = 2_000_000
    chunks = 10_000

    state = dsa.random.RandomState(seed)
    data = state.random(shape, chunks=chunks)
    return data


@pytest.fixture(params=[True, False])
def compute(data, request):
    delay_compute = request.param
    key = f"to_zarr_compute_{delay_compute}"
    if delay_compute:

        def _compute(store):
            data.to_zarr(store, component=key, zarr_version=3, compressor=None, compute=False).compute()

    else:

        def _compute(store):
            data.to_zarr(store, component=key, zarr_version=3, compressor=None, compute=True)

    return _compute


@requires_distributed
@pytest.mark.asyncio
@pytest.mark.add_object_store("gs")
async def test_memory_leak_compute_true(chunkstore_bucket, user, dask_cluster, compute, helpers):
    from distributed.diagnostics import MemorySampler

    key = "to_zarr_compute_true"
    ms = MemorySampler()
    with dask_cluster.get_client() as dclient:
        dclient.restart()
        with ms.sample(key):
            sync_repo = await get_sync_repo(chunkstore_bucket, helpers.random_repo_id(), user, shared=False)
            compute(sync_repo.store)
    max_memory_used = ms.to_pandas().max()[key]
    assert max_memory_used < 1000000000
