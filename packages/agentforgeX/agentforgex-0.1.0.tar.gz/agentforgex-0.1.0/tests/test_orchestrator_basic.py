import asyncio
from agents.base import BaseAgent, LLMInterface
from agents.orchestrator import Orchestrator


class FakeLLM(LLMInterface):
    def __init__(self, responses):
        self._responses = list(responses)

    async def complete(self, prompt: str) -> str:
        if not self._responses:
            raise RuntimeError("No more fake responses queued. Prompt was: " + prompt[:120])
        return self._responses.pop(0)


class DummyTool:
    name = "dummy"
    description = "Echoes input wrapped."

    async def run(self, input_text: str) -> str:
        await asyncio.sleep(0)
        return f"<dummy>{input_text}</dummy>"


def test_supervisor_next_then_finish():
    async def _run():
        sup_llm = FakeLLM(["NEXT:worker", "FINISH:All done"])  # second decision maybe unused
        worker_llm = FakeLLM(["RESPOND:intermediate answer"])
        supervisor = BaseAgent("supervisor", sup_llm, "Oversee task")
        worker = BaseAgent("worker", worker_llm, "Do work")
        orch = Orchestrator({"worker": worker}, supervisor, max_turns=3)
        result = await orch.run("Test task")
        assert result.finished
        assert result.final_answer in ("intermediate answer", "All done")
        assert result.turns >= 1
    asyncio.run(_run())


def test_tool_invocation_flow():
    async def _run():
        sup_llm = FakeLLM(["NEXT:worker", "FINISH:complete"])  # after one act supervisor finishes
        worker_llm = FakeLLM(["TOOL:dummy:hello", "RESPOND:done"])
        worker = BaseAgent("worker", worker_llm, "Do work", tools=[DummyTool()])
        supervisor = BaseAgent("supervisor", sup_llm, "Oversee task")
        orch = Orchestrator({"worker": worker}, supervisor, max_turns=4)
        result = await orch.run("Run tool pipeline")
        assert result.finished
        assert any("done" in m.content.lower() for m in result.transcript if m.role == 'agent')
    asyncio.run(_run())
