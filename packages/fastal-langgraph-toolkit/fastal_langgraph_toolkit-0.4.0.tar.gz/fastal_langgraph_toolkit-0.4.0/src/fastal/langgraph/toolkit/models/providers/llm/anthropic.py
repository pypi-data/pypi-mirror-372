"""Anthropic LLM provider implementation.

This module provides the Anthropic-specific implementation for language models,
supporting Claude models with their specific configuration requirements.
"""

from typing import Any

from ....exceptions import ConfigurationError
from ...base import BaseProvider

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicLLMProvider(BaseProvider):
    """Anthropic LLM provider implementation.
    
    Supports all Anthropic Claude models with customizable parameters
    including temperature and max tokens.
    """

    def __init__(self, provider_config: Any, model_name: str, **kwargs):
        """Initialize the Anthropic provider.
        
        Args:
            provider_config: Anthropic-specific configuration
            model_name: Name of the Anthropic model to use (e.g., 'claude-3-sonnet')
            **kwargs: Additional parameters to pass to the model
        """
        super().__init__(provider_config)
        self.model_name = model_name
        self.kwargs = kwargs

    def _create_model(self) -> Any:
        """Create the Anthropic chat model instance.
        
        Returns:
            Configured ChatAnthropic instance
            
        Raises:
            ConfigurationError: If Anthropic provider is not available
        """
        if not ANTHROPIC_AVAILABLE:
            raise ConfigurationError(
                "Anthropic provider not available. Install: uv add langchain-anthropic"
            )

        # Extract common parameters with defaults from config
        temperature = self.kwargs.get('temperature', self.config.temperature)
        max_tokens = self.kwargs.get('max_tokens', self.config.max_tokens)

        # Build model configuration
        model_config = {
            'model': self.model_name,
            'api_key': self.config.api_key,
            'base_url': self.config.base_url,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'timeout': self.config.timeout,
        }

        # Add any additional kwargs not already handled
        excluded_keys = {'temperature', 'max_tokens'}
        for key, value in self.kwargs.items():
            if key not in excluded_keys:
                model_config[key] = value

        return ChatAnthropic(**model_config)
    
    def is_available(self) -> bool:
        """Check if Anthropic provider is available (module installed + API key).
        
        Returns:
            True if Anthropic is available and has API key
        """
        return ANTHROPIC_AVAILABLE and bool(self.config.api_key)
    
    async def is_available_async(self) -> bool:
        """Test real Anthropic API connectivity using configured model.
        
        Tests the actual configured model to detect when models are deprecated.
        
        Returns:
            True if Anthropic API is reachable with configured model
        """
        if not self.is_available():
            return False
            
        try:
            # Test with the actual configured model
            test_model = ChatAnthropic(
                model=self.model_name,  # Use configured model
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=5,  # Short timeout for health check
                max_tokens=1
            )
            
            # Send minimal test message
            response = await test_model.ainvoke([{"role": "user", "content": "hi"}])
            return bool(response and response.content)
            
        except Exception:
            return False
