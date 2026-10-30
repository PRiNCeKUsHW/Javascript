# Module 4 quiz with answers

## Pause-and-try answers

- **Part 1** (chatbot, workflow or agent?): translating a paragraph = single call; resume + job → gap
  report = workflow; trip planning while checking prices = agent.
- **Part 2** (describe a get_weather tool): what it does (current temperature and conditions for a city),
  inputs (a city name), what it returns (temperature in °C and a short description), how it fails
  (error if the city isn't found).
- **Part 3** (predict the turns): three calculations, one per turn → 4 requests and 8 messages.
- **Part 4** (match the protection): endless tool calls → step limit; Python code in the calculator →
  allow-list calculator; "18 x 1.15" → the tool error goes back to the model, which fixes it.
- **Part 6** (read the trace): a 20% tip changes the first call (18 * 1.2) and the split that uses its
  result; the km → mi conversion doesn't change.

## Lesson quick checks

**L1.** What makes a program an agent? **The model decides the next step, in a loop, using tools.**
**L2.** Who runs the calculation when the agent uses calculate? **Your program, after the model asks.**
**L3.** How does the loop know the agent has finished? **The reply contains no tool requests** (stop reason `end_turn`).
**L4.** Why send a tool's error back to the model? **So it can fix its input and continue**; the step limit caps retries.

## Module quiz

1. The resume analyzer always runs extract, compare, advise. What is it? **A workflow.**
2. What does `stop_reason == "tool_use"` mean? **The model wants your program to run a tool.**
3. Where do tool results go? **In the next user message, as `tool_result` blocks with matching ids.**
4. Why `for turn in range(max_steps)` instead of `while True`? **It guarantees the agent stops**, and limits cost.
5. Why an AST allow-list instead of `eval()`? **`eval` runs any Python code; tool input is untrusted.**

## Extension challenge

Pick one or more; each needs code and a test that uses the fake API:

- Add a `percent_of(percent, value)` tool with its definition and errors.
- Add `--json` to print the steps and the answer as JSON.
- Stop early if the model repeats exactly the same tool call twice in a row.
- With a key: run five word problems on a real model and compare the traces.
