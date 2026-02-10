"""
Google Colab AI LLM Integration

This integration uses the google.colab.ai library to generate text using
Google's models available in Colab (Gemini, Gemma, etc.).

Note: This integration only works in Google Colab environment.
"""
from integrations.base_llm_provider import BaseLLMProvider


# Available Colab models with their details
COLAB_MODELS = {
    'colab_gemini-2.0-flash': {
        'model_name': 'google/gemini-2.0-flash',
        'description': 'Google Gemini 2.0 Flash - Fast and efficient'
    },
    'colab_gemini-2.0-flash-lite': {
        'model_name': 'google/gemini-2.0-flash-lite',
        'description': 'Google Gemini 2.0 Flash Lite - Lightweight version'
    },
    'colab_gemini-1.5-pro': {
        'model_name': 'google/gemini-1.5-pro',
        'description': 'Google Gemini 1.5 Pro - Most capable for complex tasks'
    },
}


class ColabLLMProvider(BaseLLMProvider):
    """Integration for Google Colab AI models."""
    
    def __init__(self, model_key: str):
        """Initialize Colab AI integration.
        
        Args:
            model_key: Key from COLAB_MODELS (e.g., 'colab_gemini-2.0-flash').
        """
        if model_key not in COLAB_MODELS:
            raise ValueError(
                f"Model '{model_key}' not found in Colab models. "
                f"Available: {list(COLAB_MODELS.keys())}"
            )
        
        model_config = COLAB_MODELS[model_key]
        self.model_key = model_key
        self.model_name = model_config['model_name']
        self.description = model_config['description']
        super().__init__(self.model_name)
        
        try:
            from google.colab import ai
            self.client = ai
        except ImportError:
            raise ImportError(
                "google.colab.ai is not available. "
                "Run this notebook in Google Colab."
            )
    
    def generate(
        self,
        prompt: str,
        temperature: float,
        top_p: float,
        max_tokens: int,
    ) -> str:
        """Generate response using Colab AI.
        
        Note: the Colab API wrapper does not expose decoding parameters
        such as temperature/top_p/max_tokens; these arguments are accepted
        for interface consistency but ignored.
        """
        return self.client.generate_text(prompt, model_name=self.model_name)
