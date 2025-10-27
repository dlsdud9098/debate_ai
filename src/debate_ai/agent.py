"""Agent implementation for debate system."""

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel
from debate_ai.llm_provider import LLMProvider


class AgentResponse(BaseModel):
    """Response from an agent including metadata."""

    agent_id: str
    role: str
    content: str
    timestamp: datetime


class Vote(BaseModel):
    """Vote from an agent on the current debate state."""

    agent_id: str
    decision: Literal["agree", "disagree", "needs_revision"]
    reasoning: str
    timestamp: datetime


class Agent:
    """An agent that can process prompts and return responses."""

    def __init__(
        self, agent_id: str, role: str, llm_provider: Optional[LLMProvider] = None
    ) -> None:
        """Initialize an agent.

        Args:
            agent_id: Unique identifier for this agent
            role: Role of the agent (e.g., analyst, critic, supporter)
            llm_provider: Optional LLM provider for generating responses
        """
        self.agent_id = agent_id
        self.role = role
        self.llm_provider = llm_provider

    async def process(self, prompt: str) -> str:
        """Process a prompt and return a response.

        Args:
            prompt: The prompt to process

        Returns:
            The agent's response
        """
        if self.llm_provider:
            return await self.llm_provider.generate(prompt)

        # Fallback for backward compatibility
        return f"Agent {self.agent_id} ({self.role}) received: {prompt}"

    async def process_with_metadata(self, prompt: str) -> AgentResponse:
        """Process a prompt and return a response with metadata.

        Args:
            prompt: The prompt to process

        Returns:
            AgentResponse with content and metadata
        """
        content = await self.process(prompt)
        return AgentResponse(
            agent_id=self.agent_id,
            role=self.role,
            content=content,
            timestamp=datetime.now(),
        )

    async def vote(self, topic: str, current_responses: List[str]) -> Vote:
        """Vote on the current state of the debate.

        Args:
            topic: The debate topic
            current_responses: List of current responses in the debate

        Returns:
            Vote with decision and reasoning
        """
        # Build voting prompt
        responses_text = "\n".join(
            [f"- {response}" for response in current_responses]
        )
        prompt = f"""Topic: {topic}

Current responses:
{responses_text}

Based on the above responses, do you agree with the current consensus, disagree, or think it needs revision?
Respond with one of: agree, disagree, needs_revision

Also provide your reasoning."""

        # Get LLM response
        if self.llm_provider:
            response = await self.llm_provider.generate(prompt)
        else:
            response = "agree - All points are valid"

        # Parse response to extract decision
        response_lower = response.lower()
        if "agree" in response_lower and "disagree" not in response_lower:
            decision = "agree"
        elif "disagree" in response_lower:
            decision = "disagree"
        else:
            decision = "needs_revision"

        return Vote(
            agent_id=self.agent_id,
            decision=decision,
            reasoning=response,
            timestamp=datetime.now(),
        )
