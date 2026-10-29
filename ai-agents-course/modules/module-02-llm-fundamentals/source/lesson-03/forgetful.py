# forgetful.py: a classic bug, the reply is never added to the history
from offline import lesson_client

client = lesson_client()
history = []

for question in ["My name is Priya.", "What is my name?"]:
    history.append({"role": "user", "content": question})
    response = client.messages.create(
        model="claude-opus-5-5", max_tokens=500, messages=history)
    # BUG: we forgot: history.append({"role": "assistant", "content": ...})

print([m["role"] for m in history])
