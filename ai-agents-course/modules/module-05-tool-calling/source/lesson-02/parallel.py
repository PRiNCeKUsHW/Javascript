# parallel.py: one reply can ask for several tools; answer them all in ONE message
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import project  # noqa: F401
from productivity.client import make_client
from productivity.config import load_settings
from productivity.store import Store
from productivity.tools import Context, definitions, run_tool

client = make_client(load_settings())
messages = [{"role": "user", "content": "add task Pay rent and add task Call mom"}]
reply = client.messages.create(model="claude-opus-5-5", max_tokens=2000,
                               tools=definitions(), messages=messages)
calls = [b for b in reply.content if b.type == "tool_use"]
print(f"one reply, {len(calls)} tool calls:")

with TemporaryDirectory() as folder:
    ctx = Context(Store(Path(folder) / "data.json"), date(2026, 10, 31))
    results = []
    for call in calls:
        output = run_tool(ctx, call.name, call.input)
        print(f"  {call.id}  {call.name}  ->  {output}")
        results.append({"type": "tool_result", "tool_use_id": call.id, "content": output})

messages += [{"role": "assistant", "content": reply.content},
             {"role": "user", "content": results}]          # all results, one message
print("next request sends", len(messages), "messages; the last holds",
      len(messages[-1]["content"]), "results")
