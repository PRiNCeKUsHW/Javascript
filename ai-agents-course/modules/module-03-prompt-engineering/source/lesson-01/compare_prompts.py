import project  # noqa: F401  (makes `resume` importable)
from resume.prompts import get_prompt

RESUME = "# Ana Lima\nPython developer since 2022. Built APIs with FastAPI."

for version in ("v1", "v2"):
    prompt = get_prompt("extract_profile", version)
    text = prompt.system + "\n" + prompt.render(resume=RESUME)
    print(f"--- {prompt.label}: {len(text)} characters, "
          f"about {len(text) // 4} tokens")
    print("system:", prompt.system[:70] + ("..." if len(prompt.system) > 70
                                           else ""))
    print("user:  ", prompt.render(resume="...").splitlines()[0])
