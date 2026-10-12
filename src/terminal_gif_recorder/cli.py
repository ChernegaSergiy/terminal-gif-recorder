"""
Command-line interface backward-compatibility wrapper.
"""

from __future__ import annotations

from .scripts.record import create_parser, main

__all__ = [
    "create_parser",
    "main",
]

if __name__ == "__main__":
    main()
