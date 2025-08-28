from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import AsyncGenerator, AsyncIterator, Union

from typing_extensions import Self

from remotivelabs.broker import (
    BrokerClient,
    Frame,
    FrameInfo,
    FrameName,
    FrameSubscription,
    NamespaceName,
    RestbusFrameConfig,
    RestbusSignalConfig,
    SecocProperty,
    Signal,
    SignalInfo,
    SignalName,
    WriteSignal,
)
from remotivelabs.topology.namespaces.filters import AllFramesFilter, FrameFilter, ReceiverFilter, SenderFilter, SignalFilter
from remotivelabs.topology.namespaces.input_handlers import FrameHandler, InputHandler
from remotivelabs.topology.namespaces.namespace import Namespace


class GenericNamespace(
    Namespace[Union[SenderFilter, ReceiverFilter, FrameFilter, AllFramesFilter, SignalFilter], Callable[[Frame], Awaitable[None]]]
):
    """
    GenericNamespace provides access to frames and signals in a specific namespace using a broker client.

    This class also manages restbus configurations which enable frame publishing based on filters.
    To load restbus configuration and activate the restbus, use this class as an async context manager.
    """

    def __init__(
        self,
        name: NamespaceName,
        broker_client: BrokerClient,
        restbus_configs: list[RestbusConfig] | None = None,
        decode_named_values: bool = False,
    ):
        """
        Initialize the generic namespace client.

        Args:
            name: The namespace name to operate in.
            broker_client: The client used to communicate with the broker.
            restbus_configs: Optional list of configurations with filters for the restbus.
                Applied in order; if multiple filters match the same frame, the last matching configuration takes precedence.
            decode_named_values: True will decode named values to str.

        Note:
            Use together with a `BehavioralModel` or start the instance using a context manager:
            ```python
            async with GenericNamespace(...) as broker_client:
                ...
            ```
        """
        super().__init__(name=name, broker_client=broker_client)
        self._restbus = Restbus(namespace=name, broker_client=broker_client, restbus_configs=restbus_configs or [])
        self._decode_named_values = decode_named_values

    @property
    def restbus(self) -> Restbus:
        """
        Property to interact with the restbus.
        The restbus manages periodic publishing of frames and signals.
        """
        return self._restbus

    async def open(self) -> Self:
        """
        Activate the restbus and load frame configurations using filters.
        This is an idempotent operation - calling it multiple times has no additional effect.

        Returns:
            The namespace
        """
        await self.restbus.open()
        return await super().open()

    async def close(self) -> None:
        """
        Will close the restbus, all frames are removed from the restbus in the namespace.
        This is an idempotent operation - calling it multiple times has no additional effect.
        """
        await super().close()
        await self.restbus.close()

    async def set_secoc_property(self, property: SecocProperty) -> None:
        """Set a SecOC property in the namespace."""
        await self._broker_client.set_secoc_property(namespace=self.name, property=property)

    async def list_frame_infos(self) -> list[FrameInfo]:
        """Return all available frame infos in the namespace."""
        return await self._broker_client.list_frame_infos(self.name)

    async def get_frame_info(self, name: str) -> FrameInfo | None:
        """Return information about a specific frame by name."""
        return await self._broker_client.get_frame_info(name, namespace=self.name)

    async def list_signal_infos(self) -> list[SignalInfo]:
        """Return all available signal infos in the namespace."""
        return await self._broker_client.list_signal_infos(self.name)

    async def get_signal_info(self, name: SignalName) -> SignalInfo | None:
        """Return information about a specific signal by name."""
        return await self._broker_client.get_signal_info(name, namespace=self.name)

    async def publish(self, *signals: WriteSignal) -> None:
        """
        Publish one or more signals to the broker.

        Args:
            *signals: One or more WriteSignal instances to publish.
        """
        await self._broker_client.publish((self._namespace, list(signals)))

    async def subscribe(self, *name: SignalName, on_change: bool = False) -> AsyncIterator[list[Signal]]:
        """
        Subscribe to a list of signals.

        Args:
            *signals:
                One or more signals to subscribe to.
            on_change: Whether to receive updates only on change.

        Note: does not support decoding enums

        Returns:
            An asynchronous iterator of lists of Signal objects.
        """
        return await self._broker_client.subscribe((self.name, list(name)), on_change=on_change)

    async def subscribe_frames(
        self,
        *frames: FrameSubscription,
        on_change: bool = False,
        initial_empty: bool = False,
        decode_named_values: bool = False,
    ) -> AsyncIterator[Frame]:
        """
        Subscribe to a Frames.

        Args:
            *frames: One or more frames to subscribe to.
            on_change: Whether to receive updates only on change.
            initial_empty: True will wait until the broker has sent an initial message
            decode_named_values: True will decode named values to str.

        Returns:
            An asynchronous iterator with Frames.
        """
        return await self._broker_client.subscribe_frames(
            (self.name, list(frames)), on_change=on_change, initial_empty=initial_empty, decode_named_values=decode_named_values
        )

    def create_input_handler(
        self,
        filters: Sequence[Union[SenderFilter, ReceiverFilter, FrameFilter, AllFramesFilter, SignalFilter]],
        callback: Callable[[Frame], Awaitable[None]],
    ) -> tuple[NamespaceName, InputHandler]:
        """
        Creates a list of input handlers for the given namespace to be used with a `BehavioralModel`.

        Each handler defines a filter and a corresponding async callback for processing matching frames.

        Args:
            - filters: A sequence of filter objects to select relevant frames or signals.
            - callback: An async callback function that receives and processes a Frame.
        """
        return (self.name, FrameHandler(filters=filters, cb=callback, decode_named_values=self._decode_named_values))


