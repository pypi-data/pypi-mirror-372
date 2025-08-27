"""LLM adapters to plug provider backends into BaseAgent / Orchestrator."""
from __future__ import annotations
import asyncio
from typing import Optional

from llm_providers import get_llm_response

try:  # optional async providers layer
    from providers_async import get_async_provider  # type: ignore
except Exception:  # pragma: no cover
    get_async_provider = None  # type: ignore


class SyncProviderLLM:
    """Wrap sync get_llm_response in async interface with thread offload.

    Use when you only have the synchronous provider available.
    """

    def __init__(self, provider: str):
        self.provider = provider

    async def complete(self, prompt: str) -> str:  # matches LLMInterface
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, get_llm_response, self.provider, prompt)


class AsyncProviderLLM:
    """Adapter around the async providers layer (httpx)."""

    def __init__(self, provider: str):
        if not get_async_provider:
            raise RuntimeError("Async providers layer not available in this environment")
        self._client = get_async_provider(provider)

    async def complete(self, prompt: str) -> str:
        return await self._client.complete(prompt)


class EchoLLM:
    """Deterministic mock LLM for offline smoke tests.

    Simple heuristic to produce structured directives based on turn index.
    """

    def __init__(self):
        self.calls = 0

    async def complete(self, prompt: str) -> str:
        self.calls += 1
        if "Respond with either RESPOND" in prompt and "TOOL:" in prompt and self.calls % 3 == 1:
            # Simulate tool usage first
            return "TOOL:dummy:ping"
        if "Tool dummy output" in prompt:
            return "RESPOND:tool result integrated"
        # Supervisor heuristics: alternate NEXT then FINISH
        if "Supervisor" in prompt and self.calls % 4 != 0:
            return "NEXT:worker"
        if "Supervisor" in prompt:
            return "FINISH:All done"
        return "RESPOND:default answer"
