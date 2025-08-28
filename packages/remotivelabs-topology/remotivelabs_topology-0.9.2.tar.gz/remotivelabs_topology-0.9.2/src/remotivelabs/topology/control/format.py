from __future__ import annotations

import base64
from typing import Any

"""
Utility functions for encoding and decoding bytes in JSON using a agreed upon key ("__bytes__"), as JSON does not support bytes natively.
"""


def encode_bytes(obj: Any) -> dict[str, Any]:
    """Special handling for bytes encoding"""
    if isinstance(obj, bytes):
        return {"__bytes__": base64.b64encode(obj).decode("utf-8")}
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def decode_bytes(obj: dict[str, Any]) -> Any:
    """Special handling for bytes decoding"""
    if isinstance(obj, dict) and "__bytes__" in obj:
        return base64.b64decode(obj["__bytes__"])
    return obj
