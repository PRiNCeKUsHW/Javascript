# conversation.py: the API is stateless, so we send the whole history every time
from offline import lesson_client

client = lesson_client()
history = []                                  # the conversation so far

for question in ["My name is Priya.", "What is my name?", "Thanks!"]:
    history.append({"role": "user", "content": question})
    response = client.messages.create(
        model="claude-opus-5-5", max_tokens=500, messages=history)
    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    print(f"sent {len(history) - 1} message(s), "
          f"{response.usage.input_tokens} input tokens")
    print("  ->", reply[:70], "...")
