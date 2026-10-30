import ast
import math
import operator
from collections.abc import Callable
from typing import Any

from anthropic.types import ToolParam

from calc_agent.errors import ToolError

# ---------------------------------------------------------------- calculate
OPERATORS: dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
}
FUNCTIONS: dict[str, Callable[..., Any]] = {
    "sqrt": math.sqrt, "abs": abs, "round": round}
MAX_EXPONENT = 100


def calculate(expression: str) -> str:
    """Evaluate arithmetic safely: a whitelist of operations, never eval()."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        raise ToolError(f"not a valid expression: {expression!r}") from None
    return format_number(_evaluate(tree.body))


def _evaluate(node: ast.expr) -> Any:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _evaluate(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        left, right = _evaluate(node.left), _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise ToolError(f"exponent {right} is too large")
        try:
            return OPERATORS[type(node.op)](left, right)
        except ZeroDivisionError:
            raise ToolError("division by zero") from None
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in FUNCTIONS and not node.keywords):
        args = [_evaluate(a) for a in node.args]
        try:
            return FUNCTIONS[node.func.id](*args)
        except (TypeError, ValueError) as exc:
            raise ToolError(f"{node.func.id}: {exc}") from None
    raise ToolError(f"not allowed in a calculation: {ast.unparse(node)}")


def format_number(value: float) -> str:
    """18.0 -> '18', 0.1 + 0.2 -> '0.3' (rounded to 10 decimal places)."""
    if isinstance(value, float):
        text = f"{value:.10f}".rstrip("0").rstrip(".")
        return text if text not in ("-0", "") else "0"
    return str(value)


# ---------------------------------------------------------------- convert
# factor to the base unit of each kind: metres, kilograms, litres
UNITS: dict[str, tuple[str, float]] = {
    "km": ("length", 1000.0), "m": ("length", 1.0), "cm": ("length", 0.01),
    "mi": ("length", 1609.344), "ft": ("length", 0.3048),
    "in": ("length", 0.0254), "kg": ("mass", 1.0), "g": ("mass", 0.001),
    "lb": ("mass", 0.45359237), "oz": ("mass", 0.028349523125),
    "l": ("volume", 1.0), "ml": ("volume", 0.001),
}
TEMPERATURES = {"c", "f"}


def convert(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between units of the same kind."""
    a, b = from_unit.strip().lower(), to_unit.strip().lower()
    if {a, b} <= TEMPERATURES:
        result = value * 9 / 5 + 32 if (a, b) == ("c", "f") else (
            (value - 32) * 5 / 9 if (a, b) == ("f", "c") else value)
        return f"{format_number(round(result, 4))} {b.upper()}"
    if a not in UNITS or b not in UNITS:
        known = ", ".join([*UNITS, "c", "f"])
        raise ToolError(f"unknown unit in {from_unit!r} -> {to_unit!r}; "
                        f"known units: {known}")
    (kind_a, factor_a), (kind_b, factor_b) = UNITS[a], UNITS[b]
    if kind_a != kind_b:
        raise ToolError(f"cannot convert {kind_a} ({a}) to {kind_b} ({b})")
    return f"{format_number(round(value * factor_a / factor_b, 4))} {b}"


# ---------------------------------------------------------------- definitions
TOOLS: list[ToolParam] = [
    {
        "name": "calculate",
        "description": (
            "Evaluates one arithmetic expression exactly and returns the "
            "result as text. Supports + - * / % and ** (power), parentheses, "
            "and the functions sqrt(), abs() and round(). Variables, units "
            "and words are not supported: put numbers only. Returns an error "
            "message for invalid expressions or division by zero."),
        "input_schema": {
            "type": "object",
            "properties": {"expression": {
                "type": "string",
                "description": "Numbers and operators only: (18 * 1.15) / 3"}},
            "required": ["expression"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "convert",
        "description": (
            "Converts a value between units of the same kind and returns the "
            "result with its unit. Length: km, m, cm, mi, ft, in. Mass: kg, "
            "g, lb, oz. Volume: l, ml. Temperature: c, f. Returns an error "
            "message for unknown units or different kinds (kg to km)."),
        "input_schema": {
            "type": "object",
            "properties": {
                "value": {"type": "number"},
                "from_unit": {"type": "string"},
                "to_unit": {"type": "string"},
            },
            "required": ["value", "from_unit", "to_unit"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def run_tool(name: str, args: dict[str, Any]) -> str:
    """Dispatch a tool call by name. Problems become ToolError."""
    if name == "calculate":
        return calculate(str(args.get("expression", "")))
    if name == "convert":
        try:
            value = float(args["value"])
            return convert(value, str(args["from_unit"]), str(args["to_unit"]))
        except (KeyError, TypeError, ValueError):
            raise ToolError(f"convert needs value, from_unit and to_unit; "
                            f"got {args}") from None
    raise ToolError(f"unknown tool {name!r}")
