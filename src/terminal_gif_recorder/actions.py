"""
Terminal interaction actions and keyboard key mappings.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple, Union


# Special key combinations and ANSI control sequences
KEY_MAP: Dict[str, bytes] = {
    "enter": b"\r",
    "return": b"\r",
    "tab": b"\t",
    "space": b" ",
    "backspace": b"\x7f",
    "escape": b"\x1b",
    "esc": b"\x1b",
    "up": b"\x1b[A",
    "down": b"\x1b[B",
    "right": b"\x1b[C",
    "left": b"\x1b[D",
    "home": b"\x1b[H",
    "end": b"\x1b[F",
    "ctrl+c": b"\x03",
    "ctrl+d": b"\x04",
}


class Action:
    """Represents a single atomic action during terminal simulation."""

    def __init__(
        self,
        action_type: str,
        value: Any,
        delay: Union[float, Tuple[float, float]] = 0.0,
    ) -> None:
        self.type = action_type  # 'type', 'key', 'sleep'
        self.value = value
        self.delay = delay

    def to_dict(self) -> Dict[str, Any]:
        """Serialize action to a JSON-compatible dictionary."""
        if self.type == "key":
            val = self.value.decode("latin1") if isinstance(self.value, bytes) else str(self.value)
            return {"type": "key", "value": val}
        return {"type": self.type, "value": self.value, "delay": self.delay}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Action:
        """Deserialize action from a dictionary."""
        atype = data["type"]
        val = data["value"]
        if atype == "key":
            raw_bytes = val.encode("latin1") if isinstance(val, str) else bytes(val)
            return cls("key", raw_bytes)
        delay = data.get("delay", 0.0)
        if isinstance(delay, list):
            delay = tuple(delay)
        return cls(atype, val, delay=delay)
