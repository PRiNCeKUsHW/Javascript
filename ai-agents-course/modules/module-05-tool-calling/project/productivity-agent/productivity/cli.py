import argparse
import json
import sys

from productivity import __version__
from productivity.agent import ProductivityAgent, Result, Step
from productivity.client import make_client
from productivity.config import Settings, load_settings
from productivity.errors import AgentError
from productivity.policy import Policy
from productivity.pricing import CostTracker
from productivity.store import Store
from productivity.tools import REGISTRY, Context, definitions, describe

STOP_MESSAGES = {
    "max_steps": "stopped after {turns} turns without an answer "
                 "(raise --max-steps if the task really needs more)",
    "refused": "the model declined this request",
    "cut_off": "the reply was cut off at max_tokens",
    "budget": "the budget is used up; raise PROD_BUDGET_USD",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="productivity", description="A personal productivity agent.")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("--offline", action="store_true",
                        help="use the built-in fake API (no key needed)")
    commands = parser.add_subparsers(dest="command", required=True)

    ask = commands.add_parser("ask", help="ask the agent to do something")
    ask.add_argument("request")
    ask.add_argument("--read-only", action="store_true",
                     help="allow only tools that read, never change")
    ask.add_argument("--yes", action="store_true",
                     help="approve dangerous actions without asking")
    ask.add_argument("--max-steps", type=int, default=None)

    commands.add_parser("tasks", help="show every task")
    commands.add_parser("notes", help="show every note")
    tools = commands.add_parser("tools", help="show the tools and their permissions")
    tools.add_argument("--json", action="store_true", help="print the API definitions")
    reset = commands.add_parser("reset", help="delete all tasks and notes")
    reset.add_argument("--yes", action="store_true", help="don't ask first")
    return parser


def plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def show_step(step: Step) -> None:
    args = ", ".join(f"{k}={v!r}" for k, v in step.input.items())
    mark = "!" if step.is_error else "="
    first, *rest = step.output.splitlines() or [""]
    print(f"  turn {step.turn}  act      {step.tool}({args})")
    print(f"          observe  {mark} {first}")
    for line in rest:                          # multi-line results stay aligned
        print(f"                     {line}")


def ask_human(question: str) -> bool:
    """Ask on the terminal. Piped input works too: printf 'y\\n' | ..."""
    print(f"  confirm  {question} [y/N] ", end="", flush=True)
    answer = sys.stdin.readline().strip().lower()
    if not sys.stdin.isatty():
        print(answer)                          # echo piped answers, like a terminal
    return answer in ("y", "yes")


def ask(args: argparse.Namespace, settings: Settings) -> int:
    ctx = Context(Store(settings.data_path), settings.today)
    policy = Policy(ctx, read_only=args.read_only,
                    ask_human=(lambda q: True) if args.yes else ask_human)
    agent = ProductivityAgent(make_client(settings), settings.model,
                              CostTracker(settings.budget_usd), ctx, policy,
                              args.max_steps or settings.max_steps)
    result: Result = agent.run(args.request, on_step=show_step)
    calls = len(result.steps)
    print(f"[{plural(result.turns, 'turn')} · {plural(calls, 'tool call')} · "
          f"${result.cost_usd:.5f}{' estimated' if settings.offline else ''}]",
          file=sys.stderr)
    if not result.ok:
        raise AgentError(STOP_MESSAGES[result.stop].format(turns=result.turns))
    print(result.answer)
    return 0


def run(args: argparse.Namespace, settings: Settings) -> int:
    store = Store(settings.data_path)
    if args.command == "ask":
        return ask(args, settings)
    if args.command == "tasks":
        tasks = store.tasks("all")
        print("\n".join(describe(t) for t in tasks) if tasks else "no tasks")
    elif args.command == "notes":
        notes = store.notes()
        print("\n".join(f"{n.id}. {n.title}: {n.text}" for n in notes) if notes else "no notes")
    elif args.command == "tools":
        if args.json:
            print(json.dumps(definitions(), indent=2))
        else:
            for t in REGISTRY.values():
                print(f"{t.name:<14} {t.permission:<6} timeout {t.timeout_s:g} s")
    elif args.command == "reset":
        if not (args.yes or ask_human(f"Delete every task and note in {settings.data_path}?")):
            raise AgentError("nothing was deleted")
        store.reset()
        print(f"empty store: {settings.data_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings(force_offline=args.offline)
    try:
        return run(args, settings)
    except AgentError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
