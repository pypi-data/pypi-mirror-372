import pytest

pytest.importorskip("hypothesis")
pytest.importorskip("xarray")

import hypothesis.strategies as st
import xarray as xr
from hypothesis import HealthCheck, given, settings

import arraylake.strategies as alst


@pytest.mark.slow
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(path=st.none() | alst.group_paths, var=alst.xarray_variables, name=alst.array_names)
def test_roundtrip_xarray(new_sync_repo, path, var, name):
    # The new_sync_repo fixture is function-scoped but will not be created on every hypothesis test
    # So we disable that HealthCheck, and checkout("main") to reset the state of the repo.
    # This seems to work.
    new_sync_repo.checkout("main")
    assert not new_sync_repo.status().modified_paths

    ds = xr.Dataset({name: var})
    ds.to_zarr(new_sync_repo.store, group=path, zarr_version=3)
    actual = new_sync_repo.to_xarray(path)
    xr.testing.assert_identical(ds, actual)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None, max_examples=10)
@given(ref=alst.invalid_object_ids, as_string=st.booleans())
def test_checkout_bad_commit(new_sync_repo, ref, as_string):
    # EAR-874
    if as_string:
        ref = str(ref)
    with pytest.raises(ValueError):
        new_sync_repo.checkout(ref)
