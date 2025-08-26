from __future__ import annotations

import os
import json
import argparse
from dataclasses import dataclass
from typing import Optional, Iterable

from tenacity import retry, wait_exponential_jitter, stop_after_attempt
from .safety import is_allowed
from .prompts import SYSTEM_TEACHER, STARTERS
from .errors import CLHKidAIError, CLHKidAISafetyError

# Lazily import OpenAI so mock mode doesn't require the package at runtime.
def _get_openai_client(api_key: Optional[str] = None):
    from openai import OpenAI
    return OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))


@dataclass
class CLHKidAIConfig:
    model: str = os.getenv("KIDAI_MODEL", "gpt-4o-mini")  # small & cheap
    temperature: float = float(os.getenv("KIDAI_TEMPERATURE", "0.2"))
    max_output_tokens: int = int(os.getenv("KIDAI_MAX_TOKENS", "300"))
    safe_mode: bool = os.getenv("KIDAI_SAFE_MODE", "1") not in {"0", "false", "False"}
    mock: bool = os.getenv("KIDAI_MOCK", "0") in {"1", "true", "True"}
    extra_blocklist: Iterable[str] | None = None


class CLHKidAI:
    """
    A kid-friendly one-line wrapper around OpenAI.

    Examples
    --------
    >>> ai = KidAI()  # reads OPENAI_API_KEY from env
    >>> ai.ask("Tell me a computer joke")
    'Why did the computer sneeze?...'
    """

    def __init__(self, api_key: Optional[str] = None, config: Optional[CLHKidAIConfig] = None, mock: Optional[bool] = None):
        self.config = config or CLHKidAIConfig()
        if mock is not None:
            self.config.mock = bool(mock)

        self._client = None if self.config.mock else _get_openai_client(api_key="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")

    # Simple retry on rate limits & transient failures
    @retry(wait=wait_exponential_jitter(initial=0.5, max=6), stop=stop_after_attempt(3))
    def _complete(self, system: str, user: str) -> str:
        if self.config.mock:
            # Classroom/offline predictable replies
            if "joke" in user.lower():
                return "Why was the computer cold? It left its Windows open! 😄"
            if "what is ai" in user.lower():
                return "AI is when computers learn patterns to help us, like recommending videos or spotting cats. 🤖"
            return "I’m in mock mode, but here’s a friendly answer: keep exploring and asking great questions! ✨"

        resp = self._client.chat.completions.create(  # modern OpenAI SDK
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_output_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
        )
        return (resp.choices[0].message.content or "").strip()

    def ask(self, prompt: str, *, system: Optional[str] = None) -> str:
        """Ask a simple question and get a kid-safe answer."""
        if self.config.safe_mode and not is_allowed(prompt, self.config.extra_blocklist):
            raise CLHKidAISafetyError("That topic isn’t allowed in kid-safe mode. Try another question 🙂")

        system_msg = system or SYSTEM_TEACHER
        return self._complete(system_msg, prompt)

    def starter(self, name: str) -> str:
        """Use a built-in classroom starter (e.g., 'joke', 'what_is_ai')."""
        key = name.strip().lower()
        if key not in STARTERS:
            raise CLHKidAIError(f"Unknown starter '{name}'. Try one of: {', '.join(STARTERS)}")
        return self.ask(STARTERS[key])

    def joke(self) -> str:
        """One-line: get a kid-safe computer joke."""
        return self.ask("Tell a computer-related joke for kids.")

    # Tiny CLI
    def run_cli(self, text: str) -> int:
        try:
            print(self.ask(text))
            return 0
        except CLHKidAIError as e:
            print(f"kidai error: {e}")
            return 1


def main():
    parser = argparse.ArgumentParser(description="Kid-friendly AI (kidai)")
    parser.add_argument("text", nargs="*", help="What you want to ask (e.g., 'tell me a joke')")
    parser.add_argument("--mock", action="store_true", help="Run in offline/mock mode")
    args = parser.parse_args()

    prompt = " ".join(args.text).strip() or "Tell a computer-related joke for kids."
    ai = CLHKidAI(mock=args.mock)
    raise SystemExit(ai.run_cli(prompt))
