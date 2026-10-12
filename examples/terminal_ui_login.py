#!/usr/bin/env python3
"""
Сценарій запису Login Form для terminal-ui.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from recorder import TerminalRecorder


def main():
    workdir = Path.home() / "Development/General/Мої проєкти/terminal-ui"
    output_gif = workdir / "docs/demo/login.gif"

    recorder = TerminalRecorder(
        cols=80,
        rows=20,
        theme="github-dark",
        cwd=workdir,
        initial_pause=1.2,
        final_pause=1.8,
    )

    # Запуск форми логіну
    recorder.type("php examples/login-form.php").enter(pause_after=0.8)

    # 1. Email
    recorder.type("admin@example.com").enter(pause_after=0.5)

    # 2. Password
    recorder.type("s3cur3-p@ss!").enter(pause_after=0.5)

    # 3. Checkbox (Remember me): подвійне перемикання Space
    recorder.space(pause_after=0.3)
    recorder.space(pause_after=0.5)

    # 4. Підтвердження форми
    recorder.enter(pause_after=2.0)

    print("Запис login.gif...")
    gif_file = recorder.save_gif(output_gif)
    print(f"Готово: {gif_file}")


if __name__ == "__main__":
    main()
