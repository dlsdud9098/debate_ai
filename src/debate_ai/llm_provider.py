"""LLM provider abstraction layer."""

from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The LLM's response
        """
        pass


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def __init__(self, response: str = "Mock response") -> None:
        """Initialize the mock provider.

        Args:
            response: The response to return
        """
        self.response = response
        self.last_prompt: Optional[str] = None

    async def generate(self, prompt: str) -> str:
        """Generate a mock response.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The mock response
        """
        self.last_prompt = prompt
        return self.response


class FailingLLMProvider(LLMProvider):
    """Mock LLM provider that always fails."""

    def __init__(self, error_message: str = "LLM API error") -> None:
        """Initialize the failing provider.

        Args:
            error_message: The error message to raise
        """
        self.error_message = error_message

    async def generate(self, prompt: str) -> str:
        """Generate a response (always fails).

        Args:
            prompt: The prompt to send to the LLM

        Raises:
            Exception: Always raises an exception
        """
        raise Exception(self.error_message)
