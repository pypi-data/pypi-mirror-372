from __future__ import annotations
from dataclasses import dataclass
from .nlu import LocalLLM, RuleBasedNLU, LLMConfig
from .utils import detect_platform

SYS_PROMPT = (
    "You convert natural language into ONE terminal command for the user's OS. "
    "Return your answer in this format:\n"
    "Command: <the command>\n"
    "Explanation: Explain the following command in simple terms so that even a beginner can understand. Also describe what each flag does in one sentence if present.Command: {command}"
    "Be safe; prefer read-only or dry-run flags when uncertain."
    "You convert natural language into ONE terminal command for the user's OS. "
    "Return ONLY the command, nothing else. "
    "The command should print the output directly in the terminal; do NOT redirect to a file. "
)

@dataclass
class GenResult:
    command: str
    explanation: str
    source: str  # gpt4all|rules|fallback

class CommandGenerator:
    def __init__(self, llm_cfg: LLMConfig, platform: str | None = None):
        self.platform = platform or detect_platform()
        self.llm = LocalLLM(llm_cfg)
        self.rules = RuleBasedNLU(self.platform)

    def generate(self, user_text: str) -> GenResult:
        if self.llm.impl is not None:
            prompt = f"{SYS_PROMPT}\nOS: {self.platform}\nUser: {user_text}\n"
            response = self.llm.generate(prompt).strip()

            command, explanation = "", ""
            for line in response.splitlines():
                if line.lower().startswith("command:"):
                    command = line.split(":", 1)[1].strip("` \n")
                elif line.lower().startswith("explanation:"):
                    explanation = line.split(":", 1)[1].strip()

            if command:
                return GenResult(command, explanation, "gpt4all")

        # fallback to rules (just return explanation = "Rule-based conversion")
        cmd = self.rules.convert(user_text)
        return GenResult(cmd, "Rule-based conversion", "rules")
