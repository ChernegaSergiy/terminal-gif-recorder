#!/usr/bin/env python3
"""
Приклад запису інтерактивного режиму для table-magic.
"""

from pathlib import Path
import sys

# Додаємо кореневу директорію recorder до sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from recorder import TerminalRecorder


def main():
    workdir = Path.home() / "table-magic"
    output_gif = workdir / "docs/demo/interactive.gif"

    recorder = TerminalRecorder(
        cols=80,
        rows=22,
        theme="github-dark",
        cwd=workdir,
        initial_pause=1.2,
        final_pause=1.8,
    )

    # 1. Запуск демо
    recorder.type("php examples/interactive_terminal_demo.php", char_delay_min=0.055, char_delay_max=0.085)
    recorder.sleep(0.4)
    recorder.enter(pause_after=1.5)

    # 2. Перехід на наступну сторінку (n)
    recorder.sleep(0.6)
    recorder.type("n", char_delay_min=0.06, char_delay_max=0.08)
    recorder.sleep(0.35)
    recorder.enter(pause_after=1.5)

    # 3. Повернення назад (p)
    recorder.sleep(0.6)
    recorder.type("p", char_delay_min=0.06, char_delay_max=0.08)
    recorder.sleep(0.35)
    recorder.enter(pause_after=1.3)

    # 4. Сортування (s -> Age -> desc)
    recorder.sleep(0.5)
    recorder.type("s", char_delay_min=0.06, char_delay_max=0.08)
    recorder.sleep(0.35)
    recorder.enter(pause_after=0.6)

    recorder.type("Age", char_delay_min=0.065, char_delay_max=0.09)
    recorder.sleep(0.35)
    recorder.enter(pause_after=0.6)

    recorder.type("desc", char_delay_min=0.065, char_delay_max=0.09)
    recorder.sleep(0.35)
    recorder.enter(pause_after=1.8)

    # 5. Додавання рядка (a -> Frank -> 28 -> Kyiv)
    recorder.sleep(0.5)
    recorder.type("a", char_delay_min=0.06, char_delay_max=0.08)
    recorder.sleep(0.35)
    recorder.enter(pause_after=0.6)

    recorder.type("Frank", char_delay_min=0.065, char_delay_max=0.09)
    recorder.sleep(0.35)
    recorder.enter(pause_after=0.5)

    recorder.type("28", char_delay_min=0.065, char_delay_max=0.09)
    recorder.sleep(0.35)
    recorder.enter(pause_after=0.5)

    recorder.type("Kyiv", char_delay_min=0.065, char_delay_max=0.09)
    recorder.sleep(0.35)
    recorder.enter(pause_after=1.2)

    # 6. Перехід на другу сторінку, щоб показати доданого Франка (n)
    recorder.sleep(0.5)
    recorder.type("n", char_delay_min=0.06, char_delay_max=0.08)
    recorder.sleep(0.35)
    recorder.enter(pause_after=1.8)

    # 7. Вихід (q)
    recorder.sleep(0.6)
    recorder.type("q", char_delay_min=0.06, char_delay_max=0.08)
    recorder.sleep(0.35)
    recorder.enter(pause_after=1.5)

    print(f"Запис table-magic демо у '{output_gif}'...")
    gif_file = recorder.save_gif(output_gif)
    print(f"GIF успішно збережено: {gif_file}")


if __name__ == "__main__":
    main()
