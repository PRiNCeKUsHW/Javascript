# costs.py: tokens x price = cost. Count tokens before you send.
from offline import lesson_client

PRICE_PER_MILLION = {"input": 4.00, "output": 20.00}  # Claude Opus 5.5, USD

client = lesson_client()
messages = [{"role": "user", "content": "Summarise the history of the web."}]

count = client.messages.count_tokens(model="claude-opus-5-5", messages=messages)
print("input tokens before sending:", count.input_tokens)

response = client.messages.create(
    model="claude-opus-5-5", max_tokens=1000, messages=messages)
usage = response.usage
cost = (usage.input_tokens * PRICE_PER_MILLION["input"]
        + usage.output_tokens * PRICE_PER_MILLION["output"]) / 1_000_000
print(f"{usage.input_tokens} in + {usage.output_tokens} out = ${cost:.6f}")
print(f"the same call 10,000 times a day: ${cost * 10_000:,.2f}")
