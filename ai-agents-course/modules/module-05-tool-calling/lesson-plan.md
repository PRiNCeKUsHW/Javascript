# Module 5 lesson plan

| # | Lesson | Ideas | Analogy | Demo (real output) |
|---|---|---|---|---|
| 1 | Tool calling | request → `tool_use` → your code runs → `tool_result`; parts of a definition; good descriptions | lending an assistant a phone with apps | `first_tool.py` (definition → tool_use block) |
| 2 | Many tools | registry + `@tool`; schemas from Pydantic (`schema_for`); parallel calls, one message of results | restaurant menu; one waiter, several orders | `from_pydantic.py`, `registry.py`, `parallel.py` |
| 3 | Validation | untrusted input; strict mode vs your code; `model_validate`; business rules; recovery | bank clerk checking a form | `validate.py`; agent with `PROD_FAKE_FAIL=badinput` |
| 4 | Timeouts | thread + `join(seconds)`; failures become observations; thread vs process | giving up on a queue | `timeout.py`; agent with `PROD_FAKE_SLOW=search_notes` |
| 5 | Permissions | least privilege; read/write/danger; read-only; human approval; order of checks | hotel key card | `permissions.py`; agent delete with y/N, `--read-only` |
| 6 | Project 1 | brief, architecture, honest fake, atomic store, six tools, CLI wiring | write the new page, then swap | `tools`, `reset`, a 3-part request |
| 7 | Project 2 | system prompt, loop with parallel calls, full demo, safety on purpose, tests, wrap-up | — | full demo, pytest (43), mypy |

Pacing: beginner pacing (voice 0.92, longer pauses). Each lesson: objectives, analogy, What → Why → How
→ Where, a dry-run table, a pause-and-try, an interview corner, a quick check and a recap. Lesson 7 adds
the module recap, the 5-question quiz, practice questions, the extension challenge and the docs.
