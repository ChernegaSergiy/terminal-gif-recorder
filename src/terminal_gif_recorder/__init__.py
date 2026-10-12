"""
Terminal GIF Recorder package.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from .actions import Action, KEY_MAP
from .compiler import compile_gif
from .scenario import Scenario
from .terminal import play_scenario


class TerminalRecorder(Scenario):
    """
    Convenience facade combining Scenario building and GIF compilation.
    Provides complete backward compatibility with previous versions.
    """

    def save_gif(
        self,
        output_gif_path: Union[str, Path],
        temp_cast_path: Optional[Union[str, Path]] = None,
    ) -> Path:
        """Records scenario and compiles to GIF."""
        return compile_gif(self, output_gif_path, temp_cast_path=temp_cast_path)


__all__ = [
    "Action",
    "KEY_MAP",
    "Scenario",
    "TerminalRecorder",
    "compile_gif",
    "play_scenario",
]
