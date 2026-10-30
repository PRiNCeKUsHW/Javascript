# Module 4 lesson plan: AI Agent Architecture

Audience: learners who finished Modules 2-3. Target level: explain what an agent is and when to use
one, and build a tool-using agent loop from scratch that stops and fails safely.

Delivery: **one full-module video** (six parts joined, with YouTube chapters).
**Beginner pacing** (from Module 4 on): slower voice (0.92), longer pauses, every new term explained
on first use, "why" before "how", a recap before each new step, and one "Pause and try" per part.

Provider: Anthropic Claude via the official Python SDK (`anthropic==2.3.0`), default model
`claude-opus-5-5`, manual tool-use loop with `client.messages.create(tools=...)`. API facts checked:
`stop_reason == "tool_use"`, results as `tool_result` blocks in the next user message matched by
`tool_use_id`, `is_error` for failed tools, assistant content appended unchanged (append-only history),
forced `tool_choice` is rejected on Opus 5.5 (not used), the SDK's tool runner mentioned as the
production shortcut.

**Honesty rule for demos:** no API key was available while recording. Model turns come from the
project's offline fake API (`calc_agent/fake_api.py`), a fixed script, not a model; the tools and the
loop are real. The narration says so in parts 2-6.

| # | Part | Concepts | Runnable source |
|---|---|---|---|
| 1 | Chatbots, workflows, agents | recap M2-M3; three designs by who decides the next step; agent loop diagram (decide, act, observe, answer); workflow vs agent; start simple; checks for irreversible actions; pause and try (classify 3 tasks) | concepts |
| 2 | Inside an agent | model, instructions, tools, state; a tool is your function, the model only asks; tool definition (name, description, input_schema, strict); a real tool_use block; who runs the tool; instructions with reasons; state = message list; pause and try (describe get_weather) | `source/lesson-02/` |
| 3 | The agent loop | 25-line loop: limited `for`, decide, append unchanged, stop on no tool calls, act, observe with tool_use_id, results as user message; run + six-message history; three API rules; pause and try (predict turns) | `source/lesson-03/` |
| 4 | Stopping safely | six endings; step limit demo; tool errors as observations (`is_error`), `act()`; recovery demo; never eval tool input; allow-list `_evaluate`; tool runner, Modules 5 and 7; pause and try (match protections) | `source/lesson-04/`, project |
| 5 | Project part 1 | brief, architecture, honest fake, convert, run_tool dispatcher, Step/Result, decide(), run() with stop reasons, first run | `project/smart-calculator-agent/` |
| 6 | Project part 2 | trace (show_step, on_step), multi-step demo, pause and try (read the trace), failures (kg to km, refusal, 401), tests, mypy, troubleshooting, module recap, 5-question quiz, challenge, docs | `project/smart-calculator-agent/` |
