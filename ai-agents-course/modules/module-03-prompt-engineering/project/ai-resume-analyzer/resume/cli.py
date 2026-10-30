import argparse
import sys
from pathlib import Path

import anthropic

from resume import __version__
from resume.analyzer import Analyzer
from resume.client import make_client
from resume.config import Settings, load_settings
from resume.errors import AnalyzerError
from resume.evals import run_eval, summary
from resume.pricing import CostTracker
from resume.prompts import DEFAULT_VERSIONS, PROMPTS
from resume.report import to_json, to_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resume", description="Compare a resume with a job posting.")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("--offline", action="store_true",
                        help="use the built-in fake API (no key needed)")
    commands = parser.add_subparsers(dest="command", required=True)

    analyze = commands.add_parser("analyze", help="write a skills-gap report")
    analyze.add_argument("resume", type=Path)
    analyze.add_argument("job", type=Path)
    analyze.add_argument("--prompt", default=None,
                         help="extract_profile version, e.g. v1")
    analyze.add_argument("--format", choices=["md", "json"], default="md")
    analyze.add_argument("--out", type=Path, help="save the report")

    extract = commands.add_parser("extract", help="show the extracted profile")
    extract.add_argument("resume", type=Path)
    extract.add_argument("--prompt", default=None)

    commands.add_parser("prompts", help="list prompt versions")

    evaluate = commands.add_parser("eval", help="score prompt versions")
    evaluate.add_argument("--cases", type=Path,
                          default=Path("evals/cases.json"))
    evaluate.add_argument("--versions", default="v2",
                          help="extract_profile versions, e.g. v1,v2")
    return parser


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AnalyzerError(f"cannot read {path.as_posix()}: "
                            f"{exc.strerror}") from None


def new_analyzer(settings: Settings, client: anthropic.Anthropic,
                 version: str | None) -> Analyzer:
    if version and version not in PROMPTS["extract_profile"]:
        raise AnalyzerError(f"no extract_profile version {version!r}")
    versions = {"extract_profile": version} if version else {}
    return Analyzer(client, settings.model, CostTracker(settings.budget_usd),
                    versions)


def list_prompts() -> None:
    for name, versions in PROMPTS.items():
        for version, prompt in versions.items():
            default = "  (default)" if DEFAULT_VERSIONS[name] == version else ""
            print(f"{prompt.label:22} {prompt.fingerprint}{default}")


def evaluate(args: argparse.Namespace, settings: Settings,
             client: anthropic.Anthropic) -> None:
    mode = "offline fake API" if settings.offline else settings.model
    for version in args.versions.split(","):
        analyzer = new_analyzer(settings, client, version)
        results = run_eval(analyzer, args.cases)
        correct, total = summary(results)
        prompt = analyzer.prompt("extract_profile")
        print(f"{prompt.label} ({prompt.fingerprint}) on {mode}")
        for r in results:
            print(f"  {r.case:18} {r.correct}/{r.total}"
                  + (f"  wrong: {'; '.join(r.wrong)}" if r.wrong else ""))
        print(f"  total {correct}/{total} ({100 * correct / total:.0f}%)")


def run(args: argparse.Namespace, settings: Settings) -> int:
    if args.command == "prompts":
        list_prompts()
        return 0
    client = make_client(settings)
    if args.command == "eval":
        evaluate(args, settings, client)
    elif args.command == "extract":
        analyzer = new_analyzer(settings, client, args.prompt)
        profile, dropped = analyzer.extract_profile(read(args.resume))
        print(profile.model_dump_json(indent=2))
        if dropped:
            print(f"ignored (not in the resume): {', '.join(dropped)}",
                  file=sys.stderr)
    elif args.command == "analyze":
        analyzer = new_analyzer(settings, client, args.prompt)
        report = analyzer.analyze(read(args.resume), read(args.job))
        render = to_json if args.format == "json" else to_markdown
        text = render(report, settings.model)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text, encoding="utf-8")
            print(f"saved to {args.out.as_posix()} "
                  f"(must-have match {report.score}%)")
        else:
            print(text, end="")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings(force_offline=args.offline)
    try:
        return run(args, settings)
    except AnalyzerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
