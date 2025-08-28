from decimal import Decimal
from unittest.mock import patch

import pytest

from mm_web3.calcs import (
    _get_suffix,
    _parse_random_function,
    _split_on_plus_minus_tokens,
    calc_decimal_expression,
    calc_expression_with_vars,
    convert_value_with_units,
)


class TestCalcDecimalExpression:
    def test_plain_numbers(self) -> None:
        assert calc_decimal_expression("123.45") == Decimal("123.45")
        assert calc_decimal_expression("-0.5") == Decimal("-0.5")
        assert calc_decimal_expression("0") == Decimal(0)
        assert calc_decimal_expression("  100.0  ") == Decimal("100.0")

    @patch("mm_web3.calcs.random_decimal")
    def test_random_function_valid(self, mock_random) -> None:
        mock_random.return_value = Decimal("5.5")
        result = calc_decimal_expression("random(1.0, 10.0)")
        assert result == Decimal("5.5")
        mock_random.assert_called_once_with(Decimal("1.0"), Decimal("10.0"))

    @patch("mm_web3.calcs.random_decimal")
    def test_random_function_case_insensitive(self, mock_random) -> None:
        mock_random.return_value = Decimal("2.5")
        result = calc_decimal_expression("RANDOM(1, 5)")
        assert result == Decimal("2.5")
        mock_random.assert_called_once_with(Decimal(1), Decimal(5))

    def test_random_function_invalid_args(self) -> None:
        with pytest.raises(ValueError, match="wrong expression, random part"):
            calc_decimal_expression("random(1)")

        with pytest.raises(ValueError, match="wrong expression, random part"):
            calc_decimal_expression("random(1, 2, 3)")

    def test_random_function_invalid_range(self) -> None:
        with pytest.raises(ValueError, match="wrong expression, random part"):
            calc_decimal_expression("random(10, 5)")

    def test_invalid_decimal(self) -> None:
        with pytest.raises(ValueError):
            calc_decimal_expression("invalid")


class TestConvertValueWithUnits:
    def test_plain_numbers(self) -> None:
        assert convert_value_with_units("123", {}) == 123
        assert convert_value_with_units("0", {}) == 0

    def test_unit_conversion(self) -> None:
        unit_decimals = {"eth": 18, "gwei": 9}
        assert convert_value_with_units("1eth", unit_decimals) == 10**18
        assert convert_value_with_units("1.5eth", unit_decimals) == int(Decimal("1.5") * 10**18)
        assert convert_value_with_units("100gwei", unit_decimals) == 100 * 10**9

    def test_case_insensitive_units(self) -> None:
        unit_decimals = {"ETH": 18, "GWEI": 9}
        assert convert_value_with_units("1eth", unit_decimals) == 10**18
        assert convert_value_with_units("1ETH", unit_decimals) == 10**18

    def test_whitespace_handling(self) -> None:
        unit_decimals = {"eth": 18}
        assert convert_value_with_units("  1.5eth  ", unit_decimals) == int(Decimal("1.5") * 10**18)

    def test_negative_value_error(self) -> None:
        with pytest.raises(ValueError, match="negative value is illegal"):
            convert_value_with_units("-1eth", {"eth": 18})

    def test_unknown_unit_error(self) -> None:
        with pytest.raises(ValueError, match="illegal value"):
            convert_value_with_units("1btc", {"eth": 18})


