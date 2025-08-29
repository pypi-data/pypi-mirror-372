from __future__ import annotations

from typing import Any, Union

try:
    import orjson

    def dumps(obj: Any) -> bytes:
        return orjson.dumps(obj)

    def loads(data: Union[str, bytes, bytearray]) -> Any:
        if isinstance(data, (bytes, bytearray)):
            return orjson.loads(data)
        return orjson.loads(data.encode("utf-8"))

except Exception:
    import json as _json

    def dumps(obj: Any) -> bytes:
        return _json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )

    def loads(data: Union[str, bytes, bytearray]) -> Any:
        if isinstance(data, (bytes, bytearray)):
            data = data.decode("utf-8")
        return _json.loads(data)
