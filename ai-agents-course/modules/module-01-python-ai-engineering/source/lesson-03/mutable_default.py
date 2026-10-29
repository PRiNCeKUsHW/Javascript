# mutable_default.py: a classic bug that leaks memory between conversations
def add_message(text, history=[]):          # the [] is created ONCE
    history.append(text)
    return history


print(add_message("hello from Alice"))
print(add_message("hello from Bob"))        # Bob sees Alice's message!


def add_message_fixed(text, history=None):
    if history is None:
        history = []                        # a fresh list on every call
    history.append(text)
    return history


print(add_message_fixed("hello from Alice"))
print(add_message_fixed("hello from Bob"))
