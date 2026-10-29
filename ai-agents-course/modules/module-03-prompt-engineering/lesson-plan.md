# Module 3 lesson plan: Prompt Engineering and Structured Outputs

Audience: learners who finished Module 2. Target level: write prompts that behave consistently,
get validated structured data back, split work between the model and code, version prompts and
measure changes with an evaluation set, in a tested program.

Delivery: **one full-module video** (the six lessons below joined, with YouTube chapters).

Provider: Anthropic Claude via the official Python SDK (`anthropic==2.3.0`), default model
`claude-opus-5-5`. Prompting guidance follows the current Claude prompting best practices:
context and reasons instead of emphasis ("CRITICAL/MUST"), `effort` instead of "think step by step",
structured outputs instead of "reply only in JSON" + regex, no assistant prefill (rejected with a 400
on current models), no `reasoning` field in JSON output, arithmetic and matching in code.

**Honesty rule for demos:** no API key was available while recording. Model replies on screen come
from the project's offline fake API (`resume/fake_api.py`), which fills the requested schema with
keyword rules. It is **not a model**: it ignores prompt wording and misses negation. The narration
says so (lessons 3-6), and the eval demo states that offline scores cannot compare prompt versions.
Lessons 1-3 also use scripts that need no model at all (prompt rendering, Pydantic validation).

| # | Lesson | Concepts | Runnable source |
|---|---|---|---|
| 1 | Prompt anatomy | context, task, data, constraints, examples; vague vs specific (project v1 vs v2); context and reasons beat bare rules; plain language instead of shouting; outdated advice (step-by-step, JSON-only + regex, prefill, reasoning fields); cost of a longer prompt | `source/lesson-01/` |
| 2 | Examples, tags, decomposition | data in XML tags + "data, not instructions"; prompt-injection text stays inside tags (not a guarantee); varied, labelled examples; splitting extract (model) / compare (code) / advise (model); model for judgment, code for deterministic work; prompts as frozen, versioned templates | `source/lesson-02/` |
| 3 | Structured outputs | Pydantic schemas (Field limits, descriptions, no reasoning field); what's guaranteed (shape), SDK-validated (limits), not guaranteed (truth); ValidationError types; `beta.messages.parse` wrapper; cut-off, invalid, refused, invented replies; grounding check | `source/lesson-03/`, project |
| 4 | Versioning and evals | trace/compare/roll back; registry + defaults; fingerprints (sha256 prefix); lock file + test; safe change routine; eval = cases + code grader + score; hard cases (negation); offline scores test the pipeline only; eval habits | project |
| 5 | Project part 1 | brief, architecture, honest fake, GapReport (score in code), aliases/normalisation, compare(), pipeline with effort levels and skipped advice call, first run | `project/ai-resume-analyzer/` |
| 6 | Project part 2 | Markdown/JSON report with prompt fingerprints, CLI, demo (JSON, v1, fake's negation miss, retries, refusal, missing file), tests, mypy, troubleshooting, module recap, 5-question quiz, challenge, docs | `project/ai-resume-analyzer/` |
