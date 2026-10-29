import json

from toolkit.stats import Summary


def render_markdown(summary: Summary, source: str,
                    currency: str = "USD") -> str:
    s = summary
    lines = [
        "# AI Usage Report",
        "",
        f"Source: {source}",
        f"Requests: {s.requests} ({s.ok} ok, {s.errors} errors)",
        f"Success rate: {s.success_rate:.1%}",
        f"Tokens: {s.prompt_tokens:,} prompt + "
        f"{s.completion_tokens:,} completion = {s.total_tokens:,}",
        f"Estimated cost: {s.cost:.4f} {currency}",
        f"Average latency: {s.avg_latency_ms:,.0f} ms",
        "",
        "## By model",
        "",
        "| Model | Requests | Tokens | Cost |",
        "|---|---:|---:|---:|",
    ]
    for name, m in s.by_model.items():
        lines.append(f"| {name} | {m.requests} | {m.tokens:,} | {m.cost:.4f} |")
    lines += ["", "## Top tags", ""]
    for rank, (tag, count) in enumerate(s.top_tags, start=1):
        lines.append(f"{rank}. {tag} ({count})")
    if s.unpriced_models:
        missing = ", ".join(sorted(s.unpriced_models))
        lines += ["", f"Warning: no price for {missing}"]
    return "\n".join(lines) + "\n"


def render_json(summary: Summary, source: str, currency: str = "USD") -> str:
    s = summary
    data = {
        "source": source,
        "requests": s.requests,
        "ok": s.ok,
        "errors": s.errors,
        "success_rate": round(s.success_rate, 4),
        "tokens": {"prompt": s.prompt_tokens,
                   "completion": s.completion_tokens,
                   "total": s.total_tokens},
        "cost": {"amount": round(s.cost, 6), "currency": currency},
        "avg_latency_ms": round(s.avg_latency_ms, 1),
        "by_model": {
            name: {"requests": m.requests, "tokens": m.tokens,
                   "cost": round(m.cost, 6)}
            for name, m in s.by_model.items()
        },
        "top_tags": [{"tag": t, "count": c} for t, c in s.top_tags],
        "unpriced_models": sorted(s.unpriced_models),
    }
    return json.dumps(data, indent=2) + "\n"
