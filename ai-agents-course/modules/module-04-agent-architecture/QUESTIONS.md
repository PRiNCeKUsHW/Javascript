# Module 4 question bank: AI Agent Architecture

Every question asked in the Module 4 videos, with answers. **21 questions.**

How to use it: read the question, answer it out loud or on paper, *then* click **Show answer**. Getting one wrong is useful: rewatch that lesson's chapter.

Short answer key, practice answers and the extension challenge: [quiz.md](quiz.md) · Module guide: [README.md](README.md)

## Lesson 1: Chatbots, Workflows and Agents: What Makes an AI Agent

### Quick check

**What makes a program an agent?**

- A) It uses the most powerful model
- B) The model decides the next step, in a loop, using tools
- C) It has a long system prompt
- D) It answers in JSON

<details>
<summary>Show answer</summary>

**B) The model decides the next step, in a loop, using tools**

In an agent, the model chooses actions and sees their results in a loop. In a workflow, your code chooses.

</details>

### Pause and try: chatbot, workflow or agent?

Pause the video and decide for each one.

1. Translate a paragraph into Spanish
2. Turn a resume and a job posting into a gap report
3. Plan a trip within a budget, checking prices as you go

<details>
<summary>Show answers</summary>

Here are my answers. Translation is a single call: one request, one answer. The gap report is a workflow: the steps are always the same. And trip planning is an agent: what to check next depends on the prices you find.

</details>

## Lesson 2: Inside an Agent: Model, Instructions, Tools and State

### Quick check

**When the agent uses the calculate tool, who runs the calculation?**

- A) The model, inside its own servers
- B) Your program, after the model asks for it
- C) The API, automatically
- D) Nobody: the model guesses the result

<details>
<summary>Show answer</summary>

**B) Your program, after the model asks for it**

The model only writes a request. Your program runs the function and sends the result back.

</details>

### Pause and try: describe a tool

Imagine a get_weather tool. What would you put in its description?

1. Think about: what it does, its inputs, what it returns, how it fails

<details>
<summary>Show answer</summary>

A good answer: it returns the current temperature and conditions for a city. It needs a city name. It returns the temperature in Celsius and a short description. And it returns an error if the city isn't found. Notice that's the same pattern as our calculate tool.

</details>

## Lesson 3: The Agent Loop: Decide, Act, Observe, Repeat

### Quick check

**How does the loop know the agent has finished?**

- A) The model says the word "done"
- B) The reply contains no tool requests
- C) After exactly three turns
- D) When a tool returns an error

<details>
<summary>Show answer</summary>

**B) The reply contains no tool requests**

No tool_use blocks in the reply means the model chose to answer. The stop reason is then end_turn.

</details>

### Pause and try: predict the turns

A question needs three separate calculations, one per turn.

1. How many requests? How many messages at the end?

<details>
<summary>Show answer</summary>

Four requests: three tool turns, plus one for the answer. And eight messages: the question, then three pairs of request and result, then the answer.

</details>

## Lesson 4: Stopping Safely: Step Limits, Tool Errors and Safe Tools

### Quick check

**Why send a tool's error message back to the model instead of raising an exception?**

- A) Exceptions are slow
- B) So the model can fix its input and continue
- C) The API requires it
- D) To hide the error from the user

<details>
<summary>Show answer</summary>

**B) So the model can fix its input and continue**

The error is an observation. The model can read it, correct the call, and finish. The step limit caps the retries.

</details>

### Pause and try: which protection?

Match each problem to the protection that handles it.

1. The model keeps asking for tools and never answers
2. A user types: calculate __import__('os').remove('notes.txt')
3. The model sends "18 x 1.15" instead of "18 * 1.15"

<details>
<summary>Show answers</summary>

One: the step limit. Two: the allow-list calculator, which refuses anything that isn't arithmetic. Three: the tool error goes back to the model, which fixes its input.

</details>

## Lesson 5: Project, Part 1: Smart Calculator Agent, Tools and the Loop

### Pause and try: follow the dispatcher

Use run_tool on lines 133 to 144.

1. The model asks for a tool called "delete_files". What happens?
2. It calls convert with value "lots". What happens?

<details>
<summary>Show answers</summary>

One: run tool raises a tool error, unknown tool, which goes back to the model as an observation. Nothing is deleted, because that tool simply doesn't exist in our program. Two: turning lots into a number fails, so the model gets a clear message saying convert needs a value, a from unit, and a to unit.

</details>

## Lesson 6: Project, Part 2: Traces, Demo, Tests and Wrap-up

### Module quiz

**Q1. The resume analyzer from Module 3 always runs extract, compare, advise. What is it?**

- A) An agent
- B) A workflow
- C) A chatbot
- D) A tool

<details>
<summary>Show answer</summary>

**B) A workflow**

Its steps are fixed and chosen by code, so it's a workflow. In an agent, the model chooses the steps.

</details>

**Q2. What does `stop_reason == "tool_use"` mean?**

- A) The tool has finished running
- B) The model wants your program to run a tool
- C) The model can't use tools
- D) The API ran the tool for you

<details>
<summary>Show answer</summary>

**B) The model wants your program to run a tool**

The model stopped to request a tool. Your program runs it and sends back a tool_result.

</details>

**Q3. Where do tool results go in the message list?**

- A) In the system prompt
- B) In a user message, as tool_result blocks with matching ids
- C) In the assistant's previous message
- D) Nowhere: the API remembers them

<details>
<summary>Show answer</summary>

**B) In a user message, as tool_result blocks with matching ids**

Results go in the next user message, one tool_result per request, matched by tool_use_id.

</details>

**Q4. Why should the loop be `for turn in range(max_steps)` instead of `while True`?**

- A) for loops are faster
- B) It guarantees the agent stops, even if the model never finishes
- C) The API limits loops to 6 turns
- D) while True doesn't work in Python

<details>
<summary>Show answer</summary>

**B) It guarantees the agent stops, even if the model never finishes**

A model can get stuck calling tools. A step limit always ends the loop, and limits cost.

</details>

**Q5. Why does the calculator use an AST allow-list instead of eval()?**

- A) eval is too slow
- B) eval runs any Python code, so tool input could do anything
- C) eval can't do multiplication
- D) The API forbids eval

<details>
<summary>Show answer</summary>

**B) eval runs any Python code, so tool input could do anything**

Tool input is untrusted. An allow-list permits only arithmetic and refuses everything else.

</details>

### Pause and try: read the trace

Look at the trace above.

1. Which tool call would change if the tip were 20%?
2. Which results would change after it?

<details>
<summary>Show answers</summary>

The first call changes: eighteen times one point two. And so does the split, because it uses that result. The marathon conversion doesn't change at all. Reading a trace like this is how you debug agents.

</details>
