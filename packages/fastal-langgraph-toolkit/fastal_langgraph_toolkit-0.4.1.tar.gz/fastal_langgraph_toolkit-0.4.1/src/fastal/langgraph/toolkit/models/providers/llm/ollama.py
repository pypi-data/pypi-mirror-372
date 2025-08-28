"""Ollama LLM provider implementation.

This module provides the Ollama-specific implementation for language models,
supporting locally-hosted models through the Ollama service.
"""

from typing import Any

from ....exceptions import ConfigurationError
from ...base import BaseProvider

try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class OllamaLLMProvider(BaseProvider):
    """Ollama LLM provider implementation.
    
    Supports all models available through a local Ollama installation,
    providing a way to run models locally without external API calls.
    """

    def __init__(self, provider_config: Any, model_name: str, **kwargs):
        """Initialize the Ollama provider.
        
        Args:
            provider_config: Ollama-specific configuration
            model_name: Name of the Ollama model to use (e.g., 'llama2', 'mistral')
            **kwargs: Additional parameters to pass to the model
        """
        super().__init__(provider_config)
        self.model_name = model_name
        self.kwargs = kwargs

    def _create_model(self) -> Any:
        """Create the Ollama chat model instance.
        
        Returns:
            Configured ChatOllama instance
            
        Raises:
            ConfigurationError: If Ollama provider is not available
        """
        if not OLLAMA_AVAILABLE:
            raise ConfigurationError(
                "Ollama provider not available. Install: uv add langchain-ollama"
            )

        # Extract common parameters with defaults from config
        temperature = self.kwargs.get('temperature', self.config.temperature)

        # Build model configuration
        model_config = {
            'model': self.model_name,
            'base_url': self.config.base_url,
            'temperature': temperature,
            'timeout': self.config.timeout,
        }

        # Add any additional kwargs not already handled
        excluded_keys = {'temperature'}
        for key, value in self.kwargs.items():
            if key not in excluded_keys:
                model_config[key] = value

        return ChatOllama(**model_config)
    
    def is_available(self) -> bool:
        """Check if Ollama provider is available (module installed + service running).
        
        Returns:
            True if Ollama is available and service is configured
        """
        return OLLAMA_AVAILABLE and bool(self.config.base_url)
    
    async def is_available_async(self) -> bool:
        """Test real Ollama service connectivity using configured model.
        
        Tests the actual configured model to detect when models are not available.
        
        Returns:
            True if Ollama service is reachable with configured model
        """
        if not self.is_available():
            return False
            
        try:
            # Test with the actual configured model
            test_model = ChatOllama(
                model=self.model_name,  # Use configured model
                base_url=self.config.base_url,
                timeout=5,  # Short timeout for health check
            )
            
            # Send minimal test message
            response = await test_model.ainvoke([{"role": "user", "content": "hi"}])
            return bool(response and response.content)
            
        except Exception:
            return False
