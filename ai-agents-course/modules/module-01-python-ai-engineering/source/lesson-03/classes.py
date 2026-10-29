# classes.py: bundle data with the behaviour that belongs to it
class Conversation:
    def __init__(self, system_prompt):
        self.messages = [{"role": "system", "content": system_prompt}]

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})

    def last(self):
        return self.messages[-1]["content"]

    def __len__(self):
        return len(self.messages)


chat = Conversation("You are a helpful tutor.")
chat.add("user", "What is a class?")
chat.add("assistant", "A blueprint for creating objects.")
print(len(chat), "messages")
print("Last:", chat.last())

other = Conversation("You are a code reviewer.")
print(len(other), "message in a separate object")
