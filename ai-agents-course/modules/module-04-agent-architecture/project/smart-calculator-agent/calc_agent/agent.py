from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

import anthropic
from anthropic.types import Message, MessageParam, ToolUseBlock

from calc_agent.errors import AgentError, ToolError
from calc_agent.pricing import CostTracker
from calc_agent.tools import TOOLS, run_tool

SYSTEM = (
    "You help people with everyday maths: shopping, recipes, travel and "
    "bills. Work numbers out with the tools rather than in your head, "
    "because the tools are exact. Use calculate for arithmetic and convert "
    "for units. If a tool returns an error, fix the input and try again. "
    "Answer in one or two sentences that state the number and its unit.")


@dataclass
class Step:
    """One action the agent took, and what it observed."""

    tool: str
    input: dict[str, Any]
    output: str
    is_error: bool = False


@dataclass
class Result:
    answer: str
    stop: str          # answered, max_steps, refused, cut_off, budget
    steps: list[Step] = field(default_factory=list)
    turns: int = 0
    cost_usd: float = 0.0

    @property
    def ok(self) -> bool:
        return self.stop == "answered"


@contextmanager
def friendly_errors() -> Iterator[None]:
    """Turn SDK exceptions into one clear AgentError each."""
    try:
        yield
    except anthropic.AuthenticationError:
        raise AgentError("the API key was rejected: check "
                         "ANTHROPIC_API_KEY") from None
    except anthropic.RateLimitError:
        raise AgentError("rate limited, even after retries: wait and try "
                         "again") from None
    except anthropic.APIConnectionError:
        raise AgentError("could not reach the API: check your "
                         "connection") from None
    except anthropic.APIStatusError as exc:
        raise AgentError(f"the API failed with status "
                         f"{exc.status_code}") from None


def act(call: ToolUseBlock) -> Step:
    """Run one tool call. A tool problem is an observation, not a crash."""
    try:
        return Step(call.name, call.input, run_tool(call.name, call.input))
    except ToolError as exc:
        return Step(call.name, call.input, f"Error: {exc}", is_error=True)


class CalculatorAgent:
    def __init__(self, client: anthropic.Anthropic, model: str,
                 tracker: CostTracker, max_steps: int = 6) -> None:
        self.client = client
        self.model = model
        self.tracker = tracker
        self.max_steps = max_steps

    def decide(self, messages: list[MessageParam]) -> Message:
        """Ask the model what to do next: call tools, or answer."""
        with friendly_errors():
            response = self.client.messages.create(
                model=self.model, max_tokens=8000, system=SYSTEM,
                tools=TOOLS, output_config={"effort": "low"},
                messages=messages)
        self.tracker.add(self.model, response.usage.input_tokens,
                         response.usage.output_tokens)
        return response

    def run(self, question: str,
            on_step: Callable[[Step], None] | None = None) -> Result:
        """The agent loop: decide, act, observe, repeat until done."""
        messages: list[MessageParam] = [{"role": "user", "content": question}]
        steps: list[Step] = []
        for turn in range(1, self.max_steps + 1):
            if self.tracker.spent_usd >= self.tracker.budget_usd:
                return self._stop("budget", steps, turn - 1)
            response = self.decide(messages)                    # decide
            messages.append({"role": "assistant",
                             "content": response.content})
            if response.stop_reason == "refusal":
                return self._stop("refused", steps, turn)
            if response.stop_reason == "max_tokens":
                return self._stop("cut_off", steps, turn)
            calls = [b for b in response.content if b.type == "tool_use"]
            if not calls:                                       # done
                text = "".join(b.text for b in response.content
                               if b.type == "text")
                return Result(text, "answered", steps, turn,
                              self.tracker.spent_usd)
            results: list[Any] = []
            for call in calls:
                step = act(call)                                # act
                steps.append(step)
                if on_step:
                    on_step(step)
                results.append({"type": "tool_result",          # observe
                                "tool_use_id": call.id,
                                "content": step.output,
                                "is_error": step.is_error})
            messages.append({"role": "user", "content": results})
        return self._stop("max_steps", steps, self.max_steps)

    def _stop(self, reason: str, steps: list[Step], turns: int) -> Result:
        return Result("", reason, steps, turns, self.tracker.spent_usd)
