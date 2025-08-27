"""DEPRECATED: This V1 virtual module is pending removal.
V1 repositories are legacy and will be phased out in favor of Icechunk repositories.
This module and all its contents are scheduled for removal in a future version.
"""

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Union
from urllib.parse import urlparse

from pydantic import BaseModel

from arraylake.config import config
from arraylake.log_util import get_logger
from arraylake.repos.v1.chunkstore.fsspec_compat import FSConfig
from arraylake.repos.v1.types import Path
from arraylake.repos.v1.zarr_util import (
    DATA_ROOT,
    META_ROOT,
    is_chunk_key,
    is_meta_key,
    is_v2_chunk_key,
)

logger = get_logger(__name__)

MAX_TIFF_REFERENCES = 500


class FileType(Enum):
    hdf5 = 1
    netcdf3 = 2


# type definitions
ChunkRefT = list[Union[str, int]]
MetaDictT = dict[str, Any]
ReferenceStoreT = dict[Path, Union[MetaDictT, ChunkRefT]]


# pydantic models
class ChunkGrid(BaseModel):
    chunk_shape: list[int]
    separator: str = "/"
    type: str = "regular"


class Codec(BaseModel):
    codec: str
    configuration: dict


class V3ArrayMeta(BaseModel):
    attributes: dict = {}
    chunk_grid: ChunkGrid
    chunk_memory_layout: str
    compressor: Optional[Codec] = None  # TODO: this will become codecs: list[]
    data_type: str
    extensions: list = []
    fill_value: Any = None
    shape: list[int]


class V3GroupMeta(BaseModel):
    attributes: dict = {}


def guess_file_type(fp) -> FileType:
    magic = fp.read(4)
    fp.seek(0)
    if magic[:3] == b"CDF":
        return FileType.netcdf3
    elif magic == b"\x89HDF":
        return FileType.hdf5
    else:
        raise ValueError(f"Unknown file type - magic {magic}")


def make_v3_array(zattrs: dict[str, Any], zarray: dict[str, Any]) -> V3ArrayMeta:
    chunk_grid = ChunkGrid(
        chunk_shape=zarray["chunks"],
    )

    v2_compressor_config = zarray["compressor"]
    if v2_compressor_config is not None:
        v2_compressor_id = v2_compressor_config.pop("id", None)
        compressor = Codec(
            codec=f"https://purl.org/zarr/spec/codec/{v2_compressor_id}/1.0",
            configuration=v2_compressor_config,
        )
    else:
        compressor = None

    if "filters" in zarray:
        zattrs["filters"] = zarray.pop("filters")

    array = V3ArrayMeta(
        attributes=zattrs,
        chunk_grid=chunk_grid,
        chunk_memory_layout=zarray["order"],
        compressor=compressor,
        data_type=zarray["dtype"],
        fill_value=zarray["fill_value"],
        shape=zarray["shape"],
    )
    return array


def _maybe_load_json(obj: Union[MetaDictT, bytes, str]) -> MetaDictT:
    """load json to dict if obj is string or bytes"""
    if isinstance(obj, (str, bytes)):
        return json.loads(obj)
    return obj


def remove_lead_and_trail_slash(s):
    if s.startswith("/"):
        s = s[1:]
    if s.endswith("/"):
        s = s[:-1]
    return s


def _normalize_key(key):
    return re.sub(r"(?:\/+)", "/", key)


