import json

from resume.analyzer import GapReport


def bullets(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] or ["- none"]


def to_markdown(report: GapReport, model: str) -> str:
    p, job = report.profile, report.job
    years = (f"{p.years_experience} years (job asks for {job.min_years}+)"
             + (f", {report.years_short} short" if report.years_short else ""))
    lines = [f"# Skills-gap report: {p.name} for {job.title}", "",
             f"Must-have match: {len(report.matched)}/{len(job.must_have)} "
             f"({report.score}%)", f"Experience: {years}", "",
             "## Matched must-have skills", *bullets(report.matched), "",
             "## Missing must-have skills", *bullets(report.missing_must), "",
             "## Missing nice-to-have skills",
             *bullets(report.missing_nice), ""]
    if report.suggestions:
        lines += ["## Suggestions", report.suggestions.summary, ""]
        lines += [f"- **{s.skill}**: {s.advice}"
                  for s in report.suggestions.suggestions] + [""]
    if report.dropped:
        lines += [f"Note: ignored {len(report.dropped)} extracted skill(s) "
                  f"the resume does not name: {', '.join(report.dropped)}", ""]
    tokens_in = sum(c.input_tokens for c in report.calls)
    tokens_out = sum(c.output_tokens for c in report.calls)
    cost = sum(c.cost_usd for c in report.calls)
    prompts = " · ".join(f"{c.prompt} ({c.fingerprint})" for c in report.calls)
    lines += ["---", f"Prompts: {prompts}",
              f"Model: {model} · {len(report.calls)} calls · {tokens_in} in / "
              f"{tokens_out} out tokens · ${cost:.4f}"]
    return "\n".join(lines) + "\n"


def to_json(report: GapReport, model: str) -> str:
    data = {
        "candidate": report.profile.model_dump(),
        "job": report.job.model_dump(),
        "score": report.score, "matched": report.matched,
        "missing_must": report.missing_must,
        "missing_nice": report.missing_nice,
        "years_short": report.years_short, "ignored_skills": report.dropped,
        "suggestions": (report.suggestions.model_dump()
                        if report.suggestions else None),
        "model": model,
        "calls": [vars(c) for c in report.calls],
    }
    return json.dumps(data, indent=2) + "\n"
