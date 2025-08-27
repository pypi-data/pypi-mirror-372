# assistant/main.py
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from .utils import read_yaml, detect_platform
from .nlu import LLMConfig, LocalLLM
from .command_gen import CommandGenerator
from .risk import assess
from .executor import run_shell
from .io_cli import CLI
from assistant.explain import explain_command
import subprocess

BASE = Path(__file__).resolve().parent.parent

@dataclass
class Cfg:
    platform: str
    llm: LLMConfig
    stt_enabled: bool
    stt_model_dir: str
    sample_rate: int
    require_confirmation: bool
    block_super: bool

def run_command(cmd):
    """Execute a shell command with optional redirection handling."""
    try:
        if ">" in cmd:  # Handle redirection
            parts = cmd.split(">")
            base_cmd = parts[0].strip()
            file_path = parts[-1].strip()

            # Run base command for display
            result = subprocess.run(base_cmd, shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                print("\nCommand Output:\n")
                print(result.stdout)

            # Execute original command to keep redirection
            subprocess.run(cmd, shell=True)

        else:  # Normal execution
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                print("\nCommand Output:\n")
                print(result.stdout)
            if result.stderr.strip():
                print("\nError:\n")
                print(result.stderr)

    except Exception as e:
        print(f"Execution failed: {e}")

def load_config() -> Cfg:
    cfg = read_yaml(BASE / 'config.yaml')
    plat = cfg.get('platform') or detect_platform()
    llm_cfg = LLMConfig(
        provider=(cfg.get('llm', {}) or {}).get('provider', 'gpt4all'),
        model_path=(cfg.get('llm', {}) or {}).get('model_path', ''),
        max_tokens=(cfg.get('llm', {}) or {}).get('max_tokens', 256),
        temperature=(cfg.get('llm', {}) or {}).get('temperature', 0.2),
    )
    stt = cfg.get('stt', {}) or {}
    safety = cfg.get('safety', {}) or {}
    return Cfg(
        platform=plat,
        llm=llm_cfg,
        stt_enabled=stt.get('enabled', False),
        stt_model_dir=stt.get('model_dir', ''),
        sample_rate=stt.get('sample_rate', 16000),
        require_confirmation=safety.get('require_confirmation', True),
        block_super=safety.get('block_super_dangerous', True),
    )

def main():
    cfg = load_config()
    cli = CLI()
    gen = CommandGenerator(cfg.llm, platform=cfg.platform)
    explainer_llm = LocalLLM(cfg.llm)   # reuse LLM for explanations

    cli.print(f"[bold green]AI Terminal Assistant[/] — OS: {cfg.platform}")
    cli.print("Type natural language. Use 'exit' or Ctrl+C to quit.")

    while True:
        try:
            text = cli.ask("You> ")
        except (EOFError, KeyboardInterrupt):
            cli.print("\nBye!")
            break
        if not text:
            continue
        if text.strip().lower() in {"exit", "quit"}:
            break

        # Step 1: Generate command
        result = gen.generate(text)
        command = result.command
        cli.print(f"\n[bold]Proposed command[/] ({result.source}): [cyan]{command}[/]")

        # Step 2: Risk assessment
        report = assess(command, cfg.block_super)
        if report.level == "block":
            cli.print(f"[red]Blocked[/]: {', '.join(report.reasons)}")
            continue
        elif report.level == "warn":
            cli.print(f"[yellow]Warning[/]: {', '.join(report.reasons)}")

        # Step 3: Confirmation
        if cfg.require_confirmation:
            if not cli.confirm("Run this command?"):
                cli.print("Skipped.")
                continue

        # Step 4: Execute
        exec_res = run_shell(command)
        if exec_res.stdout:
            cli.print("\n[bold]Output:[/]\n" + exec_res.stdout)
        if exec_res.stderr:
            cli.print("\n[bold red]Errors:[/]\n" + exec_res.stderr)
        cli.print(f"[dim]Exit code: {exec_res.code}[/]\n")

        # Step 5: Explanation
        try:
            explanation = explain_command(command, BASE / "data", llm=explainer_llm)
        except Exception as e:
            explanation = f"Error generating explanation: {e}"

        cli.print("[bold]Explanation:[/]\n" + (explanation or "No explanation generated.") + "\n")


if __name__ == "__main__":
    main()
