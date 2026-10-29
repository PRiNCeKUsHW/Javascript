# custom_errors.py: raise your own, specific errors
class ToolkitError(Exception):
    """Base class for errors our code raises on purpose."""


class BudgetExceeded(ToolkitError):
    pass


def charge(spent, cost, budget):
    if cost < 0:
        raise ValueError("cost cannot be negative")
    if spent + cost > budget:
        raise BudgetExceeded(f"{spent + cost:.2f} would exceed the {budget:.2f} budget")
    return spent + cost


spent = 0.0
for cost in [0.40, 0.35, 0.50]:
    try:
        spent = charge(spent, cost, budget=1.00)
        print(f"charged {cost:.2f}, total {spent:.2f}")
    except BudgetExceeded as err:
        print("stopped:", err)
