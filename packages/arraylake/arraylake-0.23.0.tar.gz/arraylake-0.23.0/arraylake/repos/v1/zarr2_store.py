"""DEPRECATED: This V1 zarr2_store module is pending removal.
V1 repositories are legacy and will be phased out in favor of Icechunk repositories.
This module and all its contents are scheduled for removal in a future version.
"""

import json
from collections.abc import Mapping
from typing import TYPE_CHECKING

from zarr._storage.store import StoreV3

from arraylake.log_util import get_logger
from arraylake.repos.v1.types import Path
from arraylake.repos.v1.zarr_util import (
    DATA_ROOT,
    ENTRY_POINT_METADATA,
    META_ROOT,
    is_chunk_key,
    is_meta_key,
    normalize_storage_path,
    sort_keys,
)

logger = get_logger(__name__)

if TYPE_CHECKING:
    from arraylake.repos.v1.repo import Repo


class ArraylakeStore(StoreV3):  # type: ignore  # no typying info for StoreV3
    """ArrayLake's Zarr Store interface

    This is an implementation of a [Zarr V3 Store](https://zarr-specs.readthedocs.io/en/latest/core/v3.0.html#id14).

    :::note
    This class is not intended to be constructed directly by users. Instead, use the `store` property on the `Repo` class.
    :::

    """

    def __init__(self, repo: "Repo"):
        self._repo = repo

    def list_prefix(self, prefix: str) -> list[str]:
        """List a prefix in the store

        Args:
            prefix : the path to list

        Returns:
            A list of document paths
        """
        return self._repo._wrap_async_iter(self._repo._arepo._list_prefix, prefix)

    def listdir(self, prefix: str) -> list[str]:
        """List a directory in the store

        Args:
            prefix: the path to list

        Returns:
            A list of document paths
        """
        return self._repo._wrap_async_iter(self._repo._arepo._list_dir, prefix)

    def getsize(self, prefix: str) -> int:
        data_prefix = DATA_ROOT + prefix
        return self._repo._synchronize(self._repo._arepo._getsize, data_prefix)

    def rmdir(self, dir: str) -> None:
        dir = normalize_storage_path(dir)
        meta_dir = (META_ROOT + dir).rstrip("")
        self._repo._synchronize(self._repo._arepo._del_prefix, meta_dir)
        data_dir = (DATA_ROOT + dir).rstrip("")
        self._repo._synchronize(self._repo._arepo._del_prefix, data_dir)

    def __getitem__(self, key) -> bytes:
        """Get a value

        Args:
            key: the path to get

        Returns:
            bytes (metadata or chunk)
        """
        if key == "zarr.json":
            return ENTRY_POINT_METADATA
        logger.debug("__getitem__", path=key, repo=self._repo.repo_name)
        self._validate_key(key)
        if is_chunk_key(key):
            return self._repo._get_chunk(key)
        elif is_meta_key(key):
            doc = self._repo._get_doc(key)
            return json.dumps(doc).encode()
        else:  # pragma: no cover
            # don't expect to ever reach this
            raise KeyError(f"unexpected key: {key}")

    def getitems(self, keys, *, contexts=None, on_error="omit") -> Mapping[str, bytes]:
        """Get multiple items

        Args:
            keys: list of paths to get

        Returns:
            Mapping where keys are paths and values are bytes (metadata or chunks)
        """
        logger.debug("getitems called with ", num_keys=len(keys), repo=self._repo.repo_name)

        if on_error != "omit":  # pragma: no cover
            raise ValueError("Only support on_error='omit' for now")
        for key in keys:
            self._validate_key(key)
        meta_keys, chunk_keys = sort_keys(keys)
        # TODO: can we have all of the needed queries in flight at the same time?
        # This two-step process is potentially inefficient
        chunk_docs = self._repo._get_chunks(chunk_keys) if chunk_keys else {}
        if "zarr.json" in meta_keys:
            meta_docs = {"zarr.json": ENTRY_POINT_METADATA}
            meta_keys.remove("zarr.json")
        else:
            meta_docs = {}
        if meta_keys:
            meta_docs.update({key: json.dumps(doc).encode() for key, doc in self._repo._get_docs(meta_keys).items()})

        # TODO: use this much better syntax once we drop Python 3.9
        # return meta_docs | chunk_docs
        return {**meta_docs, **chunk_docs}

    def __setitem__(self, key, value: bytes) -> None:
        """Set a value

        Args:
            key: the path to set

        Returns:
            bytes (metadata or chunk)
        """
        logger.debug("__setitem__", key=key)
        self._validate_key(key)
        if is_chunk_key(key):
            return self._repo._set_chunk(key, data=value)
        elif is_meta_key(key):
            if key == "zarr.json":
                raise KeyError("Cannot set zarr.json")
            doc = json.loads(value)
            return self._repo._set_doc(key, content=doc)
        else:
            raise KeyError(f"unexpected key: {key}")

    def setitems(self, items: Mapping[str, bytes]) -> None:
        """Set multiple items

        Args:
            keys : list of paths

        Returns:
            Mapping where keys are paths and values are bytes (metadata or chunks)
        """
        logger.debug("__setitems__ with ", nitems=len(items))

        for key in items:
            self._validate_key(key)
        meta_keys, chunk_keys = sort_keys(list(items))
        meta_docs = {key: json.loads(items[key]) for key in meta_keys}
        chunk_docs = {key: items[key] for key in chunk_keys}
        # It is important that we set the metadata docs before the chunk docs so that the /data node will be set first
        if meta_docs:
            self._repo._set_docs(meta_docs)
        if chunk_docs:
            self._repo._set_chunks(chunk_docs)

    def __delitem__(self, key):
        """Delete a key.

        Args:
            key: path to delete
        """
        self._validate_key(key)
        if is_chunk_key(key):
            return self._repo._del_chunk(key)
        elif is_meta_key(key):
            return self._repo._del_doc(key)
        else:  # pragma: no cover
            raise KeyError(f"unexpected key: {key}")

    def delitems(self, keys) -> None:
        """Delete multiple keys

        Args:
            keys: list of paths to delete
        """

        for key in keys:
            self._validate_key(key)
        meta_keys, chunk_keys = sort_keys(keys)
        # TODO: can we have all of the needed queries in flight at the same time?
        # This two-step process is potentially inefficient
        if chunk_keys:
            self._repo._del_chunks(chunk_keys)
        if meta_keys:
            self._repo._del_docs(meta_keys)

    def __contains__(self, key: str) -> bool:
        """check if key exists in store.

        Args:
            key: path to check
        """
        # fast path for a query that Zarr does over and over again
        if key == "zarr.json":
            return True
        logger.debug("__contains__", path=key, repo=self._repo.repo_name)
        try:
            self._validate_key(key)
        except ValueError:
            return False
        if is_chunk_key(key):
            return self._repo._chunk_exists(key)
        elif is_meta_key(key):
            return self._repo._doc_exists(key)
        else:  # pragma: no cover
            # this should never actually happen because a valid key will always resolve
            # to either a meta key or a chunk key
            return False

    def keys(self) -> list[str]:
        """Return a list of this store's keys"""

        return self.list_prefix("")

    def __iter__(self):
        """Iterate over this store's keys"""

        yield from self.keys()

    def erase_prefix(self, prefix):
        """Erase all keys with the given prefix."""
        self._repo._synchronize(self._repo._arepo._del_prefix, prefix)

    def __len__(self) -> int:
        """number of keys in this store"""
        # TODO: this is a very inefficient way to do this
        # we should consider more efficient implementations
        return len(self.keys())

    def rename(self, src_path: Path, dst_path: Path) -> None:
        self._repo._rename(src_path, dst_path)

    def __getattribute__(self, name):
        """Influence upstream Zarr by failing a hasattr check for `get_partial_values`.

        Doing so forces it to use a preferable code path for retrieving data (getitems). See:
        https://github.com/zarr-developers/zarr-python/blob/a81db0782535ba04c32c277102a6457d118a73e8/zarr/core.py#L2162-L2171
        """
        if name == "get_partial_values":
            raise AttributeError
        return super().__getattribute__(name)
