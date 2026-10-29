# Module 2 upload kit (one entry per lesson video)

Playlist: **AI Agents with Python 2026: Beginner to Production** (videos #8-#14).
Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-02-llm-fundamentals
Captions: upload `captions/lesson-NN.srt` as English subtitles for each video.

Note for every description: the demos run in **offline mode** (a built-in fake API with placeholder
replies) so they are free and repeatable; with an `ANTHROPIC_API_KEY` the same code calls Claude.

Shared thumbnail style (paste before each lesson's prompt):

> YouTube thumbnail, 16:9, 1280x720. Dark navy-black background (#0A0E17) with a faint dot grid and a soft teal glow on the right. Clean modern developer style, flat vector, no photos, no people, no real company logos. Huge bold white sans-serif headline, one part in bright teal (#2EE6A8), a short amber (#FFB547) subtitle below. Small teal pill badge at top-left reading "MODULE 02 · LESSON N". High contrast, readable on a phone, at most 6 words of large text. Spell every word exactly as given.

---

## Lesson 1: `renders/lesson-01.mp4` (5:35)

**Title:** How LLMs Actually Work: Tokens, Context Windows & Generation | AI Agents with Python #8

**Description:**
```text
Module 2 starts here: what a large language model really does, before you write a single API call. Next-token prediction, tokens, context windows, why the model has no memory, and the controls you actually have on current Claude models.

In this lesson:
• Next-token prediction, explained simply, and why models can be confidently wrong
• Tokens: what they are, roughly 4 characters each, and how to count them exactly
• Why tokens decide your cost, your limits and your speed
• The context window: what fills it (1M tokens on Claude Opus 5.5)
• The model has no memory between requests: your app resends the history
• Your controls: system prompt, max_tokens, effort, model choice

Chapters
00:00 Introduction
00:40 Next-token prediction
01:36 Tokens
02:49 The context window
03:42 Models have no memory
04:06 Your controls
04:47 Quick check
05:06 Recap

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-02-llm-fundamentals
Docs: https://platform.claude.com/docs/en/about-claude/models/overview

#Python #LLM #ClaudeAPI #AIAgents #AIEngineering
```
**Tags:** how llms work, what is a token, context window explained, large language models explained, llm for beginners, claude api, ai agents python, next token prediction

**Thumbnail prompt:** …style above… Badge "MODULE 02 · LESSON 1". Headline: "HOW LLMs" (white) / "REALLY WORK" (teal). Amber subtitle: "tokens · context · generation". On the right, a row of small rounded token chips reading "Agents", " call", " tools", "." and a glowing teal chip "→ next?".

---

## Lesson 2: `renders/lesson-02.mp4` (5:30)

**Title:** Your First Claude API Call in Python (Keys, Requests, Responses) | AI Agents with Python #9

**Description:**
```text
Make your first LLM API call from Python with the official Anthropic SDK, and take the response apart: content blocks, stop reason and token usage. Plus how to keep your API key safe.

In this lesson:
• Creating an API key and storing it in ANTHROPIC_API_KEY (never in code)
• pip install anthropic, and an offline mode so you can follow along without a key
• client.messages.create: model, max_tokens, messages
• Anatomy of a response: id, model, content blocks, stop_reason, usage
• Text, thinking and tool_use blocks
• System prompts

Chapters
00:00 Introduction
00:33 API keys
01:11 Installing the SDK
02:17 The first request
03:17 Anatomy of a response
04:13 System prompts
04:45 Quick check
05:03 Recap

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-02-llm-fundamentals
Docs: https://github.com/anthropics/anthropic-sdk-python

#Python #ClaudeAPI #LLM #AIAgents #PythonTutorial
```
**Tags:** claude api python, anthropic api tutorial, first llm api call, anthropic python sdk, api key security, llm api for beginners, messages api

**Thumbnail prompt:** …style above… Badge "MODULE 02 · LESSON 2". Headline: "YOUR FIRST" (white) / "API CALL" (teal). Amber subtitle: "Python + Claude". On the right, a dark code card showing "client.messages.create(" / "  model=\"claude-opus-5-5\"," / "  max_tokens=1000," / "  messages=[...])".

---

## Lesson 3: `renders/lesson-03.mp4` (3:54)

**Title:** Why Chatbots "Forget": Message History & Stateless LLM APIs | AI Agents with Python #10

**Description:**
```text
The LLM API remembers nothing. Your code owns the conversation, and its growing cost. Build multi-turn chat correctly, fix the classic forgotten-reply bug, and keep long conversations under control.

In this lesson:
• Why the Messages API is stateless
• Building a conversation history in Python (user / assistant roles)
• Input tokens grow every turn, and so does cost
• The forgotten-reply bug, and its fix
• Sliding windows, summaries, stored facts and prompt caching
• Trim history in user/assistant pairs

Chapters
00:00 Introduction
00:31 A stateless API
01:00 Building the history
01:39 The forgotten reply
02:11 Long conversations
03:12 Quick check
03:32 Recap

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-02-llm-fundamentals

#Python #LLM #Chatbot #ClaudeAPI #AIAgents
```
**Tags:** chatbot memory, llm conversation history, stateless api, multi turn chat python, context window cost, claude api python, ai agents

**Thumbnail prompt:** …style above… Badge "MODULE 02 · LESSON 3". Headline: "WHY CHATBOTS" (white) / "FORGET" (teal). Amber subtitle: "message history explained". On the right, three stacked chat bubbles labelled "user", "assistant", "user", the middle one faded and dashed.

---

## Lesson 4: `renders/lesson-04.mp4` (5:42)

**Title:** LLM Output Control: max_tokens, Streaming & Structured JSON (Pydantic) | AI Agents with Python #11

**Description:**
```text
Make LLM replies your program can rely on: check stop_reason, stream text as it is generated, and get validated JSON with structured outputs and Pydantic. Plus how to handle refusals.

In this lesson:
• stop_reason: end_turn, max_tokens, refusal, stop_sequence, tool_use, pause_turn
• max_tokens is a hard cap: detect cut-off replies
• Streaming with messages.stream and text_stream
• Structured outputs with messages.parse(output_format=YourModel)
• How the SDK validates constraints with Pydantic
• Refusals and automatic fallbacks

Chapters
00:00 Introduction
00:31 Stop reasons
01:05 Output limits
01:51 Streaming
02:55 Structured output
04:31 Refusals
04:58 Quick check
05:18 Recap

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-02-llm-fundamentals
Docs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs

#Python #LLM #Pydantic #ClaudeAPI #AIAgents
```
**Tags:** llm structured output, llm json output, pydantic llm, streaming llm python, max_tokens, stop_reason, claude api python

**Thumbnail prompt:** …style above… Badge "MODULE 02 · LESSON 4". Headline: "CONTROL THE" (white) / "OUTPUT" (teal). Amber subtitle: "streaming · JSON · limits". On the right, a dark card with a small JSON snippet "{ \"topic\": \"HTTP\", \"questions\": [...] }" and a green check mark.

---

## Lesson 5: `renders/lesson-05.mp4` (6:42)

**Title:** LLM APIs in Production: Errors, 429 Rate Limits, Retries & Costs | AI Agents with Python #12

**Description:**
```text
What happens when the API says no, and what every call really costs. Error types and how to catch them, rate limits and exponential backoff (built into the SDK), timeouts, key hygiene, and calculating and controlling cost.

In this lesson:
• 400/401/403/404 vs 429 vs 5xx: what to fix and what to retry
• Catching SDK exceptions, most specific first
• Rate limits and exponential backoff, shown with ANTHROPIC_LOG=info
• max_retries, timeouts and request IDs
• Prices per million tokens (Opus 5.5, Sonnet 5.5, Haiku 5.5, October 2026)
• Counting tokens before you send, and five ways to cut cost

Chapters
00:00 Introduction
00:33 Error types
01:27 Catching errors
02:28 Rate limits and retries
04:05 Costs
05:55 Quick check
06:14 Recap

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-02-llm-fundamentals
Docs: https://platform.claude.com/docs/en/api/errors · https://platform.claude.com/docs/en/api/rate-limits

#Python #LLM #ClaudeAPI #AIEngineering #AIAgents
```
**Tags:** llm api errors, rate limit 429, exponential backoff python, llm api cost, token pricing, claude api retries, production llm

**Thumbnail prompt:** …style above… Badge "MODULE 02 · LESSON 5". Headline: "429? 500?" (white) / "RETRY RIGHT" (teal). Amber subtitle: "errors · retries · costs". On the right, three small boxes in a row: a coral box "429", a coral box "500", a teal box "200 ✓", connected by arrows.

---

## Lesson 6: `renders/lesson-06.mp4` (6:03)

**Title:** Build an AI Study Assistant in Python, Part 1: Client, Costs & Streaming | AI Agents with Python #13

**Description:**
```text
Project time! We build the AI Study Assistant: a CLI tutor on the Anthropic SDK that streams explanations, tracks the cost of every call and stops at a budget, with an offline fake API for free, repeatable tests.

In this lesson:
• The brief and the architecture
• fake_api.py: a fake server the real SDK talks to (MockTransport)
• Real client or offline client, from environment variables
• pricing.py: cost per call and a budget guard
• Error mapping and server-side fallbacks for refusals
• Streaming explanations with beta.messages.stream

Chapters
00:00 Introduction
00:19 What we are building
00:53 Architecture
01:27 The offline fake API
02:28 Client and settings
03:06 Costs and budget
03:37 The assistant
05:08 First run
05:36 Recap

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-02-llm-fundamentals/project/ai-study-assistant

#Python #LLM #ClaudeAPI #PythonProject #AIAgents
```
**Tags:** ai study assistant python, llm project python, claude api project, anthropic sdk project, llm cost tracking, mock api testing, ai engineering project

**Thumbnail prompt:** …style above… Badge "MODULE 02 · LESSON 6". Headline: "BUILD AN AI" (white) / "STUDY BUDDY" (teal). Amber subtitle: "Part 1 · Python project". On the right, a dark terminal card with a teal line "$ python -m study explain decorators" and a small grey footer line "$0.00161 · stop: end_turn".

---

## Lesson 7: `renders/lesson-07.mp4` (7:37)

**Title:** Build an AI Study Assistant in Python, Part 2: Quizzes, Chat & Tests | AI Agents with Python #14

**Description:**
```text
We finish the AI Study Assistant: quizzes as validated structured output, chat with trimmed history, the CLI, a full demo including failures, 23 tests with the real SDK against a fake API, and the Module 2 quiz.

In this lesson:
• models.py: the quiz schema with Pydantic
• make_quiz with beta.messages.parse and validation
• ChatSession: history with a token budget
• The CLI: explain, quiz, chat, tokens
• Demo: retries, rate limits and refusals
• Testing LLM code without a key or network
• Module recap, 5-question quiz, extension challenge

Chapters
00:00 Introduction
00:16 Quizzes as structured output
01:14 Chat with history
01:55 The command line
02:33 Demo
03:20 Testing
04:11 Troubleshooting
04:40 Module recap
05:06 Module quiz
06:34 Extension challenge
07:01 Documentation
07:14 Next up

Next: Module 3, prompt engineering and structured outputs.
Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-02-llm-fundamentals/project/ai-study-assistant

#Python #LLM #Pytest #ClaudeAPI #AIAgents
```
**Tags:** llm quiz generator, structured output python, chat history python, testing llm code, pytest mock api, claude api project, ai agents python

**Thumbnail prompt:** …style above… Badge "MODULE 02 · LESSON 7". Headline: "QUIZZES, CHAT" (white) / "+ 23 TESTS" (teal). Amber subtitle: "Part 2 · finished project". On the right, a dark quiz card "Q1. ... A) B) C) D)" with option B highlighted teal, and a green line "23 passed".
