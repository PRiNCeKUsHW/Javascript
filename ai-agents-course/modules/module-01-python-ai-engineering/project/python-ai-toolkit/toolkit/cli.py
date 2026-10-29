import argparse
import asyncio
import sys
from pathlib import Path

from toolkit import __version__
from toolkit.config import load_prices, load_settings
from toolkit.errors import ToolkitError
from toolkit.fetch import fetch_all, save_json
from toolkit.loader import load_records
from toolkit.report import render_json, render_markdown
from toolkit.stats import summarize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="toolkit", description="Validate and report on LLM usage logs.")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="check every record")
    validate.add_argument("file", type=Path)

    report = commands.add_parser("report", help="summarize a usage file")
    report.add_argument("file", type=Path)
    report.add_argument("--format", choices=["md", "json"], default="md")
    report.add_argument("--out", type=Path, help="write to this file")
    report.add_argument("--strict", action="store_true",
                        help="fail if any record is invalid")

    fetch = commands.add_parser("fetch", help="download and merge files")
    fetch.add_argument("urls", nargs="+")
    fetch.add_argument("--out", type=Path, required=True)
    return parser


def cmd_validate(args: argparse.Namespace) -> int:
    records, problems = load_records(args.file)
    for problem in problems:
        print(f"  x {problem}")
    print(f"{len(records)} valid, {len(problems)} invalid")
    return 1 if problems else 0


def cmd_report(args: argparse.Namespace) -> int:
    settings = load_settings()
    records, problems = load_records(args.file)
    if problems:
        print(f"warning: skipped {len(problems)} invalid record(s); "
              "run 'validate' for details", file=sys.stderr)
        if args.strict:
            return 1
    summary = summarize(records, load_prices(settings.prices_file))
    render = render_json if args.format == "json" else render_markdown
    text = render(summary, args.file.as_posix(), settings.currency)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"report written to {args.out.as_posix()}")
    else:
        print(text, end="")
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    data = asyncio.run(fetch_all(args.urls))
    save_json(data, args.out)
    print(f"saved {len(data)} records from {len(args.urls)} URL(s) "
          f"to {args.out.as_posix()}")
    return 0


COMMANDS = {"validate": cmd_validate, "report": cmd_report, "fetch": cmd_fetch}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.command](args)
    except ToolkitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
