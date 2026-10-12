#!/usr/bin/env python3
"""
Terminal GIF Recorder - CLI executable and entry point shim.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root is on sys.path for direct script execution
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src import Action, KEY_MAP, Scenario, TerminalRecorder, compile_gif, play_scenario
from src.scripts.record import main

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
