# Module 5 question bank: Tool Calling and Function Execution

Every question asked in the Module 5 videos, with answers. **39 questions.**

How to use it: read the question, answer it out loud or on paper, *then* click **Show answer**. Getting one wrong is useful: rewatch that lesson's chapter.

Short answer key, practice answers and the extension challenge: [quiz.md](quiz.md) · Module guide: [README.md](README.md)

## Lesson 1: Tool Calling: How a Model Uses Your Functions

### Quick check

**The response's stop_reason is "tool_use". What should your code do?**

- A) Show the reply to the user
- B) Run the requested tool and send back a tool_result with the same id
- C) Send the same request again
- D) Nothing: the API already ran the tool

<details>
<summary>Show answer</summary>

**B) Run the requested tool and send back a tool_result with the same id**

tool_use means the model is asking your code to run a tool. Run it, then send the output back as a tool_result with the matching tool_use_id.

</details>

### Pause and try: improve a description

Rewrite this one: `"name": "notes", "description": "Notes."`

1. What does it do? When should the model use it? What does it return?

<details>
<summary>Show answer</summary>

One good answer: name it search notes. Description: searches the user's notes for words in the title or text, and returns the matching notes. Use it when the user asks about something they saved earlier.

</details>

### Interview corner

**Interviewer:** Does the model run the tool itself?

<details>
<summary>Show answer</summary>

**A good answer:** No. The model only **requests** a call: it returns a `tool_use` block with a name and input. **Your code** runs the function and sends the output back as a `tool_result` with the same id.

**Trap to avoid:** Saying "Claude executes my function". It never touches your code; you decide whether and how to run it.

</details>

**Interviewer:** What makes a good tool definition?

<details>
<summary>Show answer</summary>

**A good answer:** A clear verb **name**, a **description** that says what it does, when to use it and what it returns, and a tight **schema** (enums, required fields, `strict: true`).

**Trap to avoid:** Focusing only on the schema. The description is what the model reads to choose the tool.

</details>

## Lesson 2: Many Tools: A Registry, Schemas from Pydantic, Parallel Calls

### Quick check

**A reply contains 3 tool_use blocks. What does the next user message contain?**

- A) Only the first tool's result
- B) 3 tool_result blocks, each with its matching tool_use_id
- C) The text of the 3 results, joined into one string
- D) Nothing: tool results go in the system prompt

<details>
<summary>Show answer</summary>

**B) 3 tool_result blocks, each with its matching tool_use_id**

Every tool_use needs a tool_result with the same id, all together in the next user message.

</details>

### Pause and try: count the messages

A request needs 3 tool calls. The model asks for all 3 in its first reply, then answers.

1. How many requests? How many messages at the end?

<details>
<summary>Show answer</summary>

Two requests. And four messages: the user request, the assistant with three tool calls, the user with three results, and the final answer. Compare that with lesson three of Module 4, where one call per turn needed more round trips.

</details>

### Interview corner

**Interviewer:** Why generate tool schemas from Pydantic models?

<details>
<summary>Show answer</summary>

**A good answer:** One source of truth: the same class **describes** the input to the model and **validates** it in your code, so they can't drift apart. Less hand-written JSON, fewer mistakes.

**Trap to avoid:** Thinking the schema alone protects you. You still validate every input when it arrives (lesson 3).

</details>

**Interviewer:** The model returns two tool_use blocks. How do you respond?

<details>
<summary>Show answer</summary>

**A good answer:** Run both, then send **one** user message containing **two** `tool_result` blocks, each with its matching `tool_use_id`.

**Trap to avoid:** Sending one message per result, or answering only the first call: the next request fails.

</details>

## Lesson 3: Validating Tool Inputs: Never Trust, Always Check

### Quick check

**Which problem can only your code catch, not strict mode?**

- A) A missing required field
- B) A string where a number was expected
- C) A due date that is already in the past
- D) An extra field that isn't in the schema

<details>
<summary>Show answer</summary>

**C) A due date that is already in the past**

A past date is a well-formed date: only your code knows today's date and the rule.

</details>

### Pause and try: schema or code?

Which layer catches each problem: strict mode, or your validation code?

1. The model sends a field called "deadline" that isn't in the schema
2. The model asks to complete task 42, but there are only 3 tasks
3. The note text is 5,000 characters long; the limit is 2,000

<details>
<summary>Show answers</summary>

One: strict mode, because additional properties is false. Two: your code, because only the store knows which tasks exist. Three: your code too, because length limits aren't part of strict schemas, so Pydantic checks them.

