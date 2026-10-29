import json

from toolkit.models import UsageRecord
from toolkit.report import render_json, render_markdown
from toolkit.stats import summarize


def test_markdown_report(good_row, prices):
    summary = summarize([UsageRecord.from_dict(good_row)], prices)
    text = render_markdown(summary, source="demo.json")
    assert text.startswith("# AI Usage Report\n")
    assert "Requests: 1 (1 ok, 0 errors)" in text
    assert "| model-small | 1 | 150 | 0.0001 |" in text
    assert "1. summarize (1)" in text


def test_json_report_is_valid_json(good_row, prices):
    summary = summarize([UsageRecord.from_dict(good_row)], prices)
    data = json.loads(render_json(summary, source="demo.json", currency="EUR"))
    assert data["tokens"] == {"prompt": 100, "completion": 50, "total": 150}
    assert data["cost"]["currency"] == "EUR"
    assert data["by_model"]["model-small"]["requests"] == 1


def test_markdown_warns_about_unpriced_models(good_row, prices):
    summary = summarize([UsageRecord.from_dict({**good_row, "model": "mystery"})], prices)
    assert "Warning: no price for mystery" in render_markdown(summary, source="x")
