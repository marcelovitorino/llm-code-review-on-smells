"""
Base LLM Provider

Abstract base class for all LLM providers.
Defines the interface that all providers must implement.
"""
from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model_name: str):
        """Initialize the provider with a model name."""
        self.model_name = model_name
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float,
        top_p: float,
        max_tokens: int,
    ) -> str:
        """Generate a response for a given prompt."""
        raise NotImplementedError