</details>

### Interview corner

**Interviewer:** If you use strict tool schemas, do you still need to validate tool inputs?

<details>
<summary>Show answer</summary>

**A good answer:** Yes. Strict mode guarantees the **shape and types**. It can't check **limits** that strict schemas drop, or **business rules** like "the due date is in the future" or "task 42 exists".

**Trap to avoid:** "Strict mode means the input is correct." It means the input is well-formed.

</details>

**Interviewer:** What should a tool return when its input is invalid?

<details>
<summary>Show answer</summary>

**A good answer:** A `tool_result` with `is_error: true` and a short, specific message: **which field** and **what's allowed**. The model can then fix the call.

**Trap to avoid:** Raising an exception that crashes the loop, or a vague "invalid input" the model can't act on.

</details>

## Lesson 4: Timeouts and Failures: When a Tool Never Answers

### Quick check

**After a thread timeout fires, what happens to the stuck tool?**

- A) Python kills it immediately
- B) It keeps running in the background; we just stop waiting
- C) It is rolled back automatically
- D) The whole program exits

<details>
<summary>Show answer</summary>

**B) It keeps running in the background; we just stop waiting**

Threads can't be killed from outside in Python. Use a separate process when you must be able to stop the work.

</details>

### Pause and try: pick a timeout

Choose a sensible timeout for each tool.

1. list_tasks: reads a small local JSON file
2. search_notes: calls a remote search service
3. export_report: builds a PDF that takes about 20 seconds

<details>
<summary>Show answers</summary>

There's no single right number, but here's the reasoning. A local file should take milliseconds, so a few seconds is generous. A remote service: a few seconds, so a slow network doesn't freeze the agent. A twenty-second job needs more, perhaps sixty seconds, or better, run it in the background and let the agent check on it later.

</details>

### Interview corner

**Interviewer:** How do you stop a slow tool from freezing an agent?

<details>
<summary>Show answer</summary>

**A good answer:** Give **every tool a timeout**: run it in a worker (thread or process), wait at most N seconds, then return an error result. Prefer the client library's own timeouts for network calls.

**Trap to avoid:** Relying on the model to "notice" it's slow. The model only acts after your code returns.

</details>

**Interviewer:** Thread or process for a tool timeout?

<details>
<summary>Show answer</summary>

**A good answer:** A **thread** is simple and fine for I/O, but it can't be killed. A **process** can be terminated and isolates memory and crashes, at the cost of more overhead.

**Trap to avoid:** Claiming a thread timeout stops the work. It only stops the waiting.

</details>

## Lesson 5: Permissions and Human Confirmation: Ask Before You Act

### Quick check

**Why does the policy validate the input before asking the human?**

- A) Validation is faster than asking
- B) So a human only approves a real, well-formed action
- C) The API requires it
- D) Validation can't run after approval

<details>
<summary>Show answer</summary>

**B) So a human only approves a real, well-formed action**

Asking a person to approve an invalid or impossible call wastes their attention and teaches them to click yes.

</details>

### Pause and try: choose the level

Read, write or danger?

1. get_weather(city)
2. rename_task(task_id, title)
3. send_email(to, subject, body)

<details>
<summary>Show answers</summary>

Get weather is read: it only looks. Rename task is write: it changes data, but it's easy to undo. Send email is danger: once it's sent, you can't take it back, so a human should approve every one.

</details>

### Interview corner

**Interviewer:** How do you make a tool-using agent safe?

<details>
<summary>Show answer</summary>

**A good answer:** **Least privilege** (only the tools it needs), permission levels, **validate every input**, timeouts, and **human approval** for irreversible actions, with clear confirmation text and a log of decisions.

**Trap to avoid:** "Tell the model in the prompt to be careful." Prompts guide; only code enforces.

</details>

**Interviewer:** Where should the human-approval check live?

<details>
<summary>Show answer</summary>

**A good answer:** In **your code**, between validation and execution, so it runs no matter what the model says. The model can be told about it, but never relied on to enforce it.

**Trap to avoid:** Asking the model to ask the user for permission in its reply.

</details>

## Lesson 6: Project, Part 1: Personal Productivity Agent, Store, Tools and Policy

### Pause and try: predict the trace

The store has tasks 1 and 2. Request: "complete task 2 and delete task 7". The human would say yes.

1. How many tool calls? Is the human asked? What does each call return?

<details>
<summary>Show answer</summary>

Two tool calls, both in turn one. Complete task two succeeds. Delete task seven fails before anyone is asked, with: there is no task seven. The human is never asked about a task that doesn't exist.

