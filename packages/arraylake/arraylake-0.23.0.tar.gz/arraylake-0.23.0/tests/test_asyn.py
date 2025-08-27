import asyncio
import os
from unittest.mock import AsyncMock

import pytest

from arraylake.asyn import (
    async_gather,
    asyncio_run,
    get_lock,
    get_loop,
    loop_selector_policy,
    sync,
)


def test_sync() -> None:
    bag = []

    async def add_to_bag(n):
        bag.append(n)

    sync(add_to_bag, 1)
    assert bag == [1]


def test_asyncio_run():
    async def foo():
        return 1

    assert asyncio_run(foo()) == 1


def test_selector_policy() -> None:
    orig_policy = asyncio.get_event_loop_policy()

    with loop_selector_policy():
        new_policy = asyncio.get_event_loop_policy()

        # if on windows policy will be WindowsSelectorEventLoopPolicy
        if os.name == "nt":
            assert isinstance(new_policy, asyncio.WindowsSelectorEventLoopPolicy)
        else:
            # if uvloop is available policy will be uvloop.EventLoopPolicy
            try:
                import uvloop

                assert isinstance(new_policy, uvloop.EventLoopPolicy)
            except ImportError:
                assert orig_policy is asyncio.get_event_loop_policy()

    # confirm that policy was changed back to the original
    assert orig_policy is asyncio.get_event_loop_policy()


def test_get_loop() -> None:
    # test that we only create one loop
    loop = get_loop()
    loop2 = get_loop()
    assert loop is loop2


def test_get_lock() -> None:
    # test that we only create one lock
    lock = get_lock()
    lock2 = get_lock()
    assert lock is lock2


@pytest.mark.asyncio
async def test_async_gather() -> None:
    async def foo(i, ex=False):
        if ex:
            raise ValueError(f"ex was True - {i}")
        return i

    assert await async_gather() == []
    assert await async_gather(*[foo(1), foo(2), foo(4)]) == [1, 2, 4]

    with pytest.raises(ValueError, match=r"ex was True - 2"):
        await async_gather(*[foo(1), foo(2, ex=True), foo(4)])

    with pytest.raises(ValueError, match=r"ex was True - .*"):
        await async_gather(*[foo(1, ex=True), foo(2, ex=True), foo(4, ex=True)])


async def test_async_gather_no_concurrency_limit() -> None:
    coros = [AsyncMock(return_value=i)() for i in range(5)]
    results = await async_gather(*coros, concurrency=None)
    assert results == [0, 1, 2, 3, 4]


async def test_async_gather_concurrency_limit() -> None:
    coros = [AsyncMock(return_value=i)() for i in range(5)]
    results = await async_gather(*coros, concurrency=3)
    assert results == [0, 1, 2, 3, 4]


async def test_async_gather_exception_raises() -> None:
    coros = [AsyncMock(side_effect=Exception)() for _ in range(5)]
    with pytest.raises(Exception):
        await async_gather(*coros, concurrency=None)


async def test_async_gather_empty_coros() -> None:
    results = await async_gather()
    assert results == []


async def test_async_gather_non_coroutine() -> None:
    with pytest.raises(TypeError):
        await async_gather(1)


async def test_async_gather_non_list() -> None:
    with pytest.raises(TypeError):
        await async_gather(1, concurrency=None)


async def test_async_gather_negative_concurrency_limit() -> None:
    assert await async_gather(*[AsyncMock(return_value=1)()], concurrency=-1) == [1]