class TestCalcExpressionWithVars:
    def test_simple_arithmetic(self) -> None:
        assert calc_expression_with_vars("100 + 50") == 150
        assert calc_expression_with_vars("100 - 30") == 70
        assert calc_expression_with_vars("100 + 50 - 20") == 130

    def test_variables(self) -> None:
        variables = {"balance": 1000, "fee": 50}
        assert calc_expression_with_vars("balance", variables=variables) == 1000
        assert calc_expression_with_vars("balance + fee", variables=variables) == 1050
        assert calc_expression_with_vars("balance - fee", variables=variables) == 950

    def test_variable_multipliers(self) -> None:
        variables = {"balance": 1000}
        assert calc_expression_with_vars("0.5balance", variables=variables) == 500
        assert calc_expression_with_vars("2balance", variables=variables) == 2000
        assert calc_expression_with_vars("0.1balance + 100", variables=variables) == 200

    def test_unit_conversions(self) -> None:
        unit_decimals = {"eth": 18, "gwei": 9}
        assert calc_expression_with_vars("1eth", unit_decimals=unit_decimals) == 10**18
        assert calc_expression_with_vars("1eth + 100gwei", unit_decimals=unit_decimals) == 10**18 + 100 * 10**9

    def test_mixed_expressions(self) -> None:
        variables = {"balance": 10**18}
        unit_decimals = {"eth": 18, "gwei": 9}
        result = calc_expression_with_vars("0.5balance + 1gwei - 100", variables=variables, unit_decimals=unit_decimals)
        expected = int(Decimal("0.5") * 10**18) + 10**9 - 100
        assert result == expected

    @patch("mm_web3.calcs.random.randint")
    def test_random_function_in_expression(self, mock_randint) -> None:
        unit_decimals = {"gwei": 9}
        mock_randint.return_value = 5 * 10**9
        result = calc_expression_with_vars("100 + random(1gwei, 10gwei)", unit_decimals=unit_decimals)
        assert result == 100 + 5 * 10**9
        mock_randint.assert_called_once_with(10**9, 10 * 10**9)

    def test_case_insensitive(self) -> None:
        variables = {"Balance": 1000}
        unit_decimals = {"ETH": 18}
        result = calc_expression_with_vars("BALANCE + 1ETH", variables=variables, unit_decimals=unit_decimals)
        assert result == 1000 + 10**18

    def test_whitespace_handling(self) -> None:
        assert calc_expression_with_vars("  100   +   50  ") == 150

    def test_variable_unit_conflict(self) -> None:
        variables = {"eth": 1000}
        unit_decimals = {"eth": 18}
        with pytest.raises(ValueError, match="variable name conflicts with unit suffix"):
            calc_expression_with_vars("eth", variables=variables, unit_decimals=unit_decimals)

    def test_unrecognized_term_error(self) -> None:
        with pytest.raises(ValueError, match="unrecognized term"):
            calc_expression_with_vars("unknown_var")

    @patch("mm_web3.calcs.random.randint")
    def test_legacy(self, mock_randint) -> None:
        """Test cases to ensure compatibility with legacy functionality."""
        suffix_decimals = {"eth": 18, "gwei": 9, "t": 6}

        # Simple number: calc_expression_with_vars("100") == 100
        assert calc_expression_with_vars("100") == 100

        # Arithmetic: calc_expression_with_vars("10 + 2 - 5") == 7
        assert calc_expression_with_vars("10 + 2 - 5") == 7

        # Random function: calc_expression_with_vars("10 - random(2,2)") == 8
        mock_randint.return_value = 2
        result = calc_expression_with_vars("10 - random(2,2)")
        assert result == 8
        mock_randint.assert_called_with(2, 2)

        # Random with units:
        # calc_expression_with_vars("10gwei - random(2gwei,2gwei)", unit_decimals=suffix_decimals) == 8000000000
        mock_randint.reset_mock()
        mock_randint.return_value = 2 * 10**9  # 2gwei in wei
        result = calc_expression_with_vars("10gwei - random(2gwei,2gwei)", unit_decimals=suffix_decimals)
        assert result == 8 * 10**9  # 8gwei in wei (8000000000)
        mock_randint.assert_called_with(2 * 10**9, 2 * 10**9)

        # Variable with multiplier:
        # calc_expression_with_vars("1.5estimate + 1", variables={"estimate": 10}) == 16
        variables = {"estimate": 10}
        result = calc_expression_with_vars("1.5estimate + 1", variables=variables)
        assert result == 16

        # Error cases
        with pytest.raises(ValueError):
            calc_expression_with_vars("fff")

        with pytest.raises(ValueError):
            calc_expression_with_vars("random(3,1)")

        with pytest.raises(ValueError):
            calc_expression_with_vars("1.1gg", unit_decimals=suffix_decimals)

        # Variable-unit conflict:
        # calc_expression_with_vars("1.5eth", variables={"eth": 10}, unit_decimals=suffix_decimals)
        variables_conflict = {"eth": 10}
        with pytest.raises(ValueError, match="variable name conflicts with unit suffix"):
            calc_expression_with_vars("1.5eth", variables=variables_conflict, unit_decimals=suffix_decimals)


