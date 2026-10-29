def normalize(text):
    """Collapse runs of whitespace and trim both ends."""
    return " ".join(text.split())


def word_count(text):
    return len(normalize(text).split())
