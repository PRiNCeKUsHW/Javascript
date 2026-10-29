import json

from conftest import PROJECT
from resume.evals import run_eval, summary
from resume.report import to_json, to_markdown


def test_markdown_report(analyzer, sam, job):
    text = to_markdown(analyzer.analyze(sam, job), "claude-opus-5-5")
    assert "Must-have match: 5/6 (83%)" in text
    assert "## Missing must-have skills\n- Kubernetes" in text
    assert "extract_profile@v2" in text


def test_json_report_is_valid(analyzer, sam, job):
    data = json.loads(to_json(analyzer.analyze(sam, job), "claude-opus-5-5"))
    assert data["missing_must"] == ["Kubernetes"]
    assert len(data["calls"]) == 3


def test_eval_counts_correct_verdicts(analyzer):
    results = run_eval(analyzer, PROJECT / "evals/cases.json")
    assert summary(results) == (21, 22)
    leo = next(r for r in results if r.case == "leo-backend")
    assert leo.wrong == ["Kubernetes (expected missing, got matched)"]
