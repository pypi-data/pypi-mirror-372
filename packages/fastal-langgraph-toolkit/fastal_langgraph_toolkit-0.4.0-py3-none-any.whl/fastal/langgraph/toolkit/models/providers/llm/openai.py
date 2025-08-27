"""OpenAI LLM provider implementation.

This module provides the OpenAI-specific implementation for language models,
supporting all OpenAI chat models including GPT-4 and GPT-3.5 variants.
"""

from typing import TYPE_CHECKING, Any

from ....exceptions import ConfigurationError
from ...base import BaseProvider

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI

try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAILLMProvider(BaseProvider):
    """OpenAI LLM provider implementation with full GPT-5 support.
    
    Supports all OpenAI chat models including GPT-5 variants with automatic
    parameter mapping and advanced features. Works seamlessly with both
    chat and vision capabilities.
    
    GPT-5 specific features:
    - Automatic max_tokens → max_completion_tokens mapping
    - reasoning_effort control (minimal, low, medium, high)
    - verbosity control (low, medium, high)
    - Custom tools support with plaintext
    - Vision model compatibility
    """
    
    # GPT-5 model prefixes for automatic detection
    GPT5_MODELS = ('gpt-5', 'gpt-5-mini', 'gpt-5-nano')
    
    # GPT-5 specific parameters that should go in extra_body
    GPT5_EXTRA_BODY_PARAMS = {'reasoning_effort', 'verbosity'}

    def __init__(self, provider_config: Any, model_name: str, **kwargs):
        """Initialize the OpenAI provider.
        
        Args:
            provider_config: OpenAI-specific configuration
            model_name: Name of the OpenAI model to use (e.g., 'gpt-4')
            **kwargs: Additional parameters to pass to the model
        """
        super().__init__(provider_config)
        self.model_name = model_name
        self.kwargs = kwargs

    def _create_model(self) -> "ChatOpenAI":
        """Create the OpenAI chat model instance with GPT-5 support.
        
        Returns:
            Configured ChatOpenAI instance
            
        Raises:
            ConfigurationError: If OpenAI provider is not available
        """
        if not OPENAI_AVAILABLE:
            raise ConfigurationError(
                "OpenAI provider not available. Install: uv add langchain-openai"
            )

        # Detect if this is a GPT-5 model
        is_gpt5 = any(self.model_name.startswith(prefix) for prefix in self.GPT5_MODELS)
        
        # Extract all config attributes that might be present
        # This allows the config to contain any parameters without the provider knowing ahead of time
        config_dict = vars(self.config) if hasattr(self.config, '__dict__') else {}
        
        # Handle temperature parameter
        # First check kwargs, then config
        temperature = self.kwargs.get('temperature', config_dict.get('temperature'))
        
        # For GPT-5, normalize temperature: only use it if it's exactly 1
        if is_gpt5 and temperature is not None and temperature != 1:
            # Log a warning if a logger is available
            import warnings
            warnings.warn(
                f"GPT-5 models only support temperature=1. Ignoring temperature={temperature}",
                UserWarning
            )
            temperature = None  # Omit temperature parameter for GPT-5
        
        # Handle token parameter based on model type
        if is_gpt5:
            # GPT-5 uses max_completion_tokens parameter
            max_tokens_param = 'max_completion_tokens'
            # Check kwargs, then config
            max_tokens_value = self.kwargs.get('max_completion_tokens', 
                                              self.kwargs.get('max_tokens', 
                                              config_dict.get('max_tokens')))
        else:
            # GPT-4 and earlier use max_tokens
            max_tokens_param = 'max_tokens'
            max_tokens_value = self.kwargs.get('max_tokens', config_dict.get('max_tokens'))

        # Build base model configuration
        model_config = {
            'model': self.model_name,
            'api_key': config_dict.get('api_key'),
            'base_url': config_dict.get('base_url'),
            'organization': config_dict.get('organization'),
            max_tokens_param: max_tokens_value,
            'timeout': config_dict.get('timeout', 30),
        }
        
        # Only add temperature if it's not None (make it optional)
        if temperature is not None:
            model_config['temperature'] = temperature
        
        # Handle extra_body for GPT-5 specific parameters
        extra_body = self.kwargs.get('extra_body', {})
        
        # Process GPT-5 specific parameters from both kwargs AND config
        if is_gpt5:
            for param in self.GPT5_EXTRA_BODY_PARAMS:
                # Check kwargs first, then config
                value = self.kwargs.get(param) or config_dict.get(param)
                if value:
                    extra_body[param] = value
        
        # LangChain's ChatOpenAI expects model_kwargs with extra_body inside
        if extra_body:
            model_config['model_kwargs'] = {'extra_body': extra_body}

        # Add additional kwargs, excluding already handled ones
        excluded_keys = {'temperature', 'max_tokens', 'max_completion_tokens', 
                        'extra_body'} | self.GPT5_EXTRA_BODY_PARAMS
        additional_kwargs = {k: v for k, v in self.kwargs.items() 
                           if k not in excluded_keys}
        model_config.update(additional_kwargs)

        return ChatOpenAI(**model_config)
    
    def is_available(self) -> bool:
        """Check if OpenAI provider is available (module installed + API key).
        
        Returns:
            True if OpenAI is available and has API key
        """
        return OPENAI_AVAILABLE and bool(self.config.api_key)
    
    async def is_available_async(self) -> bool:
        """Test real OpenAI API connectivity using configured model.
        
        Tests the actual configured model to detect when models are deprecated.
        
        Returns:
            True if OpenAI API is reachable with configured model
        """
        if not self.is_available():
            return False
            
        try:
            # Test with the actual configured model
            test_model = ChatOpenAI(
                model=self.model_name,  # Use configured model
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                organization=self.config.organization,
                timeout=5,  # Short timeout for health check
                max_tokens=1
            )
            
            # Send minimal test message
            response = await test_model.ainvoke([{"role": "user", "content": "hi"}])
            return bool(response and response.content)
            
        except Exception:
            return False
