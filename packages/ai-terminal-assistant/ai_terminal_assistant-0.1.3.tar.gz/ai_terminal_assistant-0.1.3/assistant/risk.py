from __future__ import annotations
import re
from dataclasses import dataclass

# 🚨 Absolutely destructive (blocked always)
SUPER_DANGEROUS = {
    r"\brm\s+-rf\s+/(\s|$)": "Attempt to wipe root directory",
    r":\(\)\s*\{\s*:\|:\s*&\s*;\s*\}\s*;\s*:": "Fork bomb (infinite process spawn)",
    r"\bdd\s+if=/dev/zero\s+of=/dev/[a-z]+": "Disk overwrite (wipe)",
    r"\bmkfs(\.\w+)?\s+/dev/[a-z]+": "Reformatting a disk",
    r"\bformat\s+[A-Z]:": "Formatting Windows drive",
    r"\breg\s+delete\b.*\s/\w*?f\b": "Windows Registry delete /f",
}

# ⚠️ Dangerous, may harm system but not always fatal
DANGEROUS = {
    r"\brm\s+-rf\b": "Recursive forced delete",
    r"\bchmod\s+-R\s+777\b": "Dangerous permission change",
    r"\bchown\s+-R\b": "Recursive ownership change",
    r"\bdel(ete)?\b\s+.*\s/\w*?q\b": "Silent delete in Windows",
}

# 🚫 Always block these common shutdown commands
HARDBLOCK = {
    r"\bshutdown\b": "Shutdown command",
    r"\breboot\b": "Reboot command",
    r"\bpowercfg\b": "Windows power configuration",
}

@dataclass
class RiskReport:
    level: str  # none | warn | block
    reasons: list[str]


def assess(command: str, block_super: bool = True) -> RiskReport:
    """Assess risk level of a command."""
    reasons = []

    # 🔒 Check super-dangerous
    for pat, desc in SUPER_DANGEROUS.items():
        if re.search(pat, command, re.IGNORECASE):
            return RiskReport("block" if block_super else "warn",
                              [f"❌ {desc} (pattern: {pat})"])

    # 🚫 Check always-hardblocked commands
    for pat, desc in HARDBLOCK.items():
        if re.search(pat, command, re.IGNORECASE):
            return RiskReport("block", [f"❌ {desc} detected, execution blocked."])

    # ⚠️ Check dangerous but not auto-blocked
    for pat, desc in DANGEROUS.items():
        if re.search(pat, command, re.IGNORECASE):
            reasons.append(f"⚠️ {desc}")

    # ✅ No risks
    if not reasons:
        return RiskReport("none", [])

    return RiskReport("warn", reasons)