def make_v3_store(store_v2: dict[str, Any], new_path: Optional[Path] = None) -> ReferenceStoreT:
    """
    Given a mapping with Zarr V2 keys and references, return an equivalent Zarr V3 mapping

    Parameters
    ----------
    store_v2 : dict
        Mapping with Zarr V2 keys, Zarr V2 metadata objects, and chunk references (3 element list)

    Returns
    -------
    new_store : dict
        New store with Zarr V3 keys and metadata objects.
    """

    _meta_root = remove_lead_and_trail_slash(META_ROOT)
    _data_root = remove_lead_and_trail_slash(DATA_ROOT)

    new_path = "" if new_path is None else remove_lead_and_trail_slash(new_path)

    new_store: ReferenceStoreT = {}
    new_key = ""
    for key, doc in store_v2.items():
        # root group
        if key == ".zgroup":
            # handle special root group name
            if not new_path:
                new_key = f"{_meta_root}.group.json"
            else:
                new_key = f"{_meta_root}/{new_path}.group.json"

            doc = _maybe_load_json(doc)
            attrs = _maybe_load_json(store_v2.get(".zattrs", {}))
            new_store[new_key] = V3GroupMeta(attributes=attrs).model_dump()
        # arbitrary arrays
        elif key.endswith(".zarray"):
            # root level array (allowed only if new_path != "")
            if key == ".zarray" and not new_path:
                raise NotImplementedError("root level arrays are not currently supported")

            if "/" in key:
                _key = key.replace("/.zarray", ".array.json")  # e.g. foo/bar/.zarray -> foo/bar.array.json
                new_key = f"{_meta_root}/{new_path}/{_key}"
            else:
                # root level array
                assert new_path
                _key = key.replace(".zarray", ".array.json")
                new_key = f"{_meta_root}/{new_path}{_key}"

            doc = _maybe_load_json(doc)
            attrs_key = key.replace(".zarray", ".zattrs")
            attrs = _maybe_load_json(store_v2.get(attrs_key, {}))
            new_key = _normalize_key(new_key)
            new_store[new_key] = make_v3_array(attrs, doc).model_dump()
        # arbitrary groups
        elif key.endswith(".zgroup"):
            _key = key.replace("/.zgroup", ".group.json")  # e.g. foo/bar/.zgroup -> foo/bar.group.json
            new_key = _normalize_key(f"{_meta_root}/{new_path}/{_key}")
            attrs_key = key.replace(".zgroup", ".zattrs")
            attrs = _maybe_load_json(store_v2.get(attrs_key, {}))
            new_store[new_key] = V3GroupMeta(attributes=attrs).model_dump()
        # scalars but not bare directories
        elif key.endswith("/") and key + ".zarray" in store_v2:
            # Note: `list_dir` returns a mix of objects and directory paths.
            # when talking to some s3 endpoints and ingesting v2-zarr.
            var = "/" + key[:-1] if new_path else key[:-1]
            new_key = f"{_data_root}/{new_path}{var}/c0"
            new_store[new_key] = doc
            logger.info(f"Detected scalar key: {key}")
        # skip .zattrs because we already captured them in the group/array steps
        elif key.endswith(".zattrs"):
            continue
        # skip the .zmetadata (we don't need it)
        elif key.endswith(".zmetadata"):
            continue
        # chunks
        elif is_v2_chunk_key(key):
            if "/" in key:
                var, chunk = key.rsplit("/", maxsplit=1)
                new_key = f"{_data_root}/{new_path}/{var}/c" + chunk.replace(".", "/")
            else:
                # root array
                new_key = f"{_data_root}/{new_path}/c" + key.replace(".", "/")
            new_key = _normalize_key(new_key)
            new_store[new_key] = doc
        else:
            logger.warning(f"skipping unrecognized key: *{key}*")

        assert "//" not in new_key, new_key
        assert "\\" not in new_key, new_key

    return new_store


def raise_on_invalid_virtual_kwargs(kwargs):
    if "storage_options" in kwargs:
        raise ValueError("Storage options are configured automatically by Arraylake. Do not pass `storage_options`.")
    if "inline_threshold" in kwargs:
        raise ValueError("Arraylake does not support inlining of data. Do not pass `inline_threshold`.")


def find_identical_and_concat_dim(scan: list[dict[str, ReferenceStoreT]]) -> tuple[list[str], list[str]]:
    """Heuristics for how to combine a GRIB file with multiple messages."""
    import cfgrib

    identical = []
    concat = []

    # look at the first message only.
    msg = scan[0]

    # mypy can't tell that we're only looking at "meta" keys
    # which are str, so `json.loads` will work.
    possibleLevels: tuple[Union[str, None], ...] = tuple(
        json.loads(value).get("GRIB_typeOfLevel", None) for key, value in msg["refs"].items() if ".zattrs" in key  # type: ignore[arg-type]
    )
    levels = [s for s in set(possibleLevels) if s is not None]

    possible_keys = list(cfgrib.dataset.COORD_ATTRS) + levels

    first, second = tuple(sc["refs"] for sc in scan[:2])
    for key in possible_keys:
        if key == "valid_time":
            # This is a "computed" key
            # cfgrib only adds this variable
            # if "step" is the concat dimension
            continue
        # I am assuming here that `key` is a dimension I think.
        # Or at least that it is not a 0D array with key f"{key}/"
        chunk_key = f"{key}/0"
        if chunk_key not in first or chunk_key not in second:
            continue
        if first[chunk_key] != second[chunk_key]:
            concat.append(key)
        else:
            identical.append(key)
    return identical, concat


