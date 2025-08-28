"""Tests for proxy utilities."""

import pytest
from pytest_httpserver import HTTPServer
from werkzeug import Request, Response

from mm_web3 import fetch_proxies, fetch_proxies_sync, is_valid_proxy_url, random_proxy


class TestRandomProxy:
    """Test cases for the random_proxy function."""

    def test_returns_none_when_proxies_is_none(self):
        """Should return None when proxies is None."""
        result = random_proxy(None)
        assert result is None

    def test_returns_string_when_proxies_is_string(self):
        """Should return the same string when proxies is a string."""
        proxy = "http://proxy.example.com:8080"
        result = random_proxy(proxy)
        assert result == proxy

    def test_returns_proxy_from_sequence(self):
        """Should return a proxy from the sequence."""
        proxies = ["http://proxy1.com:8080", "http://proxy2.com:8080", "http://proxy3.com:8080"]
        result = random_proxy(proxies)
        assert result in proxies

    def test_returns_none_when_proxies_is_empty_list(self):
        """Should return None when proxies is an empty list."""
        result = random_proxy([])
        assert result is None


class TestIsValidProxyUrl:
    """Test cases for the is_valid_proxy_url function."""

    @pytest.mark.parametrize(
        "proxy_url",
        [
            "http://proxy.example.com:8080",
            "https://proxy.example.com:8080",
            "socks4://proxy.example.com:1080",
            "socks5://proxy.example.com:1080",
            "socks5h://proxy.example.com:1080",
            "socks5://user:pass@proxy.example.com:1080",
            "socks5h://user:pass@proxy.example.com:1080",
            "http://proxy.example.com:8080/",
            "https://user:pass@proxy.example.com:443",
        ],
    )
    def test_valid_proxy_urls(self, proxy_url: str):
        """Should return True for valid proxy URLs."""
        assert is_valid_proxy_url(proxy_url) is True

    @pytest.mark.parametrize(
        "proxy_url",
        [
            "ftp://proxy.example.com:21",
            "ssh://proxy.example.com:22",
            "telnet://proxy.example.com:23",
            "http://proxy.example.com",  # No port
            "https://proxy.example.com",  # No port
            "socks5://proxy.example.com",  # No port
            "socks4://user:pass@proxy.example.com:1080",  # SOCKS4 with auth
            "http://proxy.example.com:8080/path/to/resource",  # Extra path
            "https://proxy.example.com:8080/api/proxy",  # Extra path
            "http://:8080",  # No hostname
            "invalid-url",  # Invalid URL format
            "",  # Empty string
            "http://",  # Incomplete URL
            "://proxy.example.com:8080",  # No scheme
        ],
    )
    def test_invalid_proxy_urls(self, proxy_url: str):
        """Should return False for invalid proxy URLs."""
        assert is_valid_proxy_url(proxy_url) is False

    def test_malformed_url_exception(self):
        """Should return False when URL parsing raises an exception."""
        # This should trigger an exception in urlparse
        malformed_url = "http://[invalid-ipv6-address]:8080"
        assert is_valid_proxy_url(malformed_url) is False


