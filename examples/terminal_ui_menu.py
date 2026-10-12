#!/usr/bin/env python3
"""
Сценарій запису Interactive Menu для terminal-ui.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from recorder import TerminalRecorder


def main():
    workdir = Path.home() / "terminal-ui"
    output_gif = workdir / "docs/demo/menu.gif"

    recorder = TerminalRecorder(
        cols=80,
        rows=20,
        theme="github-dark",
        cwd=workdir,
        initial_pause=1.2,
        final_pause=1.8,
    )

    # Запуск інтерактивного меню
    recorder.type("php examples/interactive-menu.php").enter(pause_after=0.8)

    # Навігація вниз по пунктах меню
    recorder.down(pause_after=0.5)
    recorder.down(pause_after=0.5)
    recorder.down(pause_after=0.6)

    # Повернення вгору
    recorder.up(pause_after=0.7)

    # Вибір пункту (Check database connection)
    recorder.enter(pause_after=2.0)

    print("Запис menu.gif...")
    gif_file = recorder.save_gif(output_gif)
    print(f"Готово: {gif_file}")


if __name__ == "__main__":
    main()