def scan_grib2(fs_config: FSConfig, url: str, **kwargs) -> ReferenceStoreT:
    """
    Scan a GRIB2 file in S3 and return Kerchunk-style references for all keys.

    Parameters
    ----------
    url : str
        URL to GRIB file. Must start with `s3://`

    Returns
    -------
    refs : dict
        Kerchunk-style references for all keys in NetCDF file
    """
    from kerchunk.combine import MultiZarrToZarr
    from kerchunk.grib2 import scan_grib

    raise_on_invalid_virtual_kwargs(kwargs)
    kwargs["storage_options"] = fs_config.constructor_kwargs

    # list of reference dicts, one per GRIB message
    scan = scan_grib(url, **kwargs)

    if len(scan) > 1:
        # assuming that multiple messages mean concatenation
        identical, concat = find_identical_and_concat_dim(scan)
        if len(concat) > 1:
            raise NotImplementedError(f"Detected multiple possible concat dims: {concat}")
        if not concat:
            raise NotImplementedError("Detected multiple messages, but no possible concat dimensions.")
    else:
        identical = []
        concat = []

    # For a single message, doing this inserts the URI
    # from "template" into "refs", which we want
    # choosing to concatenate all messages in a file.
    combined_refs = MultiZarrToZarr(scan, concat_dims=concat, identical_dims=identical).translate()

    return combined_refs["refs"]


def scan_netcdf(fs_config: FSConfig, url: str, **kwargs) -> ReferenceStoreT:
    """
    Scan a NetCDF file in S3 and return Kerchunk-style references for all keys.

    Parameters
    ----------
    url : str
        URL to NetCDF file. Must start with `s3://` and may include sub directories (e.g. `s3://foo/bar`)

    Returns
    -------
    refs : dict
        Kerchunk-style references for all keys in NetCDF file
    """

    raise_on_invalid_virtual_kwargs(kwargs)

    with fs_config.fs.open(url) as fp:
        file_type = guess_file_type(fp)
        if file_type == FileType.hdf5:
            from kerchunk.hdf import SingleHdf5ToZarr

            scan = SingleHdf5ToZarr(fp, url, inline_threshold=0, spec=0, **kwargs)
        elif file_type == FileType.netcdf3:
            from kerchunk.netCDF3 import NetCDF3ToZarr

            # here the kerchunk API is very inconsistent
            # while SingleHdf5ToZarr can take a file-like object, NetCDF3ToZarr requires a url, plus the storage options
            scan = NetCDF3ToZarr(url, storage_options=fs_config.constructor_kwargs, inline_threshold=0, **kwargs)
        refs = scan.translate()

    if "refs" in refs:
        # another kerchunk API inconsistency
        # outputs from NetCDF3ToZarr are nested in a "refs" key for some reason
        refs = refs["refs"]

    return refs


def scan_zarr_v2(fs_config: FSConfig, url: str) -> ReferenceStoreT:
    """
    Scan a Zarr store and return Kerchunk-style references for all keys.

    Parameters
    ----------
    url : str
        URL to Zarr store. Must start with `s3://` or `gs://` and may include sub directories (e.g. `s3://foo/bar`)

    Returns
    -------
    refs : dict
        Kerchunk-style references for all keys in Zarr V2 store
    """

    parsed_url = urlparse(url)

    store_prefix = f"{parsed_url.netloc}/{parsed_url.path[1:]}"  # [1:] skips leading slash
    if not store_prefix.endswith("/"):
        store_prefix += "/"  # add trailing slash (this will be removed from all keys below)

    store: ReferenceStoreT = {}
    to_fetch = {}
    for _, _, files in fs_config.fs.walk(url, detail=True, topdown=True):
        for file_name, details in files.items():
            # For a provided `url` of `s3://bucket/foo/`
            # where walk finds a file such as `s3://bucket/foo/bar/.zattrs`
            # `file_name` is only the name of the file `.zattrs`
            # `key_path` is the complete path to the file `bucket/foo/bar/.zattrs`
            # `key` is relative to store_prefix of the url: `bar/.zattrs`
            key_path = details["name"]
            key = key_path.replace(store_prefix, "")

            # load metadata docs now
            if file_name in [".zattrs", ".zgroup", ".zarray"]:
                to_fetch[key] = key_path

            # skip the .zmetadata (we don't need it)
            elif file_name == ".zmetadata":
                continue

            # use the info in from fs.walk to populate the reference
            elif is_v2_chunk_key(file_name):
                store[key] = [f"{fs_config.protocol}://{key_path}", 0, details["size"]]

            else:
                logger.warning(f"skipping unrecognized key: {key_path}")

    if to_fetch:
        # fs.cat returns a dict with key being the full path
        _objs = fs_config.fs.cat(list(to_fetch.values()), batch_size=config.get("throttle_concurrency_size", 10))
        # parse metadata docs
        docs = {key: json.loads(doc) for key, doc in zip(to_fetch.keys(), _objs.values())}
        # update the store
        store.update(docs)

    return store


