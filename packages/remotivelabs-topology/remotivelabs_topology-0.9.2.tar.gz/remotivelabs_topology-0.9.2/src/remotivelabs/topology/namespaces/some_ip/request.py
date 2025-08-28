from __future__ import annotations

import enum
from dataclasses import dataclass, field

from remotivelabs.broker import SignalValue
from remotivelabs.topology.namespaces.some_ip.types import ServiceName


class RequestType(enum.IntEnum):
    """"""

    REQUEST = 0
    REQUEST_NO_RETURN = 1


@dataclass(frozen=True)
class SomeIPRequest:
    """
    Represents a SOME/IP request

    Attributes:
        name: The name of the request.
        service_instance_name: The name of the service associated with the request.
        raw: The raw data to be sent with the request. If non-empty, it takes priority over `parameters`.
        parameters:
            A dictionary of key-value pairs representing decoded request data.
            Note: `str` is only supported for named values (e.g., Enums).
    Note:
        When sending a request, if `raw` is non-empty, it overrides the contents of `parameters`.
    """

    name: str
    service_instance_name: ServiceName
    message_type: RequestType
    raw: bytes = b""
    parameters: dict[str, SignalValue] = field(default_factory=dict)


@dataclass(frozen=True)
class SomeIPRequestReturn(SomeIPRequest):
    message_type: RequestType = field(default=RequestType.REQUEST, init=False)


@dataclass(frozen=True)
class SomeIPRequestNoReturn(SomeIPRequest):
    message_type: RequestType = field(default=RequestType.REQUEST_NO_RETURN, init=False)
