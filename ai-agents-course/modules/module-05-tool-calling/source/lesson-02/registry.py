# registry.py: every tool in one place, with its permission and timeout
import project  # noqa: F401
from productivity.tools import REGISTRY

for name, tool in REGISTRY.items():
    fields = ", ".join(tool.params.model_fields)
    print(f"{name}({fields})  {tool.permission}, {tool.timeout_s:g} s")
