"""Tests for Agent communication."""

import pytest
from debate_ai.agent import Agent


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
