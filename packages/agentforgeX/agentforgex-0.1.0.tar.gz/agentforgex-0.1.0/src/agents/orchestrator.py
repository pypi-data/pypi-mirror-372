"""Orchestrator for coordinating multiple agents with a supervisor.

Design goals:
 1. Keep interface minimal (single run method)
 2. Provide robust parsing & guardrails for supervisor decisions
 3. Avoid unbounded context growth (truncate history window)
 4. Expose useful stats for observability
 5. Remain easily extensible (swap decision strategy later)
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Protocol
from dataclasses import dataclass, field
import time
from .base import BaseAgent
from .schemas import ChatMessage


@dataclass
class OrchestratorResult:
    transcript: List[ChatMessage]
    final_answer: str
    turns: int
    finished: bool
    finish_reason: str
    elapsed: float
    meta: Dict[str, str] = field(default_factory=dict)


def _format_window(messages: List[ChatMessage], max_lines: int) -> str:
    if len(messages) <= max_lines:
        return "\n".join(f"[{m.role}] {m.sender or ''}: {m.content}" for m in messages)
    trimmed = messages[-max_lines:]
    return "\n".join(["...(truncated)...", *[f"[{m.role}] {m.sender or ''}: {m.content}" for m in trimmed]])


def _parse_supervisor(decision: str) -> Tuple[str, Optional[str]]:
    """Return (action, payload). action in {'finish','next','invalid'}"""
    if not decision:
        return ("invalid", None)
    d = decision.strip()
    if d.upper().startswith("FINISH:"):
        return ("finish", d.split(":", 1)[1].strip())
    if d.upper().startswith("NEXT:"):
        return ("next", d.split(":", 1)[1].strip())
    return ("invalid", None)


class SupervisorStrategy(Protocol):
    async def decide(self, supervisor: BaseAgent, task: str, transcript: List[ChatMessage], agents: Dict[str, BaseAgent]) -> str: ...


class DefaultSupervisorStrategy:
    async def decide(self, supervisor: BaseAgent, task: str, transcript: List[ChatMessage], agents: Dict[str, BaseAgent]) -> str:
        sup_prompt = (
            "You are the supervisor coordinating specialist agents.\n"
            f"Task: {task}\n"
            "Decision rules:\n"
            "- If the task is solved, respond FINISH:<final concise answer>.\n"
            "- Otherwise choose the next agent best suited and respond NEXT:<agent_name>.\n"
            "Valid agents: " + ", ".join(agents.keys()) + "\n"
            "Conversation window (most recent):\n" + _format_window(transcript, 10) + "\n"
            "Make a single decisive response."
        )
        return await supervisor.decide_and_act(sup_prompt)


class Orchestrator:
    def __init__(
        self,
        agents: Dict[str, BaseAgent],
        supervisor: BaseAgent,
        max_turns: int = 12,
        history_window: int = 10,
        strategy: Optional[SupervisorStrategy] = None,
    ) -> None:
        self.agents = agents
        self.supervisor = supervisor
        self.max_turns = max_turns
        self.history_window = history_window
        self.strategy = strategy or DefaultSupervisorStrategy()
        self._transcript: List[ChatMessage] = []

    async def run(self, task: str) -> OrchestratorResult:
        self._transcript.clear()
        current_input = task
        finish_reason = "max_turns_exceeded"
        start = time.time()
        for turn in range(1, self.max_turns + 1):
            sup_decision = await self.strategy.decide(self.supervisor, task, self._transcript, self.agents)
            self._transcript.append(ChatMessage(role='supervisor', content=sup_decision, sender=self.supervisor.name))
            action, payload = _parse_supervisor(sup_decision)
            if action == 'finish' and payload:
                finish_reason = 'supervisor_finish'
                return OrchestratorResult(self._transcript, payload, turn, True, finish_reason, time.time()-start)
            if action == 'next' and payload:
                agent = self.agents.get(payload)
                if not agent:
                    self._transcript.append(ChatMessage(role='system', content=f"Unknown agent '{payload}'", sender='system'))
                    continue
                reply = await agent.decide_and_act(current_input)
                self._transcript.append(ChatMessage(role='agent', content=reply, sender=agent.name))
                current_input = reply
                continue
            self._transcript.append(ChatMessage(role='system', content='Supervisor produced invalid directive', sender='system'))
        return OrchestratorResult(self._transcript, current_input, self.max_turns, False, finish_reason, time.time()-start)