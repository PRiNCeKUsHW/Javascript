"""An offline stand-in for the Anthropic Messages API.

It speaks the same HTTP protocol as the real API, so the real `anthropic`
SDK talks to it unchanged. Instead of a model it uses simple keyword rules:
it finds known skill names in the text and fills the requested schema.
That is NOT model output. The rules ignore prompt wording, miss negation
("no Kubernetes") and know only a fixed list of skills. Use it for tests,
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
               429: "rate_limit_error", 500: "api_error", 529: "overloaded_error"}
KNOWN_SKILLS = [
    "Python", "FastAPI", "Flask", "Django", "Pydantic", "pytest", "SQL",
    "PostgreSQL", "Postgres", "MySQL", "Redis", "Docker", "Kubernetes", "AWS",
    "Terraform", "k8s", "Linux", "Git", "CI/CD", "GitHub Actions", "REST APIs",
    "GraphQL", "Kafka", "React", "TypeScript", "JavaScript", "Node.js",
    "pandas", "scikit-learn", "LangGraph",
]


def estimate_tokens(text: str) -> int:
    """Rough estimate (about 4 characters per token). Real counts differ."""
    return max(1, math.ceil(len(text) / 4))


def _text_of(content: Any) -> str:
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if isinstance(b, dict))


def find_skills(text: str) -> list[str]:
    """Known skill names in order of appearance, as the text writes them."""
    found: list[tuple[int, str]] = []
    for skill in KNOWN_SKILLS:
        match = re.search(rf"(?<![\w.]){re.escape(skill)}(?!\w)", text,
                          re.IGNORECASE)
        if match:
            found.append((match.start(), match.group(0)))
    return [name for _, name in sorted(found)]


def _tagged(text: str, tag: str) -> str:
    match = re.search(rf"<{tag}>\n?(.*?)\n?</{tag}>", text, re.DOTALL)
    return match.group(1) if match else text


def _section(text: str, *words: str) -> str:
    """The lines under the first heading that contains one of the words."""
    lines, keep, out = text.splitlines(), False, []
    for line in lines:
        if line.startswith("#"):
            keep = any(w in line.lower() for w in words)
            continue
        if keep:
            out.append(line)
    return "\n".join(out)


def _years(text: str) -> int:
    match = re.search(r"(\d+)\+?\s+years?\b", text)
    return int(match.group(1)) if match else 0


def _title(text: str) -> str:
    match = re.search(r"^# (.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else "unknown"


class FakeAnthropicAPI:
    """Callable handler for httpx2.MockTransport."""

    def __init__(self, failures: list[str] | None = None) -> None:
        # e.g. ["429", "invalid"]: the next calls misbehave that way, in order
        env = os.environ.get("RESUME_FAKE_FAIL", "")
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

        failure = self.failures.pop(0) if self.failures else ""
        if failure.isdigit():
            return self._error(int(failure))
        if failure == "refusal":
            return self._message(body, "", "refusal", input_tokens)
        text, stop = self._reply(body, failure), "end_turn"
        limit = body["max_tokens"] * 4          # characters that fit the limit
        if failure == "cutoff" or len(text) > limit:
            text, stop = text[: min(limit, len(text) // 2)], "max_tokens"
        return self._message(body, text, stop, input_tokens)

    # ------------------------------------------------------------ replies
    def _reply(self, body: dict[str, Any], failure: str) -> str:
        request = _text_of(body["messages"][-1]["content"])
        schema = (body.get("output_config", {}).get("format") or {}).get(
            "schema")
        if not schema:
            return (f"{DEMO_MARK} A real model would answer here. Set "
                    "ANTHROPIC_API_KEY to get a reply from Claude.")
        fields = schema.get("properties", {})
        if "skills" in fields:
            data = self._profile(_tagged(request, "resume"))
            if failure == "invented":
                data["skills"].append("COBOL")        # not in the resume
            if failure == "invalid":
                data["years_experience"] = -3         # breaks ge=0
        elif "must_have" in fields:
            data = self._job(_tagged(request, "job_posting"))
        else:
            data = self._suggestions(request)
        return json.dumps(data)

    @staticmethod
    def _profile(resume: str) -> dict[str, Any]:
        roles = re.findall(r"^### (.+?)(?:,| \(|$)", resume, re.MULTILINE)
        return {"name": _title(resume), "years_experience": _years(resume),
                "skills": find_skills(resume), "recent_roles": roles[:5]}

    @staticmethod
    def _job(posting: str) -> dict[str, Any]:
        return {"title": _title(posting), "min_years": _years(posting),
                "must_have": find_skills(_section(posting, "must", "require")),
                "nice_to_have": find_skills(
                    _section(posting, "nice", "bonus", "prefer"))}

    @staticmethod
    def _suggestions(request: str) -> dict[str, Any]:
        missing: list[str] = []
        for label in ("Missing required skills", "Missing preferred skills"):
            match = re.search(rf"{label}: (.*)\.", request)
            if match and match.group(1) != "none":
                missing += [s.strip() for s in match.group(1).split(",")]
        return {
            "summary": f"{DEMO_MARK} A real model would summarise the fit "
                       f"here. {len(missing)} skill(s) to work on.",
            "suggestions": [{
                "skill": skill,
                "advice": f"{DEMO_MARK} A real model would suggest a small "
                          f"project that shows {skill}.",
            } for skill in missing]}

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
    def _error(status: int) -> httpx2.Response:
        kind = ERROR_TYPES.get(status, "api_error")
        return httpx2.Response(status, headers={"retry-after": "0"}, json={
            "type": "error", "error": {"type": kind,
                                       "message": f"offline demo {kind}"}})
