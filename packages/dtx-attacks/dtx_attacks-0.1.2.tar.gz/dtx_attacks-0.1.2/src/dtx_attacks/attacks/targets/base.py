from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Mapping, Optional, Protocol, runtime_checkable
from typing import Dict, Any

@dataclass(frozen=True)
class GenerationConfig:
    """
    Generic generation knobs for the *target* model.
    Adapt these to your provider (OpenAI, HF, vLLM, etc.).
    """
    max_new_tokens: int = 256
    temperature: float = 1.0
    top_p: float = 1.0
    stop: Optional[List[str]] = None
    extra: Mapping[str, object] = field(default_factory=dict)

    def openai_format(
        self,
        *,
        include_none: bool = False,
        **overrides: Any,
    ) -> Dict[str, Any]:
        """
        Convert to OpenAI-style kwargs:
          - max_new_tokens -> max_tokens
          - temperature, top_p, stop
        Merge order (last wins): base -> extra -> overrides

        Args:
            include_none: if True, include keys whose values are None (e.g., stop=None).
            overrides: per-call kwargs that should take final precedence.

        Returns:
            dict suitable for OpenAI/LiteLLM chat.completions
        """
        base = {
            "max_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stop": self.stop,
        }

        if not include_none:
            base = {k: v for k, v in base.items() if v is not None}

        # Merge extra provider-specific kwargs, then explicit overrides
        merged = {**base, **dict(self.extra or {}), **overrides}
        return merged



@runtime_checkable
class TargetClient(Protocol):
    """
    Black-box access to the target model under attack.
    Provide adapters for OpenAI/HF/vLLM/etc. in real use.
    """
    @property
    def name(self) -> str: ...
    def reset(self) -> None: ...
    def query(self, prompt: str, config: Optional[GenerationConfig] = None) -> str: ...
    def batch_query(self, prompts: List[str], config: Optional[GenerationConfig] = None) -> List[str]: ...
