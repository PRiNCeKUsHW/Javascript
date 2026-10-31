# Module 2 question bank: LLM Fundamentals and API Integration

Every question asked in the Module 2 videos, with answers. **47 questions.**

How to use it: read the question, answer it out loud or on paper, *then* click **Show answer**. Getting one wrong is useful: rewatch that lesson's chapter.

The videos are narrated in Hinglish; the questions here are the English text shown on screen.

Short answer key, practice answers and the extension challenge: [quiz.md](quiz.md) · Module guide: [README.md](README.md)

## Lesson 1: How LLMs Work: Tokens, Context Windows and Generation

### Quick check

**Your app sends a new request without the earlier messages. What happens?**

- A) It remembers anyway
- B) It doesn't know: the model has no memory between requests
- C) The API returns an error
- D) It looks it up in its training data

<details>
<summary>Show answer</summary>

**B) It doesn't know: the model has no memory between requests**

Each request is independent. The model only sees what you send in that request, so the app must resend the history.

</details>

### Try these before the next lesson

Easy to hard.

**1. Why can an LLM be confidently wrong?**

<details>
<summary>Show answer</summary>

It writes the most *likely* continuation, not a checked fact.
Fluent, confident text is what it was trained to produce, whether or not it's true (a "hallucination").

</details>

**2. Roughly how many tokens is a 400-character English paragraph?**

<details>
<summary>Show answer</summary>

About 100 (≈ 4 characters per token). Use
`count_tokens` when you need the exact number.

</details>

**3. Your chat app sends 50 old messages every turn. Name two problems.**

<details>
<summary>Show answer</summary>

Cost (every token is billed on every request) and the
context window (it eventually fills). Also slower replies, and old, irrelevant text can distract the model.

</details>

**4. Scenario: a support bot must answer from a 300-page manual. Why not paste the whole manual into every request?**

<details>
<summary>Show answer</summary>

Pasting it into every request is expensive and slow, and may not fit
the window. Send only the relevant sections: that's retrieval, Modules 9 and 10.

</details>

### Interview corner

**Interviewer:** How does an LLM generate text?

<details>
<summary>Show answer</summary>

**A good answer:** It predicts the **next token** from everything so far, adds it, and repeats until it decides the answer is complete. It produces likely text; it does not look facts up.

**Trap to avoid:** Saying it "searches the internet" or "retrieves answers from a database". On its own, it does neither.

</details>

**Interviewer:** Why does a chatbot "remember" earlier messages if the model has no memory?

<details>
<summary>Show answer</summary>

**A good answer:** Because the **application resends the conversation history** with every request. The API is stateless; the app owns the memory.

**Trap to avoid:** Saying the model "learns" from the chat. Its weights don't change while you talk to it.

</details>

## Lesson 2: Your First API Call: Keys, Requests and Responses

### Quick check

**Which three arguments does `client.messages.create` require?**

- A) `api_key`, `model`, `prompt`
- B) `model`, `max_tokens`, `messages`
- C) `model`, `system`, `temperature`
- D) `messages`, `stream`, `usage`

<details>
<summary>Show answer</summary>

**B) `model`, `max_tokens`, `messages`**

`model`, `max_tokens` and `messages` are required. The key comes from `ANTHROPIC_API_KEY`; `system` is optional.

</details>

### Try these before the next lesson

Easy to hard.

**1. Which three arguments does `messages.create` require?**

<details>
<summary>Show answer</summary>

`model`, `max_tokens`, `messages`.

</details>

**2. Change `first_call.py` to print every block's type before its text.**

<details>
<summary>Show answer</summary>

`for block in response.content: print(block.type, getattr(block, "text", ""))`.

</details>

**3. Why is `response.content[0].text` risky in an agent?**

<details>
<summary>Show answer</summary>

The first block may be a `thinking` or `tool_use` block, which has
no `.text`. Check `block.type`.

</details>

**4. Scenario: a teammate pushed a key to GitHub. List your steps, in order.**

<details>
<summary>Show answer</summary>

