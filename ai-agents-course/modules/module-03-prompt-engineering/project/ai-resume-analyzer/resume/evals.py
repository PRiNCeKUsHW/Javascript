"""A small evaluation: does the analyzer get each must-have skill right?

Each case pairs a resume with a job posting, and a person has labelled every
must-have skill as present (true) or missing (false). The eval runs the
analyzer without advice and counts correct verdicts. Code does the grading.
"""
import json
from dataclasses import dataclass
from pathlib import Path

from resume.analyzer import Analyzer
from resume.skills import normalize


@dataclass
class CaseResult:
    case: str
    correct: int
    total: int
    wrong: list[str]


def load_cases(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_case(analyzer: Analyzer, case: dict, root: Path) -> CaseResult:
    resume = (root / case["resume"]).read_text(encoding="utf-8")
    job = (root / case["job"]).read_text(encoding="utf-8")
    report = analyzer.analyze(resume, job, with_advice=False)
    found = {normalize(s) for s in report.job.must_have}
    matched = {normalize(s) for s in report.matched}
    wrong = []
    for skill, expected in case["expected"].items():
        key = normalize(skill)
        if key not in found:
            wrong.append(f"{skill} (not extracted from the job)")
        elif (key in matched) != expected:
            got = "matched" if key in matched else "missing"
            wrong.append(f"{skill} (expected "
                         f"{'matched' if expected else 'missing'}, got {got})")
    total = len(case["expected"])
    return CaseResult(case["id"], total - len(wrong), total, wrong)


def run_eval(analyzer: Analyzer, cases_file: Path) -> list[CaseResult]:
    root = cases_file.parent
    return [run_case(analyzer, case, root) for case in load_cases(cases_file)]


def summary(results: list[CaseResult]) -> tuple[int, int]:
    return (sum(r.correct for r in results), sum(r.total for r in results))
