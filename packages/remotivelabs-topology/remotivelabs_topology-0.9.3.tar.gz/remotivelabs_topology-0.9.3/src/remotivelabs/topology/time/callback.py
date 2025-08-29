from __future__ import annotations

from typing import Protocol


class OnTickCallback(Protocol):
    """
    Callback function that will be called on each tick.
    """

    async def __call__(self, elapsed_time: float, since_last_tick: float, total_drift: float, interval: float) -> bool | None:
        """
        Args:
            elapsed_time: The time since the start of the ticker, in seconds
            since_last_tick: The time since the last tick, in seconds
            total_drift: The total drift time, in seconds
            interval: The desired interval between ticks, in seconds

        Returns:
            True if the ticker should stop, False or None otherwise
        """
