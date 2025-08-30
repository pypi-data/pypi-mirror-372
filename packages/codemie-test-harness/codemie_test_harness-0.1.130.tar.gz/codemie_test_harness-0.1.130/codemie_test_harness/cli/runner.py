from __future__ import annotations
import subprocess
import sys
from typing import Iterable, List
from pathlib import Path

try:
    from importlib.resources import files as pkg_files
except Exception:
    pkg_files = None

from .constants import CONSOLE


def _resolve_tests_path() -> str:
    """Resolve absolute path to the installed tests package.

    Priority:
    1) importlib.resources.files("tests") if the package is installed
    2) Fallback to repo layout: <repo_root>/tests relative to this file
    """
    # 1) Use importlib.resources to locate installed package "tests"
    if pkg_files is not None:
        try:
            tests_dir = pkg_files("tests")
            # Convert to a concrete filesystem path string
            return str(Path(tests_dir.joinpath("")))
        except Exception:
            pass

    # 2) Fallback to repo layout when running from source
    # runner.py -> cli -> codemie_test_harness -> <repo_root>
    repo_root = Path(__file__).resolve().parents[2]
    return str(repo_root / "tests")


def build_pytest_cmd(
    workers: int, marks: str, reruns: int, extra: Iterable[str] | None = None
) -> List[str]:
    tests_path = _resolve_tests_path()
    cmd = [sys.executable, "-m", "pytest", tests_path]
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
