"""An offline stand-in for the Anthropic Messages API.

It speaks the same HTTP protocol as the real API, so the real `anthropic`
SDK and the agent loop run unchanged. Instead of a model it follows a fixed
script: it splits the request on "and" or ";", matches each part against a
few simple patterns ("add task ...", "list tasks", "delete task 2"), asks for
ALL the matching tool calls in one turn (parallel tool use), then writes a
placeholder answer that lists the tool results. That is NOT model output: it
can't understand free-form requests, plan, or recover on its own. Use it for
tests, demos and learning without an API key.
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
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("add_task", re.compile(
        r"^add (?:a )?task:? (?P<title>.+?)(?: due (?P<due>\d{4}-\d{2}-\d{2}))?"
        r"(?: (?P<priority>low|normal|high) priority)?$", re.I)),
    ("list_tasks", re.compile(r"^(?:list|show)(?: my)?(?: (?P<status>open|done|all))? tasks$", re.I)),
    ("complete_task", re.compile(r"^(?:complete|finish) task (?P<task_id>\d+)$", re.I)),
    ("delete_task", re.compile(r"^(?:delete|remove) task (?P<task_id>\d+)$", re.I)),
    ("add_note", re.compile(r"^(?:add a )?note (?P<title>[^:]+): (?P<text>.+)$", re.I)),
    ("search_notes", re.compile(r"^search(?: my)? notes for (?P<query>.+)$", re.I)),
]


def estimate_tokens(text: str) -> int:
    """Rough estimate (about 4 characters per token). Real counts differ."""
    return max(1, math.ceil(len(text) / 4))


def plan(request: str) -> list[tuple[str, dict[str, Any]]]:
    """The tool calls the script will make, one per recognised part."""
    calls: list[tuple[str, dict[str, Any]]] = []
    for part in re.split(r"\s*(?:;|\band\b)\s*", request.strip().rstrip(".!?")):
        for name, pattern in PATTERNS:
            m = pattern.match(part)
            if not m:
                continue
            args = {k: v for k, v in m.groupdict().items()}
            if name == "add_task":
                args["priority"] = (args["priority"] or "normal").lower()
            if name == "list_tasks":
                args["status"] = (args["status"] or "open").lower()
            if "task_id" in args:
                args["task_id"] = int(args["task_id"])
            calls.append((name, args))
            break
    return calls


class FakeAnthropicAPI:
    """Callable handler for httpx2.MockTransport."""

    def __init__(self, failures: list[str] | None = None) -> None:
        # e.g. ["429", "badinput"]: the next calls misbehave that way, in order
        env = os.environ.get("PROD_FAKE_FAIL", "")
        self.failures = failures if failures is not None else [
            f for f in env.split(",") if f]
        self.requests: list[dict[str, Any]] = []
        self.calls = 0
        self.injected = 0                          # tool turns not in the plan

    def __call__(self, request: httpx2.Request) -> httpx2.Response:
        body = json.loads(request.content or b"{}")
        self.requests.append(body)
        tokens = estimate_tokens(json.dumps(body.get("messages", [])))
        failure = self.failures[0] if self.failures else ""
        if failure != "loop" and self.failures:
            self.failures.pop(0)                   # "loop" never runs out
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
        request = messages[0]["content"]
        tool_turns = sum(1 for m in messages if m["role"] == "assistant")
        if failure == "loop":
            return [self._tool_use("list_tasks", {"status": "open"})], "tool_use"
        if failure == "badinput":                  # an invalid call to recover from
            self.injected += 1
            return [self._tool_use("add_task", {"title": "Pay rent", "due": "next friday",
                                                "priority": "urgent"})], "tool_use"
        calls = plan(request) if body.get("tools") else []
        if calls and tool_turns == self.injected:  # the plan, all in one turn
            return [self._tool_use(n, a) for n, a in calls], "tool_use"
        results = [b for m in messages if m["role"] == "user"
                   and isinstance(m["content"], list)
                   for b in m["content"] if b.get("type") == "tool_result"]
        found = " | ".join(str(r["content"]).replace("\n", "; ")
                           for r in results[-len(calls):]) if calls else "none"
        text = (f"{DEMO_MARK} A real model would summarise this for you. "
                f"Tool results: {found}")
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
