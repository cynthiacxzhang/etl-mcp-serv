from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, List, Optional

try:
    import mcp
    _HAS_MCP = True
except Exception:
    mcp = None  # type: ignore
    _HAS_MCP = False

# internal registry
_REGISTRY: Dict[str, Callable[..., Any]] = {}


def _register(name: str, func: Callable[..., Any]) -> None:
    _REGISTRY[name] = func


def tools(_func: Optional[Callable] = None, **mcp_decorator_kwargs):
    """Wrapper around mcp.tool that also records the decorated callable locally.

    Supports both `@tools` and `@tools(...)` usage.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # If `mcp` is available, use its decorator so tools are also visible to MCP.
        if _HAS_MCP and hasattr(mcp, "tool"):
            decorated = mcp.tool(**mcp_decorator_kwargs)(func)
        else:
            # Fallback: use the original function as the decorated callable.
            decorated = func
        name = mcp_decorator_kwargs.get("name") or getattr(func, "__name__", None) or func.__name__
        _register(name, decorated)
        try:
            decorated.__etl_tool_name__ = name  # attach metadata
        except Exception:
            pass
        return decorated

    if _func is None:
        return decorator
    return decorator(_func)


# alias for compatibility: users may expect `@tool()`
tool = tools


def list_tools() -> List[str]:
    return list(_REGISTRY.keys())


def get_tool(name: str) -> Optional[Callable[..., Any]]:
    return _REGISTRY.get(name)


def call_tool(name: str, *args, **kwargs) -> Any:
    func = get_tool(name)
    if func is None:
        raise KeyError(f"tool not found: {name}")
    res = func(*args, **kwargs)
    if asyncio.iscoroutine(res):
        return asyncio.run(res)
    return res


async def call_tool_async(name: str, *args, **kwargs) -> Any:
    func = get_tool(name)
    if func is None:
        raise KeyError(f"tool not found: {name}")
    res = func(*args, **kwargs)
    if asyncio.iscoroutine(res):
        return await res
    return res


__all__ = ["tools", "tool", "list_tools", "get_tool", "call_tool", "call_tool_async"]
