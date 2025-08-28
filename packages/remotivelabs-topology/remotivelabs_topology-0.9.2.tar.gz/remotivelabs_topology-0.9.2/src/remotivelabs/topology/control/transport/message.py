from __future__ import annotations

import base64
import json
import uuid
from dataclasses import dataclass, field
from enum import Enum


class TransportMessageType(Enum):
    REQUEST = 0
    RESPONSE = 1


@dataclass
class TransportMessage:
    type: TransportMessageType
    source: str
    payload: bytes
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


def dumps(msg: TransportMessage) -> bytes:
    """Serialize message using JSON with base64-encoded payload"""
    data = {"type": msg.type.value, "payload": base64.b64encode(msg.payload).decode(), "id": msg.id, "source": msg.source}
    return json.dumps(data).encode()


def loads(data: bytes) -> TransportMessage:
    """Deserialize message from JSON format"""
    obj = json.loads(data.decode())
    return TransportMessage(
        type=TransportMessageType(obj["type"]), payload=base64.b64decode(obj["payload"]), id=str(obj["id"]), source=obj["source"]
    )
