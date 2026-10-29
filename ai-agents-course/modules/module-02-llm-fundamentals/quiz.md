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

## Extension challenge (code + a test using the fake API)

- `--model` option; compare costs between Opus, Sonnet and Haiku
- exact token count with `count_tokens` before each chat turn
- `quiz --take`: interactive quiz with explanations at the end
- save chat history to JSON and reload it next time
