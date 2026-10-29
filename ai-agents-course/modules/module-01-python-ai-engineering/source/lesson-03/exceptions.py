# exceptions.py: expect failure and handle it on purpose
def parse_tokens(raw):
    try:
        value = int(raw)
    except ValueError:
        print(f"  not a number: {raw!r}")
        return 0
    else:
        return value
    finally:
        print(f"  checked {raw!r}")


for raw in ["120", "abc"]:
    print(parse_tokens(raw))
