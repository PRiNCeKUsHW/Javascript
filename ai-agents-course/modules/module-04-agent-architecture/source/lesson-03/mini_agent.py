from project import lesson_client
from calc_agent.tools import TOOLS, run_tool

client = lesson_client()
messages = [{"role": "user", "content": "What is 18 * 1.15, then 20.7 / 3?"}]

for turn in range(1, 6):                       # never loop forever
    response = client.messages.create(         # 1. decide
        model="claude-opus-5-5", max_tokens=8000,
        tools=TOOLS, messages=messages)
    messages.append({"role": "assistant", "content": response.content})
    calls = [b for b in response.content if b.type == "tool_use"]
    if not calls:                              # 4. stop: no more tools
        text = next(b.text for b in response.content if b.type == "text")
        print(f"turn {turn}: answer ->", text)
        break
    results = []
    for call in calls:
        output = run_tool(call.name, call.input)   # 2. act
        print(f"turn {turn}: {call.name}({call.input}) -> {output}")
        results.append({"type": "tool_result",     # 3. observe
                        "tool_use_id": call.id, "content": output})
    messages.append({"role": "user", "content": results})

print("messages in the history:", len(messages))
