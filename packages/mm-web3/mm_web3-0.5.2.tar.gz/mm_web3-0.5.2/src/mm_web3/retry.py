from collections.abc import Awaitable, Callable
from typing import TypeVar

from mm_result import Result

from mm_web3.node import Nodes, random_node
from mm_web3.proxy import Proxies, random_proxy

T = TypeVar("T")

# Function that takes (node, proxy) and returns an Awaitable[Result[T]]
FuncWithNodeAndProxy = Callable[[str, str | None], Awaitable[Result[T]]]

# Function that takes only (proxy) and returns an Awaitable[Result[T]]
FuncWithProxy = Callable[[str | None], Awaitable[Result[T]]]


async def retry_with_node_and_proxy[T](retries: int, nodes: Nodes, proxies: Proxies, func: FuncWithNodeAndProxy[T]) -> Result[T]:
    """
    Retry the given function multiple times with random node and proxy on each attempt.

    Args:
        retries: Number of attempts to make.
        nodes: Available nodes to randomly choose from.
        proxies: Available proxies to randomly choose from.
        func: Async function that accepts (node, proxy) and returns a Result.

    Returns:
        Result with success on first successful call, or last failure with logs of attempts.
    """
    res: Result[T] = Result.err("not_started")
    logs = []

    for _ in range(retries):
        node = random_node(nodes)
        proxy = random_proxy(proxies)
        res = await func(node, proxy)
        logs.append({"node": node, "proxy": proxy, "result": res.to_dict()})
        if res.is_ok():
            return Result.ok(res.unwrap(), {"retry_logs": logs})

    return Result.err(res.unwrap_err(), {"retry_logs": logs})


async def retry_with_proxy[T](retries: int, proxies: Proxies, func: FuncWithProxy[T]) -> Result[T]:
    """
    Retry the given function multiple times using a random proxy on each attempt.


    Args:
        retries: Number of attempts to make.
        proxies: Available proxies to randomly choose from.
        func: Async function that accepts (proxy) and returns a Result.

    Returns:
        Result with success on first successful call, or last failure with logs of attempts.
    """
    res: Result[T] = Result.err("not_started")
    logs = []

    for _ in range(retries):
        proxy = random_proxy(proxies)
        res = await func(proxy)
        logs.append({"proxy": proxy, "result": res.to_dict()})
        if res.is_ok():
            return Result.ok(res.unwrap(), {"retry_logs": logs})

    return Result.err(res.unwrap_err(), {"retry_logs": logs})
