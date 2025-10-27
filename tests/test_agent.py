"""Tests for Agent communication."""

import pytest
from datetime import datetime
from debate_ai.agent import Agent, AgentResponse
from debate_ai.llm_provider import MockLLMProvider


class TestMultiAgentSystem:
    """Test multi-agent debate system."""

    async def test_system_can_initialize_multiple_agents_with_different_roles(self) -> None:
        """Test that system can initialize multiple agents with different roles."""
        agents = [
            Agent(agent_id="agent-1", role="analyst"),
            Agent(agent_id="agent-2", role="critic"),
            Agent(agent_id="agent-3", role="supporter"),
        ]

        assert len(agents) == 3
        assert agents[0].role == "analyst"
        assert agents[1].role == "critic"
        assert agents[2].role == "supporter"
        assert agents[0].agent_id == "agent-1"
        assert agents[1].agent_id == "agent-2"
        assert agents[2].agent_id == "agent-3"

    async def test_first_agent_generates_initial_response_to_query(self) -> None:
        """Test that first agent generates initial response to a query."""
        from debate_ai.debate_graph import DebateGraph

        # Create a debate graph with one agent
        mock_provider = MockLLMProvider(response="I believe microservices provide better scalability")
        agent = Agent(agent_id="agent-1", role="analyst", llm_provider=mock_provider)

        graph = DebateGraph(agents=[agent])
        result = await graph.run(topic="Should we use microservices?")

        assert result is not None
        assert len(result.responses) == 1
        assert result.responses[0].agent_id == "agent-1"
        assert "microservices" in result.responses[0].content.lower()

    async def test_second_agent_receives_first_response_and_provides_feedback(self) -> None:
        """Test that second agent receives first agent's response and provides feedback."""
        from debate_ai.debate_graph import DebateGraph

        # Create two agents with different perspectives
        provider1 = MockLLMProvider(response="Microservices provide better scalability")
        provider2 = MockLLMProvider(response="But they add operational complexity")

        agent1 = Agent(agent_id="agent-1", role="analyst", llm_provider=provider1)
        agent2 = Agent(agent_id="agent-2", role="critic", llm_provider=provider2)

        graph = DebateGraph(agents=[agent1, agent2])
        result = await graph.run(topic="Should we use microservices?")

        # Verify both agents responded
        assert len(result.responses) == 2
        assert result.responses[0].agent_id == "agent-1"
        assert result.responses[1].agent_id == "agent-2"

        # Verify second agent's prompt included first agent's response
        assert "scalability" in provider2.last_prompt.lower()
        assert "agent-1" in provider2.last_prompt

    async def test_first_agent_can_revise_based_on_feedback(self) -> None:
        """Test that first agent can revise based on feedback from other agents."""
        from debate_ai.debate_graph import DebateGraph

        # Create two agents
        provider1 = MockLLMProvider(response="Microservices provide better scalability")
        provider2 = MockLLMProvider(response="But they add operational complexity")

        agent1 = Agent(agent_id="agent-1", role="analyst", llm_provider=provider1)
        agent2 = Agent(agent_id="agent-2", role="critic", llm_provider=provider2)

        # Run debate for 2 rounds so agent-1 can revise
        graph = DebateGraph(agents=[agent1, agent2])
        result = await graph.run(topic="Should we use microservices?", max_rounds=2)

        # In round 1: agent-1, agent-2
        # In round 2: agent-1 (revision), agent-2 (revision)
        # Total: 4 responses
        assert len(result.responses) == 4
        assert result.responses[0].agent_id == "agent-1"  # Initial
        assert result.responses[1].agent_id == "agent-2"  # Feedback
        assert result.responses[2].agent_id == "agent-1"  # Revision
        assert result.responses[3].agent_id == "agent-2"  # Revision

        # Verify agent-1's second response includes context from agent-2's feedback
        # Check that provider1 received the feedback in its prompt during round 2
        assert result.round_number == 2


class TestAgentCommunication:
    """Test single agent communication."""

    async def test_agent_can_receive_prompt_and_return_response(self) -> None:
        """Test that agent can process a prompt and return a response."""
        agent = Agent(agent_id="test-agent", role="analyst")

        prompt = "What is 2 + 2?"
        response = await agent.process(prompt)

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0

    async def test_agent_can_use_different_llm_providers(self) -> None:
        """Test that agent can use different LLM providers."""
        # Create a mock provider
        mock_provider = MockLLMProvider(response="Mock response from LLM")

        # Create agent with the provider
        agent = Agent(agent_id="test-agent", role="analyst", llm_provider=mock_provider)

        prompt = "Test prompt"
        response = await agent.process(prompt)

        assert response == "Mock response from LLM"
        assert mock_provider.last_prompt == prompt

    async def test_agent_response_includes_metadata(self) -> None:
        """Test that agent response includes metadata (agent_id, timestamp)."""
        mock_provider = MockLLMProvider(response="Test response")
        agent = Agent(agent_id="test-agent-123", role="critic", llm_provider=mock_provider)

        before_time = datetime.now()
        response = await agent.process_with_metadata("Test prompt")
        after_time = datetime.now()

        assert isinstance(response, AgentResponse)
        assert response.agent_id == "test-agent-123"
        assert response.role == "critic"
        assert response.content == "Test response"
        assert response.timestamp >= before_time
        assert response.timestamp <= after_time
