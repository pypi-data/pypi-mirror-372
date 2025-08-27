import itertools
import time
from datetime import timedelta

import hypothesis.strategies as st
import pytest
from hypothesis import given, settings

import arraylake.retrier as retrier


def deltas(min_value=timedelta(), max_value=None):
    args = {"min_value": min_value, "max_value": max_value or timedelta(days=30)}
    return st.timedeltas(**args)


def negative_deltas():
    return st.timedeltas(max_value=timedelta()).filter(lambda d: d < timedelta())


def waits(*deltas_args):
    return st.iterables(deltas(*deltas_args))


max_examples = 30


@given(deltas(), st.integers(min_value=0, max_value=10))
@settings(max_examples=max_examples)
def test_constant_wait(delta, idx):
    assert next(itertools.islice(retrier.constant_wait(delta), idx, idx + 1)) == delta


@given(negative_deltas())
@settings(max_examples=max_examples)
def test_constant_wait_negative_delta(delta):
    with pytest.raises(AssertionError):
        next(retrier.constant_wait(delta))


@given(st.timedeltas(min_value=timedelta(days=-30), max_value=timedelta(days=30)), deltas(), st.integers(min_value=2, max_value=20))
@settings(max_examples=max_examples)
def test_linear_wait(delta, initial, length):
    ds = list(itertools.islice(retrier.linear_wait(delta, initial), 0, length))
    assert ds[0] == initial
    for idx in range(length - 1):
        assert ds[idx + 1] - ds[idx] == delta


@given(deltas(), negative_deltas())
@settings(max_examples=max_examples)
def test_linear_wait_negative_initial(delta, initial):
    with pytest.raises(AssertionError):
        next(retrier.linear_wait(delta, initial))


@given(deltas(min_value=timedelta(seconds=1)), st.floats(min_value=0.5, max_value=1.5), st.integers(min_value=2, max_value=10))
@settings(max_examples=max_examples)
def test_exponential_wait(initial, factor, length):
    ds = list(itertools.islice(retrier.exponential_wait(factor=factor, initial=initial), 0, length))
    assert ds[0] == initial
    for idx in range(length - 1):
        assert ds[idx + 1] / ds[idx] == pytest.approx(factor, rel=1e-4)


@given(negative_deltas(), st.floats(min_value=0.1, max_value=5))
@settings(max_examples=max_examples)
def test_exponential_wait_negative_initial(initial, factor):
    with pytest.raises(AssertionError):
        next(retrier.exponential_wait(factor=factor, initial=initial))


@given(deltas(), st.floats(max_value=0, exclude_max=True))
@settings(max_examples=max_examples)
def test_exponential_wait_negative_factor(initial, factor):
    with pytest.raises(AssertionError):
        next(retrier.exponential_wait(factor=factor, initial=initial))


@given(waits(), st.floats(min_value=0, max_value=1, exclude_min=True), st.integers(min_value=2, max_value=10))
@settings(max_examples=max_examples)
def test_proportional_jitter(waits, factor, length):
    wait1, wait2 = itertools.tee(waits)
    res = itertools.islice(zip(wait1, retrier.proportional_jitter(factor=factor, waits=wait2)), 0, length)
    assert all([original * (1 - factor) <= jittered <= original * (1 + factor) for original, jittered in res])


@given(waits(), st.integers(min_value=0, max_value=10))
@settings(max_examples=max_examples)
def test_max_tries(waits, tries):
    len(list(retrier.max_tries(tries, waits))) <= tries


@given(waits(), st.integers(max_value=-1))
@settings(max_examples=max_examples)
def test_max_tries_negative(waits, tries):
    with pytest.raises(AssertionError):
        next(retrier.max_tries(tries, waits))


async def test_retrier_repeats_on_exception():
    count = 0

    async def action():
        nonlocal count
        count += 1
        raise Exception()

    r = retrier.Retrier.from_simple_action(action)
    with pytest.raises(retrier.NoMoreRetriesError):
        await r([timedelta()] * 5)

    assert count == 5


async def test_retrier_repeats_both_actions():
    initial_count = 0
    retry_count = 0

    async def initial_action():
        nonlocal initial_count
        initial_count += 1
        raise Exception("foo")

    async def retry_action(ex):
        nonlocal retry_count
        retry_count += 1
        assert ex.message == "foo"
        raise Exception()

    r = retrier.Retrier.from_initial_and_retry(initial_action, retry_action)
    with pytest.raises(retrier.NoMoreRetriesError):
        await r([timedelta()] * 5)

    assert initial_count == 1
    assert retry_count == 4


async def test_retrier_retry_on_exception_type():
    count = 0

    class MyEx(Exception):
        pass

    async def action():
        nonlocal count
        count += 1
        if count == 1:
            raise ValueError()
        else:
            raise MyEx()

    r = retrier.Retrier.from_simple_action(action).retry_on_exception_type(ValueError)
    with pytest.raises(MyEx):
        await r([timedelta()] * 5)

    assert count == 2


async def test_retrier_returns_on_success():
    count = 0

    async def action():
        nonlocal count
        count += 1
        if count == 5:
            return "done"
        else:
            raise Exception()

    r = retrier.Retrier.from_simple_action(action)
    res = await r([timedelta()] * 10)

    assert count == 5
    assert res == "done"


async def test_retrier_inspecting_exception():
    class E(Exception):
        def __init__(self, n):
            self.n = n

    count = 0

    async def action():
        nonlocal count
        count += 1
        raise E(count)

    r = retrier.Retrier.from_simple_action(action).retry_on(lambda e: e.n < 4)

    with pytest.raises(E) as exc_info:
        await r([timedelta()] * 10)
    assert exc_info.value.n == 4


async def test_retrier_with_throwing_retry_on():
    async def action():
        raise Exception()

    r = retrier.Retrier.from_simple_action(action).retry_on(lambda e: 1 / 0)

    with pytest.raises(ZeroDivisionError) as exc_info:
        await r([timedelta()] * 10)


async def test_retrier_sleeps():
    times = []
    last = time.monotonic()

    async def action():
        nonlocal times, last
        now = time.monotonic()
        diff = now - last
        last = now
        times.append(diff)
        raise Exception()

    r = retrier.Retrier.from_simple_action(action)
    waits = [timedelta(milliseconds=n) for n in range(0, 500, 100)]
    with pytest.raises(retrier.NoMoreRetriesError):
        await r(waits)

    assert all(actual > expected for actual, expected in zip(times, [t / 10 for t in range(0, 5)]))
