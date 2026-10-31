# Module 5 YouTube packaging

Thumbnail: `assets/thumbnail-module-05.png` (1280×720). Captions: `captions/lesson-NN.srt`, `captions/module-05-full.srt`.

Source-code links point at `https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course`; adjust the branch if the course is not merged into `main`.

## Full module video (`renders/module-05-full.mp4`)

**Title**

AI Agents with Python 2026 · Module 5: Tool Calling and Function Execution (Full Module + Project)

**Description**

```text
Module 5 of "AI Agents with Python: Beginner to Production (2026)": Tool Calling and Function Execution.

Project: Personal Productivity Agent, an agent that manages tasks and notes with six tools in a registry, schemas generated from Pydantic, input validation, per-tool timeouts, read/write/danger permissions with human approval for deletes, parallel tool calls, and 43 tests.

Prerequisites: Module 4 (AI Agent Architecture), or equivalent. An Anthropic API key is optional: every demo also runs offline with a built-in scripted fake API (not a model). You need Python 3.11+ and a code editor.

Every lesson explains the concept, shows real code with real output, covers common errors, and ends with a quick check. The module closes with a recap, a 5-question quiz and an extension challenge.

Source code + README: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-05-tool-calling

Chapters
00:00 L1 Tool Calling: How a Model Uses Your Functions
00:42 What is a tool?
01:39 One tool call, step by step
03:56 Anatomy of a definition
04:22 Writing good descriptions
04:58 Pause and try
05:34 Interview corner
06:32 Quick check
06:51 Recap
07:28 L2 Many Tools: A Registry, Schemas from Pydantic, Parallel Calls
08:07 A tool registry
10:08 Schemas from Pydantic
11:56 Parallel tool calls
13:25 Pause and try
14:04 Interview corner
14:56 Quick check
15:17 Recap
15:48 L3 Validating Tool Inputs: Never Trust, Always Check
16:31 Why validate?
17:13 What strict mode covers
17:46 Validation in code
20:09 Pause and try
20:57 Interview corner
21:51 Quick check
22:11 Recap
22:44 L4 Timeouts and Failures: When a Tool Never Answers
23:18 Why timeouts?
23:54 A timeout in code
26:03 In the real agent
26:22 Limits of thread timeouts
27:04 Pause and try
27:54 Interview corner
28:48 Quick check
29:10 Recap
29:40 L5 Permissions and Human Confirmation: Ask Before You Act
30:19 Least privilege
31:01 Three permission levels
31:30 The policy in code
33:24 In the real agent
33:54 Good confirmations
34:19 Pause and try
34:53 Interview corner
35:49 Quick check
36:13 Recap
36:43 L6 Project, Part 1: Personal Productivity Agent, Store, Tools and Policy
37:03 The brief
37:39 Architecture
38:09 An honest fake
38:48 A safe data store
39:51 The six tools
40:38 Wiring it together
41:31 First run
41:58 Pause and try
42:37 Recap
43:07 L7 Project, Part 2: The Loop, the Demo, Tests and Wrap-up
43:27 The agent loop
44:47 Demo
45:12 Safety on purpose
45:40 Testing
46:32 Troubleshooting
47:10 Interview corner
48:49 Module recap
49:19 Module quiz
50:56 Practice
51:42 Extension challenge
52:09 Documentation
52:24 Next up

Official docs: platform.claude.com/docs/en/agents-and-tools/tool-use/overview · platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use · platform.claude.com/docs/en/build-with-claude/structured-outputs

#AIAgents #Python #ClaudeAPI #ToolCalling #AIEngineering
```

**Search terms**: tool calling python, function calling claude, claude tool use tutorial, parallel tool calls, pydantic json schema, ai agent safety, human in the loop ai, tool input validation, ai agent permissions, productivity agent python

## Individual lesson videos (`renders/lesson-NN.mp4`)

### Lesson 1 (07:28)

**Title:** Tool Calling: How a Model Uses Your Functions | AI Agents with Python, Module 5 Lesson 1

