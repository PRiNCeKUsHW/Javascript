from collections import Counter
from dataclasses import dataclass, field

from toolkit.models import UsageRecord

Prices = dict[str, dict[str, float]]
TOKENS_PER_PRICE_UNIT = 1_000_000


@dataclass
class ModelStats:
    requests: int = 0
    tokens: int = 0
    cost: float = 0.0


@dataclass
class Summary:
    requests: int
    ok: int
    errors: int
    prompt_tokens: int
    completion_tokens: int
    cost: float
    avg_latency_ms: float
    by_model: dict[str, ModelStats] = field(default_factory=dict)
    top_tags: list[tuple[str, int]] = field(default_factory=list)
    unpriced_models: set[str] = field(default_factory=set)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    @property
    def success_rate(self) -> float:
        return self.ok / self.requests if self.requests else 0.0


def estimate_cost(record: UsageRecord, prices: Prices) -> float | None:
    price = prices.get(record.model)
    if price is None:
        return None
    dollars = (record.prompt_tokens * price["input"]
               + record.completion_tokens * price["output"])
    return dollars / TOKENS_PER_PRICE_UNIT


def summarize(records: list[UsageRecord], prices: Prices,
              top: int = 3) -> Summary:
    by_model: dict[str, ModelStats] = {}
    tags: Counter[str] = Counter()
    unpriced: set[str] = set()
    total_cost = 0.0

    for record in records:
        stats = by_model.setdefault(record.model, ModelStats())
        stats.requests += 1
        stats.tokens += record.total_tokens
        cost = estimate_cost(record, prices)
        if cost is None:
            unpriced.add(record.model)
        else:
            stats.cost += cost
            total_cost += cost
        tags.update(record.tags)

    ok = sum(1 for r in records if r.status == "ok")
    latencies = [r.latency_ms for r in records]
    return Summary(
        requests=len(records),
        ok=ok,
        errors=len(records) - ok,
        prompt_tokens=sum(r.prompt_tokens for r in records),
        completion_tokens=sum(r.completion_tokens for r in records),
        cost=total_cost,
        avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0.0,
        by_model=dict(sorted(by_model.items())),
        top_tags=tags.most_common(top),
        unpriced_models=unpriced,
    )