class TestFetchProxies:
    """Test cases for the fetch_proxies function."""

    @pytest.fixture
    def http_server(self):
        """Create and start HTTP server for testing."""
        server = HTTPServer(host="127.0.0.1", port=0)
        server.start()
        yield server
        server.stop()

    @pytest.mark.asyncio
    async def test_fetch_valid_proxies(self, http_server: HTTPServer):
        """Should successfully fetch and validate proxy list."""
        valid_proxies = [
            "http://proxy1.example.com:8080",
            "https://proxy2.example.com:8080",
            "socks5://proxy3.example.com:1080",
        ]
        proxy_content = "\n".join(valid_proxies)

        def handler(_request: Request) -> Response:
            return Response(proxy_content, content_type="text/plain")

        http_server.expect_request("/proxies").respond_with_handler(handler)
        url = f"http://127.0.0.1:{http_server.port}/proxies"

        result = await fetch_proxies(url)
        assert result.is_ok()
        assert result.value == valid_proxies

    @pytest.mark.asyncio
    async def test_fetch_proxies_with_duplicates_and_empty_lines(self, http_server: HTTPServer):
        """Should handle duplicates and empty lines correctly."""
        proxy_content = """
        http://proxy1.example.com:8080

        https://proxy2.example.com:8080
        http://proxy1.example.com:8080

        socks5://proxy3.example.com:1080
        """

        def handler(_request: Request) -> Response:
            return Response(proxy_content, content_type="text/plain")

        http_server.expect_request("/proxies").respond_with_handler(handler)
        url = f"http://127.0.0.1:{http_server.port}/proxies"

        result = await fetch_proxies(url)
        assert result.is_ok()
        expected = [
            "http://proxy1.example.com:8080",
            "https://proxy2.example.com:8080",
            "socks5://proxy3.example.com:1080",
        ]
        assert result.value == expected

    @pytest.mark.asyncio
    async def test_fetch_proxies_with_invalid_proxy(self, http_server: HTTPServer):
        """Should return error when encountering invalid proxy."""
        proxy_content = """
        http://proxy1.example.com:8080
        ftp://invalid.proxy.com:21
        https://proxy2.example.com:8080
        """

        def handler(_request: Request) -> Response:
            return Response(proxy_content, content_type="text/plain")

        http_server.expect_request("/proxies").respond_with_handler(handler)
        url = f"http://127.0.0.1:{http_server.port}/proxies"

        result = await fetch_proxies(url)
        assert result.is_err()
        assert "Invalid proxy URL: ftp://invalid.proxy.com:21" in str(result.error)

    @pytest.mark.asyncio
    async def test_fetch_proxies_empty_response(self, http_server: HTTPServer):
        """Should return error when no valid proxies found."""

        def handler(_request: Request) -> Response:
            return Response("", content_type="text/plain")

        http_server.expect_request("/proxies").respond_with_handler(handler)
        url = f"http://127.0.0.1:{http_server.port}/proxies"

        result = await fetch_proxies(url)
        assert result.is_err()
        assert "No valid proxies found" in str(result.error)

    @pytest.mark.asyncio
    async def test_fetch_proxies_http_error(self, http_server: HTTPServer):
        """Should return error when HTTP request fails."""
        http_server.expect_request("/proxies").respond_with_response(Response(status=404))
        url = f"http://127.0.0.1:{http_server.port}/proxies"

        result = await fetch_proxies(url)
        assert result.is_err()

    @pytest.mark.asyncio
    async def test_fetch_proxies_timeout(self):
        """Should return error when request times out."""
        # Use a non-routable IP to trigger timeout
        url = "http://10.255.255.1/proxies"

        result = await fetch_proxies(url, timeout=0.1)
        assert result.is_err()


class TestFetchProxiesSync:
    """Test cases for the fetch_proxies_sync function."""

    @pytest.fixture
    def http_server(self):
        """Create and start HTTP server for testing."""
        server = HTTPServer(host="127.0.0.1", port=0)
        server.start()
        yield server
        server.stop()

    def test_fetch_valid_proxies_sync(self, http_server: HTTPServer):
        """Should successfully fetch and validate proxy list synchronously."""
        valid_proxies = [
            "http://proxy1.example.com:8080",
            "https://proxy2.example.com:8080",
            "socks5://proxy3.example.com:1080",
        ]
        proxy_content = "\n".join(valid_proxies)

        def handler(_request: Request) -> Response:
            return Response(proxy_content, content_type="text/plain")

        http_server.expect_request("/proxies").respond_with_handler(handler)
        url = f"http://127.0.0.1:{http_server.port}/proxies"

        result = fetch_proxies_sync(url)
        assert result.is_ok()
        assert result.value == valid_proxies

    def test_fetch_proxies_sync_with_invalid_proxy(self, http_server: HTTPServer):
        """Should return error when encountering invalid proxy synchronously."""
        proxy_content = """
        http://proxy1.example.com:8080
        invalid-proxy-url
        https://proxy2.example.com:8080
        """

        def handler(_request: Request) -> Response:
            return Response(proxy_content, content_type="text/plain")

        http_server.expect_request("/proxies").respond_with_handler(handler)
        url = f"http://127.0.0.1:{http_server.port}/proxies"

        result = fetch_proxies_sync(url)
        assert result.is_err()
        assert "Invalid proxy URL: invalid-proxy-url" in str(result.error)

    def test_fetch_proxies_sync_http_error(self, http_server: HTTPServer):
        """Should return error when HTTP request fails synchronously."""
        http_server.expect_request("/proxies").respond_with_response(Response(status=500))
        url = f"http://127.0.0.1:{http_server.port}/proxies"

        result = fetch_proxies_sync(url)
        assert result.is_err()
