# dicts.py: look values up by key
message = {"role": "user", "content": "What is an agent?"}
print(message["role"])                    # read by key
message["tokens"] = 6                     # add or update a key
print(message.get("model", "unknown"))    # safe read with a default
print(list(message.keys()))

conversation = [
    {"role": "system", "content": "You are a helpful tutor."},
    message,
    {"role": "assistant", "content": "A program that pursues a goal."},
]
for turn in conversation:
    print(f"{turn['role']:>9}: {turn['content']}")
