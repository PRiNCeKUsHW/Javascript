"""Run statements one by one, like the interactive Python prompt, and capture each one's output.

stdin: JSON list of statements. stdout: JSON list of output strings (stdout + stderr, tracebacks included).
Run it with the working directory and PYTHONPATH the lesson needs.
"""
import code
import contextlib
import io
import json
import sys

statements = json.load(sys.stdin)
real_stdout = sys.stdout
console = code.InteractiveInterpreter({"__name__": "__console__"})
sys.path.insert(0, "")
outputs = []
for statement in statements:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        more = console.runsource(statement, "<stdin>", "single")
    if more:
        raise SystemExit(f"incomplete statement: {statement!r}")
    outputs.append(buffer.getvalue())
json.dump(outputs, real_stdout)
