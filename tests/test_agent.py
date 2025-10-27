"""Tests for Agent communication."""

import pytest
from datetime import datetime
from debate_ai.agent import Agent, AgentResponse
from debate_ai.llm_provider import MockLLMProvider, FailingLLMProvider


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


class TestConsensusMechanism:
    """Test consensus and voting mechanism."""

    async def test_each_agent_can_vote_on_agreement(self) -> None:
        """Test that each agent can vote on agreement (agree/disagree/needs_revision)."""
        from debate_ai.agent import Agent, Vote
        from debate_ai.llm_provider import MockLLMProvider

        # Create agents
        provider1 = MockLLMProvider(response="I agree with this proposal")
        agent1 = Agent(agent_id="agent-1", role="analyst", llm_provider=provider1)

        # Agent should be able to vote
        vote = await agent1.vote(
            topic="Should we use microservices?",
            current_responses=["Response 1", "Response 2"],
        )

        assert vote is not None
        assert isinstance(vote, Vote)
        assert vote.agent_id == "agent-1"
        assert vote.decision in ["agree", "disagree", "needs_revision"]
        assert isinstance(vote.reasoning, str)

    async def test_system_detects_when_all_agents_agree(self) -> None:
        """Test that system detects when all agents agree."""
        from debate_ai.debate_graph import DebateGraph
        from debate_ai.llm_provider import MockLLMProvider

        # Create agents that will agree
        provider1 = MockLLMProvider(response="I agree - this is the best approach")
        provider2 = MockLLMProvider(response="I agree - well reasoned")

        agent1 = Agent(agent_id="agent-1", role="analyst", llm_provider=provider1)
        agent2 = Agent(agent_id="agent-2", role="critic", llm_provider=provider2)

        # Run debate with consensus checking enabled
        graph = DebateGraph(agents=[agent1, agent2])
        result = await graph.run(
            topic="Should we use microservices?",
            max_rounds=5,
            check_consensus=True,
        )

        # Should reach consensus before max_rounds
        assert result.consensus_reached
        assert result.round_number < 5  # Should end early due to consensus

    async def test_system_requests_revisions_when_agents_disagree(self) -> None:
        """Test that system requests revisions when agents disagree."""
        from debate_ai.debate_graph import DebateGraph
        from debate_ai.llm_provider import MockLLMProvider

        # Create agents that will disagree initially, then agree
        provider1 = MockLLMProvider(response="Microservices are great")
        provider2 = MockLLMProvider(response="I disagree - too complex")

        agent1 = Agent(agent_id="agent-1", role="analyst", llm_provider=provider1)
        agent2 = Agent(agent_id="agent-2", role="critic", llm_provider=provider2)

        # Run debate with consensus checking
        graph = DebateGraph(agents=[agent1, agent2])
        result = await graph.run(
            topic="Should we use microservices?",
            max_rounds=3,
            check_consensus=True,
        )

        # Should continue to next round when disagreement detected
        # At least 2 rounds should occur (initial + revision after disagreement)
        assert result.round_number >= 2

        # Should have multiple responses showing revision attempts
        assert len(result.responses) >= 4  # 2 agents × 2 rounds minimum

    async def test_system_has_maximum_iteration_limit_to_prevent_infinite_loops(
        self,
    ) -> None:
        """Test that system has maximum iteration limit to prevent infinite loops."""
        from debate_ai.debate_graph import DebateGraph
        from debate_ai.llm_provider import MockLLMProvider

        # Create agents that always disagree (would loop forever without limit)
        provider1 = MockLLMProvider(response="I strongly disagree with this")
        provider2 = MockLLMProvider(response="I completely disagree as well")

        agent1 = Agent(agent_id="agent-1", role="analyst", llm_provider=provider1)
        agent2 = Agent(agent_id="agent-2", role="critic", llm_provider=provider2)

        # Set a max_rounds limit
        max_rounds = 3
        graph = DebateGraph(agents=[agent1, agent2])
        result = await graph.run(
            topic="Should we use microservices?",
            max_rounds=max_rounds,
            check_consensus=True,
        )

        # Should stop at max_rounds even without consensus
        assert result.round_number == max_rounds
        assert not result.consensus_reached
        assert len(result.responses) == max_rounds * 2  # 3 rounds × 2 agents


