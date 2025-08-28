from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from remotivelabs.topology.comm.format import MessageDecodeError
from remotivelabs.topology.control.format import decode_bytes, encode_bytes


@dataclass
class ControlResponse:
    """
    Message structure and serialization for control responses.
    """

    status: str = "ok"
    data: Any = None


def dumps(msg: ControlResponse) -> bytes:
    result: dict[str, Any] = {"status": msg.status}
    if msg.data is not None:
        result["data"] = msg.data
    return json.dumps(result, default=encode_bytes).encode("utf-8")


def loads(data: Any) -> ControlResponse:
    try:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        parsed = json.loads(data, object_hook=decode_bytes)
        return ControlResponse(data=parsed.get("data", None), status=parsed.get("status", "ok"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise MessageDecodeError("Invalid message format") from e
