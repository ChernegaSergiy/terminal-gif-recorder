[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# Terminal GIF Recorder

[![License: CSSM Unlimited License v2.0](https://img.shields.io/pypi/l/terminal-gif-recorder)](LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/terminal-gif-recorder)](https://pypi.org/project/terminal-gif-recorder/)
[![PyPI Version](https://img.shields.io/pypi/v/terminal-gif-recorder)](https://pypi.org/project/terminal-gif-recorder/)

Python toolkit and wrapper for automated creation of high-quality demonstration GIF animations of terminal CLI utilities (for README.md, documentation, or presentations).

![Terminal GIF Recorder Demo](docs/demo/recorder.gif)

## Terminal Session Recording Challenges

Typical artifacts occur when recording manually or with simple scripts using a terminal emulator:

1. **Unwanted `exit` command at the end**: To stop an asciinema session, an `exit` command is often sent to the terminal, which is printed on the screen and captured in the final frames of the animation.
2. **Special `%` symbol in zsh**: If the previous output does not end with a newline character, zsh prints an inverted or crossed-out `%` symbol at the beginning of the line before the prompt.
3. **Git markers in prompt (`?1`, `!1`)**: If the `.cast` file is recorded directly into the project's working directory, zsh detects an untracked file during execution and displays git status markers.
4. **Inconsistent terminal dimensions**: Without fixed PTY geometry and rendering settings, lines may wrap or have inconsistent scaling across different demos.

## How It Works and Solutions

- **Clean termination via SIGHUP**: The session is stopped by sending a `SIGHUP` signal to the shell process after waiting for a configured pause. The `exit` command is never typed and never appears in the recording.
- **Isolated ZDOTDIR configuration**: The script generates a temporary `.zshrc` that sources the user's standard `~/.zshrc` to preserve styling and themes (e.g., Powerlevel10k), while disabling `PROMPT_EOL_MARK`, `PROMPT_SP`, `PROMPT_CR`, and `POWERLEVEL9K_INSTANT_PROMPT`.
- **Recording to a temporary directory (`/tmp`)**: The intermediate `.cast` file is written outside the repository, keeping the Git working tree clean throughout the entire session. The temporary file is cleaned up after GIF rendering.
- **Fixed geometry (`cols` and `rows`)**: The PTY emulator sets the exact window size using `termios.TIOCSWINSZ`, and `agg` compiles the GIF with corresponding dimensions (default: 80x20, theme: `github-dark`).
- **Typing emulation**: The `type()` method simulates human keystrokes with randomized delays between characters.

## Requirements

- **Python 3.8+**
- **asciinema** (records terminal session into asciicast format):
  ```bash
  asciinema --version
  ```
- **agg** (compiles asciicast to GIF):
  ```bash
  agg --version
  ```
  The utility automatically checks `PATH` as well as `~/.local/bin/agg`.

## Usage

### 1. Python API

Define a scenario via method chaining:

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

# Run command
recorder.type("php examples/interactive-menu.php").enter(pause_after=0.8)

# Navigation
recorder.down(pause_after=0.3)
recorder.down(pause_after=0.3)
recorder.enter(pause_after=1.5)

# Save GIF
recorder.save_gif("docs/demo/menu.gif")
```

#### TerminalRecorder Methods:

- `type(text, char_delay_min=0.045, char_delay_max=0.085)` — type text with realistic inter-keystroke intervals.
- `enter(pause_after=0.4)` — press Enter (`\r`).
- `space(pause_after=0.2)` — press Space (` `).
- `up(pause_after=0.2)`, `down()`, `left()`, `right()` — navigation arrow keys.
- `key(key_name_or_bytes)` — special keys (`ctrl+c`, `esc`, `tab`, `backspace`, etc.).
- `sleep(seconds)` — wait for a specified duration.
- `save_gif(output_path)` — run the recording session and save the resulting GIF.

### 2. Running via CLI and JSON

A scenario can be defined in JSON format:

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

CLI execution:
```bash
./recorder.py scenario.json -o docs/demo/table_demo.gif
```

CLI options:
- `-o`, `--output` — output GIF file path.
- `--cols` — terminal column width (default: 80).
- `--rows` — terminal row height (default: 20).
- `--theme` — agg color theme (default: github-dark).
- `--cwd` — working directory for the session.

## Directory Structure

```
terminal-gif-recorder/
+-- src/
|   \-- terminal_gif_recorder/  # Core package
|       +-- __init__.py         # Public package exports
|       +-- actions.py          # Action definitions and key mappings
|       +-- cli.py              # CLI backward compatibility wrapper
|       +-- compiler.py         # asciinema and agg GIF compilation
|       +-- env.py              # Binary discovery and zsh isolation
|       +-- scenario.py         # Scenario data model and builder
|       +-- terminal.py         # Pseudoterminal (PTY) runner
|       \-- scripts/            # Executable CLI scripts
|           +-- __init__.py
|           \-- record.py       # Main CLI entry point
+-- examples/
|   +-- scenario_sample.json    # Sample JSON configuration
|   +-- table_magic_demo.py     # Interactive mode scenario for table-magic
|   +-- terminal_ui_login.py    # Login form scenario for terminal-ui
|   +-- terminal_ui_menu.py     # Interactive menu scenario for terminal-ui
|   \-- terminal_ui_wizard.py   # Wizard scenario for terminal-ui
+-- .gitignore                  # Git ignore rules
+-- LICENSE                     # Project license
+-- pyproject.toml              # Package configuration
+-- README.md                   # Documentation
\-- recorder.py                 # Standalone CLI entry point shim
```

## Contributing

Contributions are welcome and appreciated! Here's how you can contribute:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please make sure to update tests as appropriate and adhere to the existing coding style.

## License

This project is licensed under the CSSM Unlimited License v2.0 (CSSM-ULv2). See the [LICENSE](LICENSE) file for details.
