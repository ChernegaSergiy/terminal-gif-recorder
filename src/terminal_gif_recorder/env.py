"""
Environment management and system utility discovery.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional


def find_binary(name: str, fallback_paths: Optional[List[str]] = None) -> str:
    """Find the path to an executable binary or raise FileNotFoundError."""
    found = shutil.which(name)
    if found:
        return found
    if fallback_paths:
        for p in fallback_paths:
            expanded = os.path.expanduser(p)
            if os.path.isfile(expanded) and os.access(expanded, os.X_OK):
                return expanded
    raise FileNotFoundError(
        f"Utility '{name}' not found. Please check your PATH or install it."
    )


def setup_clean_zdotdir() -> Path:
    """
    Creates a temporary ZDOTDIR directory with a .zshrc that sources the user's ~/.zshrc,
    while disabling unwanted characters and artifacts (such as the '%' symbol at line beginnings).
    """
    zdotdir = Path(tempfile.gettempdir()) / "terminal_recorder_zdotdir"
    zdotdir.mkdir(parents=True, exist_ok=True)
    zshrc_file = zdotdir / ".zshrc"

    zshrc_content = (
        "# Temporary profile for clean terminal recording\n"
        "[[ -f ~/.zshrc ]] && source ~/.zshrc\n\n"
        "# Suppress partial line mark (%) and extraneous control signals\n"
        'PROMPT_EOL_MARK=""\n'
        "unsetopt PROMPT_SP\n"
        "unsetopt PROMPT_CR\n"
        "POWERLEVEL9K_INSTANT_PROMPT=off\n"
    )
    zshrc_file.write_text(zshrc_content, encoding="utf-8")
    return zdotdir
