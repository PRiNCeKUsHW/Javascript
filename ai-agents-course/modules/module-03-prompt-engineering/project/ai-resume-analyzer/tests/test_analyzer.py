import pytest

from conftest import make_analyzer
from resume.errors import AnalyzerError, BudgetExceeded
from resume.fake_api import FakeAnthropicAPI


def test_analyze_compares_in_code(analyzer, sam, job):
    report = analyzer.analyze(sam, job)
    assert report.missing_must == ["Kubernetes"]
    assert "PostgreSQL" in report.matched        # Postgres in the resume
    assert report.score == 83
    assert report.years_short == 0
    assert [c.prompt for c in report.calls] == [
        "extract_profile@v2", "extract_job@v1", "suggest@v1"]


def test_requests_use_structured_output_and_the_prompt(analyzer, fake, sam):
    analyzer.extract_profile(sam)
    body = fake.requests[0]
    assert body["output_config"]["format"]["type"] == "json_schema"
    assert body["output_config"]["effort"] == "low"
    assert "<resume>" in body["messages"][0]["content"]
    assert body["system"].startswith("You extract facts from resumes")


def test_no_advice_call_when_nothing_is_missing(analyzer, fake, sam):
    job = "# Python Dev\n\n## Must have\n- Python\n"
    report = analyzer.analyze(sam, job)
    assert report.suggestions is None
    assert len(fake.requests) == 2


def test_invented_skill_is_dropped(sam):
    analyzer = make_analyzer(FakeAnthropicAPI(failures=["invented"]))
    profile, dropped = analyzer.extract_profile(sam)
    assert dropped == ["COBOL"]
    assert "COBOL" not in profile.skills


@pytest.mark.parametrize("failure, message", [
    ("invalid", "years_experience: Input should be greater than or equal to 0"),
    ("cutoff", "not complete JSON"),
    ("refusal", "declined"),
    ("401", "API key was rejected"),
])
def test_failures_become_one_clear_error(sam, failure, message):
    analyzer = make_analyzer(FakeAnthropicAPI(failures=[failure]))
    with pytest.raises(AnalyzerError, match=message):
        analyzer.extract_profile(sam)


def test_sdk_retries_rate_limits(sam):
    fake = FakeAnthropicAPI(failures=["429", "500"])
    profile, _ = make_analyzer(fake).extract_profile(sam)
    assert profile.name == "Sam Rivera"
    assert len(fake.requests) == 3


def test_budget_stops_before_the_next_call(sam, job):
    analyzer = make_analyzer(FakeAnthropicAPI(failures=[]), budget=0.001)
    with pytest.raises(BudgetExceeded):
        analyzer.analyze(sam, job)


def test_prompt_version_is_selectable(sam):
    fake = FakeAnthropicAPI(failures=[])
    make_analyzer(fake, versions={"extract_profile": "v1"}).extract_profile(sam)
    assert fake.requests[0]["system"] == "You are a helpful assistant."
