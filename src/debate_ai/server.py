"""MCP server for debate AI system."""

from typing import Any, Callable, Dict, List
from mcp.server import Server


class DebateServer:
    """MCP server for multi-agent debate system."""

    def __init__(self) -> None:
        """Initialize the debate server."""
        self.mcp_server = Server("debate-ai")
        self._tools: List[Dict[str, Any]] = []

    async def ping(self) -> str:
        """Health check endpoint."""
        return "pong"

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a tool with the MCP server."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            tool_info = {"name": func.__name__, "function": func}
            self._tools.append(tool_info)
            return func

        return decorator

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools."""
        return self._tools
