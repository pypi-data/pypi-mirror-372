from pathlib import Path
from unittest.mock import patch

import pytest

from mm_web3.account import PrivateKeyMap
from mm_web3.validators import ConfigValidators, Transfer

from .common import TEST_ETH_PRIVATE_KEYS, eth_is_valid_address, eth_private_to_address


class TestTransfer:
    """Test Transfer model."""

    def test_transfer_creation(self) -> None:
        """Test Transfer object creation."""
        transfer = Transfer(from_address="0xabc", to_address="0xdef", value="100")
        assert transfer.from_address == "0xabc"
        assert transfer.to_address == "0xdef"
        assert transfer.value == "100"

    def test_log_prefix(self) -> None:
        """Test Transfer log_prefix property."""
        transfer = Transfer(from_address="0xabc", to_address="0xdef", value="100")
        assert transfer.log_prefix == "0xabc->0xdef"


class TestConfigValidatorsTransfers:
    """Test ConfigValidators.transfers method."""

    def test_transfers_direct_input(self) -> None:
        """Test transfers validator with direct input."""
        validator = ConfigValidators.transfers(eth_is_valid_address)

        addresses = list(TEST_ETH_PRIVATE_KEYS.keys())
        from_addr = addresses[0]
        to_addr = addresses[1]

        input_str = f"{from_addr} {to_addr} 100"
        result = validator(input_str)

        assert len(result) == 1
        assert result[0].from_address == from_addr
        assert result[0].to_address == to_addr
        assert result[0].value == "100"

    def test_transfers_multiple_lines(self) -> None:
        """Test transfers validator with multiple transfers."""
        validator = ConfigValidators.transfers(eth_is_valid_address)

        addresses = list(TEST_ETH_PRIVATE_KEYS.keys())
        input_str = f"{addresses[0]} {addresses[1]} 100\n{addresses[2]} {addresses[3]} 200"
        result = validator(input_str)

        assert len(result) == 2
        assert result[0].from_address == addresses[0]
        assert result[0].to_address == addresses[1]
        assert result[0].value == "100"
        assert result[1].from_address == addresses[2]
        assert result[1].to_address == addresses[3]
        assert result[1].value == "200"

    def test_transfers_without_value(self) -> None:
        """Test transfers validator without value specification."""
        validator = ConfigValidators.transfers(eth_is_valid_address)

        addresses = list(TEST_ETH_PRIVATE_KEYS.keys())
        input_str = f"{addresses[0]} {addresses[1]}"
        result = validator(input_str)

        assert len(result) == 1
        assert result[0].from_address == addresses[0]
        assert result[0].to_address == addresses[1]
        assert result[0].value == ""

    def test_transfers_lowercase(self) -> None:
        """Test transfers validator with lowercase option."""
        validator = ConfigValidators.transfers(eth_is_valid_address, lowercase=True)

        addresses = list(TEST_ETH_PRIVATE_KEYS.keys())
        input_str = f"{addresses[0]} {addresses[1]} 100"
        result = validator(input_str)

        assert len(result) == 1
        assert result[0].from_address == addresses[0].lower()
        assert result[0].to_address == addresses[1].lower()
        assert result[0].value == "100"

    def test_transfers_from_file(self, tmp_path: Path) -> None:
        """Test transfers validator with file reference."""
        validator = ConfigValidators.transfers(eth_is_valid_address)

        addresses = list(TEST_ETH_PRIVATE_KEYS.keys())
        content = f"{addresses[0]} {addresses[1]} 100\n{addresses[2]} {addresses[3]} 200"

        transfers_file = tmp_path / "transfers.txt"
        transfers_file.write_text(content)

        input_str = f"file:{transfers_file}"
        result = validator(input_str)

        assert len(result) == 2
        assert result[0].from_address == addresses[0]
        assert result[0].to_address == addresses[1]
        assert result[0].value == "100"

    def test_transfers_invalid_address(self) -> None:
        """Test transfers validator with invalid address."""
        validator = ConfigValidators.transfers(eth_is_valid_address)

        input_str = "invalid_from invalid_to 100"

        with pytest.raises(ValueError, match="illegal address: invalid_from"):
            validator(input_str)

    def test_transfers_wrong_format(self) -> None:
        """Test transfers validator with wrong line format."""
        validator = ConfigValidators.transfers(eth_is_valid_address)

        input_str = "single_address"

        with pytest.raises(ValueError, match="illegal line: single_address"):
            validator(input_str)

    def test_transfers_empty_input(self) -> None:
        """Test transfers validator with empty input."""
        validator = ConfigValidators.transfers(eth_is_valid_address)

        with pytest.raises(ValueError, match="No valid transfers found"):
            validator("")