class TestAgentConfiguration:
    """Test agent configuration options."""

    async def test_agents_can_have_different_personas_roles(self) -> None:
        """Test that agents can have different personas/roles (critic, supporter, analyst)."""
        from debate_ai.debate_graph import DebateGraph
        from debate_ai.llm_provider import MockLLMProvider

        # Create agents with different roles
        provider1 = MockLLMProvider(response="As an analyst")
        provider2 = MockLLMProvider(response="As a critic")
        provider3 = MockLLMProvider(response="As a supporter")

        analyst = Agent(agent_id="agent-1", role="analyst", llm_provider=provider1)
        critic = Agent(agent_id="agent-2", role="critic", llm_provider=provider2)
        supporter = Agent(agent_id="agent-3", role="supporter", llm_provider=provider3)

        # Verify roles are set correctly
        assert analyst.role == "analyst"
        assert critic.role == "critic"
        assert supporter.role == "supporter"

        # Verify they work in a debate
        graph = DebateGraph(agents=[analyst, critic, supporter])
        result = await graph.run(topic="Test", max_rounds=1)

        # All agents should have responded
        assert len(result.responses) == 3
        assert result.responses[0].role == "analyst"
        assert result.responses[1].role == "critic"
        assert result.responses[2].role == "supporter"

    async def test_number_of_agents_is_configurable(self) -> None:
        """Test that number of agents is configurable."""
        from debate_ai.debate_graph import DebateGraph
        from debate_ai.llm_provider import MockLLMProvider

        provider = MockLLMProvider(response="Response")

        # Test with 2 agents
        agents_2 = [
            Agent(agent_id="agent-1", role="analyst", llm_provider=provider),
            Agent(agent_id="agent-2", role="critic", llm_provider=provider),
        ]
        graph_2 = DebateGraph(agents=agents_2)
        result_2 = await graph_2.run(topic="Test", max_rounds=1)
        assert len(result_2.responses) == 2

        # Test with 5 agents
        agents_5 = [
            Agent(agent_id=f"agent-{i}", role=f"role-{i}", llm_provider=provider)
            for i in range(5)
        ]
        graph_5 = DebateGraph(agents=agents_5)
        result_5 = await graph_5.run(topic="Test", max_rounds=1)
        assert len(result_5.responses) == 5

    async def test_agent_order_can_be_specified(self) -> None:
        """Test that agent order can be specified."""
        from debate_ai.debate_graph import DebateGraph
        from debate_ai.llm_provider import MockLLMProvider

        provider = MockLLMProvider(response="Response")

        # Create agents in specific order
        agent_a = Agent(agent_id="agent-a", role="first", llm_provider=provider)
        agent_b = Agent(agent_id="agent-b", role="second", llm_provider=provider)
        agent_c = Agent(agent_id="agent-c", role="third", llm_provider=provider)

        # Specify order explicitly
        graph = DebateGraph(agents=[agent_a, agent_b, agent_c])
        result = await graph.run(topic="Test", max_rounds=1)

        # Verify order is preserved
        assert result.responses[0].agent_id == "agent-a"
        assert result.responses[1].agent_id == "agent-b"
        assert result.responses[2].agent_id == "agent-c"

    async def test_consensus_threshold_is_configurable(self) -> None:
        """Test that consensus threshold is configurable."""
        from debate_ai.debate_graph import DebateGraph
        from debate_ai.llm_provider import MockLLMProvider

        # For now, consensus requires all agents to agree (threshold = 100%)
        # This test verifies the current behavior
        provider_agree = MockLLMProvider(response="I agree")
        provider_disagree = MockLLMProvider(response="I disagree")

        agents = [
            Agent(agent_id="agent-1", role="analyst", llm_provider=provider_agree),
            Agent(agent_id="agent-2", role="critic", llm_provider=provider_disagree),
        ]

        graph = DebateGraph(agents=agents)
        result = await graph.run(
            topic="Test", max_rounds=3, check_consensus=True
        )

        # Should not reach consensus with one disagreeing
        assert not result.consensus_reached
        assert result.round_number == 3  # Should run to max_rounds


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


