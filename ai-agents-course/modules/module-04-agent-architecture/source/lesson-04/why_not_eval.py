import project  # noqa: F401  (makes `calc_agent` importable)
from calc_agent.errors import ToolError
from calc_agent.tools import calculate

# Text a model (or a user) might send to a "calculator" tool:
attack = "__import__('os').getcwd()"

print("eval runs ANY Python:  ", eval(attack))   # never do this with tool input

try:
    calculate(attack)
except ToolError as exc:
    print("calculate refuses it:  ", exc)
print("calculate does maths:  ", calculate("(18 * 1.15) / 3"))
