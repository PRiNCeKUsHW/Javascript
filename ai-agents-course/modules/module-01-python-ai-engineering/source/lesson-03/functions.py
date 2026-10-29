# functions.py: name a piece of logic, then reuse it
def estimate_cost(tokens, price_per_million):
    """Return the cost in dollars for a number of tokens."""
    return tokens * price_per_million / 1_000_000


print(estimate_cost(1500, 0.50))
print(estimate_cost(tokens=2_000_000, price_per_million=3.00))


def shorten(text, max_words=8):
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


print(shorten("Agents decide, act and observe in a loop until the goal is reached"))
print(shorten("Short and sweet"))
print(shorten("Short and sweet", max_words=2))
