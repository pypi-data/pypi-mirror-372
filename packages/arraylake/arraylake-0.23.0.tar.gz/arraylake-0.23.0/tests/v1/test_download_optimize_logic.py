import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from arraylake import config
from arraylake.repos.v1.chunkstore.utils import (
    ByteRange,
    ChunkRequest,
    CoalescedRequests,
    SplitRequest,
    UnmodifiedRequest,
    optimize_requests,
)


@pytest.mark.parametrize(
    "max_size,coalesce_size,req,expected",
    [
        ### Single Chunk ###
        # no split
        (
            10,
            0,
            [ChunkRequest("a", ByteRange(0, 10))],
            [UnmodifiedRequest("a", ByteRange(0, 10))],
        ),
        # max_length > length, no split
        (
            11,
            0,
            [ChunkRequest("a", ByteRange(0, 10))],
            [UnmodifiedRequest("a", ByteRange(0, 10))],
        ),
        # start > 0
        (
            10,
            0,
            [ChunkRequest("a", ByteRange(1, 10))],
            [UnmodifiedRequest("a", ByteRange(1, 10))],
        ),
        # split in the middle
        (
            5,
            0,
            [ChunkRequest("a", ByteRange(0, 10))],
            [SplitRequest("a", [ByteRange(0, 5), ByteRange(5, 5)])],
        ),
        # split in the middle with offset
        (
            5,
            0,
            [ChunkRequest("a", ByteRange(1, 10))],
            [SplitRequest("a", [ByteRange(1, 5), ByteRange(6, 5)])],
        ),
        # uneven split
        (
            3,
            0,
            [ChunkRequest("a", ByteRange(0, 10))],
            [
                SplitRequest(
                    "a",
                    [
                        ByteRange(0, 3),
                        ByteRange(3, 3),
                        ByteRange(6, 3),
                        ByteRange(9, 1),
                    ],
                )
            ],
        ),
        ### Multiple Chunks ###
        # two chunks, no split
        (
            10,
            None,
            [ChunkRequest("a", ByteRange(0, 10)), ChunkRequest("b", ByteRange(10, 8))],
            [
                UnmodifiedRequest("a", ByteRange(0, 10)),
                UnmodifiedRequest("b", ByteRange(10, 8)),
            ],
        ),
        # split both chunks
        (
            5,
            None,
            [ChunkRequest("a", ByteRange(0, 10)), ChunkRequest("b", ByteRange(10, 8))],
            [
                SplitRequest("a", [ByteRange(0, 5), ByteRange(5, 5)]),
                SplitRequest("b", [ByteRange(10, 5), ByteRange(15, 3)]),
            ],
        ),
        # coalesce!
        (
            100,
            0,
            [ChunkRequest("a", ByteRange(0, 10)), ChunkRequest("b", ByteRange(10, 8))],
            [
                CoalescedRequests(
                    ByteRange(0, 18),
                    [
                        ChunkRequest("a", ByteRange(0, 10)),
                        ChunkRequest("b", ByteRange(10, 8)),
                    ],
                )
            ],
        ),
        # don't coalesce, gap exceeds the coalesce length
        (
            100,
            1,
            [ChunkRequest("a", ByteRange(0, 10)), ChunkRequest("b", ByteRange(12, 8))],
            [
                UnmodifiedRequest("a", ByteRange(0, 10)),
                UnmodifiedRequest("b", ByteRange(12, 8)),
            ],
        ),
        # coalesce two, but not the third
        (
            100,
            1,
            [
                ChunkRequest("a", ByteRange(0, 10)),
                ChunkRequest("b", ByteRange(10, 8)),
                ChunkRequest("c", ByteRange(20, 8)),
            ],
            [
                CoalescedRequests(
                    ByteRange(0, 18),
                    [
                        ChunkRequest("a", ByteRange(0, 10)),
                        ChunkRequest("b", ByteRange(10, 8)),
                    ],
                ),
                UnmodifiedRequest("c", ByteRange(20, 8)),
            ],
        ),
        # coalesce two, split the third
        (
            100,
            0,
            [
                ChunkRequest("a", ByteRange(0, 10)),
                ChunkRequest("b", ByteRange(10, 8)),
                ChunkRequest("c", ByteRange(20, 200)),
            ],
            [
                # TODO: split request comes out before coalesced request.
                # Order here is not important. Consider using sets instead of lists.
                SplitRequest("c", [ByteRange(20, 100), ByteRange(120, 100)]),
                CoalescedRequests(
                    ByteRange(0, 18),
                    [
                        ChunkRequest("a", ByteRange(0, 10)),
                        ChunkRequest("b", ByteRange(10, 8)),
                    ],
                ),
            ],
        ),
    ],
)
def test_optimize_requests(max_size, coalesce_size, req, expected):
    result = list(optimize_requests(req, max_size=max_size, coalesce_size=coalesce_size))
    assert result == expected


def test_optimize_requests_max_size_config():
    request = [ChunkRequest("a", ByteRange(0, 10))]

    with config.set({"chunkstore.max_request_size": 5}):
        assert list(optimize_requests(request)) == [SplitRequest("a", [ByteRange(0, 5), ByteRange(5, 5)])]

    with config.set({"chunkstore.max_request_size": 20}):
        assert list(optimize_requests(request)) == [UnmodifiedRequest("a", ByteRange(0, 10))]


def test_optimize_requests_coalesce_size_config():
    request = [ChunkRequest("a", ByteRange(0, 10)), ChunkRequest("b", ByteRange(20, 8))]
    with config.set({"chunkstore.coalesce_size": 30}):
        assert list(optimize_requests(request)) == [
            CoalescedRequests(
                ByteRange(0, 28),
                [
                    ChunkRequest("a", ByteRange(0, 10)),
                    ChunkRequest("b", ByteRange(20, 8)),
                ],
            )
        ]
    with config.set({"chunkstore.coalesce_size": 5}):
        assert list(optimize_requests(request)) == [UnmodifiedRequest("a", ByteRange(0, 10)), UnmodifiedRequest("b", ByteRange(20, 8))]


@settings(deadline=None)
@given(
    key=st.text(max_size=10),
    start=st.integers(min_value=0),
    length=st.integers(min_value=1, max_value=300),
    data=st.data(),
)
def test_propert_coalesce_split_requests_roundtrip(data, key, start, length):
    if data.draw(st.booleans()):
        max_size = data.draw(st.integers(min_value=0, max_value=length))
    else:
        # sometimes test max_size > length
        max_size = data.draw(st.integers(min_value=0))

    request = ChunkRequest(key, ByteRange(start, length))
    # possibly split requests
    (split,) = optimize_requests([request], coalesce_size=None, max_size=max_size)

    if length <= max_size:
        assert isinstance(split, UnmodifiedRequest)

    if isinstance(split, UnmodifiedRequest):
        to_coalesce = [ChunkRequest(split.key, split.download_range)]
    elif isinstance(split, SplitRequest):
        to_coalesce = [ChunkRequest(split.key, range_) for range_ in split.download_ranges]
    elif isinstance(split, CoalescedRequests):
        raise ValueError

    # always coalesce back to one request
    (coalesced,) = optimize_requests(to_coalesce, coalesce_size=length, max_size=None)
    if isinstance(coalesced, UnmodifiedRequest):
        actual = ChunkRequest(split.key, coalesced.download_range)
    elif isinstance(coalesced, SplitRequest):
        raise ValueError
    elif isinstance(coalesced, CoalescedRequests):
        actual = ChunkRequest(coalesced.ranges[0].key, coalesced.download_range)

    # back where we started
    assert request == actual
