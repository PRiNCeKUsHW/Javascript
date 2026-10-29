# json_demo.py: convert between Python objects and JSON text
import json
from pathlib import Path

record = {"id": "req-001", "tokens": 600, "ok": True, "error": None}

text = json.dumps(record, indent=2)         # Python -> JSON text
print(text)
Path("record.json").write_text(text, encoding="utf-8")

loaded = json.loads(Path("record.json").read_text(encoding="utf-8"))
print(loaded["tokens"] + 1, type(loaded["ok"]))

try:
    json.loads('{"id": "req-002",}')         # trailing comma: not valid JSON
except json.JSONDecodeError as err:
    print("invalid JSON:", err)
