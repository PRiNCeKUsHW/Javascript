"""An offline stand-in for the Anthropic Messages API.

It speaks the same HTTP protocol as the real API, so the real `anthropic`
SDK and the agent loop run unchanged. Instead of a model it follows a fixed
script: it finds arithmetic ("18 * 1.15") and unit conversions ("5 km to
mi") in the question, asks for one tool call per turn, then writes a
placeholder answer that lists the tool results. That is NOT model output:
it can't read word problems, plan, or check its work. Use it for tests,
demos and learning without an API key.
"""
import json
import math
import os
import re
from typing import Any

import httpx2

DEMO_MARK = "(offline demo)"
ERROR_TYPES = {400: "invalid_request_error", 401: "authentication_error",
               429: "rate_limit_error", 500: "api_error"}
EXPRESSION = re.compile(r"[(\d][\d.\s+\-*/%()]*[\d)]")
CONVERSION = re.compile(
    r"(-?\d+(?:\.\d+)?)\s*(km|mi|m|cm|ft|in|kg|g|lb|oz|l|ml|c|f)\b"
    r"\s+(?:to|in|into)\s+(km|mi|m|cm|ft|in|kg|g|lb|oz|l|ml|c|f)\b", re.I)


def estimate_tokens(text: str) -> int:
    """Rough estimate (about 4 characters per token). Real counts differ."""
    return max(1, math.ceil(len(text) / 4))


def plan(question: str) -> list[tuple[str, dict[str, Any]]]:
    """The tool calls the script will make, in order of appearance."""
    found: list[tuple[int, str, dict[str, Any]]] = []
    for m in CONVERSION.finditer(question):
        found.append((m.start(), "convert", {
            "value": float(m.group(1)), "from_unit": m.group(2).lower(),
            "to_unit": m.group(3).lower()}))
    text = CONVERSION.sub(" ", question)
    for m in EXPRESSION.finditer(text):
        expr = m.group(0).strip()
        if re.search(r"\d\s*[-+*/%]\s*[\d(]", expr):
            found.append((m.start(), "calculate", {"expression": expr}))
    return [(name, args) for _, name, args in sorted(found, key=lambda f: f[0])]


class FakeAnthropicAPI:
    """Callable handler for httpx2.MockTransport."""

    def __init__(self, failures: list[str] | None = None) -> None:
        # e.g. ["429", "loop"]: the next calls misbehave that way, in order
        env = os.environ.get("CALC_FAKE_FAIL", "")
        self.failures = failures if failures is not None else [
            f for f in env.split(",") if f]
        self.requests: list[dict[str, Any]] = []
        self.calls = 0
        self.injected = 0                         # broken calls not in the plan

    def __call__(self, request: httpx2.Request) -> httpx2.Response:
        body = json.loads(request.content or b"{}")
        self.requests.append(body)
        tokens = estimate_tokens(json.dumps(body.get("messages", [])))
        failure = self.failures[0] if self.failures else ""
        if failure != "loop" and self.failures:
            self.failures.pop(0)                  # "loop" never runs out
        if failure.isdigit():
            return self._error(int(failure))
        if failure == "refusal":
            return self._message(body, [], "refusal", tokens)
        content, stop = self._turn(body, failure)
        return self._message(body, content, stop, tokens)

    # ------------------------------------------------------------ the script
    def _turn(self, body: dict[str, Any], failure: str
              ) -> tuple[list[dict[str, Any]], str]:
        messages = body["messages"]
        question = messages[0]["content"]
        results = [b for m in messages if m["role"] == "user"
                   and isinstance(m["content"], list)
                   for b in m["content"] if b.get("type") == "tool_result"]
        if failure == "loop":
            return [self._tool_use("calculate", {"expression": "1 + 1"})], \
                "tool_use"
        if failure == "badexpr":                  # a broken call to recover from
            self.injected += 1
            return [self._tool_use("calculate", {"expression": "18 x 1.15"})], \
                "tool_use"
        steps = plan(question) if body.get("tools") else []
        done = len(results) - self.injected       # planned calls answered
        if done < len(steps):
            name, args = steps[done]
            return [self._tool_use(name, args)], "tool_use"
        found = "; ".join(str(r["content"]) for r in results
                          if not r.get("is_error")) or "none"
        text = (f"{DEMO_MARK} A real model would write the answer here. "
                f"Tool results: {found}.")
        return [{"type": "text", "text": text}], "end_turn"

    def _tool_use(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        self.calls += 1
        return {"type": "tool_use", "id": f"toolu_offline_{self.calls:02d}",
                "name": name, "input": args}

    # ------------------------------------------------------------ responses
    @staticmethod
    def _message(body: dict[str, Any], content: list[dict[str, Any]],
                 stop: str, input_tokens: int) -> httpx2.Response:
        out = estimate_tokens(json.dumps(content)) if content else 0
        return httpx2.Response(200, headers={"request-id": "req_offline"}, json={
            "id": "msg_offline", "type": "message", "role": "assistant",
            "model": body["model"], "content": content, "stop_reason": stop,
            "stop_sequence": None,
            "usage": {"input_tokens": input_tokens, "output_tokens": out},
        })

    @staticmethod
    def _error(status: int) -> httpx2.Response:
        kind = ERROR_TYPES.get(status, "api_error")
        return httpx2.Response(status, headers={"retry-after": "0"}, json={
            "type": "error", "error": {"type": kind,
                                       "message": f"offline demo {kind}"}})
