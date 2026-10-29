# first_call.py: send one message to Claude and read the reply
import anthropic

from offline import lesson_client

client = lesson_client()          # in your own code: anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1000,
    messages=[{"role": "user", "content": "What is an API, in one sentence?"}],
)

print(response.content[0].text)
print("stop reason:", response.stop_reason)
print("tokens in/out:", response.usage.input_tokens, response.usage.output_tokens)
