#!/usr/bin/env python3
"""
Terminal GIF Recorder
Automated recording of terminal interactions into high-quality GIFs via asciinema and agg.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import pty
import random
import select
import shutil
import signal
import struct
import sys
import tempfile
import termios
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


# Special key combinations and ANSI sequences
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
    while disabling unwanted characters/artifacts (such as the '%' symbol at line beginnings).
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


class Action:
    """Represents a single action during terminal emulation."""

    def __init__(self, action_type: str, value: Any, delay: float = 0.0):
        self.type = action_type  # 'type', 'key', 'sleep'
        self.value = value
        self.delay = delay


class TerminalRecorder:
    """
    Wrapper for creating step-by-step terminal interaction scenarios
    and recording them to GIF.
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
    ):
        self.cols = cols
        self.rows = rows
        self.theme = theme
        self.cwd = Path(os.path.expanduser(str(cwd))) if cwd else Path.cwd()
        self.speed = speed
        self.initial_pause = initial_pause
        self.final_pause = final_pause
        self.actions: List[Action] = []

    def sleep(self, seconds: float) -> "TerminalRecorder":
        """Pause for a specified number of seconds."""
        self.actions.append(Action("sleep", seconds / self.speed))
        return self

    def type(
        self,
        text: str,
        char_delay_min: float = 0.045,
        char_delay_max: float = 0.085,
    ) -> "TerminalRecorder":
        """Type text with realistic human typing delays between characters."""
        self.actions.append(
            Action(
                "type",
                text,
                delay=(char_delay_min / self.speed, char_delay_max / self.speed),
            )
        )
        return self

    def key(self, key_name_or_bytes: Union[str, bytes]) -> "TerminalRecorder":
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

    def enter(self, pause_after: float = 0.4) -> "TerminalRecorder":
        """Press Enter with an optional pause afterwards."""
        self.key("enter")
        if pause_after > 0:
            self.sleep(pause_after)
        return self

    def space(self, pause_after: float = 0.2) -> "TerminalRecorder":
        """Press Space."""
        self.key("space")
        if pause_after > 0:
            self.sleep(pause_after)
        return self

    def up(self, pause_after: float = 0.2) -> "TerminalRecorder":
        """Press Up arrow key."""
        self.key("up")
        if pause_after > 0:
            self.sleep(pause_after)
        return self

    def down(self, pause_after: float = 0.2) -> "TerminalRecorder":
        """Press Down arrow key."""
        self.key("down")
        if pause_after > 0:
            self.sleep(pause_after)
        return self

    def left(self, pause_after: float = 0.2) -> "TerminalRecorder":
        """Press Left arrow key."""
        self.key("left")
        if pause_after > 0:
            self.sleep(pause_after)
        return self

    def right(self, pause_after: float = 0.2) -> "TerminalRecorder":
        """Press Right arrow key."""
        self.key("right")
        if pause_after > 0:
            self.sleep(pause_after)
        return self

    def run_pty_simulation(self) -> None:
        """
        Runs the internal PTY process, replays actions, and streams output to stdout.
        Used as the target command for asciinema.
        """
        env = os.environ.copy()
        env["TERM"] = "xterm-256color"
        env["LANG"] = "en_US.UTF-8"
        env["LC_ALL"] = "en_US.UTF-8"

        zdotdir = setup_clean_zdotdir()
        env["ZDOTDIR"] = str(zdotdir)
        env["PWD"] = str(self.cwd)

        pid, master_fd = pty.fork()
        if pid == 0:
            # Child process: set terminal window geometry
            winsize = struct.pack("HHHH", self.rows, self.cols, 0, 0)
            fcntl.ioctl(sys.stdin.fileno(), termios.TIOCSWINSZ, winsize)
            os.chdir(str(self.cwd))
            os.execvpe("zsh", ["zsh", "-i"], env)
            sys.exit(0)

        # Parent process: read terminal output and write to sys.stdout
        stop_event = threading.Event()

        def reader():
            while not stop_event.is_set():
                r, _, _ = select.select([master_fd], [], [], 0.05)
                if master_fd in r:
                    try:
                        data = os.read(master_fd, 4096)
                        if not data:
                            break
                        sys.stdout.buffer.write(data)
                        sys.stdout.buffer.flush()
                    except OSError:
                        break

        t = threading.Thread(target=reader, daemon=True)
        t.start()

        # Initial pause to allow prompt rendering
        time.sleep(self.initial_pause)

        # Replay actions
        for act in self.actions:
            if act.type == "type":
                min_d, max_d = act.delay
                for ch in act.value:
                    os.write(master_fd, ch.encode("utf-8"))
                    time.sleep(random.uniform(min_d, max_d))
            elif act.type == "key":
                os.write(master_fd, act.value)
            elif act.type == "sleep":
                time.sleep(act.value)

        # Final pause before termination
        time.sleep(self.final_pause)

        # Terminate shell cleanly via SIGHUP without typing exit
        try:
            os.kill(pid, signal.SIGHUP)
            os.waitpid(pid, 0)
        except (ProcessLookupError, ChildProcessError):
            pass
        try:
            os.close(master_fd)
        except OSError:
            pass

        stop_event.set()
        t.join(timeout=1.0)

    def save_gif(
        self,
        output_gif_path: Union[str, Path],
        temp_cast_path: Optional[Union[str, Path]] = None,
    ) -> Path:
        """
        Records the scenario using asciinema and renders it to GIF using agg.
        """
        output_gif = Path(output_gif_path).resolve()
        output_gif.parent.mkdir(parents=True, exist_ok=True)

        asciinema_bin = find_binary(
            "asciinema", ["~/.local/bin/asciinema", "/usr/bin/asciinema"]
        )
        agg_bin = find_binary("agg", ["~/.local/bin/agg", "/usr/local/bin/agg"])

        # Save temporary scenario configuration for asciinema runner
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f_scenario:
            scenario_path = f_scenario.name
            json.dump(self.to_dict(), f_scenario, ensure_ascii=False)

        cast_file = (
            Path(temp_cast_path)
            if temp_cast_path
            else Path(tempfile.gettempdir()) / f"rec_{os.getpid()}_{int(time.time())}.cast"
        )

        try:
            import shlex
            runner_cmd = f"{sys.executable} {shlex.quote(str(Path(__file__).resolve()))} --execute-json {shlex.quote(scenario_path)}"
            rec_cmd = (
                f"{shlex.quote(asciinema_bin)} rec {shlex.quote(str(cast_file))} -c {json.dumps(runner_cmd)} --overwrite"
            )

            ret = os.system(rec_cmd)
            if ret != 0:
                raise RuntimeError(f"asciinema exited with error (code {ret})")

            # Render GIF via agg
            render_cmd = (
                f"{shlex.quote(agg_bin)} {shlex.quote(str(cast_file))} {shlex.quote(str(output_gif))} "
                f"--cols {self.cols} --rows {self.rows} --theme {self.theme}"
            )
            ret = os.system(render_cmd)
            if ret != 0:
                raise RuntimeError(f"agg exited with error (code {ret})")

            return output_gif

        finally:
            if os.path.exists(scenario_path):
                os.remove(scenario_path)
            if cast_file.exists() and not temp_cast_path:
                os.remove(cast_file)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize scenario to dictionary."""
        serialized_actions = []
        for act in self.actions:
            if act.type == "key":
                serialized_actions.append(
                    {
                        "type": "key",
                        "value": act.value.decode("latin1"),
                    }
                )
            else:
                serialized_actions.append(
                    {
                        "type": act.type,
                        "value": act.value,
                        "delay": act.delay,
                    }
                )
        return {
            "cols": self.cols,
            "rows": self.rows,
            "theme": self.theme,
            "cwd": str(self.cwd),
            "speed": self.speed,
            "initial_pause": self.initial_pause,
            "final_pause": self.final_pause,
            "actions": serialized_actions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TerminalRecorder":
        """Deserialize scenario from dictionary."""
        rec = cls(
            cols=data.get("cols", 80),
            rows=data.get("rows", 20),
            theme=data.get("theme", "github-dark"),
            cwd=data.get("cwd"),
            speed=data.get("speed", 1.0),
            initial_pause=data.get("initial_pause", 1.2),
            final_pause=data.get("final_pause", 1.8),
        )
        for act in data.get("actions", []):
            atype = act["type"]
            val = act["value"]
            if atype == "key":
                raw_bytes = val.encode("latin1")
                rec.actions.append(Action("key", raw_bytes))
            elif atype == "type":
                delay = tuple(act.get("delay", [0.045, 0.085]))
                rec.actions.append(Action("type", val, delay=delay))
            elif atype == "sleep":
                rec.actions.append(Action("sleep", float(val)))
        return rec


def main():
    parser = argparse.ArgumentParser(
        description="Automated terminal GIF recording utility"
    )
    parser.add_argument("scenario", nargs="?", help="Path to scenario configuration file (.json)")
    parser.add_argument("-o", "--output", help="Path to output GIF file")
    parser.add_argument("--cols", type=int, default=80, help="Terminal width in columns (default: 80)")
    parser.add_argument("--rows", type=int, default=20, help="Terminal height in rows (default: 20)")
    parser.add_argument("--theme", default="github-dark", help="Color theme for agg (default: github-dark)")
    parser.add_argument("--cwd", help="Working directory for the session")
    parser.add_argument("--execute-json", help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.execute_json:
        # Internal mode: run PTY inside asciinema
        with open(args.execute_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        recorder = TerminalRecorder.from_dict(data)
        recorder.run_pty_simulation()
        return

    if not args.scenario or not args.output:
        parser.print_help()
        print("\nUsage example:")
        print("  python3 recorder.py scenario.json -o output.gif")
        return

    scenario_path = Path(args.scenario)
    if not scenario_path.exists():
        print(f"Error: file '{scenario_path}' not found.")
        sys.exit(1)

    with open(scenario_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.cols:
        data["cols"] = args.cols
    if args.rows:
        data["rows"] = args.rows
    if args.theme:
        data["theme"] = args.theme
    if args.cwd:
        data["cwd"] = args.cwd

    recorder = TerminalRecorder.from_dict(data)
    print(f"Recording scenario '{scenario_path}' into '{args.output}'...")
    gif_path = recorder.save_gif(args.output)
    print(f"GIF successfully created: {gif_path}")


if __name__ == "__main__":
    main()
