# retries.py: the SDK retries 429s, 5xx errors and network failures for you
from offline import lesson_client

client = lesson_client(max_retries=2)    # the default is 2; 0 turns it off

response = client.messages.create(
    model="claude-opus-5-5", max_tokens=500,
    messages=[{"role": "user", "content": "Hello!"}])
print("succeeded:", response.stop_reason)
