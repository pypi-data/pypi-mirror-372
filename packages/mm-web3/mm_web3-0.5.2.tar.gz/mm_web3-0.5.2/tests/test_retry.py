"""Tests for retry utilities."""

from mm_result import Result

from mm_web3 import retry_with_node_and_proxy, retry_with_proxy


class TestRetryWithNodeAndProxy:
    async def test_success_on_first_try(self) -> None:
        async def func(_node: str, _proxy: str | None) -> Result[str]:
            return Result.ok("success")

        result = await retry_with_node_and_proxy(3, "node1", "proxy1", func)
        assert result.is_ok()
        assert result.value == "success"
        assert result.extra is not None
        assert "retry_logs" in result.extra
        assert len(result.extra["retry_logs"]) == 1

    async def test_success_on_second_try(self) -> None:
        attempts = 0

        async def func(_node: str, _proxy: str | None) -> Result[str]:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                return Result.err("first_failure")
            return Result.ok("success")

        result = await retry_with_node_and_proxy(3, "node1", "proxy1", func)
        assert result.is_ok()
        assert result.value == "success"
        assert result.extra is not None
        assert "retry_logs" in result.extra
        assert len(result.extra["retry_logs"]) == 2

    async def test_all_attempts_fail(self) -> None:
        async def func(_node: str, _proxy: str | None) -> Result[str]:
            return Result.err("failure")

        result = await retry_with_node_and_proxy(3, "node1", "proxy1", func)
        assert result.is_err()
        assert result.error == "failure"
        assert result.extra is not None
        assert "retry_logs" in result.extra
        assert len(result.extra["retry_logs"]) == 3

    async def test_multiple_nodes_and_proxies(self) -> None:
        nodes = ["node1", "node2"]
        proxies = ["proxy1", "proxy2"]
        attempts = 0

        async def func(_node: str, _proxy: str | None) -> Result[str]:
            nonlocal attempts
            attempts += 1
            if attempts == 2:
                return Result.ok("success")
            return Result.err("failure")

        result = await retry_with_node_and_proxy(3, nodes, proxies, func)
        assert result.is_ok()
        assert result.value == "success"
        assert result.extra is not None
        assert "retry_logs" in result.extra
        assert len(result.extra["retry_logs"]) == 2


class TestRetryWithProxy:
    async def test_success_on_first_try(self) -> None:
        async def func(_proxy: str | None) -> Result[str]:
            return Result.ok("success")

        result = await retry_with_proxy(3, "proxy1", func)
        assert result.is_ok()
        assert result.value == "success"
        assert result.extra is not None
        assert "retry_logs" in result.extra
        assert len(result.extra["retry_logs"]) == 1

    async def test_success_on_second_try(self) -> None:
        attempts = 0

        async def func(_proxy: str | None) -> Result[str]:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                return Result.err("first_failure")
            return Result.ok("success")

        result = await retry_with_proxy(3, "proxy1", func)
        assert result.is_ok()
        assert result.value == "success"
        assert result.extra is not None
        assert "retry_logs" in result.extra
        assert len(result.extra["retry_logs"]) == 2

    async def test_all_attempts_fail(self) -> None:
        async def func(_proxy: str | None) -> Result[str]:
            return Result.err("failure")

        result = await retry_with_proxy(3, "proxy1", func)
        assert result.is_err()
        assert result.error == "failure"
        assert result.extra is not None
        assert "retry_logs" in result.extra
        assert len(result.extra["retry_logs"]) == 3

    async def test_multiple_proxies(self) -> None:
        proxies = ["proxy1", "proxy2"]
        attempts = 0

        async def func(_proxy: str | None) -> Result[str]:
            nonlocal attempts
            attempts += 1
            if attempts == 2:
                return Result.ok("success")
            return Result.err("failure")

        result = await retry_with_proxy(3, proxies, func)
        assert result.is_ok()
        assert result.value == "success"
        assert result.extra is not None
        assert "retry_logs" in result.extra
        assert len(result.extra["retry_logs"]) == 2
