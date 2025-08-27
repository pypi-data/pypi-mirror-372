"""Structured dataclasses and protocols for the multi-agent system.

These types give us strongly-typed internal messages and actions so that the
orchestrator logic remains clean and testable.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal
import time

Role = Literal["user", "agent", "system", "tool", "supervisor"]


@dataclass
class ChatMessage:
    role: Role
    content: str
    sender: Optional[str] = None
    created_at: float = field(default_factory=time.time)


@dataclass
class ToolSpec:
    name: str
    description: str
    input_schema: Optional[Dict[str, Any]] = None  # lightweight schema (JSON Schema fragment)
    output_schema: Optional[Dict[str, Any]] = None


@dataclass
class ToolInvocation:
    tool: str
    argument: str
    requested_by: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class ToolResult:
    tool: str
    output: str
    success: bool
    error: Optional[str] = None
    elapsed: float = 0.0


@dataclass
class AgentAction:
    """Represents an agent's decision.

    Kind is one of:
      - respond: Provide a direct user-facing response
      - tool: Request a tool invocation
      - delegate: (future) suggest another agent
    """
    kind: Literal["respond", "tool", "delegate", "noop", "error"]
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_argument: Optional[str] = None
    raw_text: Optional[str] = None  # original LLM text before parsing
    parsing_error: Optional[str] = None


@dataclass
class AgentObservation:
    """Observation returned to an agent after it acted (e.g. tool result)."""
    content: str
    source: str  # tool name or system


def parse_agent_reply(text: str) -> AgentAction:
    """Parse LLM free-form reply to structured action.

    Supported syntaxes:
      TOOL:<name>:<argument>
      RESPOND:<message>
    Fallback: treat as plain respond.
    """
    raw = text.strip()
    upper = raw.upper()
    if upper.startswith("TOOL:"):
        parts = raw.split(":", 2)
        if len(parts) == 3:
            return AgentAction(kind="tool", tool_name=parts[1].strip(), tool_argument=parts[2].strip(), raw_text=raw)
        return AgentAction(kind="error", parsing_error="Malformed TOOL directive", raw_text=raw)
    if upper.startswith("RESPOND:"):
        return AgentAction(kind="respond", content=raw.split(":", 1)[1].strip(), raw_text=raw)
    # default free-form
    return AgentAction(kind="respond", content=raw, raw_text=raw)
