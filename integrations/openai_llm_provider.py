"""
OpenAI LLM Integration

This integration uses the OpenAI API to generate text using OpenAI models
(GPT-4, GPT-3.5, etc.).

Requires an OpenAI API key configured via environment variable OPENAI_API_KEY
or passed as a parameter.
"""
import os
from typing import Optional

from integrations.base_llm_provider import BaseLLMProvider


# Available OpenAI models with their details
OPENAI_MODELS = {
    'openai_gpt-4.1': {
        'model_name': 'gpt-4.1',
        'description': 'OpenAI GPT-4.1 - Latest model'
    },
    'openai_gpt-4': {
        'model_name': 'gpt-4',
        'description': 'OpenAI GPT-4 - Advanced model'
    },
    'openai_gpt-4-turbo': {
        'model_name': 'gpt-4-turbo-preview',
        'description': 'OpenAI GPT-4 Turbo - Turbo version'
    },
    'openai_gpt-3.5-turbo': {
        'model_name': 'gpt-3.5-turbo',
        'description': 'OpenAI GPT-3.5 Turbo - Fast and economical'
    },
}


class OpenAILLMProvider(BaseLLMProvider):
    """Integration for OpenAI models."""
    
    def __init__(self, model_key: str, api_key: Optional[str] = None):
        """Initialize OpenAI integration.
        
        Args:
            model_key: Key from OPENAI_MODELS (e.g., 'openai_gpt-4.1').
            api_key: OpenAI API key (optional). If not provided, uses constants.OPENAI_API_KEY.
        """
        if model_key not in OPENAI_MODELS:
            raise ValueError(
                f"Model '{model_key}' not found in OpenAI models. "
                f"Available: {list(OPENAI_MODELS.keys())}"
            )
        
        model_config = OPENAI_MODELS[model_key]
        self.model_key = model_key
        self.model_name = model_config['model_name']
        self.description = model_config['description']
        super().__init__(self.model_name)
        
        try:
            from openai import OpenAI
            effective_api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
            if not effective_api_key:
                raise ValueError(
                    "OpenAI API key not configured. "
                    "Set OPENAI_API_KEY in start_here/experiments/constants.py or pass api_key."
                )
            self.client = OpenAI(api_key=effective_api_key)
        except ImportError:
            raise ImportError(
                "openai library not installed. "
                "Run: pip install openai"
            )
    
    def generate(
        self,
        prompt: str,
        temperature: float,
        top_p: float,
        max_tokens: int,
    ) -> str:
        """Generate response using OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
