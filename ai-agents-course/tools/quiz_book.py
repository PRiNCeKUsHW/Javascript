"""Build a GitHub question bank from the questions asked in the videos.

Usage:  python tools/quiz_book.py          (all modules with scripts)

For every module it reads scripts/lesson-XX.yaml and writes QUESTIONS.md with, per lesson:
quick checks (multiple choice), interview questions, pause-and-try and practice questions.
Answers sit in collapsible <details> blocks, so readers try first and reveal after.
Answers to practice questions whose narration doesn't contain them (Hinglish narration,
or "answers are in quiz.md") come from the module's quiz.md. It also writes QUESTION_BANK.md.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LETTERS = "ABCDEFGH"


def reveal(body: str, label: str = "Show answer") -> list[str]:
    return ["<details>", f"<summary>{label}</summary>", "", body.strip(), "", "</details>", ""]


def practice_answers(quiz_md: str) -> dict[int, list[str]]:
    """Answers from quiz.md: '### Lesson N' blocks or a '## Practice questions (lesson N)' block."""
    out: dict[int, list[str]] = {}
    pattern = r"^#{2,3} (?:Lesson (\d+)\b.*|Practice questions \(lesson (\d+)\))$"
    parts = re.split(pattern, quiz_md, flags=re.M)
    for i in range(1, len(parts), 3):
        n = int(parts[i] or parts[i + 1])
        body = re.split(r"^## ", parts[i + 2], flags=re.M)[0].strip()
        items = re.split(r"^\d+\. ", body, flags=re.M)
        items = [re.sub(r"\n   ", "\n", x).strip() for x in items if x.strip()]
        items = items if len(items) > 1 or re.match(r"^\d+\. ", body) else [body]
        # drop the bold restatement of the question ("**Required arguments?** ...")
        out[n] = [re.sub(r"^\*\*[^*]+\*\*:?\s+", "", x, count=1) for x in items]
    return out


def usable_outro(scene: dict, narration: str) -> str | None:
    outro = (scene.get("outro") or "").strip()
    if not outro or narration == "hinglish" or "quiz dot md" in outro or "quiz.md" in outro:
        return None
    return outro


def lesson_block(n: int, data: dict, answers: dict[int, list[str]]) -> tuple[list[str], int]:
    narration = data.get("narration", "english")
    lines: list[str] = []
    count = 0
    quizzes = [s for s in data["scenes"] if s["type"] == "quiz"]
    interviews = [i for s in data["scenes"] if s["type"] == "interview" for i in s["items"]]
    tries = [s for s in data["scenes"] if s["type"] == "callout"
             and s.get("kind") in ("try", "practice", "scenario")]
    if not (quizzes or interviews or tries):
        return [], 0
    lines += [f"## Lesson {n}: {data['title']}", ""]

    if quizzes:
        lines += ["### Quick check" if len(quizzes) == 1 else "### Module quiz", ""]
        for q in quizzes:
            count += 1
            num = f"Q{q['number']}. " if len(quizzes) > 1 else ""
            lines += [f"**{num}{q['question']}**", ""]
            if q.get("code"):
                lines += ["```python", q["code"].rstrip(), "```", ""]
            lines += [f"- {LETTERS[i]}) {opt}" for i, opt in enumerate(q["options"])] + [""]
            lines += reveal(f"**{LETTERS[q['answer']]}) {q['options'][q['answer']]}**\n\n{q['explain']}")

    for s in tries:
        title = s.get("title", "Practice")
        lines += [f"### {title}", ""]
        if s.get("body"):
            body = s["body"].replace("Answers are in the module's quiz.md.", "").strip()
            if body:
                lines += [body, ""]
        items = [i["text"] if isinstance(i, dict) else i for i in s.get("items", [])]
        outro = usable_outro(s, narration)
        bank = answers.get(n, [])
        if outro:
            count += len(items)
            lines += [f"{k}. {t}" for k, t in enumerate(items, 1)] + [""]
            lines += reveal(outro, "Show answer" if len(items) == 1 else "Show answers")
        else:
            for k, t in enumerate(items, 1):
                count += 1
                lines += [f"**{k}. {t}**", ""]
                if len(bank) == len(items):
                    lines += reveal(bank[k - 1])
                elif k == len(items) and bank:
                    lines += reveal("\n\n".join(bank))
            if not bank:
                lines += ["_Answers: see [quiz.md](quiz.md)._", ""]

    if interviews:
        lines += ["### Interview corner", ""]
        for it in interviews:
            count += 1
            lines += [f"**Interviewer:** {it['q']}", ""]
            body = f"**A good answer:** {it['a']}"
            if it.get("trap"):
                body += f"\n\n**Trap to avoid:** {it['trap']}"
            lines += reveal(body)
    return lines, count


def build_module(mdir: Path) -> tuple[str, int, str]:
    scripts = sorted((mdir / "scripts").glob("lesson-*.yaml"))
    lessons = [yaml.safe_load(p.read_text()) for p in scripts]
    num = int(mdir.name.split("-")[1])
    title = lessons[0]["module_title"]
    quiz_md = (mdir / "quiz.md").read_text() if (mdir / "quiz.md").exists() else ""
    answers = practice_answers(quiz_md)
    body: list[str] = []
    total = 0
    for p, data in zip(scripts, lessons):
        block, c = lesson_block(int(p.stem.split("-")[1]), data, answers)
        body += block
        total += c
    hinglish = any(d.get("narration") == "hinglish" for d in lessons)
    head = [
        f"# Module {num} question bank: {title}",
        "",
        f"Every question asked in the Module {num} videos, with answers. **{total} questions.**",
        "",
        "How to use it: read the question, answer it out loud or on paper, *then* click "
        "**Show answer**. Getting one wrong is useful: rewatch that lesson's chapter.",
        "",
    ]
    if hinglish:
        head += ["The videos are narrated in Hinglish; the questions here are the English "
                 "text shown on screen.", ""]
    head += [f"Short answer key, practice answers and the extension challenge: [quiz.md](quiz.md) · "
             f"Module guide: [README.md](README.md)", ""]
    (mdir / "QUESTIONS.md").write_text("\n".join(head + body).rstrip() + "\n")
    return title, total, mdir.name


def main() -> None:
    rows = []
    for mdir in sorted((ROOT / "modules").glob("module-*")):
        if (mdir / "scripts").is_dir():
            rows.append(build_module(mdir))
    grand = sum(r[1] for r in rows)
    lines = [
        "# Course question bank",
        "",
        f"Every question asked in the videos: quick checks, module quizzes, pause-and-try, practice "
        f"and interview questions, with collapsible answers. **{grand} questions so far.**",
        "",
        "| Module | Topic | Questions |",
        "|---|---|---|",
    ]
    for title, total, name in rows:
        n = int(name.split("-")[1])
        lines.append(f"| {n} | [{title}](modules/{name}/QUESTIONS.md) | {total} |")
    lines += ["", "Regenerate after editing a lesson script: `python tools/quiz_book.py`.", ""]
    (ROOT / "QUESTION_BANK.md").write_text("\n".join(lines))
    for r in rows:
        print(f"{r[2]}: {r[1]} questions")


if __name__ == "__main__":
    main()
