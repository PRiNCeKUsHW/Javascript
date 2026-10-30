from project import lesson_client
from calc_agent.tools import TOOLS

client = lesson_client()
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=8000,
    tools=TOOLS,
    messages=[{"role": "user", "content": "What is 18 * 1.15?"}],
)

print("stop_reason:", response.stop_reason)
for block in response.content:
    if block.type == "tool_use":
        print("block:      ", block.type)
        print("name:       ", block.name)
        print("input:      ", block.input)
        print("id:         ", block.id)
