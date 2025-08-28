import os
from collections.abc import Callable
from pathlib import Path

from mm_std import parse_lines
from pydantic import BaseModel

from mm_web3.account import PrivateKeyMap
from mm_web3.calcs import calc_decimal_expression, calc_expression_with_vars
from mm_web3.proxy import fetch_proxies_sync
from mm_web3.utils import read_lines_from_file

type IsAddress = Callable[[str], bool]


class Transfer(BaseModel):
    from_address: str
    to_address: str
    value: str  # can be empty string

    @property
    def log_prefix(self) -> str:
        return f"{self.from_address}->{self.to_address}"


class ConfigValidators:
    """Pydantic field validators for cryptocurrency CLI application configuration.

    Provides static methods that return validator functions for use with Pydantic models
    in cryptocurrency CLI applications. Each validator handles complex input formats
    including direct values, file references, and external data sources.

    These validators are designed for CLI configuration files where users need flexible
    ways to specify cryptocurrency addresses, private keys, network nodes, proxies,
    and mathematical expressions for transaction amounts.
    """

    @staticmethod
    def transfers(is_address: IsAddress, lowercase: bool = False) -> Callable[[str], list[Transfer]]:
        """Validate and parse cryptocurrency transfers configuration.

        Parses transfer configurations from string or file references. Each transfer
        requires source and destination addresses, with optional value specification.

        Args:
            is_address: Function to validate cryptocurrency addresses
            lowercase: If True, convert addresses to lowercase

        Returns:
            Validator function that parses string into list of Transfer objects

        Format:
            - Direct: "from_addr to_addr [value]"
            - File reference: "file:/path/to/transfers.txt"

        The value field can be:
            - Empty string: value taken from default config
            - Decimal expression: "123.45" or "random(1.0, 5.0)"
            - Expression with variables: "0.5balance + 1eth"

        Raises:
            ValueError: If addresses are invalid, format is wrong, or no transfers found
        """

        def validator(v: str) -> list[Transfer]:
            result = []
            for line in parse_lines(v, remove_comments=True):  # don't use lowercase here because it can be a file: /To/Path.txt
                if line.startswith("file:"):
                    for file_line in read_lines_from_file(line.removeprefix("file:").strip()):
                        arr = file_line.split()
                        if len(arr) < 2 or len(arr) > 3:
                            raise ValueError(f"illegal file_line: {file_line}")
                        result.append(Transfer(from_address=arr[0], to_address=arr[1], value=arr[2] if len(arr) > 2 else ""))

                else:
                    arr = line.split()
                    if len(arr) < 2 or len(arr) > 3:
                        raise ValueError(f"illegal line: {line}")
                    result.append(Transfer(from_address=arr[0], to_address=arr[1], value=arr[2] if len(arr) > 2 else ""))

            if lowercase:
                result = [
                    Transfer(from_address=r.from_address.lower(), to_address=r.to_address.lower(), value=r.value) for r in result
                ]

            for route in result:
                if not is_address(route.from_address):
                    raise ValueError(f"illegal address: {route.from_address}")
                if not is_address(route.to_address):
                    raise ValueError(f"illegal address: {route.to_address}")

            if not result:
                raise ValueError("No valid transfers found")

            return result

        return validator

    @staticmethod
    def proxies() -> Callable[[str], list[str]]:
        """Validate and parse proxy configuration from multiple sources.

        Supports direct proxy specification, fetching from URLs, environment variables,
        and local files. Automatically deduplicates results.

        Returns:
            Validator function that parses string into unique list of proxy addresses

        Format:
            - Direct: "proxy1:port\nproxy2:port"
            - URL source: "url:http://example.com/proxies.txt"
            - Environment URL: "env_url:PROXY_URL_VAR"
            - File reference: "file:/path/to/proxies.txt"

        Raises:
            ValueError: If URL fetch fails or environment variable is missing
        """

        def validator(v: str) -> list[str]:
            result = []
            for line in parse_lines(v, deduplicate=True, remove_comments=True):
                if line.startswith("url:"):
                    url = line.removeprefix("url:").strip()
                    res = fetch_proxies_sync(url)
                    if res.is_err():
                        raise ValueError(f"Can't get proxies: {res.unwrap_err()}")
                    result += res.unwrap()
                elif line.startswith("env_url:"):
                    env_var = line.removeprefix("env_url:").strip()
                    url = os.getenv(env_var) or ""
                    if not url:
                        raise ValueError(f"missing env var: {env_var}")
                    res = fetch_proxies_sync(url)
                    if res.is_err():
                        raise ValueError(f"Can't get proxies: {res.unwrap_err()}")
                    result += res.unwrap()
                elif line.startswith("file:"):
                    path = line.removeprefix("file:").strip()
                    result += read_lines_from_file(path)
                else:
                    result.append(line)

            return list(dict.fromkeys(result))

        return validator

    @staticmethod
    def log_file() -> Callable[[Path], Path]:
        """Validate and prepare log file path with automatic directory creation.

        Creates parent directories and ensures file is writable. Expands user home directory (~).

        Returns:
            Validator function that validates Path and ensures write access

        Raises:
            ValueError: If path is not writable or cannot be created
        """

        def validator(v: Path) -> Path:
            log_file = Path(v).expanduser()
            log_file.parent.mkdir(parents=True, exist_ok=True)
            log_file.touch(exist_ok=True)
            if not log_file.is_file() or not os.access(log_file, os.W_OK):
                raise ValueError(f"wrong log path: {v}")
            return log_file

        return validator

    @staticmethod
    def nodes(allow_empty: bool = False) -> Callable[[str], list[str]]:
        """Validate blockchain node URLs configuration.

        Parses and deduplicates node URLs from string input.

        Args:
            allow_empty: If True, allows empty node list

        Returns:
            Validator function that parses string into list of node URLs

        Raises:
            ValueError: If node list is empty when allow_empty=False
        """

        def validator(v: str) -> list[str]:
            nodes = parse_lines(v, deduplicate=True, remove_comments=True)
            if not allow_empty and not nodes:
                raise ValueError("Node list cannot be empty")
            return nodes

        return validator

    @staticmethod
    def address(is_address: IsAddress, lowercase: bool = False) -> Callable[[str], str]:
        """Validate single cryptocurrency address.

        Args:
            is_address: Function to validate cryptocurrency addresses
            lowercase: If True, converts address to lowercase

        Returns:
            Validator function that validates and optionally lowercases address

        Raises:
            ValueError: If address is invalid
        """

        def validator(v: str) -> str:
            if not is_address(v):
                raise ValueError(f"illegal address: {v}")
            if lowercase:
                return v.lower()
            return v

        return validator

    @staticmethod
    def addresses(deduplicate: bool, lowercase: bool = False, is_address: IsAddress | None = None) -> Callable[[str], list[str]]:
        """Validate list of cryptocurrency addresses from string or file references.

        Supports direct address specification and file references. Optionally validates
        each address and applies transformations.

        Args:
            deduplicate: If True, deduplicates addresses
            lowercase: If True, converts addresses to lowercase
            is_address: Optional function to validate each address

        Returns:
            Validator function that parses string into list of addresses

        Format:
            - Direct: "addr1\naddr2\naddr3"
            - File reference: "file:/path/to/addresses.txt"

        Raises:
            ValueError: If any address is invalid (when is_address provided)
        """

        def validator(v: str) -> list[str]:
            result = []
            for line in parse_lines(v, deduplicate=deduplicate, remove_comments=True):
                if line.startswith("file:"):  # don't use lowercase here because it can be a file: /To/Path.txt
                    path = line.removeprefix("file:").strip()
                    result += read_lines_from_file(path)
                else:
                    result.append(line)

            if deduplicate:
                result = list(dict.fromkeys(result))

            if lowercase:
                result = [r.lower() for r in result]

            if is_address:
                for address in result:
                    if not is_address(address):
                        raise ValueError(f"illegal address: {address}")
            return result

        return validator

    @staticmethod
    def private_keys(address_from_private: Callable[[str], str]) -> Callable[[str], PrivateKeyMap]:
        """Validate and parse private keys configuration.

        Parses private keys from string or file references and converts them to
        address-to-private-key mapping using provided conversion function.

        Args:
            address_from_private: Function to derive address from private key

        Returns:
            Validator function that parses string into PrivateKeyMap

        Format:
            - Direct: "key1\nkey2\nkey3"
            - File reference: "file:/path/to/keys.txt"

        Raises:
            ValueError: If any private key is invalid or duplicate
        """

        def validator(v: str) -> PrivateKeyMap:
            private_keys = []
            for line in parse_lines(v, deduplicate=True, remove_comments=True):
                if line.startswith("file:"):
                    path = line.removeprefix("file:").strip()
                    private_keys += read_lines_from_file(path)
                else:
                    private_keys.append(line)

            return PrivateKeyMap.from_list(private_keys, address_from_private)

        return validator

    @staticmethod
    def expression_with_vars(var_name: str | None = None, unit_decimals: dict[str, int] | None = None) -> Callable[[str], str]:
        """Validate mathematical expressions with variables and units.

        Validates expressions using calc_expression_with_vars function. Supports variables,
        unit suffixes, and arithmetic operations for dynamic value calculations.

        Args:
            var_name: Variable name to include in validation context
            unit_decimals: Mapping of unit suffixes to decimal places

        Returns:
            Validator function that validates expression syntax

        Examples:
            - "0.5balance + 1eth"
            - "random(1gwei, 10gwei) - 100"

        Raises:
            ValueError: If expression syntax is invalid
        """

        def validator(v: str) -> str:
            # Use arbitrary test value to validate expression syntax without actual calculation
            variables = {var_name: 123} if var_name else {}
            calc_expression_with_vars(v, variables, unit_decimals=unit_decimals)
            return v

        return validator

    @staticmethod
    def decimal_expression() -> Callable[[str], str]:
        """Validate decimal expressions and random functions.

        Validates expressions using calc_decimal_expression function. Supports simple
        decimal values and random function calls.

        Returns:
            Validator function that validates decimal expression syntax

        Examples:
            - "123.45"
            - "random(1.0, 5.0)"

        Raises:
            ValueError: If expression syntax is invalid
        """

        def validator(v: str) -> str:
            calc_decimal_expression(v)
            return v

        return validator
