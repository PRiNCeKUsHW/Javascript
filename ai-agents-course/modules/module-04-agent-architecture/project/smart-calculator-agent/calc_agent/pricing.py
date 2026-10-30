from dataclasses import dataclass, field

from calc_agent.errors import AgentError


# US dollars per 1 million tokens (input, output). Published list prices for
# Claude models in October 2026. Prices change: check the pricing page.
PRICES: dict[str, tuple[float, float]] = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}
PER_MILLION = 1_000_000


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    if model not in PRICES:
        raise KeyError(f"no price for model {model!r}")
    price_in, price_out = PRICES[model]
    return (input_tokens * price_in + output_tokens * price_out) / PER_MILLION


@dataclass
class CostTracker:
    """Adds up what every call costs and stops before the budget is gone."""

    budget_usd: float
    spent_usd: float = 0.0
    calls: list[float] = field(default_factory=list)

    def check(self) -> None:
        if self.spent_usd >= self.budget_usd:
            raise AgentError(
                f"budget of ${self.budget_usd:.4f} used up "
                f"(spent ${self.spent_usd:.4f}); raise CALC_BUDGET_USD")

    def add(self, model: str, input_tokens: int, output_tokens: int) -> float:
        cost = cost_usd(model, input_tokens, output_tokens)
        self.spent_usd += cost
        self.calls.append(cost)
        return cost
