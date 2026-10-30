import pytest

from calc_agent.errors import ToolError
from calc_agent.tools import TOOLS, calculate, convert, run_tool


@pytest.mark.parametrize("expression, expected", [
    ("2 + 3 * 4", "14"),
    ("(18 * 1.15) / 3", "6.9"),
    ("0.1 + 0.2", "0.3"),
    ("-5 + 2", "-3"),
    ("2 ** 10", "1024"),
    ("sqrt(16) + abs(-2)", "6"),
    ("round(2.567, 1)", "2.6"),
    ("17 % 5", "2"),
])
def test_calculate(expression, expected):
    assert calculate(expression) == expected


@pytest.mark.parametrize("expression, message", [
    ("__import__('os').getcwd()", "not allowed"),
    ("open('secrets.txt')", "not allowed"),
    ("x + 1", "not allowed"),
    ("18 x 1.15", "not a valid expression"),
    ("1 / 0", "division by zero"),
    ("9 ** 999", "too large"),
    ("sqrt(-1)", "sqrt"),
])
def test_calculate_refuses_unsafe_or_invalid(expression, message):
    with pytest.raises(ToolError, match=message):
        calculate(expression)


def test_convert_units_and_temperatures():
    assert convert(42.195, "km", "mi") == "26.2188 mi"
    assert convert(2, "lb", "kg") == "0.9072 kg"
    assert convert(100, "C", "F") == "212 F"


def test_convert_errors():
    with pytest.raises(ToolError, match="unknown unit"):
        convert(1, "parsec", "km")
    with pytest.raises(ToolError, match="cannot convert mass"):
        convert(1, "kg", "km")


def test_run_tool_dispatches_and_rejects_unknown_tools():
    assert run_tool("calculate", {"expression": "1 + 1"}) == "2"
    assert run_tool("convert", {"value": 1, "from_unit": "m",
                                "to_unit": "cm"}) == "100 cm"
    with pytest.raises(ToolError, match="unknown tool"):
        run_tool("delete_files", {})
    with pytest.raises(ToolError, match="convert needs"):
        run_tool("convert", {"value": "lots"})


def test_tool_definitions_are_strict_schemas():
    for tool in TOOLS:
        schema = tool["input_schema"]
        assert tool["strict"] is True
        assert schema["additionalProperties"] is False
        assert set(schema["required"]) == set(schema["properties"])