@dataclass
class RestbusConfig:
    """
    Configuration for the Restbus

    Attributes:
        restbus_filters: List of filters used to select frames; matching frames will be configured and managed by the restbus.
        delay_multiplier: Multiplier for applying artificial delays; default is 1 (no delay).
        cycle_time_millis: Optional fixed cycle time in milliseconds for publishing.
            By default the cycle time from the signal database is used.
    """

    restbus_filters: list[Union[SenderFilter, ReceiverFilter, FrameFilter, AllFramesFilter, SignalFilter]]
    delay_multiplier: float = 1
    cycle_time_millis: float | None = None


class Restbus:
    """
    Restbus provides a way to publish frames according to their cycle time.
    Sending recurring frames is common with for example CAN or LIN. Notice that each Namespace has its own Restbus.
    It allows configuring frame publishing behavior, applying filters, and controlling the restbus lifecycle.

    Also notice that new frames can be added or removed in order to emulate how different
    frames are sent depending on the state of the model.

    Usage:
        Should be used with through a `Namespace` implementation such as `GenericNamespace`, but can be used standalone.

        ```python
        async with Restbus(namespace, broker_client, restbus_configs) as restbus:
            await restbus.start()
        ```
    Args:
        namespace: The namespace to operate in.
        broker_client: The broker client to communicate with.
        restbus_configs: Optional list of configurations with filters for the restbus.
            Applied in order; if multiple filters match the same frame, the last matching configuration takes precedence.
    """

    def __init__(self, namespace: NamespaceName, broker_client: BrokerClient, restbus_configs: list[RestbusConfig] | None = None):
        self._namespace = namespace
        self._broker_client = broker_client
        self._restbus_configs = restbus_configs or []
        self._is_open = False
        self._configured_frames: set[FrameName] = set()

    async def open(self) -> Self:
        """
        Open the restbus and initialize it with configured frames.
        This is an idempotent operation - calling it multiple times has no additional effect.
        """
        if self._is_open:
            return self

        frame_infos = await self._broker_client.list_frame_infos(self._namespace)
        frames: dict[FrameName, RestbusFrameConfig] = {}
        for config in self._restbus_configs:
            matched_filters = set()
            for frame_info in frame_infos:
                for filter in config.restbus_filters:
                    if filter.filter_frames(frame_info):
                        matched_filters.add(filter)
                        cycle_time = (config.cycle_time_millis or frame_info.cycle_time_millis) * config.delay_multiplier
                        frame_config = RestbusFrameConfig(name=frame_info.name, cycle_time=cycle_time)
                        frames[frame_info.name] = frame_config
            for filter in config.restbus_filters:
                if filter not in matched_filters:
                    raise ValueError(f"Filter {filter} did not match any frames")

        if frames:
            await self.add(*frames.values())
            self._configured_frames.update(frames.keys())

        self._is_open = True
        return self

    async def close(self) -> None:
        """
        Close the restbus for this namespace, this will remove all configuration and put the restbus in idle state.
        This is an idempotent operation - calling it multiple times has no additional effect.
        """
        if not self._is_open:
            return

        await self._broker_client.restbus.close(self._namespace)
        self._configured_frames.clear()
        self._is_open = False

    async def __aenter__(self) -> Self:
        return await self.open()

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()

    async def add(self, *frame_configs: RestbusFrameConfig, start: bool = False):
        """
        Add frames by configuration to the restbus.

        Args:
            *frame_configs: One or more frame configurations
            start: Whether to start the restbus publishing immediately.
                Note: this flag controls a global state for the entire restbus, not individual frames.
        """
        await self._broker_client.restbus.add((self._namespace, list(frame_configs)), start=start)

    async def start(self):
        """Start restbus publishing for this namespace."""
        await self._broker_client.restbus.start(self._namespace)

    async def stop(self):
        """Stop restbus publishing for this namespace."""
        await self._broker_client.restbus.stop(self._namespace)

    async def remove(self, *frames: FrameName):
        """
        Remove frames from the restbus.

        Args:
            *frames: One or more frame names to remove
        """
        await self._broker_client.restbus.remove((self._namespace, list(frames)))

    async def update_signals(self, *signal_configs: RestbusSignalConfig) -> None:
        """
        Update signal configurations for the restbus.

        Args:
            *signal_configs: Signal configurations to update.
        """
        await self._broker_client.restbus.update_signals((self._namespace, list(signal_configs)))

    async def reset_signals(self, *signals: SignalName) -> None:
        """
        Reset specified signals in the restbus to their original values.

        Args:
            *signals: Signal names to reset.
        """
        await self._broker_client.restbus.reset_signals((self._namespace, list(signals)))

    async def reset(self) -> None:
        """Reset all restbus data for this namespace."""
        await self._broker_client.restbus.reset_namespaces(self._namespace)

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[TransactionContext, None]:
        """
        Context manager for batching signal updates and resets.

        Usage:
            ```python
            async with restbus.transaction() as tx:
                tx.updates.append(...)
                tx.resets.append(...)
            ```
        """
        tc = TransactionContext()
        yield tc
        if len(tc.resets) > 0:
            await self.reset_signals(*tc.resets)
        if len(tc.updates) > 0:
            await self.update_signals(*tc.updates)


@dataclass
class TransactionContext:
    updates: list[RestbusSignalConfig] = field(default_factory=list)
    resets: list[FrameName] = field(default_factory=list)

    def update(self, *signal_config: RestbusSignalConfig) -> None:
        self.updates.extend(signal_config)

    def set_update_bit(self, *signals: SignalName) -> None:
        self.updates.extend([RestbusSignalConfig.set_update_bit(name) for name in signals])

    def reset_signal(self, *signals: SignalName) -> None:
        self.resets.extend(signals)