class TestConfigValidatorsProxies:
    """Test ConfigValidators.proxies method."""

    def test_proxies_direct_input(self) -> None:
        """Test proxies validator with direct proxy list."""
        validator = ConfigValidators.proxies()

        input_str = "proxy1:8080\nproxy2:3128"
        result = validator(input_str)

        assert result == ["proxy1:8080", "proxy2:3128"]

    def test_proxies_deduplication(self) -> None:
        """Test proxies validator deduplicates results."""
        validator = ConfigValidators.proxies()

        input_str = "proxy1:8080\nproxy1:8080\nproxy2:3128"
        result = validator(input_str)

        assert result == ["proxy1:8080", "proxy2:3128"]

    def test_proxies_from_file(self, tmp_path: Path) -> None:
        """Test proxies validator with file reference."""
        validator = ConfigValidators.proxies()

        proxy_file = tmp_path / "proxies.txt"
        proxy_file.write_text("proxy1:8080\nproxy2:3128")

        input_str = f"file:{proxy_file}"
        result = validator(input_str)

        assert result == ["proxy1:8080", "proxy2:3128"]

    def test_proxies_env_url_missing(self) -> None:
        """Test proxies validator with missing environment variable."""
        validator = ConfigValidators.proxies()

        input_str = "env_url:MISSING_VAR"

        with pytest.raises(ValueError, match="missing env var: MISSING_VAR"):
            validator(input_str)


class TestConfigValidatorsLogFile:
    """Test ConfigValidators.log_file method."""

    def test_log_file_creation(self, tmp_path: Path) -> None:
        """Test log file validator creates file and directories."""
        validator = ConfigValidators.log_file()

        log_path = tmp_path / "logs" / "app.log"
        result = validator(log_path)

        assert result == log_path
        assert log_path.exists()
        assert log_path.is_file()
        assert log_path.parent.exists()

    def test_log_file_tilde_expansion(self, tmp_path: Path) -> None:
        """Test log file validator expands tilde in path."""
        validator = ConfigValidators.log_file()

        test_path = tmp_path / "test.log"

        # Mock expanduser to return our test path
        with patch.object(Path, "expanduser", return_value=test_path):
            result = validator(Path("~/test.log"))
            assert result == test_path
            assert test_path.exists()

    def test_log_file_existing_file(self, tmp_path: Path) -> None:
        """Test log file validator with existing file."""
        validator = ConfigValidators.log_file()

        log_path = tmp_path / "existing.log"
        log_path.write_text("existing content")

        result = validator(log_path)
        assert result == log_path
        assert log_path.read_text() == "existing content"


class TestConfigValidatorsNodes:
    """Test ConfigValidators.nodes method."""

    def test_nodes_basic(self) -> None:
        """Test nodes validator with basic input."""
        validator = ConfigValidators.nodes()

        input_str = "http://node1.example.com\nhttp://node2.example.com"
        result = validator(input_str)

        assert result == ["http://node1.example.com", "http://node2.example.com"]

    def test_nodes_deduplication(self) -> None:
        """Test nodes validator deduplicates URLs."""
        validator = ConfigValidators.nodes()

        input_str = "http://node1.example.com\nhttp://node1.example.com\nhttp://node2.example.com"
        result = validator(input_str)

        assert result == ["http://node1.example.com", "http://node2.example.com"]

    def test_nodes_empty_not_allowed(self) -> None:
        """Test nodes validator fails with empty input when not allowed."""
        validator = ConfigValidators.nodes(allow_empty=False)

        with pytest.raises(ValueError, match="Node list cannot be empty"):
            validator("")

    def test_nodes_empty_allowed(self) -> None:
        """Test nodes validator allows empty input when configured."""
        validator = ConfigValidators.nodes(allow_empty=True)

        result = validator("")
        assert result == []