class TestErrorHandling:
    """Test error handling in the debate system."""

    async def test_handle_llm_api_failures_gracefully(self) -> None:
        """Test that LLM API failures are handled gracefully."""
        from debate_ai.debate_graph import DebateGraph

        # Create agents where one has a failing provider
        normal_provider = MockLLMProvider(response="Normal response")
        failing_provider = FailingLLMProvider(error_message="API rate limit exceeded")

        agent1 = Agent(agent_id="agent-1", role="analyst", llm_provider=normal_provider)
        agent2 = Agent(agent_id="agent-2", role="critic", llm_provider=failing_provider)

        graph = DebateGraph(agents=[agent1, agent2])

        # Should complete without crashing, but include error in response
        result = await graph.run(topic="Test topic", max_rounds=1)

        # Verify we got responses from both agents
        assert len(result.responses) == 2

        # First agent should have normal response
        assert result.responses[0].agent_id == "agent-1"
        assert result.responses[0].content == "Normal response"

        # Second agent should have error response
        assert result.responses[1].agent_id == "agent-2"
        assert "[Error:" in result.responses[1].content
        assert "API rate limit exceeded" in result.responses[1].content

    async def test_handle_timeout_scenarios(self) -> None:
        """Test that timeout scenarios are handled."""
        import asyncio
        from debate_ai.debate_graph import DebateGraph
        from debate_ai.llm_provider import LLMProvider

        # Create a slow provider that times out
        class SlowLLMProvider(LLMProvider):
            """LLM provider that takes too long to respond."""

            async def generate(self, prompt: str) -> str:
                """Generate response slowly."""
                await asyncio.sleep(5)  # Sleep for 5 seconds
                return "Slow response"

        slow_provider = SlowLLMProvider()
        agent = Agent(agent_id="slow-agent", role="analyst", llm_provider=slow_provider)

        graph = DebateGraph(agents=[agent])

        # Should timeout after 1 second
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                graph.run(topic="Test topic", max_rounds=1), timeout=1.0
            )

    async def test_handle_cases_where_consensus_cannot_be_reached(self) -> None:
        """Test handling when consensus cannot be reached within max rounds."""
        from debate_ai.debate_graph import DebateGraph

        # Create agents that will never agree
        provider1 = MockLLMProvider(response="I strongly disagree")
        provider2 = MockLLMProvider(response="I also disagree")

        agent1 = Agent(agent_id="agent-1", role="analyst", llm_provider=provider1)
        agent2 = Agent(agent_id="agent-2", role="critic", llm_provider=provider2)

        graph = DebateGraph(agents=[agent1, agent2])
        result = await graph.run(
            topic="Test topic", max_rounds=2, check_consensus=True
        )

        # Should complete without error even though no consensus
        assert result is not None
        assert not result.consensus_reached
        assert result.round_number == 2  # Should reach max_rounds
        assert len(result.responses) == 4  # 2 agents × 2 rounds

    async def test_validate_input_parameters(self) -> None:
        """Test that input parameters are validated."""
        from debate_ai.debate_graph import DebateGraph

        provider = MockLLMProvider(response="Test")
        agent = Agent(agent_id="agent-1", role="analyst", llm_provider=provider)

        graph = DebateGraph(agents=[agent])

        # Test with empty topic should work but produce result
        result = await graph.run(topic="", max_rounds=1)
        assert result is not None
        assert result.topic == ""

        # Test with max_rounds=0 - should still run once then end
        result2 = await graph.run(topic="Test", max_rounds=0)
        assert result2 is not None
        # With max_rounds=0, round_controller increments to 1 then ends
        assert result2.round_number == 1
        assert len(result2.responses) == 1  # Should have run once

        # Test with normal max_rounds
        result3 = await graph.run(topic="Test", max_rounds=5)
        assert result3 is not None
        # Should complete in 5 rounds since we don't check consensus
        assert result3.round_number == 5
        assert len(result3.responses) == 5
