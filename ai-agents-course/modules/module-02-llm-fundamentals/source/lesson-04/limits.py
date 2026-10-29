# limits.py: max_tokens caps the reply; stop_reason tells you why it ended
from offline import lesson_client

client = lesson_client()

for limit in [1000, 15]:
    response = client.messages.create(
        model="claude-opus-5-5", max_tokens=limit,
        messages=[{"role": "user", "content": "Explain recursion."}])
    print(f"max_tokens={limit}: stop_reason={response.stop_reason}, "
          f"output_tokens={response.usage.output_tokens}")
    if response.stop_reason == "max_tokens":
        print("  the reply was cut off; raise max_tokens or ask for less")
