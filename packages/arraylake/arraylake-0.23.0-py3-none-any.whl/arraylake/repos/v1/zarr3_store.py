# mypy: ignore-errors

"""DEPRECATED: This V1 zarr3_store module is pending removal.
V1 repositories are legacy and will be phased out in favor of Icechunk repositories.
This module and all its contents are scheduled for removal in a future version.
"""

import json
from collections.abc import AsyncGenerator, AsyncIterator, Iterable
from typing import Any, Callable, NewType

import zarr
import zarr.abc
import zarr.abc.codec
from numpy.typing import DTypeLike
from zarr.abc.store import ByteRequest, Store
from zarr.codecs.bytes import BytesCodec
from zarr.codecs.vlen_utf8 import VLenBytesCodec, VLenUTF8Codec
from zarr.core.buffer import Buffer, BufferPrototype
from zarr.core.common import BytesLike

from arraylake.log_util import get_logger

logger = get_logger(__name__)

shuffle_dict = {0: "noshuffle", 1: "shuffle", 2: "bitshuffle"}
EMPTY_GROUP_DOC: dict[str, Any] = {"attributes": {}}


def to_codec(compressor: dict[str, Any], dtype: DTypeLike) -> dict[str, Any]:
    """Convert old-style compressor dict to new-style codec dict."""
    if "codec" in compressor:
        codec_name = compressor["codec"].replace("https://purl.org/zarr/spec/codec/", "").split("/")[0]
        codec_class = zarr.registry.get_codec_class(codec_name)
        # unfortunate special casing thanks to bad decisions in V3 spec
        kwargs = compressor["configuration"].copy()
        if codec_name == "blosc":
            shuffle = kwargs.pop("shuffle")
            kwargs["shuffle"] = shuffle_dict[shuffle]
            kwargs["typesize"] = dtype.itemsize  # type: ignore
        codec = codec_class(**kwargs)
    elif "id" in compressor:
        # old style filter
        codec_name = "numcodecs." + compressor.pop("id")
        codec_class = zarr.registry.get_codec_class(codec_name)
        codec = codec_class(**compressor)
    return codec.to_dict()


def fix_array_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    """Transform old-style V3 metadata to new-style V3 metadata."""

    new_meta = meta.copy()
    new_attrs = meta["attributes"].copy()
    dimension_names = new_attrs.pop("_ARRAY_DIMENSIONS", None)
    # for some reason `filters` sometimes ends up in `attributes`
    filters = new_attrs.pop("filters", [])
    if filters is None:
        filters = []
    new_meta["attributes"] = new_attrs
    if dimension_names:
        new_meta["dimension_names"] = dimension_names
    _ = new_meta.pop("extensions", None)  # no longer used
    new_meta["zarr_format"] = 3
    new_meta["node_type"] = "array"
    old_chunk_grid = new_meta.pop("chunk_grid")
    new_meta["chunk_grid"] = {"name": "regular", "configuration": {"chunk_shape": old_chunk_grid["chunk_shape"]}}
    new_meta["chunk_key_encoding"] = {"name": "default", "configuration": {"separator": "/"}}
    assert new_meta["chunk_memory_layout"] == "C"
    del new_meta["chunk_memory_layout"]

    keep_filters: list[dict] = []
    bytes_codec: zarr.abc.codec.BaseCodec | None = None
    for f in filters:
        if f["id"] == "vlen-utf8":
            bytes_codec = VLenUTF8Codec()
        elif f["id"] == "vlen-bytes":
            bytes_codec = VLenBytesCodec()
        else:
            keep_filters.append(f)
    if bytes_codec is None:
        bytes_codec = BytesCodec()

    try:
        data_type = zarr.core.metadata.v3.DataType.parse(new_meta["data_type"])
    except ValueError as e:
        # special handling for incomplete string data_type in old V3
        original_dtype = meta["data_type"]
        if original_dtype["extension"] == "TODO: object array protocol URL":
            if isinstance(bytes_codec, VLenUTF8Codec):
                data_type = zarr.core.metadata.v3.DataType.string
            else:
                raise ValueError(f"Can't determine data_type from {original_dtype}") from e
        elif original_dtype["extension"] == "TODO: unicode array protocol URL":
            raise NotImplementedError(f"Fixed length strings ({original_dtype['type']}) are not yet supported in zarr 3")
        else:
            raise ValueError(f"Can't determine data_type from {original_dtype}") from e
    new_meta["data_type"] = data_type.value

    # codecs
    # print("data_type", data_type)
    # np_dtype = data_type.to_numpy()
    # print("np_dtype", np_dtype)
    # bc = zarr.codecs._get_default_array_bytes_codec(np_dtype)
    # codecs = [bc.to_dict()]
    np_dtype = data_type.to_numpy()
    codecs = []
    for f in keep_filters:
        codecs.append(to_codec(f, np_dtype))
    codecs.append(bytes_codec.to_dict())
    compressor = new_meta.pop("compressor", None)
    if compressor:
        codecs.append(to_codec(compressor, np_dtype))
    new_meta["codecs"] = codecs

    return new_meta


