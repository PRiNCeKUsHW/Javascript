"""An offline stand-in for the Anthropic Messages API.

It speaks the same HTTP protocol as the real API, so the real `anthropic` SDK
talks to it unchanged: requests, streaming, structured output, errors and
retries all go through the SDK's own code. The replies are canned, clearly
marked placeholders, NOT model output. Use it for tests, demos and learning
without an API key.
"""
import json
import math
import os
import re
from typing import Any

import httpx2

DEMO_MARK = "(offline demo reply)"
ERROR_TYPES = {400: "invalid_request_error", 401: "authentication_error",
               429: "rate_limit_error", 500: "api_error", 529: "overloaded_error"}


def estimate_tokens(text: str) -> int:
    """Rough estimate (about 4 characters per token). Real counts differ."""
    return max(1, math.ceil(len(text) / 4))


def _text_of(content: Any) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict))


class FakeAnthropicAPI:
    """Callable handler for httpx2.MockTransport."""

    def __init__(self, failures: list[str] | None = None) -> None:
        # e.g. ["429", "500"]: the next calls fail that way, in order
        env = os.environ.get("STUDY_FAKE_FAIL", "")
        self.failures = failures if failures is not None else [
            f for f in env.split(",") if f]
        self.requests: list[dict[str, Any]] = []

    def __call__(self, request: httpx2.Request) -> httpx2.Response:
        body = json.loads(request.content or b"{}")
        self.requests.append(body)
        prompt = (_text_of(body.get("system", "")) + " "
                  + " ".join(_text_of(m["content"]) for m in body["messages"]))
        input_tokens = estimate_tokens(prompt)
        if request.url.path.endswith("/count_tokens"):
            return httpx2.Response(200, json={"input_tokens": input_tokens})

        text, stop = self._reply(body), "end_turn"
        if self.failures:
            failure = self.failures.pop(0)
            if failure != "refusal":
                return self._error(int(failure))
            text, stop = "", "refusal"         # the model declined
        limit = body["max_tokens"] * 4          # characters that fit the limit
        if len(text) > limit:
            text, stop = text[:limit], "max_tokens"
        if body.get("stream"):
            return self._stream(body, text, stop, input_tokens)
        return self._message(body, text, stop, input_tokens)

    # ------------------------------------------------------------ replies
    def _reply(self, body: dict[str, Any]) -> str:
        messages = body["messages"]
        question = _text_of(messages[-1]["content"])
        output_format = body.get("output_config", {}).get("format")
        if output_format:
            return json.dumps(self._quiz(question))
        if len(messages) > 1:
            earlier = len(messages) - 1
            return (f"{DEMO_MARK} You said: \"{question[:60]}\". This request "
                    f"carried {earlier} earlier message(s), so I can see the "
                    "conversation so far.")
        topic = re.sub(r"\s+", " ", question).strip()[:80]
        return (f"{DEMO_MARK} A real model would explain this now: "
                f"\"{topic}\". Offline mode returns this placeholder instead, "
                "so you can test the whole program without an API key. Set "
                "ANTHROPIC_API_KEY to get a real explanation from Claude.")

    @staticmethod
    def _quiz(question: str) -> dict[str, Any]:
        match = re.search(r"(\d+) multiple-choice questions about (.+?)\.",
                          question)
        count = int(match.group(1)) if match else 3
        topic = match.group(2) if match else "the topic"
        return {"topic": topic, "questions": [{
            "question": f"Demo question {i} about {topic}?",
            "options": [f"Option {c}" for c in "ABCD"],
            "answer_index": (i - 1) % 4,
            "explanation": f"{DEMO_MARK} placeholder explanation {i}.",
        } for i in range(1, count + 1)]}

    # ------------------------------------------------------------ responses
    @staticmethod
    def _message(body: dict[str, Any], text: str, stop: str,
                 input_tokens: int) -> httpx2.Response:
        content = [{"type": "text", "text": text}] if text else []
        return httpx2.Response(200, headers={"request-id": "req_offline"}, json={
            "id": "msg_offline", "type": "message", "role": "assistant",
            "model": body["model"], "content": content, "stop_reason": stop,
            "stop_sequence": None,
            "usage": {"input_tokens": input_tokens,
                      "output_tokens": estimate_tokens(text) if text else 0},
        })

    @staticmethod
    def _stream(body: dict[str, Any], text: str, stop: str,
                input_tokens: int) -> httpx2.Response:
        def event(kind: str, data: dict[str, Any]) -> str:
            return f"event: {kind}\ndata: {json.dumps({'type': kind, **data})}\n\n"

        chunks = re.findall(r"\S+\s*", text)
        events = [event("message_start", {"message": {
            "id": "msg_offline", "type": "message", "role": "assistant",
            "model": body["model"], "content": [], "stop_reason": None,
            "stop_sequence": None,
            "usage": {"input_tokens": input_tokens, "output_tokens": 1}}})]
        if text:
            events.append(event("content_block_start", {
                "index": 0, "content_block": {"type": "text", "text": ""}}))
            events += [event("content_block_delta", {
                "index": 0, "delta": {"type": "text_delta", "text": c}})
                for c in chunks]
            events.append(event("content_block_stop", {"index": 0}))
        events.append(event("message_delta", {
            "delta": {"stop_reason": stop, "stop_sequence": None},
            "usage": {"output_tokens": estimate_tokens(text) if text else 0}}))
        events.append(event("message_stop", {}))
        return httpx2.Response(200, content="".join(events).encode(), headers={
            "content-type": "text/event-stream", "request-id": "req_offline"})

    @staticmethod
    def _error(status: int) -> httpx2.Response:
        kind = ERROR_TYPES.get(status, "api_error")
        return httpx2.Response(status, headers={"retry-after": "0"}, json={
            "type": "error", "error": {"type": kind,
                                       "message": f"offline demo {kind}"}})
