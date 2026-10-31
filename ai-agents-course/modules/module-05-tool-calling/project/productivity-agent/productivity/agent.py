from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

import anthropic
from anthropic.types import Message, MessageParam, ToolUseBlock

from productivity.errors import AgentError, ToolError
from productivity.policy import Policy
from productivity.pricing import CostTracker
from productivity.tools import Context, definitions, run_tool

SYSTEM = (
    "You are a personal productivity assistant. You manage the user's tasks "
    "and notes with the tools, because the tools are the only way to read or "
    "change them. When the user asks for several independent things, call the "
    "tools for all of them in the same turn. Look a task's number up with "
    "list_tasks before completing or deleting it. If a tool returns an error, "
    "fix the input if you can; if the user declined an action, don't retry "
    "it. Today is {today}. Finish with a short, friendly summary of what "
    "changed.")


@dataclass
class Step:
    """One tool call the agent made, and what it observed."""

    turn: int
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


class ProductivityAgent:
    def __init__(self, client: anthropic.Anthropic, model: str,
                 tracker: CostTracker, ctx: Context, policy: Policy,
                 max_steps: int = 6) -> None:
        self.client = client
        self.model = model
        self.tracker = tracker
        self.ctx = ctx
        self.policy = policy
        self.max_steps = max_steps

    def decide(self, messages: list[MessageParam]) -> Message:
        """Ask the model what to do next: call tools, or answer."""
        with friendly_errors():
            response = self.client.messages.create(
                model=self.model, max_tokens=8000,
                system=SYSTEM.format(today=self.ctx.today.isoformat()),
                tools=definitions(), output_config={"effort": "low"},
                messages=messages)
        self.tracker.add(self.model, response.usage.input_tokens,
                         response.usage.output_tokens)
        return response

    def act(self, turn: int, call: ToolUseBlock) -> Step:
        """Run one tool call. Any problem is an observation, not a crash."""
        try:
            output = run_tool(self.ctx, call.name, call.input, self.policy)
            return Step(turn, call.name, call.input, output)
        except ToolError as exc:
            return Step(turn, call.name, call.input, f"Error: {exc}", is_error=True)

    def run(self, request: str,
            on_step: Callable[[Step], None] | None = None) -> Result:
        """The agent loop: decide, act on every tool call, observe, repeat."""
        messages: list[MessageParam] = [{"role": "user", "content": request}]
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
            for call in calls:                                  # every call, in order
                step = self.act(turn, call)                     # act
                steps.append(step)
                if on_step:
                    on_step(step)
                results.append({"type": "tool_result",          # observe
                                "tool_use_id": call.id,
                                "content": step.output,
                                "is_error": step.is_error})
            messages.append({"role": "user", "content": results})   # all in ONE message
        return self._stop("max_steps", steps, self.max_steps)

    def _stop(self, reason: str, steps: list[Step], turns: int) -> Result:
        return Result("", reason, steps, turns, self.tracker.spent_usd)
