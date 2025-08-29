from __future__ import annotations

import asyncio
import inspect
import time
from typing import Callable

from hamcrest import assert_that
from hamcrest.core.matcher import Matcher
from tenacity import AsyncRetrying, stop_after_delay


class RetryAssert:
    """
    A class to perform asynchronous retries on a condition, with configurable timeout.
    Use await_at_most() to create this class.
    """

    def __init__(self, timeout=10) -> None:
        """
        Initializes the RetryAssert instance.

        :param timeout: The maximum duration to wait before giving up, in seconds.
        """
        self.timeout = timeout

    async def until(self, func: Callable, matcher: Matcher) -> None:
        """
        Waits until the result of the given function matches the provided matcher, retrying until timeout.

        :param func: A callable that returns the result to be tested.
        :param matcher: A matcher from hamcrest to evaluate the result against.

        :raises TypeError: If func is not a callable.
        """
        if not callable(func):
            raise TypeError(f"Arguments used in .until(Callable) must be of type Callable, was {type(func)}")

        retrying = AsyncRetrying(stop=stop_after_delay(self.timeout))
        remaining = self.timeout
        async for attempt in retrying:
            with attempt:
                result = func()
                if inspect.isawaitable(result):
                    result = await asyncio.wait_for(result, timeout=remaining)
                remaining = self.timeout + 1 - (time.monotonic() - attempt.retry_state.start_time)

                assert_that(result, matcher)


def await_at_most(seconds: float) -> RetryAssert:
    """
    Factory function to create a RetryAssert instance with a specified timeout.

    :param seconds: The maximum duration to wait before giving up, in seconds.
    :return: A configured instance of RetryAssert.
    """
    return RetryAssert(timeout=seconds)