def scan_tiff(fs_config: FSConfig, url: str, name: str, **kwargs) -> ReferenceStoreT:
    """
    Scan a TIFF file in S3 and return Kerchunk-style references for all keys.
    Parameters
    ----------
    url : str
        URL to TIFF file. Must start with `s3://` and may include sub directories (e.g. `s3://foo/bar`)
    name : str
        Name for Array
    Returns
    -------
    refs : dict
        Kerchunk-style references for all keys in TIFF file.
    """
    from kerchunk.tiff import tiff_to_zarr

    if "storage_options" in kwargs:
        raise ValueError("Storage options are configured automatically by Arraylake. Do not pass `storage_options`.")

    refs_kerchunk = tiff_to_zarr(urlpath=url, remote_options=fs_config.constructor_kwargs, **kwargs)
    if len(refs_kerchunk) > MAX_TIFF_REFERENCES:
        raise ValueError(
            f"The number of references > {MAX_TIFF_REFERENCES} is too large to ingest. "
            "This particular file is likely not a good fit for Arraylake. "
            "We recommend opening the file with rioxarray and writing it to Arraylake"
            "with to_zarr. "
        )

    # Follow rioxarray conventions
    refs_kerchunk[".zattrs"] = refs_kerchunk[".zattrs"].replace('"S"]', '"band"]')

    name = remove_lead_and_trail_slash(name)
    refs = {f"{name}/{k}": v for k, v in refs_kerchunk.items()}
    refs[".zgroup"] = '{"zarr_format": 2}'

    return refs


@dataclass
class VirtualLocation:
    uri: str
    offset: int
    length: int


def reformat_kerchunk_refs(
    refs: dict[str, Any], new_path: Path
) -> tuple[dict[Path, MetaDictT], dict[Path, VirtualLocation], dict[Path, bytes]]:
    """
    Reformat Kerchunk-style references to Zarr V3 / Arraylake references

    Parameters
    ----------
    refs : dict
        Mapping of references from Kerchunk (or similar)
    new_path : str
        Root path for reference data.

    Returns
    -------
    meta_docs : dict
        Metadata documents, reformatted to align with Arraylake specifications
    chunk_locations : dict
        Chunk locations, reformatted to align with Arraylake specifications
    """
    from arraylake.repos.v1.chunkstore.base_chunkstore import encode_inline_data

    meta_docs = {}
    chunk_locations = {}
    inlined_refs = {}  # type: dict[Path, bytes]

    if new_path.endswith("/"):
        new_path = new_path[:-1]

    if new_path == "" and ".zarray" in refs:
        raise ValueError("root level arrays are not supported, provide a target path for this virtual dataset")

    v3_refs = make_v3_store(refs, new_path)

    for k, v in v3_refs.items():
        key = Path(k)
        if key == "zarr.json":
            pass
        elif is_chunk_key(key):
            if isinstance(v, list):
                # byte range reference
                chunk_locations[key] = VirtualLocation(uri=v[0], offset=v[1], length=v[2])  # type: ignore
            elif isinstance(v, str):
                # Received inlined encoded byte string from kerchunk
                # This is particularly necessary for GRIB2 where
                # kerchunk always inlines the generated coordinate values (not stored in GRIB file)
                # For all the other formats we disable the kerchunk inlining.
                # Decode to plain bytes here and then rely on chunkstore.add_chunks to inline the data later.
                # This way we dont duplicate handling of "inline_threshold"
                inlined_refs[key] = encode_inline_data(v)
            else:
                raise ValueError(f"Bad reference. key: {k}, value: {v}")

        elif is_meta_key(key):
            assert isinstance(v, dict), key
            meta_docs[key] = v

    return meta_docs, chunk_locations, inlined_refs
