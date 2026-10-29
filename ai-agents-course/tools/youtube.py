"""Write modules/<module>/youtube.md: titles, descriptions, chapter timestamps and search terms.

Timestamps come from the built lesson timelines (identical to the rendered videos, which
`tools/module.py validate` checks to within half a second).

usage: python tools/youtube.py 1
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/PRiNCeKUsHW/ai-agents-python-2026/tree/main/ai-agents-course"

MODULES = {
    1: {
        "title": "Python for AI Engineering",
        "project": "Python AI Toolkit",
        "project_dir": "python-ai-toolkit",
        "project_blurb": "a command-line tool that validates a JSON log of LLM API calls and reports "
                         "requests, success rate, tokens, estimated cost, latency and top tags, as "
                         "Markdown or JSON, with concurrent downloads and 42 pytest tests.",
        "prereq": "No AI experience needed. Any programming experience helps, but every Python concept is explained.",
        "terms": ["python for ai", "python tutorial for beginners", "ai engineering", "ai agents python",
                  "python dataclasses", "python json", "httpx", "python async await", "pytest tutorial",
                  "python cli project"],
        "tags": "#Python #AIAgents #AIEngineering #PythonTutorial #LLM",
        "docs": "docs.python.org/3/tutorial · www.python-httpx.org · docs.pytest.org",
    },
    2: {
        "title": "LLM Fundamentals and API Integration",
        "project": "AI Study Assistant",
        "project_dir": "ai-study-assistant",
        "project_blurb": "a command-line tutor built on the Anthropic Python SDK that streams "
                         "explanations, writes quizzes as validated JSON, chats with trimmed history, "
                         "and tracks the cost of every call against a budget, with 23 tests.",
        "prereq": "Module 1 (Python for AI Engineering) or equivalent Python. An Anthropic API key is "
                  "optional: every demo also runs in an offline mode with a built-in fake API.",
        "terms": ["llm api python", "anthropic api tutorial", "claude api python", "tokens and context window",
                  "llm streaming python", "structured output json", "api rate limits retries",
                  "llm api cost", "ai study assistant project"],
        "tags": "#Python #LLM #ClaudeAPI #AIAgents #AIEngineering",
        "docs": "platform.claude.com/docs/en/build-with-claude/structured-outputs · "
                "platform.claude.com/docs/en/api/errors · platform.claude.com/docs/en/about-claude/pricing",
    },
    3: {
        "title": "Prompt Engineering and Structured Outputs",
        "project": "AI Resume Analyzer",
        "project_dir": "ai-resume-analyzer",
        "project_blurb": "a command-line tool that compares a resume with a job posting and writes a "
                         "skills-gap report, with versioned prompts, structured outputs validated by "
                         "Pydantic, a grounding check, an evaluation set and 27 tests.",
        "prereq": "Module 2 (LLM Fundamentals and API Integration) or equivalent. An Anthropic API key "
                  "is optional: every demo also runs offline with a built-in fake API (keyword rules, "
                  "not a model).",
        "terms": ["prompt engineering", "prompt engineering python", "structured output llm",
                  "pydantic llm", "llm json output", "prompt versioning", "llm evaluation",
                  "prompt injection", "ai resume analyzer", "claude api python"],
        "tags": "#PromptEngineering #Python #LLM #Pydantic #AIAgents",
        "docs": "platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices · "
                "platform.claude.com/docs/en/build-with-claude/structured-outputs · "
                "platform.claude.com/docs/en/test-and-evaluate/develop-tests",
    },
}


def stamp(t):
    t = int(t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def main(m):
    info = MODULES[m]
    mdir = next((ROOT / "modules").glob(f"module-{m:02d}-*"))
    lessons = sorted(int(p.stem.split("-")[1]) for p in (mdir / "scripts").glob("lesson-*.yaml"))
    datas = {n: json.loads((ROOT / f"studio/src/data/m{m:02d}-l{n:02d}.json").read_text()) for n in lessons}
    src = f"{REPO}/{mdir.relative_to(ROOT).as_posix()}"
    out = [f"# Module {m} YouTube packaging", "",
           f"Thumbnail: `assets/thumbnail-module-{m:02d}.png` (1280×720). Captions: `captions/lesson-NN.srt`, "
           f"`captions/module-{m:02d}-full.srt`.", "",
           f"Source-code links point at `{REPO}`; adjust the branch if the course is not merged into `main`.", ""]

    # full module video
    total, chapters = 0.0, []
    for n in lessons:
        d = datas[n]
        for c in d["chapters"]:
            chapters.append((total + c["t"], f"L{n} {d['title']}" if c["t"] == 0 else c["title"]))
        total += d["durationInFrames"] / d["fps"]
    yt, last = [], -99.0
    for t, title in chapters:
        if t - last >= 10:
            yt.append(f"{stamp(t)} {title}")
            last = t
    out += [f"## Full module video (`renders/module-{m:02d}-full.mp4`)", "",
            "**Title**", "", f"AI Agents with Python 2026 · Module {m}: {info['title']} (Full Module + Project)", "",
            "**Description**", "", "```text",
            f"Module {m} of \"AI Agents with Python: Beginner to Production (2026)\": {info['title']}.",
            "",
            f"Project: {info['project']}, {info['project_blurb']}",
            "",
            f"Prerequisites: {info['prereq']} You need Python 3.11+ and a code editor.",
            "",
            "Every lesson explains the concept, shows real code with real output, covers common errors, "
            "and ends with a quick check. The module closes with a recap, a 5-question quiz and an extension challenge.",
            "",
            f"Source code + README: {src}",
            "",
            "Chapters", *yt, "",
            f"Official docs: {info['docs']}",
            "", info["tags"], "```", "",
            "**Search terms**: " + ", ".join(info["terms"]), ""]

    # per-lesson videos
    out += ["## Individual lesson videos (`renders/lesson-NN.mp4`)", ""]
    for n in lessons:
        d = datas[n]
        dur = d["durationInFrames"] / d["fps"]
        lines, last = [], -99.0
        for c in d["chapters"]:
            if c["t"] - last >= 10:
                lines.append(f"{stamp(c['t'])} {c['title']}")
                last = c["t"]
        out += [f"### Lesson {n} ({stamp(dur)})", "",
                f"**Title:** {d['title']} | AI Agents with Python, Module {m} Lesson {n}", "",
                "```text",
                f"Lesson {n} of Module {m} ({info['title']}) in \"AI Agents with Python: Beginner to Production (2026)\".",
                "",
                f"Source code: {src}",
                "",
                *lines, "", info["tags"], "```", ""]
    (mdir / "youtube.md").write_text("\n".join(out), encoding="utf-8")
    print(f"youtube.md: full module {stamp(total)}, {len(yt)} chapters")


if __name__ == "__main__":
    main(int(sys.argv[1]))
