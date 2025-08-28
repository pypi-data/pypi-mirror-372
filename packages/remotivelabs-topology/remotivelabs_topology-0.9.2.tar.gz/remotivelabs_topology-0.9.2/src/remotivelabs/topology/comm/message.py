from typing import TypeVar

ControlMessageT = TypeVar("ControlMessageT")
"""
A generic type of message.

May be anything from bytes to complex datastructures. It is up to the implementor of the ControlMessageFormat to define the
serialization/deserialization of the message to/from its data format on the Transport.
"""