```text
Lesson 1 of Module 5 (Tool Calling and Function Execution) in "AI Agents with Python: Beginner to Production (2026)".

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-05-tool-calling

00:00 Introduction
00:42 What is a tool?
01:39 One tool call, step by step
03:56 Anatomy of a definition
04:22 Writing good descriptions
04:58 Pause and try
05:34 Interview corner
06:32 Quick check
06:51 Recap

#AIAgents #Python #ClaudeAPI #ToolCalling #AIEngineering
```

### Lesson 2 (08:20)

**Title:** Many Tools: A Registry, Schemas from Pydantic, Parallel Calls | AI Agents with Python, Module 5 Lesson 2

```text
Lesson 2 of Module 5 (Tool Calling and Function Execution) in "AI Agents with Python: Beginner to Production (2026)".

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-05-tool-calling

00:00 Introduction
00:39 A tool registry
02:39 Schemas from Pydantic
04:27 Parallel tool calls
05:56 Pause and try
06:35 Interview corner
07:28 Quick check
07:48 Recap

#AIAgents #Python #ClaudeAPI #ToolCalling #AIEngineering
```

### Lesson 3 (06:55)

**Title:** Validating Tool Inputs: Never Trust, Always Check | AI Agents with Python, Module 5 Lesson 3

```text
Lesson 3 of Module 5 (Tool Calling and Function Execution) in "AI Agents with Python: Beginner to Production (2026)".

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-05-tool-calling

00:00 Introduction
00:42 Why validate?
01:24 What strict mode covers
01:57 Validation in code
04:20 Pause and try
05:09 Interview corner
06:02 Quick check
06:23 Recap

#AIAgents #Python #ClaudeAPI #ToolCalling #AIEngineering
```

### Lesson 4 (06:56)

**Title:** Timeouts and Failures: When a Tool Never Answers | AI Agents with Python, Module 5 Lesson 4

```text
Lesson 4 of Module 5 (Tool Calling and Function Execution) in "AI Agents with Python: Beginner to Production (2026)".

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-05-tool-calling

00:00 Introduction
00:33 Why timeouts?
01:09 A timeout in code
03:19 In the real agent
03:37 Limits of thread timeouts
04:19 Pause and try
05:10 Interview corner
06:04 Quick check
06:25 Recap

#AIAgents #Python #ClaudeAPI #ToolCalling #AIEngineering
```

### Lesson 5 (07:02)

**Title:** Permissions and Human Confirmation: Ask Before You Act | AI Agents with Python, Module 5 Lesson 5

```text
Lesson 5 of Module 5 (Tool Calling and Function Execution) in "AI Agents with Python: Beginner to Production (2026)".

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-05-tool-calling

00:00 Introduction
00:38 Least privilege
01:21 Three permission levels
01:49 The policy in code
03:44 In the real agent
04:13 Good confirmations
04:38 Pause and try
05:12 Interview corner
06:08 Quick check
06:32 Recap

#AIAgents #Python #ClaudeAPI #ToolCalling #AIEngineering
```

### Lesson 6 (06:23)

**Title:** Project, Part 1: Personal Productivity Agent, Store, Tools and Policy | AI Agents with Python, Module 5 Lesson 6

```text
Lesson 6 of Module 5 (Tool Calling and Function Execution) in "AI Agents with Python: Beginner to Production (2026)".

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-05-tool-calling

00:00 Introduction
00:20 The brief
00:55 Architecture
01:25 An honest fake
02:05 A safe data store
03:08 The six tools
03:54 Wiring it together
04:47 First run
05:14 Pause and try
05:54 Recap

#AIAgents #Python #ClaudeAPI #ToolCalling #AIEngineering
```

### Lesson 7 (09:39)

**Title:** Project, Part 2: The Loop, the Demo, Tests and Wrap-up | AI Agents with Python, Module 5 Lesson 7

```text
Lesson 7 of Module 5 (Tool Calling and Function Execution) in "AI Agents with Python: Beginner to Production (2026)".

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-05-tool-calling

00:00 Introduction
00:19 The agent loop
01:40 Demo
02:05 Safety on purpose
02:33 Testing
03:24 Troubleshooting
04:02 Interview corner
05:42 Module recap
06:12 Module quiz
07:48 Practice
08:35 Extension challenge
09:02 Documentation
09:17 Next up

#AIAgents #Python #ClaudeAPI #ToolCalling #AIEngineering
```
