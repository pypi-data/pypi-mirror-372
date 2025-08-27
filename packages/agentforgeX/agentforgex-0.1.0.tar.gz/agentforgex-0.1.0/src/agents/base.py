"""Base abstractions for multi-agent system (structured version)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Protocol
import time
from .schemas import ChatMessage, parse_agent_reply, AgentAction


class LLMInterface(Protocol):
    async def complete(self, prompt: str) -> str: ...


class Tool(Protocol):
    name: str
    description: str
    async def run(self, input_text: str) -> str: ...


@dataclass
class AgentMetrics:
    tool_calls: int = 0
    tokens_in: int = 0  # placeholder for future token accounting
    tokens_out: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    def finish(self):
        self.end_time = time.time()


class BaseAgent:
    def __init__(
        self,
        name: str,
        llm: LLMInterface,
        system_prompt: str,
        tools: Optional[List[Tool]] = None,
        memory_window: int = 12,
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.tools = {t.name: t for t in (tools or [])}
        self.memory_window = memory_window
        self.history: List[ChatMessage] = []
        self.metrics = AgentMetrics()

    # -- History helpers --------------------------------------------------
    def add_message(self, role: str, content: str, sender: Optional[str] = None):
        self.history.append(ChatMessage(role=role, content=content, sender=sender or self.name))
        # Trim
        if len(self.history) > self.memory_window:
            self.history = self.history[-self.memory_window:]

    def format_history(self) -> str:
        return "\n".join(f"[{m.role}] {m.sender or ''}: {m.content}" for m in self.history)

    # -- Core decision flow -----------------------------------------------
    async def decide_and_act(self, user_input: str) -> str:
        self.add_message('user', user_input, sender='external')
        tool_listing = '' if not self.tools else (
            'Tools:\n' + '\n'.join(f"- {n}: {t.description}" for n, t in self.tools.items()) + '\n'
        )
        prompt = (
            f"System: {self.system_prompt}\n"
            f"Conversation (most recent first):\n{self.format_history()}\n"
            f"{tool_listing}Respond with either RESPOND:<answer> or TOOL:<name>:<arg>.\n"
            f"User request: {user_input}\n"
        )
        raw_reply = await self.llm.complete(prompt)
        action: AgentAction = parse_agent_reply(raw_reply)
        if action.kind == 'tool' and action.tool_name in self.tools:
            tool = self.tools[action.tool_name]
            start = time.time()
            output = await tool.run(action.tool_argument or '')
            elapsed = time.time() - start
            self.metrics.tool_calls += 1
            # Reflect tool result
            follow = await self.llm.complete(
                f"Tool {action.tool_name} output: {output[:1000]}\nCraft RESPOND:<answer> to user."
            )
            self.add_message('tool', output[:500], sender=action.tool_name)
            self.add_message('agent', follow, sender=self.name)
            return follow
        # Plain respond or parse error fallback
        content = action.content or action.raw_text or ''
        self.add_message('agent', content)
        return content