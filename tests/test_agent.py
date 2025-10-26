"""Tests for Agent communication."""

import pytest
from debate_ai.agent import Agent
from debate_ai.llm_provider import MockLLMProvider


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
