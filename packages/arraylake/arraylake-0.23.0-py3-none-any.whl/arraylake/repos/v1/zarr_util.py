"""DEPRECATED: This V1 zarr_util module is pending removal.
V1 repositories are legacy and will be phased out in favor of Icechunk repositories.
This module and all its contents are scheduled for removal in a future version.
"""

import json
import re
from collections.abc import Sequence
from typing import Union

META_ROOT = "meta/root/"
DATA_ROOT = "data/root/"

# https://zarr-specs.readthedocs.io/en/latest/core/v3.0.html#entry-point-metadata
ENTRY_POINT_METADATA = json.dumps(
    {
        "zarr_format": "https://purl.org/zarr/spec/core/3.0",
        "metadata_encoding": "https://purl.org/zarr/spec/core/3.0",
        "metadata_key_suffix": ".json",
        "extensions": [],
    }
).encode()


def is_chunk_key(key):
    return key.startswith("data/")


def is_meta_key(key):
    return key.startswith("meta/") or key == "zarr.json"


def is_v2_chunk_key(key):
    """is key a valid v2 key

    examples:
      - "foo/bar/spam/1.2.3.4"
      - "foo/bar/0.0"
      - "foo/0"
    """
    segments = key.split("/")
    if segments:
        last_segment = segments[-1]
        return re.match(r"^(\d+\.)*\d+$", last_segment) is not None


def sort_keys(keys: Sequence[str]) -> tuple[list[str], list[str]]:
    """Convenience function to sort keys into meta_keys and chunk_keys"""
    chunk_keys = []
    meta_keys = []
    bad_keys = []
    for key in keys:
        if is_chunk_key(key):
            chunk_keys.append(key)
        elif is_meta_key(key):
            meta_keys.append(key)
        else:  # pragma: no cover
            bad_keys.append(key)
    if bad_keys:  # pragma: no cover
        # don't expect to get here because we have already called self._validate_key
        raise ValueError(f"unexpected keys: {key}")
    return meta_keys, chunk_keys


# vendored from Zarr
# https://github.com/zarr-developers/zarr-python/blob/ed94877ff69d859f2e9d412e775e2887bc6c71bf/zarr/util.py#L340C1-L380C16
def normalize_storage_path(path: Union[str, bytes, None]) -> str:
    # handle bytes
    if isinstance(path, bytes):
        path = str(path, "ascii")

    # ensure str
    if path is not None and not isinstance(path, str):
        path = str(path)

    if path:
        # convert backslash to forward slash
        path = path.replace("\\", "/")

        # ensure no leading slash
        while len(path) > 0 and path[0] == "/":
            path = path[1:]

        # ensure no trailing slash
        while len(path) > 0 and path[-1] == "/":
            path = path[:-1]

        # collapse any repeated slashes
        previous_char = None
        collapsed = ""
        for char in path:
            if char == "/" and previous_char == "/":
                pass
            else:
                collapsed += char
            previous_char = char
        path = collapsed

        # don't allow path segments with just '.' or '..'
        segments = path.split("/")
        if any(s in {".", ".."} for s in segments):
            raise ValueError("path containing '.' or '..' segment not allowed")

    else:
        path = ""

    return path
