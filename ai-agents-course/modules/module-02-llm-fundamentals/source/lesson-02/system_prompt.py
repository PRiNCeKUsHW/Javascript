# system_prompt.py: set the model's role and rules with a system prompt
from offline import lesson_client

client = lesson_client()

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1000,
    system="You are a patient tutor. Answer in at most two sentences.",
    messages=[{"role": "user", "content": "Why do we use virtual environments?"}],
)

for block in response.content:        # content is a list of blocks
    if block.type == "text":
        print(block.text)
