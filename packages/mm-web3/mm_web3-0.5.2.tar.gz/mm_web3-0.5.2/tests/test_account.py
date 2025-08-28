from pathlib import Path
from typing import cast

import pytest
from pydantic import ValidationInfo

from mm_web3.account import PrivateKeyMap

from .common import TEST_ETH_PRIVATE_KEYS, eth_private_to_address


class TestPrivateKeyMapBasic:
    """Test basic PrivateKeyMap functionality."""

    def test_contains_all_addresses_with_all_present(self) -> None:
        """Test contains_all_addresses when all addresses are present."""
        pk_map = PrivateKeyMap(TEST_ETH_PRIVATE_KEYS)
        addresses = list(TEST_ETH_PRIVATE_KEYS.keys())
        assert pk_map.contains_all_addresses(addresses)

    def test_contains_all_addresses_with_subset(self) -> None:
        """Test contains_all_addresses with a subset of addresses."""
        pk_map = PrivateKeyMap(TEST_ETH_PRIVATE_KEYS)
        addresses = list(TEST_ETH_PRIVATE_KEYS.keys())[:2]
        assert pk_map.contains_all_addresses(addresses)

    def test_contains_all_addresses_with_missing(self) -> None:
        """Test contains_all_addresses when some addresses are missing."""
        pk_map = PrivateKeyMap(TEST_ETH_PRIVATE_KEYS)
        addresses = [*TEST_ETH_PRIVATE_KEYS.keys(), "0x1234567890123456789012345678901234567890"]
        assert not pk_map.contains_all_addresses(addresses)

    def test_contains_all_addresses_empty_list(self) -> None:
        """Test contains_all_addresses with empty list."""
        pk_map = PrivateKeyMap(TEST_ETH_PRIVATE_KEYS)
        assert pk_map.contains_all_addresses([])


class TestPrivateKeyMapValidation:
    """Test PrivateKeyMap validation and type conversion."""

    def test_validate_existing_privatekeymap(self) -> None:
        """Test that existing PrivateKeyMap passes validation."""
        original = PrivateKeyMap(TEST_ETH_PRIVATE_KEYS)
        validated = PrivateKeyMap.validate(original, cast(ValidationInfo, None))
        assert validated is original

    def test_validate_dict_with_strings(self) -> None:
        """Test validation of dict with string keys and values."""
        test_dict = {"addr1": "key1", "addr2": "key2"}
        result = PrivateKeyMap.validate(test_dict, cast(ValidationInfo, None))
        assert isinstance(result, PrivateKeyMap)
        assert result == test_dict

    def test_validate_dict_with_non_string_keys(self) -> None:
        """Test validation fails with non-string keys."""
        test_dict = {123: "key1", "addr2": "key2"}
        with pytest.raises(TypeError, match="All keys in PrivateKeyMap must be strings"):
            PrivateKeyMap.validate(test_dict, cast(ValidationInfo, None))

    def test_validate_dict_with_non_string_values(self) -> None:
        """Test validation fails with non-string values."""
        test_dict = {"addr1": 123, "addr2": "key2"}
        with pytest.raises(TypeError, match="All values in PrivateKeyMap must be strings"):
            PrivateKeyMap.validate(test_dict, cast(ValidationInfo, None))

    def test_validate_invalid_type(self) -> None:
        """Test validation fails with invalid type."""
        with pytest.raises(TypeError, match="Invalid type for PrivateKeyMap"):
            PrivateKeyMap.validate("invalid", cast(ValidationInfo, None))


class TestPrivateKeyMapFromList:
    """Test PrivateKeyMap.from_list method."""

    def test_from_list_valid_keys(self) -> None:
        """Test from_list with valid private keys."""
        private_keys = list(TEST_ETH_PRIVATE_KEYS.values())
        result = PrivateKeyMap.from_list(private_keys, eth_private_to_address)

        assert len(result) == len(TEST_ETH_PRIVATE_KEYS)
        for address, private_key in TEST_ETH_PRIVATE_KEYS.items():
            assert result[address] == private_key

    def test_from_list_single_key(self) -> None:
        """Test from_list with single private key."""
        private_key = next(iter(TEST_ETH_PRIVATE_KEYS.values()))
        expected_address = next(iter(TEST_ETH_PRIVATE_KEYS.keys()))

        result = PrivateKeyMap.from_list([private_key], eth_private_to_address)

        assert len(result) == 1
        assert result[expected_address] == private_key

    def test_from_list_empty_list(self) -> None:
        """Test from_list with empty list."""
        result = PrivateKeyMap.from_list([], eth_private_to_address)
        assert len(result) == 0
        assert isinstance(result, PrivateKeyMap)

    def test_from_list_duplicate_keys(self) -> None:
        """Test from_list fails with duplicate private keys."""
        private_key = next(iter(TEST_ETH_PRIVATE_KEYS.values()))
        private_keys = [private_key, private_key]

        with pytest.raises(ValueError, match="duplicate private keys found"):
            PrivateKeyMap.from_list(private_keys, eth_private_to_address)

    def test_from_list_invalid_key(self) -> None:
        """Test from_list fails with invalid private key."""
        invalid_keys = ["invalid_key", "0x123"]

        with pytest.raises(ValueError, match="invalid private key"):
            PrivateKeyMap.from_list(invalid_keys, eth_private_to_address)

    def test_from_list_address_function_raises(self) -> None:
        """Test from_list handles address function that raises exception."""

        def failing_address_func(_private_key: str) -> str:
            raise ValueError("Address conversion failed")

        private_keys = list(TEST_ETH_PRIVATE_KEYS.values())[:1]

        with pytest.raises(ValueError, match="invalid private key"):
            PrivateKeyMap.from_list(private_keys, failing_address_func)


