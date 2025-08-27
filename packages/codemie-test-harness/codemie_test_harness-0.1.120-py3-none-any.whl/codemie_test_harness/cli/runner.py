from __future__ import annotations
import subprocess
import sys
from typing import Iterable, List
from .constants import CONSOLE


def build_pytest_cmd(
    workers: int, marks: str, reruns: int, extra: Iterable[str] | None = None
) -> List[str]:
    cmd = [sys.executable, "-m", "pytest"]
    if workers:
        cmd += ["-n", str(workers)]
    if marks:
        cmd += ["-m", str(marks)]
    if reruns and int(reruns) > 0:
        cmd += ["--reruns", str(reruns)]
    if extra:
        cmd += list(extra)
    return cmd


def run_pytest(
    workers: int, marks: str, reruns: int, extra: Iterable[str] | None = None
) -> None:
    cmd = build_pytest_cmd(workers, marks, reruns, extra)
    CONSOLE.print("[cyan]Running:[/] " + " ".join(cmd))
    raise SystemExit(subprocess.call(cmd))
