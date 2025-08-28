import random
import re
from decimal import Decimal

from mm_std import random_decimal


def calc_decimal_expression(expression: str) -> Decimal:
    """Calculate decimal value from string expression.

    Supports:
    - Plain numbers: "123.45", "-0.5"
    - Random function: "random(min, max)" returns random decimal between min and max

    Args:
        expression: String expression to calculate

    Returns:
        Calculated decimal value

    Raises:
        ValueError: If expression format is invalid or random range is invalid (min > max)
    """
    expression = expression.lower().strip()
    if expression.startswith("random(") and expression.endswith(")"):
        arr = expression.lstrip("random(").rstrip(")").split(",")
        if len(arr) != 2:
            raise ValueError(f"wrong expression, random part: {expression}")
        try:
            from_value = Decimal(arr[0])
            to_value = Decimal(arr[1])
        except Exception as e:
            raise ValueError(f"wrong expression, random part: {expression}") from e
        if from_value > to_value:
            raise ValueError(f"wrong expression, random part: {expression}")
        return random_decimal(from_value, to_value)

    try:
        return Decimal(expression)
    except Exception as e:
        raise ValueError(f"invalid decimal expression: {expression}") from e


def convert_value_with_units(value: str, unit_decimals: dict[str, int]) -> int:
    """Convert value with units to base integer units.

    Converts values like "1.5eth" to base units (wei) using decimal places mapping.

    Args:
        value: String value to convert (e.g., "123.45eth", "100")
        unit_decimals: Mapping of unit suffixes to decimal places (e.g., {"eth": 18})

    Returns:
        Value converted to base integer units

    Raises:
        ValueError: If value is negative or unit suffix is not recognized
    """
    value = value.lower().strip()
    if value.startswith("-"):
        raise ValueError(f"negative value is illegal: {value}")
    if value.isdigit():
        return int(value)
    unit_decimals = {k.lower(): v for k, v in unit_decimals.items()}
    for suffix in unit_decimals:
        if value.endswith(suffix):
            value = value.removesuffix(suffix)
            return int(Decimal(value) * 10 ** unit_decimals[suffix])

    raise ValueError(f"illegal value: {value}")


def calc_expression_with_vars(
    expression: str, variables: dict[str, int] | None = None, unit_decimals: dict[str, int] | None = None
) -> int:
    """Calculate complex integer expression with variables, units and random values.

    Supports:
    - Arithmetic operations: "+", "-"
    - Variables with multipliers: "balance", "0.5balance"
    - Unit conversions: "1.5eth", "100gwei"
    - Random function: "random(1eth, 2eth)"
    - Mixed expressions: "0.2balance + random(1gwei, 2gwei) - 100"

    Args:
        expression: String expression to calculate
        variables: Mapping of variable names to their integer values
        unit_decimals: Mapping of unit suffixes to decimal places

    Returns:
        Calculated integer value in base units

    Raises:
        ValueError: If expression format is invalid
        TypeError: If expression is not a string
    """
    if not isinstance(expression, str):
        raise TypeError(f"expression is not str: {expression}")
    expression = expression.lower().strip()
    if unit_decimals is None:
        unit_decimals = {}
    if variables is None:
        variables = {}
    unit_decimals = {k.lower(): v for k, v in unit_decimals.items()}
    variables = {k.lower(): v for k, v in variables.items()}

    # Check for conflicts between variable names and unit suffixes
    for var_name in variables:
        if var_name in unit_decimals:
            raise ValueError(f"variable name conflicts with unit suffix: {var_name}")

    try:
        result = 0
        for token in _split_on_plus_minus_tokens(expression.lower()):
            operator = token[0]
            term = token[1:]
            suffix = _get_suffix(term, unit_decimals)

            if term.isdigit():
                term_value = int(term)
            elif suffix is not None:
                term_value = convert_value_with_units(term, unit_decimals)
            elif variables:
                # Check if term ends with any variable name
                matched_var = None
                for var_name in variables:
                    if term.endswith(var_name):
                        matched_var = var_name
                        break

                if matched_var:
                    multiplier_part = term.removesuffix(matched_var)
                    multiplier = Decimal(multiplier_part) if multiplier_part else Decimal(1)
                    term_value = int(multiplier * variables[matched_var])
                # Check for random function
                elif term.startswith("random(") and term.endswith(")"):
                    term_value = _parse_random_function(term, unit_decimals)
                else:
                    raise ValueError(f"unrecognized term: {term}")  # noqa: TRY301
            elif term.startswith("random(") and term.endswith(")"):
                term_value = _parse_random_function(term, unit_decimals)
            else:
                raise ValueError(f"unrecognized term: {term}")  # noqa: TRY301

            if operator == "+":
                result += term_value
            if operator == "-":
                result -= term_value

        return result  # noqa: TRY300
    except Exception as e:
        raise ValueError(e) from e


def _parse_random_function(term: str, unit_decimals: dict[str, int]) -> int:
    """Extract random function parameters and generate random value within range.

    Supports unit conversion in random bounds to ensure consistent base units.
    """
    content = term.lstrip("random(").rstrip(")")
    parts = content.split(",")
    if len(parts) != 2:
        raise ValueError(f"random function must have exactly 2 arguments: {term}")

    from_value = convert_value_with_units(parts[0].strip(), unit_decimals)
    to_value = convert_value_with_units(parts[1].strip(), unit_decimals)

    if from_value > to_value:
        raise ValueError(f"random range invalid, min > max: {term}")

    return random.randint(from_value, to_value)


def _get_suffix(item: str, unit_decimals: dict[str, int]) -> str | None:
    """Find unit suffix in term to enable unit conversion.

    Returns first matching suffix to avoid ambiguity in complex expressions.
    """
    for suffix in unit_decimals:
        if item.endswith(suffix):
            return suffix
    return None


def _split_on_plus_minus_tokens(value: str) -> list[str]:
    """Split expression into signed terms for sequential evaluation.

    Normalizes input by removing spaces and adding leading '+' when needed.
    Each token contains operator (+ or -) followed by the term value.
    """
    value = "".join(value.split())
    if not value:
        raise ValueError("value is empty")
    if "++" in value:
        raise ValueError("++ in value")
    if "--" in value:
        raise ValueError("-- in value")
    if value.endswith("-"):
        raise ValueError("ends with -")
    if value.endswith("+"):
        raise ValueError("ends with +")

    if not value.startswith("+") and not value.startswith("-"):
        value = "+" + value

    result: list[str] = []
    rest_value = value
    while True:
        if not rest_value:
            return result
        items = re.split(r"[+\-]", rest_value)
        if rest_value.startswith("+"):
            result.append("+" + items[1])
            rest_value = rest_value.removeprefix("+" + items[1])
        elif rest_value.startswith("-"):
            result.append("-" + items[1])
            rest_value = rest_value.removeprefix("-" + items[1])
