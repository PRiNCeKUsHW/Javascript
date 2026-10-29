# variables.py: names that point at values
model = "model-small"        # str: text
max_tokens = 500             # int: whole number
temperature = 0.2            # float: decimal number
streaming = False            # bool: True or False
api_key = None               # None: "no value yet"

print(type(model), type(max_tokens), type(temperature))
print(f"Calling {model} with up to {max_tokens} tokens")

max_tokens = max_tokens * 4  # a name can point at a new value
print(f"New limit: {max_tokens:,} tokens, streaming={streaming}")
