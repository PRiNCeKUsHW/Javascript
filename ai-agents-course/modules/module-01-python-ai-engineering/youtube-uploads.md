# Module 1 upload kit (one entry per lesson video)

Playlist name: **AI Agents with Python 2026 (Beginner to Production)**
Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-01-python-ai-engineering
Captions: upload `captions/lesson-NN.srt` as English subtitles for each video.

Shared thumbnail style (paste before each lesson's prompt):

> YouTube thumbnail, 16:9, 1280x720. Dark navy-black background (#0A0E17) with a faint dot grid and a soft teal glow on the right. Clean modern developer style, flat vector, no photos, no people, no logos. Huge bold white sans-serif headline (Inter ExtraBold style), one word highlighted in bright teal (#2EE6A8), a short amber (#FFB547) subtitle below. Small teal pill badge at top-left reading "MODULE 01 · LESSON N". A thin glowing circular "agent loop" ring with four small dots on the right edge. High contrast, readable on a phone, at most 6 words of large text. Spell every word exactly as given.

---

## Lesson 1: `renders/lesson-01.mp4` (7:10)

**Title:** What Is an AI Agent? Course Roadmap + Python Setup | AI Agents with Python 2026 #1

**Description:**
```text
Start here! What an AI agent really is (decide → act → observe → repeat), how this 18-module course takes you from Python basics to a deployed AI agent app, and a clean Python setup with virtual environments.

In this lesson:
• What makes a program an "agent": the model decides, your Python code acts
• The 6-part roadmap: foundations, agents from scratch, RAG & MCP, LangGraph & multi-agent, testing & security, FastAPI & Docker
• Preview of the Module 1 project: the Python AI Toolkit
• Python 3.11+, venv, activation on macOS/Linux/Windows, pip install with pinned versions, pip freeze
• The project layout we will grow into

Chapters
00:00 Welcome
00:25 What is an AI agent?
01:19 The course roadmap
02:19 How every module works
02:50 Module 1 goals
03:30 Project preview
04:07 Prerequisites
04:35 Setup with a virtual environment
06:08 Project layout
06:45 Recap

Next: Lesson 2, the data every AI app is made of.
Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-01-python-ai-engineering
Docs: https://docs.python.org/3/library/venv.html

#Python #AIAgents #AIEngineering #PythonTutorial #LLM
```
**Tags:** ai agents, ai agents python, what is an ai agent, python for ai, python virtual environment, venv tutorial, ai engineering course, python tutorial 2026

**Thumbnail prompt:** …style above… Badge "MODULE 01 · LESSON 1". Headline on two lines: "WHAT IS AN" (white) / "AI AGENT?" with "AI AGENT?" in teal. Amber subtitle: "+ Python setup". On the right, the agent loop ring labelled with four small words: "Think", "Act", "Observe", "Repeat".

---

## Lesson 2: `renders/lesson-02.mp4` (7:20)

**Title:** Python Lists, Dictionaries & Sets for AI (Chat Messages as Data) | AI Agents with Python #2

**Description:**
```text
The data every AI application is built from: variables, f-strings, lists, dictionaries, sets and comprehensions, using the exact shapes LLM APIs use. A chat conversation is just a list of {"role", "content"} dictionaries!

In this lesson:
• str, int, float, bool, None and type()
• f-strings and number formatting
• Lists: indexes, slices, append, enumerate
• Dictionaries: keys, .get() with defaults, KeyError
• Sets: unique tags and tool allowlists
• List and dict comprehensions
• Which structure to choose, plus a quick quiz

Chapters
00:00 Introduction
00:41 Variables and types
02:20 Lists
03:10 Dictionaries
04:28 Sets
05:15 Comprehensions
05:59 Choosing a structure
06:30 Quick check
06:50 Recap

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-01-python-ai-engineering
Docs: https://docs.python.org/3/tutorial/datastructures.html

#Python #AIAgents #PythonTutorial #PythonForBeginners #LLM
```
**Tags:** python lists, python dictionary, python sets, f-strings, list comprehension, python for ai, python data structures, chat messages python

**Thumbnail prompt:** …style above… Badge "MODULE 01 · LESSON 2". Headline: "PYTHON DATA" (white) / "FOR AI" (teal). Amber subtitle: "lists · dicts · sets". On the right, a small dark code card showing: {"role": "user", "content": "Hi"}

---

## Lesson 3: `renders/lesson-03.mp4` (8:25)

**Title:** Python Functions, Classes & Exceptions (+ the Bug That Leaks User Data) | AI Agents with Python #3

**Description:**
```text
Organise your logic, model your data, and fail on purpose instead of by accident.

In this lesson:
• Functions: parameters, defaults, keyword arguments, return values
• The mutable default argument bug, and why it can leak one user's chat into another's
• Classes, objects, __init__, self and methods
• Dataclasses with field(default_factory=...)
• try / except / else / finally
• Custom exceptions (a budget limit for agents)
• Never use a bare except
• How to read a traceback from the bottom up

Chapters
00:00 Introduction
00:41 Functions
02:13 The mutable default bug
02:55 Classes
04:19 Dataclasses
05:10 Exceptions
06:01 Raising your own errors
07:06 Reading a traceback
07:35 Quick check
07:57 Recap

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-01-python-ai-engineering
Docs: https://docs.python.org/3/library/dataclasses.html

#Python #AIAgents #PythonTutorial #OOP #LLM
```
**Tags:** python functions, python classes, python dataclass, python exceptions, mutable default argument, python traceback, python oop tutorial, python for ai

**Thumbnail prompt:** …style above… Badge "MODULE 01 · LESSON 3". Headline: "FUNCTIONS," (white) / "CLASSES," (white) / "EXCEPTIONS" (teal). Amber subtitle: "the bug that leaks data". Small coral-red warning triangle icon near the subtitle.

---

## Lesson 4: `renders/lesson-04.mp4` (7:31)

**Title:** Python Modules, Files, JSON & API Keys in .env (Done Right) | AI Agents with Python #4

**Description:**
```text
Real AI projects are never one file. Split code into packages, read and write files, exchange JSON, and keep API keys out of your code.

In this lesson:
• Modules vs packages, __init__.py, imports, if __name__ == "__main__"
• Fixing ModuleNotFoundError
• pathlib: read, write, append, and why encoding="utf-8" matters
• JSON ↔ Python, json.dumps / json.loads, JSONDecodeError
• Environment variables with os.environ.get
• .env, .env.example and .gitignore: never commit secrets

Chapters
00:00 Introduction
00:34 Modules and packages
02:37 Files with pathlib
03:34 JSON
04:58 Environment variables
06:41 Quick check
07:01 Recap

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-01-python-ai-engineering
Docs: https://docs.python.org/3/library/json.html · https://docs.python.org/3/library/pathlib.html

#Python #AIAgents #PythonTutorial #JSON #LLM
```
**Tags:** python json, python modules and packages, pathlib, environment variables python, .env file, api key security, python files, python for ai

**Thumbnail prompt:** …style above… Badge "MODULE 01 · LESSON 4". Headline: "JSON, FILES &" (white) / "SECRETS" (teal). Amber subtitle: "keep API keys safe". On the right, a small padlock icon and a dark card reading ".env" with the text "LLM_API_KEY=••••••".

---

## Lesson 5: `renders/lesson-05.mp4` (7:20)

**Title:** Python Async/Await + HTTP Requests with httpx (3s → 1s) | AI Agents with Python #5

**Description:**
```text
Every language model lives behind a web API. Learn type hints, HTTP requests with httpx, and async/await, and measure three calls dropping from 3 seconds to 1.

In this lesson:
• Type hints: list[float], dict[str, float], X | None, and checking them with mypy
• HTTP in one picture: request, response, status codes (incl. 429 rate limits)
• httpx.get with timeouts, raise_for_status(), .json()
• Why async? Most AI time is spent waiting
• async def, await, asyncio.gather, asyncio.run
• Concurrent HTTP with httpx.AsyncClient

Chapters
00:00 Introduction
00:40 Type hints
02:08 HTTP in one picture
03:22 Requests with httpx
04:25 Why async?
06:29 Quick check
06:50 Recap

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-01-python-ai-engineering
Docs: https://www.python-httpx.org · https://docs.python.org/3/library/asyncio.html

#Python #AsyncIO #AIAgents #PythonTutorial #LLM
```
**Tags:** python async await, asyncio tutorial, httpx, python http requests, type hints python, mypy, asyncio gather, python for ai

**Thumbnail prompt:** …style above… Badge "MODULE 01 · LESSON 5". Headline: "ASYNC" (teal) / "PYTHON" (white). Amber subtitle: "3 seconds → 1 second". On the right, two horizontal timeline bars: a long coral bar labelled "3.0s" above a short teal bar labelled "1.0s".

---

## Lesson 6: `renders/lesson-06.mp4` (8:27)

**Title:** Build a Python AI Toolkit CLI, Part 1: Data Model & Validation | AI Agents with Python #6

**Description:**
```text
Project time! We start building the Python AI Toolkit, a command-line tool that validates a JSON log of LLM API calls and reports tokens, cost and latency.

In this lesson:
• The brief and an architecture with one job per module
• The input: a JSON usage log (prompt vs completion tokens)
• errors.py: a clean exception hierarchy
• models.py: a frozen dataclass, @property, a @classmethod constructor and full validation
• loader.py: collect problems instead of crashing
• config.py: settings from environment variables and a tiny .env loader
• stats.py: Counter, setdefault and a one-pass summary

Chapters
00:00 Introduction
00:17 What we are building
01:05 Architecture
01:49 The data
02:31 Errors first
02:52 The data model
05:10 Loading files
05:49 Configuration
06:33 Statistics
07:37 First results
08:02 Recap

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-01-python-ai-engineering/project/python-ai-toolkit

#Python #PythonProject #AIAgents #AIEngineering #LLM
```
**Tags:** python project, python cli project, data validation python, python dataclass project, llm token cost, ai engineering project, python for ai

**Thumbnail prompt:** …style above… Badge "MODULE 01 · LESSON 6". Headline: "BUILD AN" (white) / "AI TOOLKIT" (teal). Amber subtitle: "Part 1 · Python project". On the right, a dark terminal card with red lines: "x record 2: prompt_tokens must be ≥ 0" and a final white line "1 valid, 4 invalid".

---

## Lesson 7: `renders/lesson-07.mp4` (10:42)

**Title:** Build a Python AI Toolkit CLI, Part 2: argparse, Tests & Demo | AI Agents with Python #7

**Description:**
```text
We finish the Python AI Toolkit: Markdown/JSON reports, concurrent downloads, an argparse CLI with proper exit codes, a full demo, 42 pytest tests, troubleshooting, and the Module 1 quiz.

In this lesson:
• report.py: Markdown for people, JSON for programs
• fetch.py: async downloads with clear errors and an injectable transport
• cli.py: argparse sub-commands, exit codes, stderr, a dispatch dictionary
• Full demo, including failures
• pytest: fixtures, parametrize, httpx.MockTransport (no network)
• mypy, common errors and fixes
• Module recap, 5-question quiz, extension challenge

Chapters
00:00 Introduction
00:15 Writing reports
01:14 Downloading logs
01:53 The command line
03:32 Demo
05:10 Testing
06:33 Troubleshooting
07:32 Module recap
08:00 Module quiz
09:35 Extension challenge
10:03 Documentation
10:17 Next up

Next: Module 2, LLM fundamentals and API integration.
Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-01-python-ai-engineering/project/python-ai-toolkit
Docs: https://docs.python.org/3/library/argparse.html · https://docs.pytest.org

#Python #Pytest #AIAgents #PythonProject #LLM
```
**Tags:** python argparse, pytest tutorial, python cli tool, httpx mock, python testing, python project tutorial, ai engineering, python for ai

**Thumbnail prompt:** …style above… Badge "MODULE 01 · LESSON 7". Headline: "SHIP IT:" (white) / "CLI + TESTS" (teal). Amber subtitle: "Part 2 · 42 tests passing". On the right, a dark terminal card with the green line "42 passed in 0.11s".
