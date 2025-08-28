# mm-web3

A Python library providing utilities for working with multiple blockchain networks, proxy management, and reliable network operations for cryptocurrency applications.

## Features

### 🔗 Multi-Blockchain Support
- **19 blockchain networks** including Ethereum, Arbitrum, Polygon, Solana, Aptos, StarkNet and more
- **4 network types**: EVM, Solana, Aptos, StarkNet
- Network-specific explorer URL generation for tokens and accounts
- Address formatting utilities (lowercase for certain networks)

### 🌐 Proxy Management
- Fetch proxy lists from remote URLs
- Validate proxy URLs (HTTP, HTTPS, SOCKS4, SOCKS5)
- Random proxy selection from pools
- Support for authenticated proxies

### 🔄 Retry Logic
- Automatic retry with random node/proxy combinations
- Configurable retry attempts
- Detailed logging of retry attempts
- Support for both node+proxy and proxy-only scenarios

### ⚙️ Configuration System
- TOML-based configuration with validation
- ZIP archive support with optional encryption
- Async and sync configuration loading
- Pydantic-based validation with detailed error reporting

### 🎯 Node Management
- Random blockchain node selection
- Support for single nodes or node pools
- URL normalization (trailing slash removal)


## Quick Start

### Basic Usage

```python
import asyncio
from mm_web3 import Network, fetch_proxies, random_node, random_proxy

async def main():
    # Get explorer URL for a token
    network = Network.ETHEREUM
    token_url = network.explorer_token("0xa0b86991c31cc0e37faeded5b4648648e8dd4a0425")
    print(f"USDC on Ethereum: {token_url}")

    # Fetch proxies from a URL
    proxies_result = await fetch_proxies("https://example.com/proxy-list.txt")
    if proxies_result.is_ok():
        proxies = proxies_result.unwrap()
        proxy = random_proxy(proxies)
        print(f"Using proxy: {proxy}")

    # Select random node from a pool
    nodes = [
        "https://eth-mainnet.g.alchemy.com/v2/your-key",
        "https://mainnet.infura.io/v3/your-key",
        "https://rpc.ankr.com/eth"
    ]
    node = random_node(nodes)
    print(f"Using node: {node}")

asyncio.run(main())
```

### Configuration with TOML

```python
from pathlib import Path
from pydantic import BaseModel
from mm_web3.config import Web3CliConfig

class MyConfig(Web3CliConfig):
    api_key: str
    networks: list[str]
    retry_count: int = 3

# config.toml
"""
api_key = "your-api-key"
networks = ["ethereum", "polygon", "arbitrum-one"]
retry_count = 5
"""

config = MyConfig.read_toml_config_or_exit(Path("config.toml"))
print(f"Loaded config: {config.api_key}")
```

### Retry Logic with Nodes and Proxies

```python
import asyncio
from mm_web3.retry import retry_with_node_and_proxy
from mm_result import Result

async def make_request(node: str, proxy: str | None) -> Result[dict]:
    # Your HTTP request logic here
    # Return Result.ok(data) on success or Result.err(error) on failure
    pass

async def main():
    nodes = ["https://rpc1.example.com", "https://rpc2.example.com"]
    proxies = ["http://proxy1:8080", "http://proxy2:8080"]

    result = await retry_with_node_and_proxy(
        retries=3,
        nodes=nodes,
        proxies=proxies,
        func=make_request
    )

    if result.is_ok():
        data = result.unwrap()
        print(f"Success: {data}")
    else:
        print(f"Failed after retries: {result.error}")

asyncio.run(main())
```

## Supported Networks

### EVM Networks
- Ethereum, Arbitrum One, Avalanche C-Chain
- Base, BSC, Celo, Core
- Fantom, Linea, OpBNB, OP Mainnet
- Polygon, Polygon zkEVM, Scroll
- zkSync Era, Zora

### Other Networks
- **Solana**: Solana mainnet
- **Aptos**: Aptos mainnet
- **StarkNet**: StarkNet mainnet

Each network provides:
- Explorer URL generation for tokens and accounts
- Network type classification
- Address formatting preferences

## Configuration

The library supports TOML configuration files with:
- **Validation**: Pydantic-based schema validation
- **ZIP Support**: Load configs from encrypted ZIP archives
- **Async Loading**: For configs with async validators
- **Error Handling**: Detailed validation error messages

### Configuration Example

```toml
# config.toml
[network]
default = "ethereum"
nodes = [
    "https://eth-mainnet.g.alchemy.com/v2/key1",
    "https://mainnet.infura.io/v3/key2"
]

[proxy]
enabled = true
sources = ["https://proxy-list.example.com/free.txt"]
timeout = 5.0

[retry]
max_attempts = 3
backoff_seconds = 1.0
```

## Development

### Setup

```bash
# Clone and setup
git clone <repository-url>
cd mm-cryptocurrency
uv sync

# Run tests
just test

# Format code
just format

# Run linting
just lint

# Run security audit
just audit
```

### Requirements

- **Python 3.13+**
- **uv** for package management
- Dependencies: `mm-http`, `mm-print`, `mm-result`

### Testing

The library includes comprehensive tests covering:
- Network definitions and utilities
- Proxy fetching and validation
- Configuration loading and validation
- Retry logic and error handling
- Utility functions

Run tests with: `just test` or `uv run pytest`

## API Reference

### Core Classes

- **`Network`**: Enum of supported blockchain networks
- **`NetworkType`**: Base network types (EVM, Solana, etc.)
- **`Web3CliConfig`**: Base class for TOML configuration

### Functions

- **`fetch_proxies(url)`**: Fetch proxy list from URL
- **`fetch_proxies_sync(url)`**: Synchronous proxy fetching
- **`random_proxy(proxies)`**: Select random proxy from pool
- **`random_node(nodes)`**: Select random node from pool
- **`is_valid_proxy_url(url)`**: Validate proxy URL format
- **`retry_with_node_and_proxy()`**: Retry with node/proxy rotation
- **`retry_with_proxy()`**: Retry with proxy-only rotation

### Type Aliases

- **`Proxies`**: `str | Sequence[str] | None` - Proxy configuration
- **`Nodes`**: `str | Sequence[str]` - Node configuration
