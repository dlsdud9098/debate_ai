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
