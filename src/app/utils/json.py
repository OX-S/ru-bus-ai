from __future__ import annotations
import orjson
from fastapi.responses import ORJSONResponse

__all__ = ["ORJSONResponse", "jload", "jdump"]

def jload(b: bytes):
    return orjson.loads(b)

def jdump(obj) -> bytes:
    return orjson.dumps(obj)