class TestParseRandomFunction:
    @patch("mm_web3.calcs.random.randint")
    def test_valid_random_function(self, mock_randint) -> None:
        unit_decimals = {"gwei": 9}
        mock_randint.return_value = 5 * 10**9
        result = _parse_random_function("random(1gwei, 10gwei)", unit_decimals)
        assert result == 5 * 10**9
        mock_randint.assert_called_once_with(10**9, 10 * 10**9)

    def test_invalid_arguments_count(self) -> None:
        with pytest.raises(ValueError, match="random function must have exactly 2 arguments"):
            _parse_random_function("random(1)", {})

        with pytest.raises(ValueError, match="random function must have exactly 2 arguments"):
            _parse_random_function("random(1, 2, 3)", {})

    def test_invalid_range(self) -> None:
        with pytest.raises(ValueError, match="random range invalid, min > max"):
            _parse_random_function("random(10, 5)", {})


class TestGetSuffix:
    def test_finds_matching_suffix(self) -> None:
        unit_decimals = {"eth": 18, "gwei": 9}
        assert _get_suffix("1eth", unit_decimals) == "eth"
        assert _get_suffix("100gwei", unit_decimals) == "gwei"

    def test_no_matching_suffix(self) -> None:
        unit_decimals = {"eth": 18}
        assert _get_suffix("100", unit_decimals) is None
        assert _get_suffix("1btc", unit_decimals) is None

    def test_returns_first_match(self) -> None:
        # Test that it returns first matching suffix when multiple could match
        unit_decimals = {"wei": 0, "gwei": 9}
        assert _get_suffix("1gwei", unit_decimals) in ["wei", "gwei"]


class TestSplitOnPlusMinusTokens:
    def test_simple_expressions(self) -> None:
        assert _split_on_plus_minus_tokens("100") == ["+100"]
        assert _split_on_plus_minus_tokens("+100") == ["+100"]
        assert _split_on_plus_minus_tokens("-100") == ["-100"]

    def test_complex_expressions(self) -> None:
        assert _split_on_plus_minus_tokens("100+50") == ["+100", "+50"]
        assert _split_on_plus_minus_tokens("100-50") == ["+100", "-50"]
        assert _split_on_plus_minus_tokens("100+50-20") == ["+100", "+50", "-20"]
        assert _split_on_plus_minus_tokens("-100+50") == ["-100", "+50"]

    def test_whitespace_removal(self) -> None:
        assert _split_on_plus_minus_tokens("100 + 50 - 20") == ["+100", "+50", "-20"]

    def test_error_conditions(self) -> None:
        with pytest.raises(ValueError, match="value is empty"):
            _split_on_plus_minus_tokens("")

        with pytest.raises(ValueError, match=r"\+\+ in value"):
            _split_on_plus_minus_tokens("100++50")

        with pytest.raises(ValueError, match="-- in value"):
            _split_on_plus_minus_tokens("100--50")

        with pytest.raises(ValueError, match="ends with -"):
            _split_on_plus_minus_tokens("100-")

        with pytest.raises(ValueError, match="ends with +"):
            _split_on_plus_minus_tokens("100+")
