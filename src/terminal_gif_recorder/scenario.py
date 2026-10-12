"""
Scenario definition and fluent builder API.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .actions import Action, KEY_MAP


class Scenario:
    """
    Represents an automated terminal recording scenario.
    Provides a fluent builder interface to chain keystrokes, typing, and pauses.
    """

    def __init__(
        self,
        cols: int = 80,
        rows: int = 20,
        theme: str = "github-dark",
        cwd: Optional[Union[str, Path]] = None,
        speed: float = 1.0,
        initial_pause: float = 1.2,
        final_pause: float = 1.8,
        actions: Optional[List[Action]] = None,
    ) -> None:
        self.cols = cols
        self.rows = rows
        self.theme = theme
        self.cwd = Path(os.path.expanduser(str(cwd))) if cwd else Path.cwd()
        self.speed = speed
        self.initial_pause = initial_pause
        self.final_pause = final_pause
        self.actions: List[Action] = actions if actions is not None else []

    def sleep(self, seconds: float) -> Scenario:
        """Pause execution for a given number of seconds."""
        self.actions.append(Action("sleep", seconds / self.speed))
        return self

    def type(
        self,
        text: str,
        char_delay_min: float = 0.045,
        char_delay_max: float = 0.085,
    ) -> Scenario:
        """Type text with realistic human typing delays between keystrokes."""
        self.actions.append(
            Action(
                "type",
                text,
                delay=(char_delay_min / self.speed, char_delay_max / self.speed),
            )
        )
        return self

    def key(self, key_name_or_bytes: Union[str, bytes]) -> Scenario:
        """Press a special key or send a raw byte sequence."""
        if isinstance(key_name_or_bytes, str):
            lower = key_name_or_bytes.lower()
            if lower in KEY_MAP:
                raw = KEY_MAP[lower]
            else:
                raw = key_name_or_bytes.encode("latin1")
        else:
            raw = key_name_or_bytes
        self.actions.append(Action("key", raw))
        return self

    def enter(self, pause_after: float = 0.4) -> Scenario:
        """Press Enter with an optional pause afterwards."""
        self.key("enter")
        if pause_after > 0:
            self.sleep(pause_after)
        return self

    def space(self, pause_after: float = 0.2) -> Scenario:
        """Press Space with an optional pause afterwards."""
        self.key("space")
        if pause_after > 0:
            self.sleep(pause_after)
        return self

    def up(self, pause_after: float = 0.2) -> Scenario:
        """Press Up arrow key with an optional pause afterwards."""
        self.key("up")
        if pause_after > 0:
            self.sleep(pause_after)
        return self

    def down(self, pause_after: float = 0.2) -> Scenario:
        """Press Down arrow key with an optional pause afterwards."""
        self.key("down")
        if pause_after > 0:
            self.sleep(pause_after)
        return self

    def left(self, pause_after: float = 0.2) -> Scenario:
        """Press Left arrow key with an optional pause afterwards."""
        self.key("left")
        if pause_after > 0:
            self.sleep(pause_after)
        return self

    def right(self, pause_after: float = 0.2) -> Scenario:
        """Press Right arrow key with an optional pause afterwards."""
        self.key("right")
        if pause_after > 0:
            self.sleep(pause_after)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Serialize scenario into a dictionary."""
        return {
            "cols": self.cols,
            "rows": self.rows,
            "theme": self.theme,
            "cwd": str(self.cwd),
            "speed": self.speed,
            "initial_pause": self.initial_pause,
            "final_pause": self.final_pause,
            "actions": [act.to_dict() for act in self.actions],
        }

    def to_file(self, path: Union[str, Path]) -> None:
        """Save scenario to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Scenario:
        """Deserialize scenario from a dictionary."""
        actions = [Action.from_dict(item) for item in data.get("actions", [])]
        return cls(
            cols=data.get("cols", 80),
            rows=data.get("rows", 20),
            theme=data.get("theme", "github-dark"),
            cwd=data.get("cwd"),
            speed=data.get("speed", 1.0),
            initial_pause=data.get("initial_pause", 1.2),
            final_pause=data.get("final_pause", 1.8),
            actions=actions,
        )

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> Scenario:
        """Load scenario from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
