from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ScriptResult:
    ok: bool
    stdout: str
    stderr: str
    returncode: int

    def json(self) -> Any:
        return json.loads(self.stdout)


def run_script(root: Path, script: str, *args: str, check: bool = False) -> ScriptResult:
    proc = subprocess.run(
        ["bash", str(root / "scripts" / script), *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"{script} failed: {proc.stderr or proc.stdout}")
    return ScriptResult(proc.returncode == 0, proc.stdout, proc.stderr, proc.returncode)
