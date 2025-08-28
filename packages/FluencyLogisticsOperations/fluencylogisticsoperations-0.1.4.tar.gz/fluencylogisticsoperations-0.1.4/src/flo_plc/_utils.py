from __future__ import annotations
from typing import Any, List

def quote_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'

def format_value_kw(v: Any) -> str:
    if isinstance(v, str):
        return quote_string(v)
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    return str(v)

def format_args(positional: List[Any], keyword: dict[str, Any]) -> str:
    parts: List[str] = []
    if positional:
        parts.extend(str(a) for a in positional)
    if keyword:
        parts.extend(f"{k}={format_value_kw(v)}" for k, v in keyword.items())
    return ", ".join(parts)
