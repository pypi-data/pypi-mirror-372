from __future__ import annotations

from typing import Any, Generic, Protocol

from remotivelabs.topology.comm.message import ControlMessageT


class MessageDecodeError(Exception):
    """
    Raised when a message cannot be parsed from bytes
    """


class MessageFormat(Protocol, Generic[ControlMessageT]):
    """
    MessageFormat allows the implementor to define the data format and serialization protocol for control messages in RemotiveTopology. In
    practice, almost all implementations will involve ECU control in some form, but the interface allows for other uses-cases as well.
    Most data formats, like JSON, are lossy, which means that it is unable to represent all Python data types. For example, bytes and
    complex data types like objects do not have a corresponding representation in JSON. Consequently, the serialization process must be
    customized for each data format, based on the types that the format supports.

    A message is sent over a Transport, which provides the mechanism for sending and receiving messages.
    """

    def loads(self, data: Any) -> ControlMessageT:
        """
        Parse a control message, most likely from bytes.
        Raises MessageDecodeError if the data is not a valid control message
        """

    def dumps(self, msg: ControlMessageT) -> bytes:
        """Serialize a control message into bytes"""
