# lists.py: an ordered collection you can change
messages = ["Hi!", "What is an agent?", "Thanks"]
print(messages[0])          # first item: index 0
print(messages[-1])         # last item
print(len(messages))        # how many items

messages.append("Bye")      # add to the end
print(messages[1:3])        # a slice: items 1 and 2

for number, text in enumerate(messages, start=1):
    print(number, text)
