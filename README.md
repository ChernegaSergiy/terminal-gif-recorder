# Terminal GIF Recorder

Інструментарій та обгортка на Python для автоматизованого створення якісних демонстраційних GIF-анімацій термінальних CLI-утиліт (для додавання в README.md, документацію або презентації).

---

## Проблематика запису термінальних сесій

При ручному або простому скриптовому записі через емулятор терміналу виникають типові артефакти:

1. **Зайва команда exit у фіналі**: щоб зупинити запис сесії asciinema, у термінал часто надсилається команда `exit`, яка друкується на екрані та потрапляє в останні кадри анімації.
2. **Службовий символ % у zsh**: якщо попередній вивід не закінчується символом нового рядка, zsh виводить інвертований або закреслений знак `%` на початку рядка перед промптом.
3. **Маркери Git у prompt (?1, !1)**: якщо записувати файл `.cast` безпосередньо у робочу директорію проєкту, zsh фіксує невідстежуваний файл під час виконання та відображає індикатор змін.
4. **Неузгоджені розміри терміналу**: без фіксації геометрії PTY та налаштувань рендерингу рядки можуть обрізатися або мати різний масштаб у різних демонстраціях.

---

## Принцип роботи та рішення

- **Завершення через SIGHUP**: сесія зупиняється надсиланням сигналу `SIGHUP` процесу оболонки після витримки паузи. Команда `exit` не набирається і не з'являється у записі.
- **Ізольована конфігурація ZDOTDIR**: скрипт створює тимчасовий `.zshrc`, який завантажує стандартний `~/.zshrc` користувача для збереження теми оформлення (наприклад, Powerlevel10k), але вимикає `PROMPT_EOL_MARK`, `PROMPT_SP`, `PROMPT_CR` та `POWERLEVEL9K_INSTANT_PROMPT`.
- **Запис у тимчасову директорію (/tmp)**: проміжний файл `.cast` записується поза репозиторієм, завдяки чому робоче дерево Git залишається чистим під час усієї сесії. Після рендерингу в GIF тимчасовий файл видаляється.
- **Фіксована геометрія (cols та rows)**: PTY емулятор задає точний розмір вікна через `termios.TIOCSWINSZ`, а `agg` компілює GIF із відповідними розмірами (за замовчуванням 80x20, тема `github-dark`).
- **Емуляція введення**: функція `type()` симулює набір тексту з випадковою затримкою між натисканнями клавіш.

---

## Системні вимоги

- **Python 3.8+**
- **asciinema** (запис термінальної сесії у формат asciicast):
  ```bash
  asciinema --version
  ```
- **agg** (компіляція asciicast у GIF):
  ```bash
  agg --version
  ```
  Утиліта автоматично перевіряє `PATH`, а також локальну директорію `~/.local/bin/agg`.

---

## Використання

### 1. Python API

Створення сценарію через ланцюжок викликів:

```python
from pathlib import Path
from recorder import TerminalRecorder

recorder = TerminalRecorder(
    cols=80,
    rows=20,
    theme="github-dark",
    cwd="/path/to/project",
    initial_pause=1.2,
    final_pause=1.8,
)

# Запуск команди
recorder.type("php examples/interactive-menu.php").enter(pause_after=0.8)

# Навігація
recorder.down(pause_after=0.3)
recorder.down(pause_after=0.3)
recorder.enter(pause_after=1.5)

# Збереження GIF
recorder.save_gif("docs/demo/menu.gif")
```

#### Методи TerminalRecorder:

- `type(text, char_delay_min=0.045, char_delay_max=0.085)` — набір тексту з інтервалами між символами.
- `enter(pause_after=0.4)` — натискання Enter (`\r`).
- `space(pause_after=0.2)` — натискання Space (` `).
- `up(pause_after=0.2)`, `down()`, `left()`, `right()` — клавіші навігації.
- `key(key_name_or_bytes)` — спеціальні клавіші (`ctrl+c`, `esc`, `tab`, `backspace` тощо).
- `sleep(seconds)` — витримка паузи.
- `save_gif(output_path)` — запуск запису та збереження результуючого GIF.

---

### 2. Запуск через CLI та JSON

Сценарій може бути збережений у форматі JSON:

`scenario.json`:
```json
{
  "cols": 80,
  "rows": 20,
  "theme": "github-dark",
  "initial_pause": 1.2,
  "final_pause": 1.8,
  "actions": [
    { "type": "type", "value": "php bin/table-magic interact data.csv" },
    { "type": "key", "value": "\r" },
    { "type": "sleep", "value": 1.0 },
    { "type": "type", "value": "n" },
    { "type": "key", "value": "\r" },
    { "type": "sleep", "value": 1.5 },
    { "type": "type", "value": "q" },
    { "type": "key", "value": "\r" }
  ]
}
```

Команда запуску:
```bash
./recorder.py scenario.json -o docs/demo/table_demo.gif
```

Опції CLI:
- `-o`, `--output` — шлях до вихідного GIF-файлу.
- `--cols` — кількість колонок терміналу (за замовчуванням: 80).
- `--rows` — кількість рядків терміналу (за замовчуванням: 20).
- `--theme` — тема оформления agg (за замовчуванням: github-dark).
- `--cwd` — робоча директорія сесії.

---

## Структура директорії

```text
terminal-gif-recorder/
├── README.md                          # Документація
├── recorder.py                        # Бібліотека та CLI утиліта
└── examples/
    ├── terminal_ui_wizard.py          # Сценарій wizard.gif для terminal-ui
    ├── terminal_ui_login.py           # Сценарій login.gif для terminal-ui
    ├── terminal_ui_menu.py            # Сценарій menu.gif для terminal-ui
    ├── table_magic_demo.py            # Сценарій інтерактивного режиму для table-magic
    └── scenario_sample.json           # Приклад JSON-конфігурації
```
