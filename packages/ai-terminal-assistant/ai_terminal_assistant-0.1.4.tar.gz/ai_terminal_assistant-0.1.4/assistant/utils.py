import os, sys, platform, shutil, re
from pathlib import Path
from typing import Tuple


def detect_platform() -> str:
    p = sys.platform
    if p.startswith("linux"): return "linux"
    if p == "darwin": return "darwin"
    if p in ("win32", "cygwin"): return "windows"
    return "linux"


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def split_cmd(cmd: str) -> list[str]:
    # naive splitter that respects quoted substrings
    return re.findall(r'\"[^\"]*\"|\'[^\']*\'|\S+', cmd)


def read_yaml(path: Path) -> dict:
    import yaml
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def load_flag_explanations(path: Path) -> dict:
    """Load YAML file containing command explanations."""
    from collections import defaultdict
    data = read_yaml(path)
    out = defaultdict(dict)
    for k, v in (data or {}).items():
        out[k] = v
    return out


def explain_command(cmd: str, data_dir: Path, llm=None) -> str:
    """
    Explain a command using YAML lookup first, then fallback to LLM if available.
    """
    parts = split_cmd(cmd)
    if not parts:
        return "Could not parse command."

    main = parts[0]
    flags = [p for p in parts[1:] if p.startswith("-")]

    # Load explanations from YAML (commands.yaml in data/)
    yaml_file = data_dir / "commands.yaml"
    flag_data = load_flag_explanations(yaml_file)

    explanation = []

    # Lookup main command
    if main in flag_data:
        cmd_info = flag_data[main]
        desc = cmd_info.get("description")
        if desc:
            explanation.append(f"**{main}** → {desc}")

        # Lookup flags
        if flags:
            for f in flags:
                f_info = cmd_info.get("flags", {}).get(f)
                if f_info:
                    explanation.append(f"Flag {f}: {f_info}")

    # If nothing found in YAML and LLM available, ask it
    if not explanation and llm:
        prompt = f"Explain what this command does in simple terms:\n\n{cmd}"
        try:
            resp = llm.generate(prompt).strip()
            if resp:
                return resp
        except Exception:
            pass

    if not explanation:
        return "No explanation found."

    return "\n".join(explanation)
