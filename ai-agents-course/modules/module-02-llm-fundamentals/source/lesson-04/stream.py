# stream.py: show the reply while it is being generated
from offline import lesson_client

client = lesson_client()

with client.messages.stream(
    model="claude-opus-5-5",
    max_tokens=2000,
    messages=[{"role": "user", "content": "Explain streaming in one paragraph."}],
) as stream:
    for text in stream.text_stream:          # small pieces, as they arrive
        print(text, end="", flush=True)
    final = stream.get_final_message()       # the complete message at the end

print("\nstop reason:", final.stop_reason)
