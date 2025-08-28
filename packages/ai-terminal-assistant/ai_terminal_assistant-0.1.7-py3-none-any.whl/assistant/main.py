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
import yaml
import importlib.resources


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
    """Load config.yaml from inside the assistant package, with defaults as fallback."""
    try:
        config_path = importlib.resources.files("assistant").joinpath("config.yaml")
        with config_path.open("r", encoding="utf-8") as f:
            raw_cfg = yaml.safe_load(f) or {}
    except FileNotFoundError:
        print("⚠️ config.yaml not found, using defaults")
        raw_cfg = {}

    # Fallback defaults
    llm_cfg = raw_cfg.get("llm", {
        "provider": "gpt4all",
        "model_path": "assistant\\model\\mistral-7b-instruct.Q4_K_M.gguf",
        "temperature": 0.7,
        "max_tokens": 512,
    })

    # ✅ Ensure model_path is always resolved relative to BASE
    model_path = Path(llm_cfg["model_path"])
    if not model_path.is_absolute():
        model_path = BASE / model_path
    llm_cfg["model_path"] = str(model_path)

    print(f"📂 Using model: {llm_cfg['model_path']}")  # ✅ Debug print

    stt_cfg = raw_cfg.get("stt", {"enabled": False, "model_dir": "", "sample_rate": 16000})
    safety_cfg = raw_cfg.get("safety", {"require_confirmation": True, "block_super_dangerous": True})

    return Cfg(
        platform=detect_platform(),
        llm=LLMConfig(**llm_cfg),   # ✅ Convert dict → LLMConfig
        stt_enabled=stt_cfg.get("enabled", False),
        stt_model_dir=stt_cfg.get("model_dir", ""),
        sample_rate=stt_cfg.get("sample_rate", 16000),
        require_confirmation=safety_cfg.get("require_confirmation", True),
        block_super=safety_cfg.get("block_super_dangerous", True),
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
