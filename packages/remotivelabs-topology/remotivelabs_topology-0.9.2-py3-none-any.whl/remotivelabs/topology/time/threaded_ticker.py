from __future__ import annotations

import asyncio
import logging
import time
from threading import Timer

from remotivelabs.topology.time.callback import OnTickCallback

_logger = logging.getLogger(__name__)


class ThreadedTicker:
    """
    ThreadedTicker provides similar functionality to asyncio.Task for timer-based operations. It calls the on_tick callback at regular
    intervals. The biggest difference is that ThreadedTicker schedules the callback to run on the event loop, but have no further control
    over the callback execution. Hence, it cannot compensate for long callback execution times. The upside is that it is guaranteed to run
    at the specified interval due to the timer being a thread-based solution. However, as mentioned before, if the callback takes longer
    than the interval, the number of scheduled callbacks will accumulate over time.

    Note that the timer is a best effort timer. The actual interval may be longer than the specified interval due to thread scheduling and
    callback scheduling time.
    """

    def __init__(self, interval_in_sec: float, on_tick: OnTickCallback, loop: asyncio.AbstractEventLoop) -> None:
        self._on_tick = on_tick
        self._interval = interval_in_sec
        self._timer: Timer | None = None
        self._start_time = 0.0
        self._last_tick = self._start_time
        self._total_drift = 0.0
        self._loop = loop

    @property
    def running(self) -> bool:
        return self._timer is not None

    def _tick(self) -> None:
        if not self.running:
            return

        tick_time = time.monotonic()
        elapsed_time = tick_time - self._start_time
        since_last_tick = tick_time - self._last_tick
        self._total_drift += since_last_tick - self._interval
        self._last_tick = tick_time

        # We put the callback on the event loop to allow it to run asynchronously
        async def _callback_task():
            stop = await self._on_tick(
                elapsed_time=elapsed_time,
                since_last_tick=since_last_tick,
                total_drift=self._total_drift,
                interval=self._interval,
            )
            if stop:
                self.cancel()  # cancel the timer if the callback returns False

        self._loop.call_soon_threadsafe(lambda: asyncio.create_task(_callback_task()))

        # Schedule next tick with compensated interval; longer if we're ahead of schedule, shorter if we're behind
        next_interval = max(0, self._interval - (since_last_tick - self._interval))
        self._timer = Timer(next_interval, self._tick)
        self._timer.start()

    def start(self) -> None:
        if not self.running:
            _logger.debug(f"timer scheduled at every {self._interval} seconds")
            self._start_time = time.monotonic()
            self._last_tick = self._start_time
            self._total_drift = 0.0

            # Schedule tick after the first interval
            self._timer = Timer(self._interval, self._tick)
            self._timer.start()

    def cancel(self) -> None:
        if self.running:
            assert self._timer is not None
            self._timer.cancel()
            self._timer.join()
            self._timer = None
            _logger.debug("timer cancelled")


def create_ticker(interval_in_sec: float, on_tick: OnTickCallback, loop: asyncio.AbstractEventLoop | None = None) -> ThreadedTicker:
    """
    Creates a ticker that calls the on_tick function at the given interval.

    Note that the timer is a best effort timer. The actual interval may be longer than the specified interval due to thread scheduling and
    callback execution time.

    Args:
        interval_in_sec: The time interval in seconds between each tick.
        on_tick: Callback coroutine that will be called on each tick. Make sure to handle exceptions in the callback, as they will not be
                 caught by the ticker.
        loop: The event loop to schedule callbacks on. If None, uses the current loop.
    """
    if loop is None:
        loop = asyncio.get_running_loop()

    ticker = ThreadedTicker(interval_in_sec, on_tick, loop)
    ticker.start()
    return ticker
