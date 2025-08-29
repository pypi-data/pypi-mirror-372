from __future__ import annotations

import enum
from dataclasses import dataclass, field

from remotivelabs.broker import SignalValue


class ReturnCode(enum.IntEnum):
    """"""

    E_OK = 0
    E_NOT_OK = 1
    E_UNKNOWN_SERVICE = 2
    E_UNKNOWN_METHOD = 3
    E_NOT_READY = 4
    E_NOT_REACHABLE = 5
    E_TIMEOUT = 6
    E_WRONG_PROTOCOL_VERSION = 7
    E_WRONG_INTERFACE_VERSION = 8
    E_MALFORMED_MESSAGE = 9
    E_WRONG_MESSAGE_TYPE = 10


class ErrorReturnCode(enum.IntEnum):
    """"""

    E_NOT_OK = 1
    E_UNKNOWN_SERVICE = 2
    E_UNKNOWN_METHOD = 3
    E_NOT_READY = 4
    E_NOT_REACHABLE = 5
    E_TIMEOUT = 6
    E_WRONG_PROTOCOL_VERSION = 7
    E_WRONG_INTERFACE_VERSION = 8
    E_MALFORMED_MESSAGE = 9
    E_WRONG_MESSAGE_TYPE = 10


@dataclass
class SomeIPResponse:
    """
    Represents a SOME/IP response

    Attributes:
        raw: The raw data received in the response. If non-empty, it takes priority over `parameters`.
        parameters:
            A dictionary of key-value pairs representing decoded response data.
            Note: `str` is only supported for named values (e.g., Enums).

    Note:
        When processing a response, if `raw` is non-empty, it overrides the contents of `parameters`.
    """

    raw: bytes = b""
    parameters: dict[str, SignalValue] = field(default_factory=dict)


@dataclass
class SomeIPError:
    """
    Represents a SOME/IP error response

    Attributes:
        return_code: The return code of the response.
    """

    return_code: int | str
