"""Tests for MCP server initialization."""

import pytest
from debate_ai.server import DebateServer


class TestMCPServerInitialization:
    """Test MCP server can be initialized."""

    def test_server_can_be_initialized(self) -> None:
        """Test that MCP server can be created."""
        server = DebateServer()
        assert server is not None
        assert isinstance(server, DebateServer)

    async def test_server_responds_to_ping(self) -> None:
        """Test that MCP server responds to health check."""
        server = DebateServer()
        response = await server.ping()
        assert response is not None
        assert response == "pong"
