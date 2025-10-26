"""Agent implementation for debate system."""


class Agent:
    """An agent that can process prompts and return responses."""

    def __init__(self, agent_id: str, role: str) -> None:
        """Initialize an agent.

        Args:
            agent_id: Unique identifier for this agent
            role: Role of the agent (e.g., analyst, critic, supporter)
        """
        self.agent_id = agent_id
        self.role = role

    async def process(self, prompt: str) -> str:
        """Process a prompt and return a response.

        Args:
            prompt: The prompt to process

        Returns:
            The agent's response
        """
        # Simple implementation to pass the test
        # Will be replaced with actual LLM integration
        return f"Agent {self.agent_id} ({self.role}) received: {prompt}"
