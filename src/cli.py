"""
Command-line interface for Terminal GIF Recorder.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .compiler import compile_gif
from .scenario import Scenario
from .terminal import play_scenario


def create_parser() -> argparse.ArgumentParser:
    """Creates the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="terminal-gif-recorder",
        description="Automated terminal GIF recording utility",
    )
    parser.add_argument("scenario", nargs="?", help="Path to scenario configuration file (.json)")
    parser.add_argument("-o", "--output", help="Path to output GIF file")
    parser.add_argument("--cols", type=int, default=80, help="Terminal width in columns (default: 80)")
    parser.add_argument("--rows", type=int, default=20, help="Terminal height in rows (default: 20)")
    parser.add_argument("--theme", default="github-dark", help="Color theme for agg (default: github-dark)")
    parser.add_argument("--cwd", help="Working directory for the session")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier (default: 1.0)")
    parser.add_argument("--play-scenario", help=argparse.SUPPRESS)
    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Internal worker mode triggered by asciinema to run PTY simulation
    if args.play_scenario:
        scenario = Scenario.from_file(args.play_scenario)
        play_scenario(scenario)
        return

    if not args.scenario or not args.output:
        parser.print_help()
        print("\nUsage example:")
        print("  terminal-gif-recorder scenario.json -o output.gif")
        return

    scenario_path = Path(args.scenario)
    if not scenario_path.exists():
        print(f"Error: file '{scenario_path}' not found.", file=sys.stderr)
        sys.exit(1)

    scenario = Scenario.from_file(scenario_path)

    if args.cols:
        scenario.cols = args.cols
    if args.rows:
        scenario.rows = args.rows
    if args.theme:
        scenario.theme = args.theme
    if args.cwd:
        scenario.cwd = Path(args.cwd)
    if args.speed:
        scenario.speed = args.speed

    print(f"Recording scenario '{scenario_path}' into '{args.output}'...")
    gif_path = compile_gif(scenario, args.output)
    print(f"GIF successfully created: {gif_path}")


if __name__ == "__main__":
    main()