</details>

## Lesson 7: Project, Part 2: The Loop, the Demo, Tests and Wrap-up

### Module quiz

**Q1. Who actually runs a tool's function?**

- A) The Claude API, on its servers
- B) Your code, after the model requests it
- C) The model, inside its reply
- D) The Anthropic SDK, automatically, in every case

<details>
<summary>Show answer</summary>

**B) Your code, after the model requests it**

The model only requests a call with a tool_use block. Your code decides whether and how to run it.

</details>

**Q2. Why generate tool schemas from Pydantic classes?**

- A) Pydantic schemas are shorter
- B) One class both describes the input to the model and validates it in code
- C) The API only accepts Pydantic
- D) It makes the model faster

<details>
<summary>Show answer</summary>

**B) One class both describes the input to the model and validates it in code**

One source of truth: the schema the model sees and the validation your code runs come from the same class.

</details>

**Q3. With strict: true, which check is still your job?**

- A) That required fields are present
- B) That the priority is one of the enum values
- C) That the task with that id exists
- D) That no extra fields are sent

<details>
<summary>Show answer</summary>

**C) That the task with that id exists**

Strict mode guarantees shape and types. Only your code knows which tasks exist, and other business rules.

</details>

**Q4. A thread timeout fires after 2 seconds. What does it guarantee?**

- A) The tool's work is undone
- B) The agent stops waiting and gets an error result
- C) The thread is killed
- D) The tool is retried automatically

<details>
<summary>Show answer</summary>

**B) The agent stops waiting and gets an error result**

It stops the waiting, not the work. Use a process when you must be able to stop the work.

</details>

**Q5. Where must the human-approval check for delete_task live?**

- A) In the system prompt
- B) In the tool description
- C) In your code, between validation and execution
- D) In the model's reply to the user

<details>
<summary>Show answer</summary>

**C) In your code, between validation and execution**

Only code enforces. Prompts and descriptions guide the model, but can't stop a call.

</details>

### Practice questions

Easy to hard.

**1. Write a schema-ready Pydantic class for rename_task(task_id, title)**

<details>
<summary>Show answer</summary>

```python
class RenameTask(BaseModel):
    task_id: int = Field(ge=1, description="The task's number")
    title: str = Field(min_length=1, max_length=120, description="The new title")
```

</details>

**2. Which permission level for clear_completed_tasks()? Why?**

<details>
<summary>Show answer</summary>

danger. It deletes many items at once and can't be undone, so a
human should approve it (and the question should say how many tasks will be deleted).

</details>

**3. The model sends 4 tool calls; one times out. What does the next user message contain?**

<details>
<summary>Show answer</summary>

one user message with 4 `tool_result` blocks, in order, each with its
id; the timed-out one has `is_error: true` and "... timed out after N s".

</details>

**4. Scenario: a support agent can issue refunds. Design its tools and safety checks.**

<details>
<summary>Show answer</summary>

tools such as `find_order` (read), `refund_status` (read) and `issue_refund`
(danger). Validate amount ≤ order total and the order belongs to the customer; cap the amount the
agent may refund without a human; require approval with the exact order, amount and reason; log every
decision; idempotency keys so a retry can't refund twice; start in read-only mode.

</details>

### Interview corner

**Interviewer:** Walk me through what happens when an agent calls a tool.

<details>
<summary>Show answer</summary>

**A good answer:** Your code sends tools + messages. The model replies `stop_reason: tool_use` with `tool_use` blocks. Your code **validates**, **checks permission**, **runs with a timeout**, and returns `tool_result`s (same ids, `is_error` on failure) in one user message. Repeat until no tool calls.

**Trap to avoid:** Skipping validation and permissions, or saying the API runs the tool.

</details>

**Interviewer:** How would you let an agent send emails safely?

<details>
<summary>Show answer</summary>

**A good answer:** Make `send_email` a **danger** tool: validate recipients and content, show the human the exact email and ask for approval **every time**, log decisions, rate-limit, and start in a read-only or draft-only mode.

**Trap to avoid:** "Add 'never send spam' to the system prompt." Instructions are not enforcement.

</details>

**Interviewer:** What's the difference between strict tool use and validating in your code?

<details>
<summary>Show answer</summary>

**A good answer:** Strict tool use guarantees the input **matches the schema**: fields and types. Your validation enforces **limits and business rules**, and turns failures into clear errors the model can fix.

**Trap to avoid:** Treating them as alternatives. You want both.

</details>
