import argparse
import json
import sys

from calc_agent import __version__
from calc_agent.agent import CalculatorAgent, Result, Step
from calc_agent.client import make_client
from calc_agent.config import Settings, load_settings
from calc_agent.errors import AgentError, ToolError
from calc_agent.pricing import CostTracker
from calc_agent.tools import TOOLS, calculate

STOP_MESSAGES = {
    "max_steps": "stopped after {turns} turns without an answer "
                 "(raise --max-steps if the task really needs more)",
    "refused": "the model declined this request",
    "cut_off": "the reply was cut off at max_tokens",
    "budget": "the budget is used up; raise CALC_BUDGET_USD",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="calc_agent", description="A calculator agent.")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("--offline", action="store_true",
                        help="use the built-in fake API (no key needed)")
    commands = parser.add_subparsers(dest="command", required=True)

    ask = commands.add_parser("ask", help="ask the agent a question")
    ask.add_argument("question")
    ask.add_argument("--max-steps", type=int, default=None)
    ask.add_argument("--quiet", action="store_true", help="hide the trace")

    calc = commands.add_parser("calc", help="run the calculator tool directly")
    calc.add_argument("expression")

    commands.add_parser("tools", help="show the tool definitions")
    return parser


def show_step(step: Step) -> None:
    args = ", ".join(f"{k}={v!r}" for k, v in step.input.items())
    mark = "!" if step.is_error else "="
    print(f"  act      {step.tool}({args})")
    print(f"  observe  {mark} {step.output}")


def ask(args: argparse.Namespace, settings: Settings) -> int:
    steps = args.max_steps or settings.max_steps
    agent = CalculatorAgent(make_client(settings), settings.model,
                            CostTracker(settings.budget_usd), steps)
    result: Result = agent.run(args.question,
                               on_step=None if args.quiet else show_step)
    print(f"[{result.turns} turns · {len(result.steps)} tool calls · "
          f"${result.cost_usd:.4f}]", file=sys.stderr)
    if not result.ok:
        message = STOP_MESSAGES[result.stop].format(turns=result.turns)
        raise AgentError(message)
    print(f"answer: {result.answer}")
    return 0


def run(args: argparse.Namespace, settings: Settings) -> int:
    if args.command == "tools":
        print(json.dumps(TOOLS, indent=2))
        return 0
    if args.command == "calc":
        try:
            print(calculate(args.expression))
        except ToolError as exc:
            raise AgentError(str(exc)) from None
        return 0
    return ask(args, settings)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings(force_offline=args.offline)
    try:
        return run(args, settings)
    except AgentError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
