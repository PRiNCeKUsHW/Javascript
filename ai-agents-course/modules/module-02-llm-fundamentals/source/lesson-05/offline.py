"""Lesson helper: a real Claude client when ANTHROPIC_API_KEY is set,
otherwise the SDK pointed at the project's offline fake API (placeholder replies,
no real model). Lesson code only ever calls the normal SDK methods."""
import os
import sys
from pathlib import Path

import anthropic
import httpx2

sys.path.insert(0, str(Path(__file__).resolve().parents[2]
                       / "project/ai-study-assistant"))
from study.fake_api import FakeAnthropicAPI  # noqa: E402


def lesson_client(**options) -> anthropic.Anthropic:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return anthropic.Anthropic(**options)
    transport = httpx2.MockTransport(FakeAnthropicAPI())
    return anthropic.Anthropic(
        api_key="offline", base_url="http://offline.invalid",
        http_client=anthropic.DefaultHttpxClient(transport=transport), **options)
