# type_hints.py: describe what goes in and what comes out
def average_latency(latencies: list[float]) -> float:
    return sum(latencies) / len(latencies) if latencies else 0.0


def find_price(prices: dict[str, float], model: str) -> float | None:
    return prices.get(model)


print(average_latency([820.0, 640.0, 2140.0]))
print(find_price({"model-small": 0.5}, "model-large"))
print(average_latency("oops"))      # hints are NOT checked when the code runs
