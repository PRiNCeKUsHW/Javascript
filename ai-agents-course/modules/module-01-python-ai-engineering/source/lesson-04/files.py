# files.py: read and write text files with pathlib
from pathlib import Path

notes = Path("notes.txt")
notes.write_text("first line\nsecond line\n", encoding="utf-8")

text = notes.read_text(encoding="utf-8")
print(text.splitlines())

with notes.open("a", encoding="utf-8") as f:    # "a" means append
    f.write("third line\n")

for number, line in enumerate(notes.read_text(encoding="utf-8").splitlines(), start=1):
    print(number, line)
print(notes.exists(), notes.suffix, notes.stat().st_size, "bytes")
