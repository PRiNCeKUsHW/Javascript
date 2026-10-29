import argparse
import sys
from pathlib import Path

from study import __version__
from study.assistant import Answer, ChatSession, StudyAssistant
from study.client import make_client
from study.config import load_settings
from study.errors import StudyError
from study.models import Quiz
from study.pricing import CostTracker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="study", description="An AI study assistant.")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("--offline", action="store_true",
                        help="use the built-in fake API (no key needed)")
    commands = parser.add_subparsers(dest="command", required=True)

    explain = commands.add_parser("explain", help="explain a concept")
    explain.add_argument("topic")
    explain.add_argument("--level", default="beginner",
                         choices=["beginner", "intermediate", "advanced"])
    explain.add_argument("--max-tokens", type=int, default=2000)

    quiz = commands.add_parser("quiz", help="generate a quiz")
    quiz.add_argument("topic")
    quiz.add_argument("--count", type=int, default=5)
    quiz.add_argument("--out", type=Path, help="save the quiz as JSON")
    quiz.add_argument("--answers", help="grade answers, e.g. A,C,B")

    commands.add_parser("chat", help="chat; one message per line (stdin)")

    tokens = commands.add_parser("tokens", help="count the tokens in text")
    tokens.add_argument("text")
    return parser


def footer(answer: Answer, model: str) -> str:
    return (f"[{model} · {answer.input_tokens} in / {answer.output_tokens} out"
            f" tokens · ${answer.cost_usd:.5f} · stop: {answer.stop_reason}]")


def grade(quiz: Quiz, answers: str) -> int:
    letters = [a.strip().upper() for a in answers.split(",")]
    score = 0
    for number, (q, letter) in enumerate(zip(quiz.questions, letters), 1):
        correct = "ABCD"[q.answer_index]
        ok = letter == correct
        score += ok
        print(f"Q{number}: {'correct' if ok else f'wrong, answer {correct}'}")
    print(f"Score: {score}/{len(quiz.questions)}")
    return score


def run(args: argparse.Namespace, assistant: StudyAssistant,
        offline: bool = False) -> int:
    model = assistant.model
    if args.command == "explain":
        answer = assistant.explain(
            args.topic, args.level, args.max_tokens,
            on_text=lambda t: print(t, end="", flush=True))
        print()
        if answer.truncated:
            print("warning: the answer was cut off at --max-tokens",
                  file=sys.stderr)
        print(footer(answer, model), file=sys.stderr)
    elif args.command == "quiz":
        quiz, answer = assistant.make_quiz(args.topic, args.count)
        for number, q in enumerate(quiz.questions, 1):
            print(f"Q{number}. {q.question}")
            for letter, option in zip("ABCD", q.options):
                print(f"   {letter}) {option}")
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(quiz.model_dump_json(indent=2) + "\n",
                                encoding="utf-8")
            print(f"saved to {args.out.as_posix()}")
        if args.answers:
            grade(quiz, args.answers)
        print(footer(answer, model), file=sys.stderr)
    elif args.command == "chat":
        session = ChatSession(assistant)
        for line in sys.stdin:
            if not line.strip() or line.strip() == "exit":
                break
            answer = session.send(line.strip())
            print(f"you> {line.strip()}\nbot> {answer.text}")
            print(footer(answer, model), file=sys.stderr)
    elif args.command == "tokens":
        note = " (offline estimate)" if offline else ""
        print(f"{assistant.count_tokens(args.text)} input tokens{note}")
    spent = assistant.tracker.spent_usd
    print(f"session cost: ${spent:.5f} of ${assistant.tracker.budget_usd:.2f}"
          " budget", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings(force_offline=args.offline)
    assistant = StudyAssistant(make_client(settings), settings.model,
                               CostTracker(settings.budget_usd))
    try:
        return run(args, assistant, settings.offline)
    except StudyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
