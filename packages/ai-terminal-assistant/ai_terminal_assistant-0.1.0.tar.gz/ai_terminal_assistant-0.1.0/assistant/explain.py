import re
from pathlib import Path
from typing import Optional
from assistant.utils import load_flag_explanations, split_cmd, detect_platform


def explain_command(command: str, data_dir: Path, llm=None) -> Optional[str]:
    """
    Explain the given command in simple, beginner-friendly terms.
    Only describe the flags that are actually used in the command.
    """

    # Detect OS
    current_os = detect_platform()
    flags_file = data_dir / ("flags_windows.yaml" if current_os == "windows" else "flags_linux.yaml")

    # Load flag explanations (dict)
    flag_explanations = load_flag_explanations(flags_file)

    # Split command into parts
    parts = split_cmd(command)
    if not parts:
        return None

    base_cmd = parts[0]
    explanations = []

    # Base command explanation
    if base_cmd in flag_explanations and "_desc" in flag_explanations[base_cmd]:
        explanations.append(f"**{base_cmd}**: {flag_explanations[base_cmd]['_desc']}")

    # Explain only the flags actually present in the command
    for part in parts[1:]:
        if part in flag_explanations.get(base_cmd, {}):
            explanations.append(f"Flag `{part}` → {flag_explanations[base_cmd][part]}")

    # Handle common patterns dynamically (not just flags)
    if "*.py" in command:
        explanations.append("This command filters and shows only Python files (`*.py`).")
    if "*.txt" in command:
        explanations.append("This command filters and shows only text files (`*.txt`).")

    # If explanations found, return nicely formatted
    if explanations:
        return "\n".join(explanations)

    # Fallback: ask LLM if available
    if llm:
        return llm.generate(f"Explain this command in simple terms: {command}")

    return None
