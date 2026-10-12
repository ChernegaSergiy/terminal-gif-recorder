#!/usr/bin/env python3
"""
Terminal GIF Recorder - CLI executable and entry point shim.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root and src directory are on sys.path for direct script execution
root_dir = Path(__file__).resolve().parent
src_dir = root_dir / "src"
for p in (str(root_dir), str(src_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

from terminal_gif_recorder import Action, KEY_MAP, Scenario, TerminalRecorder, compile_gif, play_scenario
from terminal_gif_recorder.scripts.record import main

__all__ = [
    "Action",
    "KEY_MAP",
    "Scenario",
    "TerminalRecorder",
    "compile_gif",
    "main",
    "play_scenario",
]

if __name__ == "__main__":
    main()
