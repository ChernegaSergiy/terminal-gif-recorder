"""
Pseudoterminal (PTY) runner and keystroke playback engine.
"""

from __future__ import annotations

import fcntl
import os
import pty
import random
import select
import signal
import struct
import sys
import termios
import threading
import time

from .env import setup_clean_zdotdir
from .scenario import Scenario


def play_scenario(scenario: Scenario) -> None:
    """
    Executes a terminal scenario inside a pseudo-terminal (PTY) fork,
    replaying typing and key presses, and streaming output to stdout.
    Terminates cleanly via SIGHUP without typing an 'exit' command.
    """
    env = os.environ.copy()
    env["TERM"] = "xterm-256color"
    env["LANG"] = "en_US.UTF-8"
    env["LC_ALL"] = "en_US.UTF-8"

    zdotdir = setup_clean_zdotdir()
    env["ZDOTDIR"] = str(zdotdir)
    env["PWD"] = str(scenario.cwd)

    pid, master_fd = pty.fork()
    if pid == 0:
        # Child process: configure window geometry and launch shell
        winsize = struct.pack("HHHH", scenario.rows, scenario.cols, 0, 0)
        fcntl.ioctl(sys.stdin.fileno(), termios.TIOCSWINSZ, winsize)
        os.chdir(str(scenario.cwd))
        os.execvpe("zsh", ["zsh", "-i"], env)
        sys.exit(0)

    # Parent process: stream terminal output to sys.stdout
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

    # Initial pause for prompt rendering
    time.sleep(scenario.initial_pause)

    # Replay scenario actions
    for act in scenario.actions:
        if act.type == "type":
            min_d, max_d = act.delay
            for ch in act.value:
                os.write(master_fd, ch.encode("utf-8"))
                time.sleep(random.uniform(min_d, max_d))
        elif act.type == "key":
            os.write(master_fd, act.value)
        elif act.type == "sleep":
            time.sleep(act.value)

    # Final pause before terminating
    time.sleep(scenario.final_pause)

    # Terminate shell cleanly via SIGHUP to avoid printing 'exit'
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
