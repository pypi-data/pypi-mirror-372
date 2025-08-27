# dtx_attacks/clients/openai_target.py
from __future__ import annotations

from typing import List, Optional
from .base import TargetClient, GenerationConfig
from dtx_attacks.models.openai_model import OpenAIModel


class OpenAITarget(TargetClient):
    """
    Simple TargetClient that sends each prompt as a user message to an OpenAIModel
    and returns the assistant's text. Optionally prepends a system prompt.
    """

    def __init__(self, model: OpenAIModel, system_prompt: Optional[str] = None) -> None:
        self._model = model
        self._system_prompt = system_prompt or "You are a helpful, safe assistant."

    @property
    def name(self) -> str:
        return getattr(self._model, "model_name", "openai/unknown")

    def reset(self) -> None:
        # Stateless adapter; nothing to reset
        pass

    def batch_query(self, prompts: List[str], config: Optional[GenerationConfig] = None) -> List[str]:
        cfg = (config or GenerationConfig()).openai_format()
        batched = [
            [
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": p},
            ]
            for p in prompts
        ]
        return self._model.batch_chat(batched, **cfg)

    def query(self, prompt: str, config: Optional[GenerationConfig] = None) -> str:
        cfg = (config or GenerationConfig()).openai_format()
        msgs = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": prompt},
        ]
        return self._model.chat(msgs, **cfg)
