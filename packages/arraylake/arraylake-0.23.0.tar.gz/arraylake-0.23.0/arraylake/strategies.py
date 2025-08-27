"""
DEPRECATED: This V1 testing strategies module is pending removal.
V1 repositories are legacy and will be phased out in favor of Icechunk repositories.
This module and all its contents are scheduled for removal in a future version.
This file is only used by V1 tests and can be removed when V1 support is dropped.
"""

import datetime

import bson
import hypothesis.strategies as st
import xarray.testing.strategies as xrst

from arraylake.repos.v1.zarr_util import META_ROOT

# Copied from Xarray
# only use characters within the "Latin Extended-A" subset of unicode
_readable_characters = st.characters(categories=["L", "N"], max_codepoint=0x017F)
_attr_keys = st.text(_readable_characters, min_size=1)
_attr_values = st.recursive(
    st.none() | st.booleans() | xrst._readable_strings,  # | xrst._small_arrays
    lambda children: st.lists(children) | st.dictionaries(_attr_keys, children),
    max_leaves=3,
)

# No '/' in array names?
# No '.' in paths?
zarr_key_chars = st.sampled_from("-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz")

# Strategies for testing
meta_paths = st.lists(
    st.text(zarr_key_chars, min_size=1),
    min_size=1,
    max_size=5,
).map(lambda x: META_ROOT + "/".join(x) + ".json")
group_paths = st.just("/") | st.text(zarr_key_chars, min_size=1)
xarray_variables = xrst.variables(attrs=st.none() | st.dictionaries(_attr_keys, _attr_values))  # type: ignore[arg-type]
array_names = st.text(zarr_key_chars | st.just("."), min_size=1).filter(lambda t: not t.startswith((".", "..")))

# These object Ids will never be created during tests unless we mess with the time.
invalid_object_ids = st.datetimes(
    # empirically determined
    min_value=datetime.datetime(1970, 1, 1),
    max_value=datetime.datetime.now() - datetime.timedelta(days=1),
).map(lambda dt: bson.objectid.ObjectId.from_datetime(dt))
