import sys

import anthropic
import httpx2

from study.config import Settings
from study.fake_api import FakeAnthropicAPI

OFFLINE_NOTICE = ("offline mode: replies come from a built-in fake API, not a "
                  "real model (set ANTHROPIC_API_KEY to use Claude)")


def make_client(settings: Settings,
                fake: FakeAnthropicAPI | None = None) -> anthropic.Anthropic:
    """A real client, or the same SDK pointed at the offline fake API."""
    if not settings.offline:
        # reads ANTHROPIC_API_KEY from the environment; never hard-code keys
        return anthropic.Anthropic(max_retries=settings.max_retries,
                                   timeout=60.0)
    print(OFFLINE_NOTICE, file=sys.stderr)
    transport = httpx2.MockTransport(fake or FakeAnthropicAPI())
    return anthropic.Anthropic(
        api_key="offline", base_url="http://offline.invalid",
        max_retries=settings.max_retries,
        http_client=anthropic.DefaultHttpxClient(transport=transport))
