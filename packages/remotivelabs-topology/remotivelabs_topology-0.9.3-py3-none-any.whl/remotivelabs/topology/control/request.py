from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from remotivelabs.topology.comm.format import MessageDecodeError
from remotivelabs.topology.control.format import decode_bytes, encode_bytes


@dataclass
class ControlRequest:
    """
    Message structure and serialization for control requests.
    Attributes:
        type: The type of control message.
        argument (Any | None): Optional argument to the control message.
            Must be JSON-serializable if provided.
    """

    type: str
    argument: Any | None = None


def dumps(msg: ControlRequest) -> bytes:
    """Serialize a ControlRequest to bytes"""
    msg_dict = asdict(msg)
    json_str = json.dumps(msg_dict, default=encode_bytes)
    return json_str.encode("utf-8")


def loads(data: bytes | str) -> ControlRequest:
    """Deserialize bytes or string to a ControlRequest"""
    try:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        decoded = json.loads(data, object_hook=decode_bytes)

        if not all(key in decoded for key in ["type"]):
            raise MessageDecodeError("Missing required fields in message")

        return ControlRequest(type=decoded["type"], argument=decoded.get("argument", None))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise MessageDecodeError(f"Invalid message format: {str(e)}") from e
    except ValueError as e:
        raise MessageDecodeError(f"Invalid enum value: {str(e)}") from e
