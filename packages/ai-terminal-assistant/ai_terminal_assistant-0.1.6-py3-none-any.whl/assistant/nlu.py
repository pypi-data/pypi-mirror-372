from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from .utils import detect_platform
from gpt4all import GPT4All
import re

@dataclass
class LLMConfig:
    provider: str = "llama.cpp"  # Use llama.cpp for .gguf models
    model_path: str = r"C:\Users\Nidhi\Desktop\FInal year project implementation\models\mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    max_tokens: int = 256
    temperature: float = 0.2


class LocalLLM:
    """
    Wrapper for local LLMs (llama.cpp or GPT4All)
    """

    def __init__(self, cfg: LLMConfig):
        self.cfg = cfg
        self.impl = None

        if cfg.provider == "llama.cpp" and cfg.model_path and Path(cfg.model_path).exists():
            try:
                from llama_cpp import Llama
                self.impl = Llama(
                    model_path=cfg.model_path,
                    n_ctx=cfg.max_tokens
                )
            except Exception as e:
                print(f"[ERROR] Failed to load llama.cpp model: {e}")
                self.impl = None

        elif cfg.provider == "gpt4all" and cfg.model_path and Path(cfg.model_path).exists():
            try:
                from gpt4all import GPT4All
                self.impl = GPT4All(model=cfg.model_path)
            except Exception as e:
                print(f"[ERROR] Failed to load GPT4All model: {e}")
                self.impl = None

    def generate(self, prompt: str) -> str:
        if self.impl is None:
            return ""
        try:
            if self.cfg.provider == "llama.cpp":
                result = self.impl(
                    prompt,
                    max_tokens=self.cfg.max_tokens,
                    temperature=self.cfg.temperature
                )
                # extract text from first choice
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0].get("text", "").strip()
                return ""
            else:
                # GPT4All
                return self.impl.generate(prompt, max_tokens=self.cfg.max_tokens, temp=self.cfg.temperature).strip()
        except Exception as e:
            print(f"[ERROR] Generation failed: {e}")
            return ""



# Minimal, transparent rule-based fallback
class RuleBasedNLU:
    def __init__(self, platform: Optional[str] = None):
        self.platform = platform or detect_platform()

    def convert(self, text: str) -> str:
        t = text.lower().strip()
        if "list" in t and "wifi" in t:
            if self.platform == "windows":
                return "netsh wlan show networks"
            elif self.platform == "darwin":
                return "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s"
            else:
                return "nmcli dev wifi list"
        if ("kill" in t or "stop" in t) and "port" in t:
            if self.platform == "windows":
                return "for /f \"tokens=5\" %a in ('netstat -ano ^| findstr :8080') do taskkill /PID %a /F"
            else:
                return "lsof -ti:8080 | xargs -r kill"
        if "venv" in t and ("create" in t or "make" in t):
            if self.platform == "windows":
                return "python -m venv .venv && .venv\\Scripts\\activate"
            else:
                return "python -m venv .venv && source .venv/bin/activate"
        if ("find" in t or "search" in t) and ("large" in t or ">" in t) and ("log" in t):
            if self.platform == "windows":
                return "forfiles /S /M *.log /C \"cmd /c if @fsize GEQ 104857600 echo @path\""
            else:
                return "find . -type f -name '*.log' -size +100M -print"
        return "echo 'I did not understand; please rephrase.'"
