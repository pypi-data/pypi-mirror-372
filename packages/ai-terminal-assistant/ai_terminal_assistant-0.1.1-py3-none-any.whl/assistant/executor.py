from __future__ import annotations
import subprocess, shlex, sys
from dataclasses import dataclass
from .utils import detect_platform

@dataclass
class ExecResult:
    code: int
    stdout: str
    stderr: str


def run_shell(command: str) -> ExecResult:
    plat = detect_platform()
    if plat == "windows":
        proc = subprocess.run(command, shell=True, capture_output=True, text=True)
    else:
        proc = subprocess.run(command, shell=True, executable="/bin/bash", capture_output=True, text=True)
    return ExecResult(proc.returncode, proc.stdout, proc.stderr)