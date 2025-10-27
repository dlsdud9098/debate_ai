"""MCP server for debate AI system."""

from typing import Any, Callable, Dict, List
from mcp.server import Server
from debate_ai.agent import Agent
from debate_ai.debate_graph import DebateGraph


class DebateServer:
    """MCP server for multi-agent debate system."""

    def __init__(self) -> None:
        """Initialize the debate server."""
        self.mcp_server = Server("debate-ai")
        self._tools: List[Dict[str, Any]] = []
        self._agents: List[Agent] = []

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

    def register_debate_tool(self, agents: List[Agent]) -> None:
        """Register the debate_on_topic tool with the given agents.

        Args:
            agents: List of agents to participate in debates
        """
        self._agents = agents

        async def debate_on_topic(
            topic: str, max_rounds: int = 3, check_consensus: bool = True
        ) -> Dict[str, Any]:
            """Run a multi-agent debate on a given topic.

            Args:
                topic: The topic to debate
                max_rounds: Maximum number of debate rounds
                check_consensus: Whether to check for consensus

            Returns:
                Dictionary with debate results
            """
            graph = DebateGraph(agents=self._agents)
            result = await graph.run(
                topic=topic, max_rounds=max_rounds, check_consensus=check_consensus
            )

            return {
                "topic": result.topic,
                "consensus_reached": result.consensus_reached,
                "round_number": result.round_number,
                "total_responses": len(result.responses),
            }

        # Register the tool
        tool_info = {"name": "debate_on_topic", "function": debate_on_topic}
        self._tools.append(tool_info)
