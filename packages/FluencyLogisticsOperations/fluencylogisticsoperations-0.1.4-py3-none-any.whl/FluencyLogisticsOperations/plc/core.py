from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional
from urllib.parse import parse_qs

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .._version import __version__
from .._utils import format_args
from .segment import Segment
from .node import FloNode

__all__ = ["PLC"]


def _default_token_provider() -> str:
    token = os.environ.get("FLO_TOKEN")
    if not token:
        raise RuntimeError("FLO_TOKEN is not set and no token_provider was supplied to PLC().")
    return token


def _build_retry(total: int = 3) -> Retry:
    return Retry(
        total=total,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("POST",),
        raise_on_status=False,
    )


@dataclass
class PLC:
    """
    Public Layer Client (PLC) for FLO Gateway.

    - Captures dot-notation chains and posts a single form field `method` to `/rpc`
    - Positional args are unquoted; kwargs are JSON-like with quoted strings
    - Parses form-encoded or JSON responses into pandas.DataFrame
    """

    base_url: Optional[str] = None
    token_provider: Callable[[], str] = field(default_factory=_default_token_provider)
    timeout_seconds: float = 60.0
    leaf_methods: set[str] = field(
        default_factory=lambda: {
            "get", "collect", "iter",
            "patch", "post", "put",
            "delete",
        }
    )
    session: Optional[requests.Session] = None

    def __post_init__(self) -> None:
        if not self.base_url:
            self.base_url = os.environ.get("FLO_BASE_URL", "https://fluency-logistics-operations.io")
        self.base_url = self.base_url.rstrip("/")
        if self.session is None:
            s = requests.Session()
            adapter = HTTPAdapter(max_retries=_build_retry())
            s.mount("http://", adapter)
            s.mount("https://", adapter)
            self.session = s

    @property
    def client(self) -> "FloNode":
        return FloNode(self, [Segment("client")])

    def _execute(self, segments: List["Segment"]) -> pd.DataFrame:
        method_expr = ".".join(seg.render() for seg in segments)
        url = f"{self.base_url}/rpc"
        headers = {
            "Authorization": f"Bearer {self.token_provider()}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/x-www-form-urlencoded, application/json;q=0.9",
            "User-Agent": f"FLO-Public/{__version__}",
        }
        resp = self.session.post(
            url, data={"method": method_expr}, headers=headers, timeout=self.timeout_seconds
        )

        ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        body_text = resp.text or ""

        if resp.status_code >= 400:
            detail = body_text
            try:
                if ctype == "application/x-www-form-urlencoded":
                    parsed = parse_qs(body_text)
                    detail = parsed.get("error", [detail])[0]
                elif ctype == "application/json":
                    j = resp.json()
                    detail = j.get("error") or j
            except Exception:
                pass
            raise RuntimeError(f"FLO RPC failed ({resp.status_code}) for method='{method_expr}': {detail}")

        payload_obj: Any = None
        try:
            if ctype == "application/x-www-form-urlencoded":
                form = parse_qs(body_text)
                raw = form.get("payload", [None])[0] or form.get("data", [None])[0]
                if raw is None and len(form) == 1:
                    raw = next(iter(form.values()))[0]
                if raw is None:
                    return pd.DataFrame()
                try:
                    payload_obj = json.loads(raw)
                except json.JSONDecodeError:
                    return pd.DataFrame([{"payload": raw}])
            elif ctype == "application/json":
                payload_obj = resp.json()
            else:
                try:
                    payload_obj = json.loads(body_text)
                except Exception:
                    return pd.DataFrame([{"payload": body_text}])
        except Exception as e:
            raise RuntimeError(f"Failed to parse FLO RPC response for method='{method_expr}': {e}")

        return _to_dataframe(payload_obj)


def _to_dataframe(obj: Any) -> pd.DataFrame:
    """Best-effort conversion to pandas.DataFrame."""
    try:
        if isinstance(obj, dict):
            if "data" in obj and isinstance(obj["data"], list):
                return pd.DataFrame(obj["data"])
            return pd.json_normalize(obj)
        if isinstance(obj, list):
            return pd.DataFrame(obj)
        return pd.DataFrame([{"value": obj}])
    except Exception:
        return pd.DataFrame([{"payload": json.dumps(obj, ensure_ascii=False)}])
