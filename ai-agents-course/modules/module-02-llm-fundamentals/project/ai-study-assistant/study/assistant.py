from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

import anthropic
import pydantic
from anthropic.types.beta import BetaMessage, BetaMessageParam

from study.errors import StudyError
from study.models import Quiz
from study.pricing import CostTracker
from study.prompts import (CHAT_SYSTEM, EXPLAIN_REQUEST, EXPLAIN_SYSTEM,
                           QUIZ_REQUEST, QUIZ_SYSTEM)

# If the model declines a request, the API can re-run it on another model.
FALLBACK_BETA = "server-side-fallback-2026-07-01"


@dataclass
class Answer:
    text: str
    stop_reason: str
    input_tokens: int
    output_tokens: int
    cost_usd: float

    @property
    def truncated(self) -> bool:
        return self.stop_reason == "max_tokens"


@contextmanager
def friendly_errors() -> Iterator[None]:
    """Turn SDK exceptions into one clear StudyError each (most specific first)."""
    try:
        yield
    except anthropic.AuthenticationError:
        raise StudyError("the API key was rejected: check ANTHROPIC_API_KEY") \
            from None
    except anthropic.RateLimitError:
        raise StudyError("rate limited, even after retries: wait and try "
                         "again") from None
    except anthropic.APITimeoutError:
        raise StudyError("the request timed out: try again") from None
    except anthropic.APIConnectionError:
        raise StudyError("could not reach the API: check your connection") \
            from None
    except anthropic.BadRequestError as exc:
        raise StudyError(f"the request was rejected: {exc.message}") from None
    except anthropic.APIStatusError as exc:
        raise StudyError(f"the API failed with status {exc.status_code}: "
                         "try again later") from None


class StudyAssistant:
    def __init__(self, client: anthropic.Anthropic, model: str,
                 tracker: CostTracker) -> None:
        self.client = client
        self.model = model
        self.tracker = tracker

    def _base(self) -> dict[str, Any]:
        return {"model": self.model, "betas": [FALLBACK_BETA],
                "fallbacks": "default"}

    def _answer(self, message: BetaMessage) -> Answer:
        usage = message.usage
        cost = self.tracker.add(self.model, usage.input_tokens,
                                usage.output_tokens)
        if message.stop_reason == "refusal":
            raise StudyError("the model declined this request")
        text = "".join(b.text for b in message.content if b.type == "text")
        return Answer(text, message.stop_reason or "", usage.input_tokens,
                      usage.output_tokens, cost)

    def explain(self, topic: str, level: str = "beginner",
                max_tokens: int = 2000,
                on_text: Callable[[str], None] | None = None) -> Answer:
        """Stream an explanation; on_text receives each piece as it arrives."""
        self.tracker.check()
        content = EXPLAIN_REQUEST.format(topic=topic, level=level)
        with friendly_errors(), self.client.beta.messages.stream(
                **self._base(), max_tokens=max_tokens, system=EXPLAIN_SYSTEM,
                output_config={"effort": "low"},
                messages=[{"role": "user", "content": content}]) as stream:
            for text in stream.text_stream:
                if on_text:
                    on_text(text)
            message = stream.get_final_message()
        return self._answer(message)

    def make_quiz(self, topic: str, count: int = 5) -> tuple[Quiz, Answer]:
        """Ask for a quiz as structured output, validated into a Quiz."""
        self.tracker.check()
        content = QUIZ_REQUEST.format(count=count, topic=topic)
        try:
            with friendly_errors():
                response = self.client.beta.messages.parse(
                    **self._base(), max_tokens=16000, system=QUIZ_SYSTEM,
                    output_format=Quiz, output_config={"effort": "medium"},
                    messages=[{"role": "user", "content": content}])
        except pydantic.ValidationError as exc:
            raise StudyError(f"the quiz did not match the schema "
                             f"({exc.error_count()} problem(s))") from None
        answer = self._answer(response)
        if answer.truncated or response.parsed_output is None:
            raise StudyError("the quiz was cut off: ask for fewer questions")
        return response.parsed_output, answer

    def reply(self, history: list[BetaMessageParam],
              max_tokens: int = 1000) -> Answer:
        """One chat turn. The API is stateless: send the whole history."""
        self.tracker.check()
        with friendly_errors():
            message = self.client.beta.messages.create(
                **self._base(), max_tokens=max_tokens, system=CHAT_SYSTEM,
                output_config={"effort": "low"}, messages=history)
        return self._answer(message)

    def count_tokens(self, text: str) -> int:
        with friendly_errors():
            result = self.client.messages.count_tokens(
                model=self.model, messages=[{"role": "user", "content": text}])
        return result.input_tokens


def rough_tokens(text: str) -> int:
    """Quick local estimate (about 4 characters per token). Not exact."""
    return max(1, len(text) // 4)


class ChatSession:
    """Keeps the conversation and trims the oldest turns to fit a budget."""

    def __init__(self, assistant: StudyAssistant,
                 history_budget: int = 2000) -> None:
        self.assistant = assistant
        self.history_budget = history_budget
        self.history: list[BetaMessageParam] = []

    def history_tokens(self) -> int:
        return sum(rough_tokens(str(m["content"])) for m in self.history)

    def trim(self) -> int:
        """Drop the oldest user+assistant pair until the history fits."""
        dropped = 0
        while self.history_tokens() > self.history_budget \
                and len(self.history) > 2:
            del self.history[:2]
            dropped += 2
        return dropped

    def send(self, text: str) -> Answer:
        self.history.append({"role": "user", "content": text})
        self.trim()
        try:
            answer = self.assistant.reply(self.history)
        except StudyError:
            self.history.pop()          # keep history valid: drop the question
            raise
        self.history.append({"role": "assistant", "content": answer.text})
        return answer