def fix_group_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    new_meta = meta.copy()
    new_meta["zarr_format"] = 3
    new_meta["node_type"] = "group"
    return new_meta


UnknownPath = NewType("UnknownPath", str)
GroupPath = NewType("GroupPath", str)
ArrayPath = NewType("ArrayPath", str)
ChunkPath = NewType("ChunkPath", str)
MetaPath = NewType("MetaPath", str)
KnownOldV3Path = GroupPath | ArrayPath | ChunkPath


def v3_path_to_old_v3_paths(path: UnknownPath) -> tuple[GroupPath, ArrayPath] | tuple[ChunkPath]:
    splits = path.split("/")
    fname = splits[-1]
    if fname == "zarr.json":
        if len(splits) == 1:
            # special case for root group
            node_name = "root"
            basedir = "meta"
        else:
            node_name = splits[-2]
            prefix = splits[:-2]
            basedir = "/".join(["meta", "root"] + prefix)
        # we don't know if the node is a group or array, so we have to generate both paths
        return (
            GroupPath("/".join([basedir, f"{node_name}.group.json"])),
            ArrayPath("/".join([basedir, f"{node_name}.array.json"])),
        )
    else:
        if "c" in splits:
            # this is a chunk
            chunk_index = splits.index("c")
            prefix = splits[:chunk_index]
            basedir = "/".join(["data", "root"] + prefix)
            chunk_key = "c" + "/".join(splits[slice(chunk_index + 1, None)])
            return (ChunkPath("/".join([basedir, chunk_key])),)
        else:
            # V2 path: .zgroup, .zarray
            raise KeyError("unexpected path " + path)


def old_v3_path_to_v3_path(path: str) -> str:
    # special case for root metadata documents
    if path in ("meta/root.group.json", "meta/root.array.json"):
        return "zarr.json"
    # handle both relative and absolute paths
    if path.startswith("data/root/") or path.startswith("meta/root/"):
        path = path[10:]
    if path.endswith(".json"):
        # this is a metadata doc
        splits = path.split("/")
        fname = splits[-1]
        node_name, node_type, ext = fname.rsplit(".", maxsplit=2)
        new_fname = f"{node_name}/zarr.json"
        return "/".join(splits[:-1] + [new_fname])
    else:
        # this is a chunk
        left, right = path.rsplit("c", maxsplit=1)
        return f"{left}c/{right}"


class AsyncIteratorWrapper:
    def __init__(self, coroutine, apply: Callable | None = None):
        self._coroutine = coroutine
        self._apply = apply

    def __aiter__(self):
        return self

    async def __anext__(self):
        item = await self._coroutine.__anext__()
        if self._apply is not None:
            return self._apply(item)
        else:
            return item