class TestPrivateKeyMapFromFile:
    """Test PrivateKeyMap.from_file method."""

    def test_from_file_valid_keys(self, tmp_path: Path) -> None:
        """Test from_file with valid private keys file."""
        private_keys = list(TEST_ETH_PRIVATE_KEYS.values())

        test_file = tmp_path / "private_keys.txt"
        test_file.write_text("\n".join(private_keys))

        result = PrivateKeyMap.from_file(test_file, eth_private_to_address)

        assert len(result) == len(TEST_ETH_PRIVATE_KEYS)
        for address, private_key in TEST_ETH_PRIVATE_KEYS.items():
            assert result[address] == private_key

    def test_from_file_empty_file(self, tmp_path: Path) -> None:
        """Test from_file with empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        result = PrivateKeyMap.from_file(test_file, eth_private_to_address)
        assert len(result) == 0
        assert isinstance(result, PrivateKeyMap)

    def test_from_file_whitespace_only_file(self, tmp_path: Path) -> None:
        """Test from_file with file containing only whitespace."""
        test_file = tmp_path / "whitespace.txt"
        test_file.write_text("   \n\t\n   ")

        result = PrivateKeyMap.from_file(test_file, eth_private_to_address)
        assert len(result) == 0
        assert isinstance(result, PrivateKeyMap)

    def test_from_file_single_key(self, tmp_path: Path) -> None:
        """Test from_file with single private key."""
        private_key = next(iter(TEST_ETH_PRIVATE_KEYS.values()))
        expected_address = next(iter(TEST_ETH_PRIVATE_KEYS.keys()))

        test_file = tmp_path / "single_key.txt"
        test_file.write_text(private_key)

        result = PrivateKeyMap.from_file(test_file, eth_private_to_address)
        assert len(result) == 1
        assert result[expected_address] == private_key

    def test_from_file_with_tilde_expansion(self) -> None:
        """Test from_file handles tilde expansion in path."""
        private_keys = list(TEST_ETH_PRIVATE_KEYS.values())[:1]

        # Create file in home directory to test tilde expansion
        temp_path = Path.home() / "test_private_keys.txt"
        temp_path.write_text("\n".join(private_keys))

        # Use tilde path
        tilde_path = Path("~/test_private_keys.txt")

        try:
            result = PrivateKeyMap.from_file(tilde_path, eth_private_to_address)
            assert len(result) == 1
        finally:
            temp_path.unlink(missing_ok=True)

    def test_from_file_nonexistent(self) -> None:
        """Test from_file fails with nonexistent file."""
        nonexistent_path = Path("/nonexistent/path/file.txt")

        with pytest.raises(ValueError, match="can't read from the file"):
            PrivateKeyMap.from_file(nonexistent_path, eth_private_to_address)

    def test_from_file_permission_denied(self, tmp_path: Path) -> None:
        """Test from_file handles permission denied gracefully."""
        test_file = tmp_path / "no_permissions.txt"
        test_file.write_text("test")
        test_file.chmod(0o000)  # Remove all permissions

        with pytest.raises(ValueError, match="can't read from the file"):
            PrivateKeyMap.from_file(test_file, eth_private_to_address)

    def test_from_file_invalid_keys_in_file(self, tmp_path: Path) -> None:
        """Test from_file fails when file contains invalid private keys."""
        test_file = tmp_path / "invalid_keys.txt"
        test_file.write_text("invalid_key_1\ninvalid_key_2")

        with pytest.raises(ValueError, match="invalid private key"):
            PrivateKeyMap.from_file(test_file, eth_private_to_address)

    def test_from_file_duplicate_keys_in_file(self, tmp_path: Path) -> None:
        """Test from_file fails when file contains duplicate private keys."""
        private_key = next(iter(TEST_ETH_PRIVATE_KEYS.values()))
        test_file = tmp_path / "duplicate_keys.txt"
        test_file.write_text(f"{private_key}\n{private_key}")

        with pytest.raises(ValueError, match="duplicate private keys found"):
            PrivateKeyMap.from_file(test_file, eth_private_to_address)
