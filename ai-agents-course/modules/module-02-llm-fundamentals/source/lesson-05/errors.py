# errors.py: catch specific API errors, most specific first
import anthropic

from offline import lesson_client

client = lesson_client(max_retries=0)    # no retries, so we see each error


def ask(question: str) -> str:
    try:
        response = client.messages.create(
            model="claude-opus-5-5", max_tokens=500,
            messages=[{"role": "user", "content": question}])
    except anthropic.AuthenticationError:
        return "check your API key"
    except anthropic.RateLimitError:
        return "rate limited: wait, then retry"
    except anthropic.APIStatusError as exc:
        return f"API error {exc.status_code}: retry later if it is 5xx"
    except anthropic.APIConnectionError:
        return "network problem"
    return response.content[0].text[:40] + "..."


print(ask("hello"))