class TestConfigValidatorsAddress:
    """Test ConfigValidators.address method."""

    def test_address_valid(self) -> None:
        """Test address validator with valid address."""
        validator = ConfigValidators.address(eth_is_valid_address)

        valid_address = next(iter(TEST_ETH_PRIVATE_KEYS.keys()))
        result = validator(valid_address)

        assert result == valid_address

    def test_address_invalid(self) -> None:
        """Test address validator with invalid address."""
        validator = ConfigValidators.address(eth_is_valid_address)

        with pytest.raises(ValueError, match="illegal address: invalid_address"):
            validator("invalid_address")

    def test_address_lowercase(self) -> None:
        """Test address validator with lowercase option."""
        validator = ConfigValidators.address(eth_is_valid_address, lowercase=True)

        valid_address = next(iter(TEST_ETH_PRIVATE_KEYS.keys()))
        result = validator(valid_address)

        assert result == valid_address.lower()


class TestConfigValidatorsAddresses:
    """Test ConfigValidators.addresses method."""

    def test_addresses_direct_input(self) -> None:
        """Test addresses validator with direct input."""
        validator = ConfigValidators.addresses(deduplicate=True, is_address=eth_is_valid_address)

        addresses = list(TEST_ETH_PRIVATE_KEYS.keys())[:2]
        input_str = f"{addresses[0]}\n{addresses[1]}"
        result = validator(input_str)

        assert result == addresses

    def test_addresses_deduplication(self) -> None:
        """Test addresses validator with deduplication."""
        validator = ConfigValidators.addresses(deduplicate=True, is_address=eth_is_valid_address)

        address = next(iter(TEST_ETH_PRIVATE_KEYS.keys()))
        input_str = f"{address}\n{address}"
        result = validator(input_str)

        assert result == [address]

    def test_addresses_no_deduplication(self) -> None:
        """Test addresses validator without deduplication."""
        validator = ConfigValidators.addresses(deduplicate=False, is_address=eth_is_valid_address)

        address = next(iter(TEST_ETH_PRIVATE_KEYS.keys()))
        input_str = f"{address}\n{address}"
        result = validator(input_str)

        assert result == [address, address]

    def test_addresses_lowercase(self) -> None:
        """Test addresses validator with lowercase option."""
        validator = ConfigValidators.addresses(deduplicate=True, lowercase=True, is_address=eth_is_valid_address)

        address = next(iter(TEST_ETH_PRIVATE_KEYS.keys()))
        result = validator(address)

        assert result == [address.lower()]

    def test_addresses_from_file(self, tmp_path: Path) -> None:
        """Test addresses validator with file reference."""
        validator = ConfigValidators.addresses(deduplicate=True, is_address=eth_is_valid_address)

        addresses = list(TEST_ETH_PRIVATE_KEYS.keys())[:2]
        addresses_file = tmp_path / "addresses.txt"
        addresses_file.write_text("\n".join(addresses))

        input_str = f"file:{addresses_file}"
        result = validator(input_str)

        assert result == addresses

    def test_addresses_invalid_address(self) -> None:
        """Test addresses validator with invalid address."""
        validator = ConfigValidators.addresses(deduplicate=True, is_address=eth_is_valid_address)

        input_str = "invalid_address"

        with pytest.raises(ValueError, match="illegal address: invalid_address"):
            validator(input_str)

    def test_addresses_no_validation(self) -> None:
        """Test addresses validator without address validation."""
        validator = ConfigValidators.addresses(deduplicate=True)

        input_str = "any_string\nanother_string"
        result = validator(input_str)

        assert result == ["any_string", "another_string"]


