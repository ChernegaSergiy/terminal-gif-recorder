"""
Recording orchestration and GIF compilation via asciinema and agg.
"""

from __future__ import annotations

import json
import os
import shlex
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional, Union

from .env import find_binary
from .scenario import Scenario


def compile_gif(
    scenario: Scenario,
    output_gif_path: Union[str, Path],
    temp_cast_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Records the scenario using asciinema and compiles it into a GIF via agg.
    Returns the absolute path to the generated GIF file.
    """
    output_gif = Path(output_gif_path).resolve()
    output_gif.parent.mkdir(parents=True, exist_ok=True)

    asciinema_bin = find_binary(
        "asciinema", ["~/.local/bin/asciinema", "/usr/bin/asciinema"]
    )
    agg_bin = find_binary("agg", ["~/.local/bin/agg", "/usr/local/bin/agg"])

    # Write temporary scenario file to pass into internal runner
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f_tmp:
        scenario_file = f_tmp.name
        json.dump(scenario.to_dict(), f_tmp, ensure_ascii=False)

    cast_file = (
        Path(temp_cast_path)
        if temp_cast_path
        else Path(tempfile.gettempdir()) / f"rec_{os.getpid()}_{int(time.time())}.cast"
    )

    try:
        # Internal runner command executed within asciinema pseudo-terminal
        runner_cmd = (
            f"{shlex.quote(sys.executable)} -m src.scripts.record --play-scenario {shlex.quote(scenario_file)}"
        )
        rec_cmd = (
            f"{shlex.quote(asciinema_bin)} rec {shlex.quote(str(cast_file))} "
            f"-c {json.dumps(runner_cmd)} --overwrite"
        )

        ret = os.system(rec_cmd)
        if ret != 0:
            raise RuntimeError(f"asciinema exited with error (code {ret})")

        # Compile recorded asciicast to GIF using agg
        render_cmd = (
            f"{shlex.quote(agg_bin)} {shlex.quote(str(cast_file))} {shlex.quote(str(output_gif))} "
            f"--cols {scenario.cols} --rows {scenario.rows} --theme {scenario.theme}"
        )
        ret = os.system(render_cmd)
        if ret != 0:
            raise RuntimeError(f"agg exited with error (code {ret})")

        return output_gif

    finally:
        if os.path.exists(scenario_file):
            os.remove(scenario_file)
        if cast_file.exists() and not temp_cast_path:
            os.remove(cast_file)
