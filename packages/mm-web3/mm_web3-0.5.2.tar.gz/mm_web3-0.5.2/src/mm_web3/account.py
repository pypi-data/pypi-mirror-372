from __future__ import annotations

import contextlib
from collections.abc import Callable
from pathlib import Path

from pydantic import GetCoreSchemaHandler, ValidationInfo
from pydantic_core import core_schema


class PrivateKeyMap(dict[str, str]):
    """Map of addresses to private keys with fast lookup by address."""

    def contains_all_addresses(self, addresses: list[str]) -> bool:
        """Check if all addresses are in the map."""
        return set(addresses) <= set(self.keys())

    @classmethod
    def __get_pydantic_core_schema__(cls, _source: object, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        # Use the dict schema as the basis.
        return core_schema.with_info_after_validator_function(
            cls.validate,  # our function that converts a dict to PrivateKeyMap
            handler(dict),  # get the schema for a plain dict
        )

    @classmethod
    def validate(cls, value: object, _info: ValidationInfo) -> PrivateKeyMap:
        """
        Convert and validate an input value into a PrivateKeyMap.

        - If the input is already a PrivateKeyMap, return it.
        - If it is a dict, check that all keys and values are strings and
          then return a PrivateKeyMap.
        - Otherwise, raise a TypeError.
        """
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            # Optionally, ensure all keys and values are strings.
            if not all(isinstance(k, str) for k in value):
                raise TypeError("All keys in PrivateKeyMap must be strings")
            if not all(isinstance(v, str) for v in value.values()):
                raise TypeError("All values in PrivateKeyMap must be strings")
            return cls(value)
        raise TypeError("Invalid type for PrivateKeyMap. Expected dict or PrivateKeyMap.")

    @staticmethod
    def from_list(private_keys: list[str], address_from_private: Callable[[str], str]) -> PrivateKeyMap:
        """Create a dictionary of private keys with addresses as keys.

        Args:
            private_keys: List of private keys. Must be fully valid:
                - No empty strings
                - No whitespace-only strings
                - No duplicates
            address_from_private: Function to derive address from private key

        Raises:
            ValueError: if any private key is invalid
        """
        # Check for duplicates
        if len(private_keys) != len(set(private_keys)):
            raise ValueError("duplicate private keys found")

        result = PrivateKeyMap()
        for private_key in private_keys:
            address = None
            with contextlib.suppress(Exception):
                address = address_from_private(private_key)
            if address is None:
                raise ValueError("invalid private key")
            result[address] = private_key
        return result

    @staticmethod
    def from_file(private_keys_file: Path, address_from_private: Callable[[str], str]) -> PrivateKeyMap:
        """Create a dictionary of private keys with addresses as keys from a file.
        Raises:
            ValueError: If the file cannot be read or any private key is invalid.
        """
        private_keys_file = private_keys_file.expanduser()
        try:
            content = private_keys_file.read_text().strip()
        except OSError as e:
            raise ValueError(f"can't read from the file: {private_keys_file}") from e

        private_keys = content.split("\n") if content else []
        return PrivateKeyMap.from_list(private_keys, address_from_private)
