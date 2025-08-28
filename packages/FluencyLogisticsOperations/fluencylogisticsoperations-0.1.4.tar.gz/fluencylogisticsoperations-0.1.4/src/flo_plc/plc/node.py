from __future__ import annotations

from typing import Any, List

from .._utils import format_args
from .segment import Segment


class FloNode:
    def __init__(self, flo: "PLC", segments: List[Segment]):
        self._flo = flo
        self._segments = segments

    def __getattr__(self, name: str) -> "FloNode":
        if name.startswith("_"):
            raise AttributeError(name)
        return FloNode(self._flo, self._segments + [Segment(name)])

    def __call__(self, *args: Any, **kwargs: Any):
        if not self._segments:
            raise RuntimeError("Invalid FLO chain: no segments")

        last = self._segments[-1]
        args_repr = format_args(list(args), kwargs)
        updated_last = last.with_args(args_repr)
        updated_segments = self._segments[:-1] + [updated_last]

        if last.name in self._flo.leaf_methods:
            return self._flo._execute(updated_segments)
        return FloNode(self._flo, updated_segments)

    def __repr__(self) -> str:  # pragma: no cover
        path = ".".join(s.render() for s in self._segments)
        return f"<FLO chain: {path}>"
