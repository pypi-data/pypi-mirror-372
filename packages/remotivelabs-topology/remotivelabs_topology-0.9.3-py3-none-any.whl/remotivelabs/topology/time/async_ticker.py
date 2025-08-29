from __future__ import annotations

import asyncio
import logging
import time

from remotivelabs.topology.time.callback import OnTickCallback

_logger = logging.getLogger(__name__)


async def _ticker(interval_in_sec: float, on_tick: OnTickCallback):
    """
    Runs an infinite loop that calls the on_tick callback at the given interval. It takes into account the time it takes to execute the
    callback and adjusts the sleep time accordingly.

    Note: if sleep time is negative, we're behind schedule. We use the special sleep(0), which avoids being scheduled on the event loop and
    only yields if there are other tasks waiting to run. This is the fastest way to "catch up", but it is still "best effort".

    It is possible to stop the ticker by returning True from the on_tick callback. You can also stop the ticker by cancelling the task.
    """
    _logger.debug(f"timer scheduled at every {interval_in_sec} seconds")
    start_time = time.monotonic()
    last_tick = start_time
    total_drift = 0.0

    try:
        # initial delay
        await asyncio.sleep(interval_in_sec)

        # loop until cancelled or callback returns False
        while True:
            tick_time = time.monotonic()
            elapsed_time = tick_time - start_time  # total time since ticker start
            since_last_tick = tick_time - last_tick  # time since last tick
            total_drift += since_last_tick - interval_in_sec  # drift is the difference between the expected and actual time
            last_tick = tick_time

            if await on_tick(
                elapsed_time=elapsed_time,
                since_last_tick=since_last_tick,
                total_drift=total_drift,
                interval=interval_in_sec,
            ):
                break  # cancel the timer if the callback returns True

            callback_duration = time.monotonic() - tick_time  # time it took to execute the callback

            sleep_time = max(0, interval_in_sec - callback_duration)
            await asyncio.sleep(sleep_time)

    except asyncio.CancelledError:
        _logger.debug("timer cancelled")


def create_ticker(interval_in_sec: float, on_tick: OnTickCallback, loop: asyncio.AbstractEventLoop | None = None) -> asyncio.Task:
    """
    Creates a ticker that calls the on_tick function at the given interval.

    Note that the timer is a best effort timer. The actual interval may be longer than the specified interval if concurrent tasks are
    unwilling to yield the CPU.

    Args:
        interval_in_sec: The time interval in seconds between each tick
        on_tick: Callback function that will be called on each tick.
        loop: The event loop to schedule callbacks on. If None, uses the current loop

    Returns:
        A task that can be awaited or cancelled to stop the ticker
    """
    if loop is None:
        loop = asyncio.get_running_loop()

    return loop.create_task(_ticker(interval_in_sec, on_tick))
