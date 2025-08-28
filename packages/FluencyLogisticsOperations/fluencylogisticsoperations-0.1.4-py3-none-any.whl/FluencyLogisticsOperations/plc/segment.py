from __future__ import annotations
from typing import Optional

class Segment:
    def __init__(self, name: str, args_repr: Optional[str] = None):
        self.name = name
        self.args_repr = args_repr

    def with_args(self, args_repr: str) -> "Segment":
        return Segment(self.name, args_repr)

    def render(self) -> str:
        if self.args_repr is None:
            return self.name
        return f"{self.name}({self.args_repr})"
