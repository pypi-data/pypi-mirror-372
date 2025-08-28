import time
import functools
import logging
from typing import Callable, Optional, Any
import asyncio  


logger = logging.getLogger("timer")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

def timed(
    *,
    logger: Callable[[str], Any] = logger.info,
    unit: str = "ms",
    fmt: str = "[{func_name}] elapsed: {elapsed:.3f}{unit}",
):
    """
    通用计时装饰器（支持同步 & 异步函数）

    参数
    ----
    logger : callable
        输出函数，默认 logging.info，可换成 print 等
    unit : str
        时间单位，可选 "s"、"ms"、"us"
    fmt : str
        输出格式模板，支持 {func_name} 和 {elapsed}
    """
    factor = {"s": 1, "ms": 1e3, "us": 1e6}[unit]

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    return await fn(*args, **kwargs)
                finally:
                    elapsed = (time.perf_counter() - start) * factor
                    logger(fmt.format(func_name=fn.__name__, elapsed=elapsed, unit=unit))
            return async_wrapper
        else:
            @functools.wraps(fn)
            def sync_wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    return fn(*args, **kwargs)
                finally:
                    elapsed = (time.perf_counter() - start) * factor
                    logger(fmt.format(func_name=fn.__name__, elapsed=elapsed, unit=unit))
            return sync_wrapper
    return decorator


# ------------------ 使用示例 ------------------
if __name__ == "__main__":
    import asyncio

    @timed(unit="ms")
    def add(a, b):
        time.sleep(0.5)
        return a + b

    @timed(unit="ms")
    async def async_add(a, b):
        await asyncio.sleep(0.3)
        return a + b

    # 同步
    print(add(1, 2))

    # 异步
    asyncio.run(async_add(3, 4))