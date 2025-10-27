"""LangGraph-based debate system for multi-agent communication."""

from typing import List, Optional, TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from debate_ai.agent import Agent, AgentResponse


class DebateState(TypedDict):
    """State for the debate graph."""

    topic: str
    responses: Annotated[List[AgentResponse], operator.add]
    round_number: int
    consensus_reached: bool


class DebateResult:
    """Result of a debate session."""

    def __init__(self, state: DebateState) -> None:
        """Initialize debate result from state."""
        self.topic = state["topic"]
        self.responses = state["responses"]
        self.round_number = state["round_number"]
        self.consensus_reached = state["consensus_reached"]


class DebateGraph:
    """LangGraph-based multi-agent debate system."""

    def __init__(self, agents: List[Agent]) -> None:
        """Initialize the debate graph.

        Args:
            agents: List of agents to participate in the debate
        """
        self.agents = agents
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(DebateState)

        # Add a node for each agent
        for i, agent in enumerate(self.agents):
            node_name = f"agent_{i}"
            workflow.add_node(node_name, self._create_agent_node(agent, i))

        # Add a round controller node
        workflow.add_node("round_controller", self._round_controller_node)

        # Set entry point to first agent
        if self.agents:
            workflow.set_entry_point("agent_0")

        # Connect agents in sequence
        for i in range(len(self.agents) - 1):
            workflow.add_edge(f"agent_{i}", f"agent_{i+1}")

        # Last agent goes to round controller
        if self.agents:
            workflow.add_edge(f"agent_{len(self.agents)-1}", "round_controller")

        # Round controller decides: continue to agent_0 or END
        workflow.add_conditional_edges(
            "round_controller",
            self._should_continue,
            {
                "continue": "agent_0",
                "end": END,
            },
        )

        return workflow.compile()

    def _create_agent_node(self, agent: Agent, agent_index: int):
        """Create a node function for an agent.

        Args:
            agent: The agent for this node
            agent_index: Index of this agent in the agent list

        Returns:
            Async function that processes the agent's turn
        """

        async def agent_node(state: DebateState) -> dict:
            """Process one agent's turn in the debate."""
            # Build prompt with context from previous responses
            if state["responses"]:
                context = "\n".join(
                    [
                        f"{resp.agent_id} ({resp.role}): {resp.content}"
                        for resp in state["responses"]
                    ]
                )
                prompt = f"Topic: {state['topic']}\n\nPrevious responses:\n{context}\n\nYour response:"
            else:
                prompt = f"Topic: {state['topic']}\n\nProvide your initial response:"

            # Get agent's response with error handling
            try:
                response = await agent.process_with_metadata(prompt)
                return {"responses": [response]}
            except Exception as e:
                # Create error response instead of crashing
                from datetime import datetime

                error_response = AgentResponse(
                    agent_id=agent.agent_id,
                    role=agent.role,
                    content=f"[Error: {str(e)}]",
                    timestamp=datetime.now(),
                )
                return {"responses": [error_response]}

        return agent_node

    async def _round_controller_node(self, state: DebateState) -> dict:
        """Control round progression.

        Args:
            state: Current debate state

        Returns:
            Updated state with incremented round number and consensus status
        """
        updates = {"round_number": state["round_number"] + 1}

        # Check for consensus if enabled
        if hasattr(self, "_check_consensus") and self._check_consensus:
            consensus = await self._check_for_consensus(state)
            updates["consensus_reached"] = consensus

        return updates

    async def _check_for_consensus(self, state: DebateState) -> bool:
        """Check if all agents agree on the current state.

        Args:
            state: Current debate state

        Returns:
            True if consensus is reached, False otherwise
        """
        # Need at least one round completed to check consensus
        if state["round_number"] < 1 or not state["responses"]:
            return False

        # Get all agents to vote
        votes = []
        response_contents = [resp.content for resp in state["responses"]]

        for agent in self.agents:
            vote = await agent.vote(state["topic"], response_contents)
            votes.append(vote)

        # Check if all agents agree
        return all(vote.decision == "agree" for vote in votes)

    def _should_continue(self, state: DebateState) -> str:
        """Decide whether to continue the debate or end.

        Args:
            state: Current debate state

        Returns:
            "continue" if more rounds needed, "end" otherwise
        """
        # Check if consensus is reached
        if state["consensus_reached"]:
            return "end"

        # Check if we've reached max_rounds
        # round_number increments after each full round
        # So if round_number < max_rounds, continue
        if hasattr(self, "_max_rounds") and state["round_number"] < self._max_rounds:
            return "continue"

        return "end"

    async def run(
        self, topic: str, max_rounds: int = 1, check_consensus: bool = False
    ) -> DebateResult:
        """Run the debate on a given topic.

        Args:
            topic: The topic to debate
            max_rounds: Maximum number of debate rounds
            check_consensus: Whether to check for consensus after each round

        Returns:
            DebateResult containing all responses and metadata
        """
        # Store max_rounds and check_consensus for use in round controller
        self._max_rounds = max_rounds
        self._check_consensus = check_consensus

        initial_state: DebateState = {
            "topic": topic,
            "responses": [],
            "round_number": 0,
            "consensus_reached": False,
        }

        final_state = await self.graph.ainvoke(initial_state)
        return DebateResult(final_state)