class ArraylakeStore(Store):
    _read_only = True
    _is_open = True

    def __init__(self, arepo):
        self._arepo = arepo

    def __eq__(self, other) -> bool:
        return other._arepo == self._arepo

    async def exists(self, key: str) -> bool:
        raise NotImplementedError

    async def get(
        self,
        key: str,
        prototype: BufferPrototype,
        byte_range: ByteRequest | None = None,
    ) -> Buffer | None:
        if byte_range is not None:
            raise NotImplementedError("byte_range is not supported")

        possible_paths = v3_path_to_old_v3_paths(UnknownPath(key))
        if len(possible_paths) == 1:
            # it's a chunk
            try:
                chunk_data = await self._arepo._get_chunk(possible_paths[0])
            except KeyError:
                # Zarr V3 expects None if the chunk doesn't exist
                return None
            return prototype.buffer.from_bytes(chunk_data)
        elif len(possible_paths) == 2:
            # try getting both group and array
            result = await self._arepo._get_docs(possible_paths)

            if len(result) == 0 and key == "zarr.json":
                # special handling for implicit root group
                result = {"meta/root.group.json": EMPTY_GROUP_DOC}
            # result is a dict with only one key
            elif len(result) != 1:
                raise AssertionError("expected one key, got " + str(result.keys()))
            found_key, doc = result.popitem()
            if found_key == possible_paths[0]:
                doc_fixed = fix_group_metadata(doc)
            elif found_key == possible_paths[1]:
                doc_fixed = fix_array_metadata(doc)
            else:
                raise KeyError("unexpected key " + result)
            return prototype.buffer.from_bytes(json.dumps(doc_fixed).encode())

    async def get_partial_values(
        self,
        prototype: BufferPrototype,
        key_ranges: Iterable[tuple[str, ByteRequest | None]],
    ) -> list[Buffer | None]:
        raise NotImplementedError

    @property
    def supports_writes(self) -> bool:
        return False

    async def set(self, key: str, value: Buffer) -> None:
        raise NotImplementedError

    @property
    def supports_deletes(self) -> bool:
        return False

    async def delete(self, key: str) -> None:
        raise NotImplementedError

    @property
    def supports_partial_writes(self) -> bool:
        return False

    async def set_partial_values(self, key_start_values: Iterable[tuple[str, int, BytesLike]]) -> None:
        raise NotImplementedError

    @property
    def supports_listing(self) -> bool:
        return True

    def list(self) -> AsyncIterator[str]:
        raise NotImplementedError

    def list_prefix(self, prefix: str) -> AsyncIterator[str]:
        """
        Retrieve all keys in the store that begin with a given prefix. Keys are returned relative
        to the root of the store.
        """
        # let's try just listing the metadata and see what happens
        return AsyncIteratorWrapper(self._arepo._list_prefix("meta/root/" + prefix), apply=old_v3_path_to_v3_path)

    async def _list_members(self, prefix: str) -> AsyncGenerator[str, None]:
        # TODO: should we apply the old_v3_path_to_v3_path function here?
        # TODO: are we possibly missing the root here?
        async for item in self._arepo._list_dir("meta/root/" + prefix):
            if item.endswith(".array.json") or item.endswith(".group.json"):
                yield item[:-11]

    def list_dir(self, prefix: str) -> AsyncIterator[str]:
        """
        Retrieve all keys and prefixes with a given prefix and which do not contain the character
        “/” after the given prefix.
        """
        # Q: should we apply the old_v3_path_to_v3_path function here?
        return AsyncIteratorWrapper(self._list_members(prefix))

    def _get_many(
        self, requests: Iterable[tuple[str, BufferPrototype, ByteRequest | None]]
    ) -> AsyncGenerator[tuple[str, Buffer | None], None]:
        raise NotImplementedError

    async def getsize(self, key: str) -> int:
        raise NotImplementedError

    async def getsize_prefix(self, prefix: str) -> int:
        data_prefix = "data/root/" + prefix
        return await self._arepo._getsize(data_prefix)