class TestConfigValidatorsPrivateKeys:
    """Test ConfigValidators.private_keys method."""

    def test_private_keys_direct_input(self) -> None:
        """Test private keys validator with direct input."""
        validator = ConfigValidators.private_keys(eth_private_to_address)

        private_keys = list(TEST_ETH_PRIVATE_KEYS.values())[:2]
        input_str = "\n".join(private_keys)
        result = validator(input_str)

        assert isinstance(result, PrivateKeyMap)
        assert len(result) == 2
        for address, private_key in TEST_ETH_PRIVATE_KEYS.items():
            if private_key in private_keys:
                assert result[address] == private_key

    def test_private_keys_from_file(self, tmp_path: Path) -> None:
        """Test private keys validator with file reference."""
        validator = ConfigValidators.private_keys(eth_private_to_address)

        private_keys = list(TEST_ETH_PRIVATE_KEYS.values())[:2]
        keys_file = tmp_path / "keys.txt"
        keys_file.write_text("\n".join(private_keys))

        input_str = f"file:{keys_file}"
        result = validator(input_str)

        assert isinstance(result, PrivateKeyMap)
        assert len(result) == 2

    def test_private_keys_invalid_key(self) -> None:
        """Test private keys validator with invalid key."""
        validator = ConfigValidators.private_keys(eth_private_to_address)

        input_str = "invalid_private_key"

        with pytest.raises(ValueError, match="invalid private key"):
            validator(input_str)

    def test_private_keys_duplicate_keys(self) -> None:
        """Test private keys validator with duplicate keys.

        Note: The validator uses parse_lines with deduplicate=True, so duplicate
        lines are automatically removed during parsing. This tests that behavior.
        """
        validator = ConfigValidators.private_keys(eth_private_to_address)

        private_key = next(iter(TEST_ETH_PRIVATE_KEYS.values()))
        input_str = f"{private_key}\n{private_key}"

        # Should succeed because duplicates are removed during parsing
        result = validator(input_str)
        assert isinstance(result, PrivateKeyMap)
        assert len(result) == 1


class TestConfigValidatorsExpressionWithVars:
    """Test ConfigValidators.expression_with_vars method."""

    def test_expression_with_vars_simple(self) -> None:
        """Test expression validator with simple arithmetic."""
        validator = ConfigValidators.expression_with_vars()

        expression = "100 + 50"
        result = validator(expression)

        assert result == expression

    def test_expression_with_vars_variable(self) -> None:
        """Test expression validator with variables."""
        validator = ConfigValidators.expression_with_vars(var_name="balance")

        expression = "0.5balance + 100"
        result = validator(expression)

        assert result == expression

    def test_expression_with_vars_units(self) -> None:
        """Test expression validator with unit decimals."""
        unit_decimals = {"eth": 18, "gwei": 9}
        validator = ConfigValidators.expression_with_vars(unit_decimals=unit_decimals)

        expression = "1eth + 100gwei"
        result = validator(expression)

        assert result == expression

    def test_expression_with_vars_invalid(self) -> None:
        """Test expression validator with invalid expression."""
        validator = ConfigValidators.expression_with_vars()

        with pytest.raises(ValueError):
            validator("invalid_expression")

    def test_expression_with_vars_variable_unit_conflict(self) -> None:
        """Test expression validator with variable-unit conflict."""
        unit_decimals = {"eth": 18}
        validator = ConfigValidators.expression_with_vars(var_name="eth", unit_decimals=unit_decimals)

        with pytest.raises(ValueError, match="variable name conflicts with unit suffix"):
            validator("1eth")


class TestConfigValidatorsDecimalExpression:
    """Test ConfigValidators.decimal_expression method."""

    def test_decimal_expression_simple(self) -> None:
        """Test decimal expression validator with simple number."""
        validator = ConfigValidators.decimal_expression()

        expression = "123.45"
        result = validator(expression)

        assert result == expression

    def test_decimal_expression_random(self) -> None:
        """Test decimal expression validator with random function."""
        validator = ConfigValidators.decimal_expression()

        expression = "random(1.0, 5.0)"
        result = validator(expression)

        assert result == expression

    def test_decimal_expression_invalid(self) -> None:
        """Test decimal expression validator with invalid expression."""
        validator = ConfigValidators.decimal_expression()

        with pytest.raises(ValueError):
            validator("invalid_decimal")

    def test_decimal_expression_invalid_random(self) -> None:
        """Test decimal expression validator with invalid random function."""
        validator = ConfigValidators.decimal_expression()

        with pytest.raises(ValueError):
            validator("random(10, 5)")  # min > max
