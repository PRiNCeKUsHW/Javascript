import textkit
from textkit.cleaning import word_count


def main():
    raw = "   Agents   use   tools.  "
    print(repr(textkit.normalize(raw)))
    print(word_count(raw), "words")


if __name__ == "__main__":
    main()
