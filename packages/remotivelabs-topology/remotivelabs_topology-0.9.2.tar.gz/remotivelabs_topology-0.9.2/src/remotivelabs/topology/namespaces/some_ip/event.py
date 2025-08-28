from __future__ import annotations

from dataclasses import dataclass, field

from remotivelabs.broker import SignalValue
from remotivelabs.topology.namespaces.some_ip.types import ServiceName


@dataclass
class SomeIPEvent:
    """
    Represents a SOME/IP event.

    Attributes:
        name: The name of the event.
        service_instance_name: The name of the service associated with the event.
        raw: Raw bytes of the event payload. If non-empty, it takes precedence over `parameters` when emitting an event.
        parameters:
            A dictionary of key-value pairs representing decoded event data.
            Note: `str` is only supported for named values (e.g., Enums).

    Note:
        When handling the event, if `raw` is non-empty, it overrides the contents of `parameters`.
    """

    name: str
    service_instance_name: ServiceName
    raw: bytes = b""
    parameters: dict[str, SignalValue] = field(default_factory=dict)
