# Module 3 upload kit (one single video)

Playlist: **AI Agents with Python 2026: Beginner to Production** (video #15).
File: `renders/module-03-full.mp4` (30:32). Captions: upload `captions/module-03-full.srt` as English subtitles.

**Title:** Prompt Engineering in Python: Structured Outputs, Pydantic & Prompt Evals (Full Course) | AI Agents with Python #15

**Description:**
```text
Write prompts that work consistently, get validated JSON back, and prove a prompt change is an improvement. Then build an AI Resume Analyzer that turns a resume and a job posting into a skills-gap report.

In this video:
• Prompt anatomy: context, task, data, constraints, examples
• Why "CRITICAL / MUST", "think step by step" and "reply only in JSON" are outdated
• XML tags to separate data from instructions (and prompt injection)
• Task decomposition: the model for judgment, Python for everything deterministic
• Structured outputs with Pydantic: what's guaranteed, and what can still fail
• Grounding checks: validating meaning, not just shape
• Prompt versioning with fingerprints, and evaluations with labelled cases
• Project: AI Resume Analyzer with 27 tests

Note: no API key was used while recording. Model replies come from a built-in offline fake API (keyword rules, not a model), so the code runs for free; with ANTHROPIC_API_KEY the same code calls Claude.

Chapters
00:00 L1 Prompt Anatomy: Instructions, Context and Constraints
00:42 Prompt anatomy
01:21 Be specific
02:29 Constraints with reasons
03:05 Outdated advice
04:16 Quick check
04:36 Recap
05:00 L2 Examples, XML Tags and Task Decomposition
05:36 Tags separate data
06:21 Prompt injection
06:50 Examples
07:23 Task decomposition
08:34 Reusable prompts
09:04 Quick check
09:23 Recap
09:46 L3 Structured Outputs: Pydantic Schemas and Parsing Failures
10:21 Schemas with Pydantic
11:11 What is guaranteed
11:46 Validation errors
12:09 Handling parse failures
12:49 Check meaning, not just shape
13:33 Quick check
13:52 Recap
14:19 L4 Prompt Versioning and Evaluations
14:53 Why version prompts?
15:17 Versions and fingerprints
16:36 Evaluations
18:57 Quick check
19:15 Recap
19:39 L5 Project, Part 1: AI Resume Analyzer, Extraction and Comparison
19:58 The brief
20:24 Architecture
20:55 An honest fake
21:32 The report data
21:58 Comparing in code
22:34 The pipeline
23:09 First run
23:40 Recap
24:02 L6 Project, Part 2: Reports, Demo, Tests and Wrap-up
24:18 The report
24:51 The command line
25:12 Demo
26:03 Testing
26:50 Troubleshooting
27:21 Module recap
27:46 Module quiz
29:23 Extension challenge
29:54 Documentation
30:11 Next up

Source code: https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course/modules/module-03-prompt-engineering
Docs: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

#PromptEngineering #Python #LLM #Pydantic #AIAgents
```
**Tags:** prompt engineering, prompt engineering python, structured output llm, pydantic llm, llm json output, prompt versioning, llm evaluation, prompt injection, ai resume analyzer, claude api python, ai agents python

**Thumbnail prompt:** YouTube thumbnail, 16:9, 1280x720. Dark navy-black background (#0A0E17) with a faint dot grid and a soft teal glow on the right. Clean modern developer style, flat vector, no photos, no people, no real company logos. Huge bold white sans-serif headline, one part in bright teal (#2EE6A8), a short amber (#FFB547) subtitle below. Small teal pill badge at top-left reading "MODULE 03 · FULL COURSE". High contrast, readable on a phone, at most 6 words of large text. Spell every word exactly as given. Headline: "PROMPTS THAT" (white) / "WORK" (teal). Amber subtitle: "Pydantic · JSON · evals". On the right, a dark terminal card with a teal line "$ python -m resume eval" and below it "total 21/22 (95%)", plus a small green check mark.

(A ready-made thumbnail is also in `assets/thumbnail-module-03.png`.)