(1) Revoke it in the Console immediately, (2) create a new key and
update your environment, (3) check usage for anything you didn't make, (4) remove it from the code and
add `.env` to `.gitignore`. Rewriting git history alone isn't enough: assume it was already copied.

</details>

### Interview corner

**Interviewer:** What is an API?

<details>
<summary>Show answer</summary>

**A good answer:** A defined way for one program to ask another for something: you send a **request** in an agreed format, and get a **response** back. Like a waiter between you and the kitchen.

**Trap to avoid:** Saying an API is "a library" or "a website". It's the contract for the conversation between programs.

</details>

**Interviewer:** How do you keep API keys out of your code?

<details>
<summary>Show answer</summary>

**A good answer:** Store them in **environment variables** or a secrets manager, never in the source. Use separate keys per app, and revoke a key the moment it leaks.

**Trap to avoid:** "I put it in a config file in the repo." Anything committed to git should be treated as public.

</details>

## Lesson 3: Conversations: Message History and the Growing Context

### Quick check

**A conversation has 10 earlier messages. How many messages does your next request send?**

- A) 1
- B) 2
- C) 11
- D) It depends on the model's memory

<details>
<summary>Show answer</summary>

**C) 11**

The API is stateless: you send all 10 earlier messages plus the new one (unless you trim the history on purpose).

</details>

### Try these before the next lesson

Easy to hard.

**1. A conversation has 10 messages. How many does the next request send?**

<details>
<summary>Show answer</summary>

11.

</details>

**2. Fix `forgetful.py` and show the roles printed after the fix.**

<details>
<summary>Show answer</summary>

`['user', 'assistant', 'user', 'assistant']`.

</details>

**3. Write `trim(history, max_messages)` that drops the oldest pairs.**

<details>
<summary>Show answer</summary>

`while len(history) > max_messages and len(history) > 2: del history[:2]`
(drop the oldest user + assistant pair, so it still starts with `user`).

</details>

**4. Scenario: users complain the bot "forgets" after an error. What might your code be doing?**

<details>
<summary>Show answer</summary>

The code probably resets the history in its error
handler, or never appended the reply before the failed turn. On an error, remove only the unanswered
question (as `ChatSession.send` does) and keep the rest.

</details>

### Interview corner

**Interviewer:** What does it mean that the Messages API is stateless?

<details>
<summary>Show answer</summary>

**A good answer:** The server keeps **no memory between requests**. Each request must contain everything the model needs, including the conversation history, which the client stores and resends.

**Trap to avoid:** Confusing stateless with "no conversation possible". Conversations work fine; the client carries the state.

</details>

**Interviewer:** A long chat is getting slow and expensive. What would you do?

<details>
<summary>Show answer</summary>

**A good answer:** Measure tokens per turn, then **trim old turns in pairs**, summarise older context, or keep facts in a store and add only what's relevant. Prompt caching cuts the cost of the unchanged prefix.

**Trap to avoid:** "Use a model with a bigger context window." That delays the problem and raises the bill.

</details>

## Lesson 4: Controlling Output: Limits, Streaming and Structured JSON

### Quick check

**Your code parses the reply as JSON and it fails on a long reply. What should you check first?**

- A) The API key
- B) Whether `stop_reason` is `max_tokens`
- C) The temperature setting
- D) The Python version

<details>
<summary>Show answer</summary>

**B) Whether `stop_reason` is `max_tokens`**

A reply cut off at `max_tokens` ends mid-JSON. Check `stop_reason`, raise the limit, or ask for less.

</details>

### Try these before the next lesson

Easy to hard.

**1. What are the two most common stop reasons, and what does each mean?**

<details>
<summary>Show answer</summary>

`end_turn` (finished) and `max_tokens` (cut off at your limit).

</details>

**2. In `stream.py`, what happens without `flush=True`?**

<details>
<summary>Show answer</summary>

the pieces can sit in Python's output buffer and appear in bursts, so the
streaming effect is lost.

</details>

**3. Add a `difficulty` field (easy, medium or hard) to the Quiz schema.**

<details>
<summary>Show answer</summary>

