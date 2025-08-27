from collections.abc import Generator
from itertools import chain, repeat
from typing import NamedTuple, Optional

from arraylake.config import config

# This parameter determines the maximium size of a single request to object storage.
# Requests larger than this will be split into multiple parts.
MAX_REQUEST_SIZE = 8 * 1024 * 1024

# This parameter determines how much _extra_ data we are willing to download in order to coalesce
# two requests into a single request. If the distance between two requests is less than this value,
# they will be coalesced into a single request and the extra data thrown away.
COALESCE_SIZE = 1024 * 1024


class ByteRange(NamedTuple):
    """A contiguous range of bytes within a file."""

    start: int
    length: int


class ChunkRequest(NamedTuple):
    """A pointer to full chunk that exists in a file."""

    # an identifier for the chunk
    key: str
    # the range of bytes in the file that the chunk occupies
    range: ByteRange


class UnmodifiedRequest(NamedTuple):
    """A single download request to make, containing a single chunk"""

    key: str
    download_range: ByteRange


class CoalescedRequests(NamedTuple):
    """A single download request to make, containing one or more chunks"""

    # the bytes we need to download
    download_range: ByteRange
    # the way we need to split them up
    ranges: list[ChunkRequest]


class SplitRequest(NamedTuple):
    """Multiple download requests to make, whose bytes will be combined into a single chunk"""

    key: str
    download_ranges: list[ByteRange]


OptimizedRequest = UnmodifiedRequest | CoalescedRequests | SplitRequest


def split_range_into_parts(request_range: ByteRange, max_length: int) -> list[ByteRange]:
    """Given a single contiguous range of data, split it into chunks of at most `max_length` bytes."""
    end = request_range.start + request_range.length
    starts = range(request_range.start, end, max_length)
    chunk_lens = chain(repeat(max_length, len(starts) - 1), [end - starts[-1]])
    return [ByteRange(start, length) for start, length in zip(starts, chunk_lens)]


# helper function
def _coalesced_or_unmodified_request(download_range: ByteRange, requests: list[ChunkRequest]) -> UnmodifiedRequest | CoalescedRequests:
    if len(requests) == 1:
        assert requests[0].range == download_range
        return UnmodifiedRequest(requests[0].key, requests[0].range)
    else:
        return CoalescedRequests(download_range, requests)


def optimize_requests(
    requests: list[ChunkRequest],
    coalesce_size: Optional[int] = None,
    max_size: Optional[int] = None,
) -> Generator[OptimizedRequest, None, None]:
    coalesce_size = coalesce_size if coalesce_size is not None else (config.get("chunkstore.coalesce_size", None) or COALESCE_SIZE)

    # Handle being passed max_size=0 or max_size=None
    max_size = (max_size or config.get("chunkstore.max_request_size", None)) or MAX_REQUEST_SIZE

    # sort chunks by their start
    requests.sort(key=lambda r: r.range.start)

    # this holds ranges we intend to coalesce
    sub_requests: list[ChunkRequest] = []

    for request in requests:
        # if the request is too big, we split it
        if request.range.length > max_size:
            sub_ranges = split_range_into_parts(request.range, max_size)
            yield SplitRequest(request.key, sub_ranges)
            continue

        # fast path for length 1 requests - nothing to coalesce
        if len(requests) == 1:
            yield UnmodifiedRequest(request.key, request.range)
            continue

        # otherwise we have an opportunity to coalesce
        if len(sub_requests) == 0:
            # initialize a new coalesced range
            coalesced_range = request.range
            sub_requests = [request]
        else:
            distance = request.range.start - (coalesced_range.start + coalesced_range.length)
            if distance > coalesce_size or (coalesced_range.length + distance + request.range.length) > max_size:
                # yield the coalesced range
                yield _coalesced_or_unmodified_request(coalesced_range, sub_requests)
                # start a new coalesced range
                coalesced_range = request.range
                sub_requests = [request]
            else:
                # add to the coalesced range
                coalesced_range = ByteRange(coalesced_range.start, coalesced_range.length + distance + request.range.length)
                sub_requests.append(request)

    # yield the last coalesced range
    if len(sub_requests) > 0:
        yield _coalesced_or_unmodified_request(coalesced_range, sub_requests)
