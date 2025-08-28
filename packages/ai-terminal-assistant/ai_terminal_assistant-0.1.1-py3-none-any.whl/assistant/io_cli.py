from __future__ import annotations
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console

console = Console()

class CLI:
    def __init__(self, history_path: str = ".assistant_history"):
        self.session = PromptSession(history=FileHistory(history_path))

    def ask(self, prompt: str) -> str:
        return self.session.prompt(prompt)

    def confirm(self, msg: str) -> bool:
        ans = self.session.prompt(f"{msg} [y/N]: ").strip().lower()
        return ans in {"y", "yes"}

    def print(self, *args, **kwargs):
        console.print(*args, **kwargs)
