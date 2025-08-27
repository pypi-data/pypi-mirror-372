"""A mechanism to retry operations, async sleeping between attempts.

The most important part of the interface in this module, are the functions
used to generate `Waits` objects, a chain of timedelta that define how much
to wait between retries.

Example usage: call coroutine `coro`, retrying 5 times, or until ValueError is raised.
Between attempts, sleep for an increasing amount of time, with jitter applied
in every wait.

```python

waits = max_tries(5, proportional_jitter(0.5, linear_wait(timedelta(1), timedelta())))
retrier = Retrier.from_simple_action(coro).retry_unless_exception_type(ValueError)

result = retrier(waits)

```

"""

from __future__ import annotations

import asyncio
import itertools
import random
from collections.abc import Coroutine, Iterable, Iterator
from datetime import timedelta
from typing import Any, Callable, Generic, TypeVar

from typing_extensions import TypeAlias


class NoMoreRetriesError(Exception):
    pass


Waits: TypeAlias = Iterable[timedelta]

RetrierRes = TypeVar("RetrierRes")


class Retrier(Generic[RetrierRes]):
    """A Callable that can retry operations sleeping in between attempts.

    What operations to execute, and what exceptions are considered retryable,
    are defined at initialization time. How much to wait between retries is
    defined on the __call__ call.

    All operations are considered successful if they don't raise an exceptions,
    in that case retry attempts stop and __call__ returns the last result.
    """

    def __init__(
        self,
        initial_action: Callable[[], Coroutine[Any, Any, RetrierRes]],
        retry_actions: Iterator[Callable[[Exception], Coroutine[Any, Any, RetrierRes]]],
        retryable_exception: Callable[[Exception], bool] = lambda _: True,
    ):
        """Low level constructor, you probably want to use one of the class methods.

        Parameters:
        - initial_action: the coroutine to attempt initially. Retries will be done if it raises.
        - retry_actions: an iterator to other coroutines to attempt in order. Retries will will continue if the coroutines raise.
          These coroutines take the exception thrown by the previous attempt
        - retryable_exception: a function to decide if the exception result of an action must be retried.
          Retrying stops if retryable_exception returns False, raising the last exception.
        """
        self.initial_action = initial_action
        self.retry_actions = retry_actions
        self.retryable_exception = retryable_exception

    @classmethod
    def from_simple_action(cls, action: Callable[[], Coroutine[Any, Any, RetrierRes]]) -> Retrier[RetrierRes]:
        """Create a retrier that executes `action`, always asking for retries on any exceptions"""
        return cls(initial_action=action, retry_actions=itertools.repeat(lambda _: action()))

    @classmethod
    def from_initial_and_retry(
        cls,
        initial_action: Callable[[], Coroutine[Any, Any, RetrierRes]],
        retry_action: Callable[[Exception], Coroutine[Any, Any, RetrierRes]],
    ) -> Retrier[RetrierRes]:
        """Create a Retrier that executes `initial_action` first and then `retry_action` on retries.

        It always asks for retries on any exceptions"""
        return cls(initial_action=initial_action, retry_actions=itertools.repeat(lambda e: retry_action(e)))

    def retry_on(self, test: Callable[[Exception], bool]) -> Retrier[RetrierRes]:
        """Set the exception filter that checks if retry is needed"""
        self.retryable_exception = test
        return self

    def retry_on_exception_type(self, exception_type: type) -> Retrier[RetrierRes]:
        """Retry only if the raised exception has type `exception_type`"""
        return self.retry_on(lambda e: isinstance(e, exception_type))

    async def _sleep(self, wait: timedelta) -> None:
        await asyncio.sleep(wait.total_seconds())

    async def __call__(self, waits: Waits) -> RetrierRes:
        """Trigger the actions and retries.

        Parameters:

            waits: An iterable to timedelays that will be used to wait between actions.
            The total number of retries will the the size of the longest iterable: waits or actions.

        Returns:
        The result of the first non raising action executed.

        Raises:
            NoMoreRetriesError if waits or the provided actions is exhausted before a seccussful action.
        """
        waits_it = iter(waits)
        try:
            first_wait = next(waits_it)
        except StopIteration:
            raise NoMoreRetriesError()

        await self._sleep(first_wait)
        exception = None
        try:
            return await self.initial_action()
        except Exception as err:
            exception = err

        if self.retryable_exception(exception):
            for action, wait in zip(self.retry_actions, waits_it):
                await asyncio.sleep(wait.total_seconds())
                try:
                    final_res = await action(exception)
                    return final_res
                except Exception as err:
                    if self.retryable_exception(err):
                        exception = err
                    else:
                        raise err
        else:
            raise exception

        raise NoMoreRetriesError()


def max_tries(n: int, waits: Waits) -> Waits:
    """Limit `waits` to up to n elements"""
    assert n >= 0
    return itertools.islice(waits, n)


def constant_wait(wait: timedelta = timedelta()) -> Waits:
    """Return a Waits that always sleeps for `wait`"""
    assert wait >= timedelta()
    return itertools.repeat(wait)


def linear_wait(delta: timedelta, initial: timedelta = timedelta()) -> Waits:
    """Return a Waits that waits for `initial` in the first attempt and then increases the wait by `delta` every time."""
    assert initial >= timedelta()
    while True:
        yield initial
        initial += delta


def exponential_wait(factor: float, initial: timedelta) -> Waits:
    """Return a Waits that waits for `initial` in the first attempt and then multiplies the wait by `factor` every time."""
    assert initial >= timedelta()
    assert factor >= 0
    while True:
        yield initial
        initial *= factor


def _apply_jitter(factor: float, t: timedelta) -> timedelta:
    assert 0 < factor <= 1
    min = t.total_seconds() * (1 - factor)
    max = t.total_seconds() * (1 + factor)
    return timedelta(seconds=random.uniform(min, max))


def jitter(jitter_factors: Iterable[float], waits: Waits) -> Waits:
    """Modify `waits` by applying a jitter to each wait.

    Each `jitter_factor` will add a component to the wait, rendered from a uniform
    distribution [wait * (1-factor), wait * (1+factor)].

    The resulting `Waits` will have as many elements as the longest of
    `waits` and `jitter_factors`.
    """
    return map(lambda tuple: _apply_jitter(*tuple), zip(jitter_factors, waits))


def proportional_jitter(factor: float, waits: Waits) -> Waits:
    """A jittered `Waits` using the same factor for every wait.

    See" `jitter`.
    """
    return jitter(itertools.repeat(factor), waits)
