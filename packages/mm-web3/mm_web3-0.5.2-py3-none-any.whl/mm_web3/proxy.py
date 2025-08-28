"""Proxy utilities for HTTP requests."""

import random
from collections.abc import Sequence
from urllib.parse import urlparse

from mm_http import http_request, http_request_sync
from mm_result import Result

type Proxies = str | Sequence[str] | None
"""Proxy configuration: single URL, sequence of URLs, or None for no proxy."""


def random_proxy(proxies: Proxies) -> str | None:
    """Select a random proxy from the given configuration."""
    if proxies is None:
        return None

    if isinstance(proxies, str):
        return proxies

    # proxies is a Sequence[str] at this point
    if proxies:
        return random.choice(proxies)

    return None


async def fetch_proxies(proxies_url: str, timeout: float = 5) -> Result[list[str]]:
    """Fetch proxies from the given url. Expects content-type: text/plain with one proxy per line. Each proxy must be valid."""
    res = await http_request(proxies_url, timeout=timeout)
    if res.is_err():
        return res.to_result_err()

    proxies = [p.strip() for p in (res.body or "").splitlines() if p.strip()]
    proxies = list(dict.fromkeys(proxies))
    for proxy in proxies:
        if not is_valid_proxy_url(proxy):
            return res.to_result_err(f"Invalid proxy URL: {proxy}")

    if not proxies:
        return res.to_result_err("No valid proxies found")
    return res.to_result_ok(proxies)


def fetch_proxies_sync(proxies_url: str, timeout: float = 5) -> Result[list[str]]:
    """Synchronous version of fetch_proxies."""
    res = http_request_sync(proxies_url, timeout=timeout)
    if res.is_err():
        return res.to_result_err()

    proxies = [p.strip() for p in (res.body or "").splitlines() if p.strip()]
    proxies = list(dict.fromkeys(proxies))
    for proxy in proxies:
        if not is_valid_proxy_url(proxy):
            return res.to_result_err(f"Invalid proxy URL: {proxy}")

    if not proxies:
        return res.to_result_err("No valid proxies found")
    return res.to_result_ok(proxies)


def is_valid_proxy_url(proxy_url: str) -> bool:
    """
    Check if the given URL is a valid proxy URL.

    A valid proxy URL must have:
      - A scheme in {"http", "https", "socks4", "socks5", "zsocks5h"}.
      - A non-empty hostname.
      - A specified port.
      - No extra path components (the path must be empty or "/").

    For SOCKS4 URLs, authentication (username/password) is not supported.

    Examples:
      is_valid_proxy_url("socks5h://user:pass@proxy.example.com:1080") -> True
      is_valid_proxy_url("http://proxy.example.com:8080") -> True
      is_valid_proxy_url("socks4://proxy.example.com:1080") -> True
      is_valid_proxy_url("socks4://user:pass@proxy.example.com:1080") -> False
      is_valid_proxy_url("ftp://proxy.example.com:21") -> False
      is_valid_proxy_url("socks4://proxy.example.com:1080/bla-bla-bla") -> False
    """
    try:
        parsed = urlparse(proxy_url)
    except Exception:
        return False

    allowed_schemes = {"http", "https", "socks4", "socks5", "socks5h"}
    if parsed.scheme not in allowed_schemes:
        return False

    if not parsed.hostname:
        return False

    if not parsed.port:
        return False

    # For SOCKS4, authentication is not supported.
    if parsed.scheme == "socks4" and (parsed.username or parsed.password):
        return False

    # Ensure that there is no extra path (only allow an empty path or a single "/")
    if parsed.path and parsed.path not in ("", "/"):  # noqa: SIM103
        return False

    return True