`difficulty: Literal["easy", "medium", "hard"]` on `Question` (from `typing`).

</details>

**4. Scenario: JSON parsing fails only on long replies. What do you check first, and how do you fix it?**

<details>
<summary>Show answer</summary>

Check `stop_reason == "max_tokens"`. Raise `max_tokens`,
ask for less (fewer questions), and never parse a truncated reply.

</details>

### Interview corner

**Interviewer:** Why would you stream an LLM response?

<details>
<summary>Show answer</summary>

**A good answer:** Generation happens token by token, so streaming shows text **as it is produced**: the user sees progress in moments, total time is the same, and very long replies avoid request timeouts.

**Trap to avoid:** Saying streaming makes the model faster. It doesn't; it makes the wait feel shorter.

</details>

**Interviewer:** How do you get reliable JSON from an LLM?

<details>
<summary>Show answer</summary>

**A good answer:** Use **structured outputs**: pass a JSON schema (or a Pydantic model) so the reply is constrained to it, parse into an object, and still check `stop_reason` and validate business rules.

**Trap to avoid:** "Ask for JSON in the prompt and fix it with regex." That breaks on the first unusual reply.

</details>

## Lesson 5: Production Basics: Errors, Rate Limits, Retries and Costs

### Quick check

**Which error should your code retry?**

- A) 401 Authentication error
- B) 400 Bad request
- C) 429 Rate limit
- D) 404 Not found

<details>
<summary>Show answer</summary>

**C) 429 Rate limit**

A 429 recovers after waiting. 400, 401 and 404 fail the same way every time until you fix the request or the key.

</details>

### Try these before the project

Easy to hard.

**1. A 401 error: retry or fix? Why?**

<details>
<summary>Show answer</summary>

Fix. The key is missing, wrong or revoked; a retry fails the same way.

</details>

**2. Cost of 2,000 input + 500 output tokens on Opus 5.5?**

<details>
<summary>Show answer</summary>

2,000 × $4 / 1M + 500 × $20 / 1M = $0.008 + $0.010 = **$0.018**.

</details>

**3. Write a loop that retries 3 times with doubling waits (no SDK retries).**

<details>
<summary>Show answer</summary>

`for attempt in range(3): try: return call() except RateLimitError: time.sleep(0.5 * 2 ** attempt)`,
then raise after the last attempt. Add a little random jitter in real code.

</details>

**4. Scenario: your bill doubled overnight. List three things you'd check.**

<details>
<summary>Show answer</summary>

Check (1) request volume and any loop that retries or
repeats calls, (2) tokens per request (did history or documents grow? untrimmed chats?), (3) which model
and `max_tokens`/`effort` were used (did someone switch to a bigger model?). Then add a budget check.

</details>

### Interview corner

**Interviewer:** Which API errors should you retry, and how?

<details>
<summary>Show answer</summary>

**A good answer:** Retry **429, 5xx and network errors** with exponential backoff plus jitter, and a cap on attempts. Don't retry other 4xx errors: they fail the same way until you fix the request or the key.

**Trap to avoid:** Retrying every error in a tight loop. That hammers the server and burns rate limit.

</details>

**Interviewer:** Why catch specific exceptions before general ones?

<details>
<summary>Show answer</summary>

**A good answer:** Python runs the **first matching `except`**. A parent class like `APIStatusError` matches every HTTP error, so if it comes first, the specific handlers never run.

**Trap to avoid:** A bare `except Exception:` that hides bugs and swallows the error details.

</details>

## Lesson 6: Project, Part 1: AI Study Assistant, Client, Costs and Explanations

### Pause and try: trace the budget

Budget $0.002. Each call costs $0.0013.

**1. How many calls run before BudgetExceeded?**

<details>
<summary>Show answer</summary>

2 calls run. After the second, $0.0026 ≥ $0.002, so the third
`check()` raises `BudgetExceeded`.

</details>

## Lesson 7: Project, Part 2: Quizzes, Chat, Tests and Wrap-up

### Module quiz

**Q1. Why do output tokens matter so much for cost?**

