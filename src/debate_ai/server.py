"""MCP server for debate AI system."""

from mcp.server import Server


class DebateServer:
    """MCP server for multi-agent debate system."""

    def __init__(self) -> None:
        """Initialize the debate server."""
        self.mcp_server = Server("debate-ai")
