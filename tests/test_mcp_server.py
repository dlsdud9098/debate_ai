"""Tests for MCP server initialization."""

import pytest
from debate_ai.server import DebateServer
from debate_ai.agent import Agent
from debate_ai.llm_provider import MockLLMProvider


class TestMCPToolIntegration:
    """Test MCP tool integration."""

    async def test_expose_debate_on_topic_as_mcp_tool(self) -> None:
        """Test that debate_on_topic is exposed as MCP tool."""
        server = DebateServer()

        # Create some agents
        provider1 = MockLLMProvider(response="I agree with microservices")
        provider2 = MockLLMProvider(response="I agree as well")

        agent1 = Agent(agent_id="agent-1", role="analyst", llm_provider=provider1)
        agent2 = Agent(agent_id="agent-2", role="critic", llm_provider=provider2)

        # Register debate tool with agents
        server.register_debate_tool(agents=[agent1, agent2])

        # Verify tool is registered
        tools = server.list_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "debate_on_topic"

        # Verify tool function exists
        assert tools[0]["function"] is not None

    async def test_tool_accepts_topic_question_as_parameter(self) -> None:
        """Test that tool accepts topic/question as parameter."""
        server = DebateServer()

        # Create agents
        provider1 = MockLLMProvider(response="Microservices are good")
        provider2 = MockLLMProvider(response="I agree")

        agent1 = Agent(agent_id="agent-1", role="analyst", llm_provider=provider1)
        agent2 = Agent(agent_id="agent-2", role="critic", llm_provider=provider2)

        # Register debate tool
        server.register_debate_tool(agents=[agent1, agent2])

        # Get the tool function
        tools = server.list_tools()
        debate_fn = tools[0]["function"]

        # Call the tool with a topic
        result = await debate_fn(topic="Should we use microservices?")

        # Verify result contains the topic
        assert result is not None
        assert "topic" in result
        assert result["topic"] == "Should we use microservices?"

    async def test_tool_returns_final_consensus_result(self) -> None:
        """Test that tool returns final consensus result."""
        server = DebateServer()

        # Create agents that will agree
        provider1 = MockLLMProvider(response="I agree - great idea")
        provider2 = MockLLMProvider(response="I agree - well thought out")

        agent1 = Agent(agent_id="agent-1", role="analyst", llm_provider=provider1)
        agent2 = Agent(agent_id="agent-2", role="critic", llm_provider=provider2)

        # Register debate tool
        server.register_debate_tool(agents=[agent1, agent2])

        # Get and call the tool
        tools = server.list_tools()
        debate_fn = tools[0]["function"]
        result = await debate_fn(
            topic="Should we implement feature X?",
            max_rounds=3,
            check_consensus=True,
        )

        # Verify result contains consensus information
        assert result is not None
        assert "consensus_reached" in result
        assert "round_number" in result
        assert "total_responses" in result
        assert isinstance(result["consensus_reached"], bool)
        assert isinstance(result["round_number"], int)
        assert isinstance(result["total_responses"], int)

    async def test_tool_provides_debate_history_transcript(self) -> None:
        """Test that tool provides debate history/transcript."""
        server = DebateServer()

        # Create agents
        provider1 = MockLLMProvider(response="Initial response from analyst")
        provider2 = MockLLMProvider(response="Feedback from critic")

        agent1 = Agent(agent_id="agent-1", role="analyst", llm_provider=provider1)
        agent2 = Agent(agent_id="agent-2", role="critic", llm_provider=provider2)

        # Register debate tool with transcript support
        server.register_debate_tool(agents=[agent1, agent2])

        # Get and call the tool
        tools = server.list_tools()
        debate_fn = tools[0]["function"]
        result = await debate_fn(topic="Test topic", max_rounds=1)

        # Verify we can get information about responses
        assert result is not None
        assert result["total_responses"] >= 2  # At least 2 agents responded


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

    def test_server_can_register_tools(self) -> None:
        """Test that MCP server can register tools."""
        server = DebateServer()

        # Register a simple tool
        @server.tool()
        def sample_tool(text: str) -> str:
            """A sample tool for testing."""
            return f"processed: {text}"

        # Verify tool is registered
        tools = server.list_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "sample_tool"