- A) They're free
- B) They usually cost several times more than input tokens
- C) They're only counted when streaming
- D) They don't count toward the context window

<details>
<summary>Show answer</summary>

**B) They usually cost several times more than input tokens**

On Claude Opus 5.5, output tokens cost $20 per million vs $4 for input: five times more. Ask for concise answers.

</details>

**Q2. What does `stop_reason == "max_tokens"` tell you?**

- A) The request was rate limited
- B) The reply was cut off at your limit and may be incomplete
- C) The model refused
- D) The context window is full of history

<details>
<summary>Show answer</summary>

**B) The reply was cut off at your limit and may be incomplete**

The reply hit `max_tokens` and stopped, possibly mid-sentence or mid-JSON. Raise the limit or ask for less.

</details>

**Q3. A chat bot forgets everything said earlier. What's the most likely bug?**

- A) The model's memory is full
- B) The app doesn't send the earlier messages with each request
- C) The API key expired
- D) Streaming is turned off

<details>
<summary>Show answer</summary>

**B) The app doesn't send the earlier messages with each request**

The API is stateless. The app must send the history (and store each reply) on every request.

</details>

**Q4. Which errors are worth retrying automatically?**

- A) 400 and 404
- B) 401 and 403
- C) 429, 5xx and connection errors
- D) Every error

<details>
<summary>Show answer</summary>

**C) 429, 5xx and connection errors**

Rate limits, server errors and network failures can recover. The Anthropic SDK retries them twice by default, with backoff.

</details>

**Q5. What does `client.messages.parse(..., output_format=Quiz)` give you?**

- A) Plain text you must parse yourself
- B) A validated `Quiz` object in `parsed_output`
- C) A guarantee the quiz is factually correct
- D) A faster, cheaper request

<details>
<summary>Show answer</summary>

**B) A validated `Quiz` object in `parsed_output`**

You get a validated object that matches the schema. Structure is guaranteed, **truth is not**: facts still need checking.

</details>

### Real-world scenario: a college help-desk bot

Your college wants a bot that answers student questions from the **admissions FAQ**, remembers the conversation, and must **never cost more than ₹500 a day**.

**1. Where does the conversation memory live, and how is it trimmed?**

<details>
<summary>Show answer</summary>

the app keeps the history per student session (a list, or a database for many users),
trimmed in user + assistant pairs to a token budget.

</details>

**2. How do you enforce the daily budget?**

<details>
<summary>Show answer</summary>

track the cost of every call (tokens × price), store the day's total, and check it
**before** each call; refuse with a friendly message once ₹500 (converted to dollars) is reached.

</details>

**3. What does the bot do on a 429, a 401 and a refusal?**

<details>
<summary>Show answer</summary>

429: let the SDK retry with backoff, then say "busy, try again". 401: alert the developers
(the key is wrong); don't retry. Refusal: show a polite fallback message and log it.

</details>

### Interview corner

**Interviewer:** How would you test code that calls an LLM API without spending money?

<details>
<summary>Show answer</summary>

**A good answer:** Put a **test double behind the real SDK**: a fake server (here an `httpx` MockTransport) that speaks the same protocol, so tests run the real client code, and can script errors, refusals and truncation.

**Trap to avoid:** Mocking your own function so the SDK never runs. Then retries, streaming and parsing are never tested.

</details>

**Interviewer:** How do you stop an AI feature from running up a huge bill?

<details>
<summary>Show answer</summary>

**A good answer:** Measure tokens on every call, convert to cost, and **check a budget before each call**. Add `max_tokens`, step limits for loops, and alerts on spend.

**Trap to avoid:** "We'll watch the dashboard." By the time you look, a loop may have spent the money.

</details>

**Interviewer:** Structured output passed validation. Is the content correct?

<details>
<summary>Show answer</summary>

**A good answer:** Not necessarily. The schema guarantees **shape**, not **truth**. You still check facts, business rules (e.g. the answer index points to a real option) and test with evals.

**Trap to avoid:** Treating schema-valid as correct.

</details>
