# Module 5 quiz with answers

## Lesson quick checks

**L1.** `stop_reason` is `"tool_use"`. What should your code do?
**Answer:** run the requested tool and send back a `tool_result` with the same `tool_use_id`.

**L2.** A reply contains 3 `tool_use` blocks. What does the next user message contain?
**Answer:** 3 `tool_result` blocks, each with its matching id, all in that one message.

**L3.** Which problem can only your code catch, not strict mode?
**Answer:** a due date already in the past (a well-formed date that breaks a business rule).

**L4.** After a thread timeout fires, what happens to the stuck tool?
**Answer:** it keeps running in the background; we only stop waiting. Use a process to stop the work.

**L5.** Why validate the input before asking the human?
**Answer:** so a human only ever approves a real, well-formed action.

## Pause-and-try answers

- **L1, improve a description:** name `search_notes`; "Searches the user's notes for words in the title
  or text and returns the matching notes. Use it when the user asks about something they saved."
- **L2, count the messages:** 2 requests; 4 messages (request, 3 tool calls, 3 results, answer).
- **L3, schema or code:** unknown field → strict mode; task 42 missing → your code; 5,000-character
  note → your code (length limits aren't part of strict schemas; Pydantic checks them).
- **L4, pick a timeout:** local file: a few seconds; remote service: a few seconds; a 20 s job: about
  60 s, or better, run it in the background.
- **L5, choose the level:** `get_weather` read; `rename_task` write; `send_email` danger.
- **L6, predict the trace:** 2 calls in turn 1; `complete_task 2` succeeds; `delete_task 7` fails with
  "there is no task 7" before anyone is asked.

## Module quiz

1. Who actually runs a tool's function? **Your code, after the model requests it.**
2. Why generate schemas from Pydantic? **One class describes the input to the model and validates it
   in code: one source of truth.**
3. With `strict: true`, which check is still your job? **That the task with that id exists** (business
   rules).
4. What does a 2 s thread timeout guarantee? **The agent stops waiting and gets an error result** (the
   thread is not killed).
5. Where must the approval check for `delete_task` live? **In your code, between validation and
   execution.** Prompts guide; only code enforces.

## Practice questions (lesson 7)

1. **`rename_task` input class:**
   ```python
   class RenameTask(BaseModel):
       task_id: int = Field(ge=1, description="The task's number")
       title: str = Field(min_length=1, max_length=120, description="The new title")
   ```
2. **`clear_completed_tasks()`:** danger. It deletes many items at once and can't be undone, so a
   human should approve it (and the question should say how many tasks will be deleted).
3. **4 calls, one times out:** one user message with 4 `tool_result` blocks, in order, each with its
   id; the timed-out one has `is_error: true` and "... timed out after N s".
4. **Scenario, refunds:** tools such as `find_order` (read), `refund_status` (read) and `issue_refund`
   (danger). Validate amount ≤ order total and the order belongs to the customer; cap the amount the
   agent may refund without a human; require approval with the exact order, amount and reason; log every
   decision; idempotency keys so a retry can't refund twice; start in read-only mode.

## Extension challenge (code + a test using the fake API)

- Add `rename_task(task_id, title)` as a write tool.
- Add `due_soon(days)`: open tasks due within N days (read).
- Log every policy decision to an audit file, with the time.
- Run `search_notes` in a subprocess, so a timeout really stops the work.
