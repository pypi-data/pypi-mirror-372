from collections.abc import AsyncGenerator

import numpy as np
import pytest

zarr = pytest.importorskip("zarr", minversion="3.0.0")

from arraylake.repos.v1.zarr3_store import (
    AsyncIteratorWrapper,
    fix_group_metadata,
    old_v3_path_to_v3_path,
    to_codec,
    v3_path_to_old_v3_paths,
)


@pytest.mark.parametrize(
    "input,expected",
    [
        (
            ({"codec": "https://purl.org/zarr/spec/codec/zstd/1.0", "configuration": {"checksum": False, "level": 0}}, np.dtype("f8")),
            {"name": "zstd", "configuration": {"checksum": False, "level": 0}},
        ),
        (
            (
                {
                    "codec": "https://purl.org/zarr/spec/codec/blosc/1.0",
                    "configuration": {"blocksize": 0, "clevel": 5, "cname": "lz4", "shuffle": 1},
                },
                np.dtype("f8"),
            ),
            {"name": "blosc", "configuration": {"blocksize": 0, "clevel": 5, "cname": "lz4", "shuffle": "shuffle", "typesize": 8}},
        ),
        # old style filter
        (
            ({"astype": "<i8", "dtype": "<i2", "id": "fixedscaleoffset", "offset": 50, "scale": 0.04}, np.dtype("f8")),
            {
                "name": "numcodecs.fixedscaleoffset",
                "configuration": {"id": "fixedscaleoffset", "astype": "<i8", "dtype": "<i2", "offset": 50, "scale": 0.04},
            },
        ),
    ],
)
def test_to_codec(input, expected) -> None:
    assert to_codec(*input) == expected


# # TODO
# def test_fix_array_metadata() -> None:
#     pass


@pytest.mark.parametrize(
    "input,expected",
    [
        ({"attributes": {}}, {"attributes": {}, "node_type": "group", "zarr_format": 3}),
        (
            {"attributes": {"foo": "bar", "spam": ["eggs", "bacon"]}},
            {"attributes": {"foo": "bar", "spam": ["eggs", "bacon"]}, "node_type": "group", "zarr_format": 3},
        ),
    ],
)
def test_fix_group_metadata(input, expected) -> None:
    assert fix_group_metadata(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ("zarr.json", ("meta/root.group.json", "meta/root.array.json")),
        ("a/b/c/zarr.json", ("meta/root/a/b/c.group.json", "meta/root/a/b/c.array.json")),
        ("a/b/c/0", ("data/root/a/b/c0",)),
        ("a/b/c/0/0/1", ("data/root/a/b/c0/0/1",)),
    ],
)
def test_v3_path_to_old_v3_paths(input: str, expected: str) -> None:
    assert v3_path_to_old_v3_paths(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ("meta/root.group.json", "zarr.json"),
        ("meta/root/a.array.json", "a/zarr.json"),
        ("meta/root/a/b/c/d.group.json", "a/b/c/d/zarr.json"),
        ("data/root/a/b/c0", "a/b/c/0"),
        ("data/root/a/b/c0/1", "a/b/c/0/1"),
    ],
)
def test_old_v3_path_to_v3_path(input: str, expected: str) -> None:
    assert old_v3_path_to_v3_path(input) == expected


async def test_async_iterator_wrapper() -> None:
    vals = ["a", "b", "c"]

    async def gen() -> AsyncGenerator[str, None]:
        for val in vals:
            yield val

    wrapper = AsyncIteratorWrapper(gen())
    assert vals == [v async for v in wrapper]


async def test_async_iterator_wrapper_with_apply() -> None:
    vals = ["a", "b", "c"]

    async def gen() -> AsyncGenerator[str, None]:
        for val in vals:
            yield val

    wrapper = AsyncIteratorWrapper(gen(), apply=lambda x: x.upper())
    assert ["A", "B", "C"] == [v async for v in wrapper]
