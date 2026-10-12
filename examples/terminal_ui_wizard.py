#!/usr/bin/env python3
"""
Приклад запису Setup Wizard для terminal-ui.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from recorder import TerminalRecorder


def main():
    workdir = Path.home() / "Development/General/Мої проєкти/terminal-ui"
    output_gif = workdir / "docs/demo/wizard.gif"

    recorder = TerminalRecorder(
        cols=80,
        rows=20,
        theme="github-dark",
        cwd=workdir,
        initial_pause=1.2,
        final_pause=1.8,
    )

    # Запуск майстра
    recorder.type("php examples/wizard.php").enter(pause_after=0.8)

    # 1. Project name: microservice-app
    recorder.type("microservice-app").enter(pause_after=0.6)

    # 2. Framework: Symfony
    recorder.type("sym").enter(pause_after=0.6)

    # 3. Features: Down, Space (Docker), Down, Down, Down, Space (PHPStan), Enter
    recorder.down(pause_after=0.3).space(pause_after=0.3)
    recorder.down(pause_after=0.2).down(pause_after=0.2).down(pause_after=0.3).space(pause_after=0.5)
    recorder.enter(pause_after=0.6)

    # 4. Workers: Right 4 times, Enter
    recorder.right(pause_after=0.2).right(pause_after=0.2).right(pause_after=0.2).right(pause_after=0.5)
    recorder.enter(pause_after=0.5)

    # 5. Підтвердження
    recorder.enter(pause_after=2.0)

    print("Запис wizard.gif...")
    gif_file = recorder.save_gif(output_gif)
    print(f"Готово: {gif_file}")


if __name__ == "__main__":
    main()
