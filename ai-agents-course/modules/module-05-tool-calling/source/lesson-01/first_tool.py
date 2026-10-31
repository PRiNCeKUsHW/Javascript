# first_tool.py: one tool definition, and the tool_use block a model sends back
import json

import project  # noqa: F401  (lets us import the course project)
from productivity.client import make_client
from productivity.config import load_settings

add_task = {
    "name": "add_task",
    "description": "Adds a task to the user's to-do list. Use it when the "
                   "user asks to remember or plan something they must do.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "What to do"},
            "due": {"anyOf": [{"type": "string", "format": "date"}, {"type": "null"}]},
            "priority": {"type": "string", "enum": ["low", "normal", "high"]},
        },
        "required": ["title", "due", "priority"],
        "additionalProperties": False,
    },
    "strict": True,
}

client = make_client(load_settings())
response = client.messages.create(
    model="claude-opus-5-5", max_tokens=2000, tools=[add_task],
    messages=[{"role": "user", "content": "add task Pay rent high priority"}])

print("stop_reason:", response.stop_reason)
for block in response.content:
    if block.type == "tool_use":
        print("tool:", block.name)
        print("input:", json.dumps(block.input))
