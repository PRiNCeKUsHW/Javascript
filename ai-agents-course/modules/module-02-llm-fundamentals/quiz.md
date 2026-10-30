# Module 2 quiz with answers

## Lesson quick checks

**L1.** Your app sends a new request without the earlier messages. What happens?
**Answer:** the model doesn't know them; it has no memory between requests and only sees what you send.

**L2.** Which three arguments does `client.messages.create` require?
**Answer:** `model`, `max_tokens`, `messages` (the key comes from `ANTHROPIC_API_KEY`; `system` is optional).

**L3.** A conversation has 10 earlier messages. How many messages does the next request send?
**Answer:** 11: all ten plus the new one (unless you trim on purpose).

**L4.** JSON parsing fails on long replies. What do you check first?
**Answer:** whether `stop_reason == "max_tokens"`, meaning the reply was cut off mid-JSON.

**L5.** Which error should be retried: 401, 400, 429 or 404?
**Answer:** 429. It recovers after waiting; the others need a fix.

## Module quiz

1. Why do output tokens matter so much for cost? **They usually cost several times more than input
   tokens** ($20 vs $4 per million on Claude Opus 5.5).
2. What does `stop_reason == "max_tokens"` mean? **The reply was cut off at your limit and may be incomplete.**
3. A chat bot forgets earlier messages. Most likely bug? **The app doesn't send (or store) the history.**
4. Which errors are worth retrying automatically? **429, 5xx and connection errors.** The SDK retries
   them twice by default, with backoff.
5. What does `messages.parse(..., output_format=Quiz)` give you? **A validated `Quiz` object in
   `parsed_output`.** Structure is guaranteed; factual correctness is not.

## Practice questions (from the videos)

Try them before reading the answers. Easy to hard, one real-world scenario each.

### Lesson 1: How LLMs work
1. **Why can an LLM be confidently wrong?** It writes the most *likely* continuation, not a checked fact.
   Fluent, confident text is what it was trained to produce, whether or not it's true (a "hallucination").
2. **Tokens in a 400-character English paragraph?** About 100 (≈ 4 characters per token). Use
   `count_tokens` when you need the exact number.
3. **50 old messages every turn: two problems.** Cost (every token is billed on every request) and the
   context window (it eventually fills). Also slower replies, and old, irrelevant text can distract the model.
4. **Scenario: a 300-page manual.** Pasting it into every request is expensive and slow, and may not fit
   the window. Send only the relevant sections: that's retrieval, Modules 9 and 10.

### Lesson 2: Your first API call
1. **Required arguments?** `model`, `max_tokens`, `messages`.
2. **Print every block's type:** `for block in response.content: print(block.type, getattr(block, "text", ""))`.
3. **Why is `content[0].text` risky?** The first block may be a `thinking` or `tool_use` block, which has
   no `.text`. Check `block.type`.
4. **Scenario: a key pushed to GitHub.** (1) Revoke it in the Console immediately, (2) create a new key and
   update your environment, (3) check usage for anything you didn't make, (4) remove it from the code and
   add `.env` to `.gitignore`. Rewriting git history alone isn't enough: assume it was already copied.

### Lesson 3: Conversations
1. **10 messages, next request sends?** 11.
2. **Fixed `forgetful.py` prints:** `['user', 'assistant', 'user', 'assistant']`.
3. **`trim(history, max_messages)`:** `while len(history) > max_messages and len(history) > 2: del history[:2]`
   (drop the oldest user + assistant pair, so it still starts with `user`).
4. **Scenario: the bot "forgets" after an error.** The code probably resets the history in its error
   handler, or never appended the reply before the failed turn. On an error, remove only the unanswered
   question (as `ChatSession.send` does) and keep the rest.

### Lesson 4: Controlling output
1. **Two common stop reasons:** `end_turn` (finished) and `max_tokens` (cut off at your limit).
2. **Without `flush=True`:** the pieces can sit in Python's output buffer and appear in bursts, so the
   streaming effect is lost.
3. **A difficulty field:** `difficulty: Literal["easy", "medium", "hard"]` on `Question` (from `typing`).
4. **Scenario: JSON fails only on long replies.** Check `stop_reason == "max_tokens"`. Raise `max_tokens`,
   ask for less (fewer questions), and never parse a truncated reply.

### Lesson 5: Production basics
1. **401: retry or fix?** Fix. The key is missing, wrong or revoked; a retry fails the same way.
2. **2,000 in + 500 out on Opus 5.5:** 2,000 × $4 / 1M + 500 × $20 / 1M = $0.008 + $0.010 = **$0.018**.
3. **Retry loop:** `for attempt in range(3): try: return call() except RateLimitError: time.sleep(0.5 * 2 ** attempt)`,
   then raise after the last attempt. Add a little random jitter in real code.
4. **Scenario: the bill doubled overnight.** Check (1) request volume and any loop that retries or
   repeats calls, (2) tokens per request (did history or documents grow? untrimmed chats?), (3) which model
   and `max_tokens`/`effort` were used (did someone switch to a bigger model?). Then add a budget check.

### Lesson 6: Pause and try
**Budget $0.002, $0.0013 per call:** 2 calls run. After the second, $0.0026 ≥ $0.002, so the third
`check()` raises `BudgetExceeded`.

### Lesson 7: Scenario, a college help-desk bot
1. **Memory:** the app keeps the history per student session (a list, or a database for many users),
   trimmed in user + assistant pairs to a token budget.
2. **Daily budget:** track the cost of every call (tokens × price), store the day's total, and check it
   **before** each call; refuse with a friendly message once ₹500 (converted to dollars) is reached.
3. **Errors:** 429: let the SDK retry with backoff, then say "busy, try again". 401: alert the developers
   (the key is wrong); don't retry. Refusal: show a polite fallback message and log it.

## Extension challenge (code + a test using the fake API)

- `--model` option; compare costs between Opus, Sonnet and Haiku
- exact token count with `count_tokens` before each chat turn
- `quiz --take`: interactive quiz with explanations at the end
- save chat history to JSON and reload it next time
