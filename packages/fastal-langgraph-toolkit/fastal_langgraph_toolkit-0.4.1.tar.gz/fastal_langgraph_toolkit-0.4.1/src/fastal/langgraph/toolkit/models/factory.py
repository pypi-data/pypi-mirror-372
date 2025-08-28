"""Factory classes for creating LLM and embedding provider instances.

This module provides factory classes that abstract the creation of provider
instances, handling configuration and provider selection logic.
"""

import logging
import warnings
from typing import Any

try:
    from langchain_core.embeddings import Embeddings
    from langchain_core.language_models.chat_models import BaseChatModel
except ImportError as e:
    logging.error(f"Core LangChain imports failed: {e}")
    raise

from ..exceptions import ConfigurationError
from .providers.embeddings import (
    BedrockEmbeddingProvider,
    OllamaEmbeddingProvider,
    OpenAIEmbeddingProvider,
)
from .providers.llm import (
    AnthropicLLMProvider,
    BedrockLLMProvider,
    OllamaLLMProvider,
    OpenAILLMProvider,
)
from .providers.stt import (
    OpenAISTTProvider,
)

logger = logging.getLogger(__name__)

# Check provider availability for LLM/Embeddings
PROVIDERS_AVAILABLE = {
    'openai': False,
    'anthropic': False,
    'ollama': False,
    'bedrock': False,
}

try:
    import langchain_openai
    PROVIDERS_AVAILABLE['openai'] = True
except ImportError:
    pass

try:
    import langchain_anthropic
    PROVIDERS_AVAILABLE['anthropic'] = True
except ImportError:
    pass

try:
    import langchain_ollama
    PROVIDERS_AVAILABLE['ollama'] = True
except ImportError:
    pass

try:
    import boto3
    import langchain_aws
    PROVIDERS_AVAILABLE['bedrock'] = True
except ImportError:
    pass

# Check provider availability for STT (different requirements)
STT_PROVIDERS_AVAILABLE = {
    'openai': False,
    'google': False,
    'azure': False,
}

try:
    import openai
    STT_PROVIDERS_AVAILABLE['openai'] = True
except ImportError:
    pass

# Future: add Google and Azure STT checks here


class LLMFactory:
    """Factory for creating LLM instances.
    
    This factory handles the creation of different LLM providers based on
    configuration, abstracting away the specific implementation details.
    
    .. deprecated:: 0.4.0
        LLMFactory is deprecated and will be made private in v1.0.0.
        Use :class:`ModelFactory.create_llm` instead.
    """

    _provider_classes = {
        "openai": OpenAILLMProvider,
        "anthropic": AnthropicLLMProvider,
        "ollama": OllamaLLMProvider,
        "bedrock": BedrockLLMProvider,
    }

    @classmethod
    def create_llm(
        cls,
        provider: str,
        model_name: str,
        provider_config: Any | None = None,
        **kwargs
    ) -> BaseChatModel:
        """Create an LLM instance.
        
        .. deprecated:: 0.4.0
            Use :meth:`ModelFactory.create_llm` instead.
            Direct usage of LLMFactory will be removed in v1.0.0.
        
        Args:
            provider: The LLM provider to use
            model_name: Name of the model to instantiate
            provider_config: Provider-specific configuration (uses default if None)
            **kwargs: Additional arguments to pass to the provider
        
        Returns:
            Configured LLM instance ready for use
            
        Raises:
            ConfigurationError: If the provider is unknown or unavailable
        """
        warnings.warn(
            "LLMFactory is deprecated and will be made private in v1.0.0. "
            "Use ModelFactory.create_llm() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        if provider not in cls._provider_classes:
            raise ConfigurationError(f"Unknown LLM provider: {provider}")

        # Check if provider module is available
        if not PROVIDERS_AVAILABLE.get(provider, False):
            raise ConfigurationError(
                f"LLM provider '{provider}' is not available. "
                f"Install with: uv add langchain-{provider}"
            )

        if provider_config is None:
            raise ConfigurationError(
                f"Provider configuration is required. "
                f"Please provide configuration for '{provider}' provider."
            )

        provider_class = cls._provider_classes[provider]
        provider_instance = provider_class(provider_config, model_name, **kwargs)

        return provider_instance.model



class EmbeddingFactory:
    """Factory for creating embedding instances.
    
    This factory handles the creation of different embedding providers based on
    configuration, abstracting away the specific implementation details.
    
    .. deprecated:: 0.4.0
        EmbeddingFactory is deprecated and will be made private in v1.0.0.
        Use :class:`ModelFactory.create_embeddings` instead.
    """

    _provider_classes = {
        "openai": OpenAIEmbeddingProvider,
        "ollama": OllamaEmbeddingProvider,
        "bedrock": BedrockEmbeddingProvider,
    }

    @classmethod
    def create_embeddings(
        cls,
        provider: str,
        model_name: str,
        provider_config: Any | None = None,
        **kwargs
    ) -> Embeddings:
        """Create an embeddings instance.
        
        .. deprecated:: 0.4.0
            Use :meth:`ModelFactory.create_embeddings` instead.
            Direct usage of EmbeddingFactory will be removed in v1.0.0.
        
        Args:
            provider: The embedding provider to use
            model_name: Name of the model to instantiate
            provider_config: Provider-specific configuration (uses default if None)
            **kwargs: Additional arguments to pass to the provider
        
        Returns:
            Configured embeddings instance ready for use
            
        Raises:
            ConfigurationError: If the provider is unknown or unavailable
        """
        warnings.warn(
            "EmbeddingFactory is deprecated and will be made private in v1.0.0. "
            "Use ModelFactory.create_embeddings() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        if provider not in cls._provider_classes:
            raise ConfigurationError(f"Unknown embedding provider: {provider}")

        # Check if provider module is available
        if not PROVIDERS_AVAILABLE.get(provider, False):
            raise ConfigurationError(
                f"Embedding provider '{provider}' is not available. "
                f"Install with: uv add langchain-{provider}"
            )

        if provider_config is None:
            raise ConfigurationError(
                f"Provider configuration is required. "
                f"Please provide configuration for '{provider}' provider."
            )

        provider_class = cls._provider_classes[provider]
        provider_instance = provider_class(provider_config, model_name, **kwargs)

        return provider_instance.model



class STTFactory:
    """Factory for creating speech-to-text instances.
    
    This factory handles the creation of different STT providers based on
    configuration, abstracting away the specific implementation details.
    
    .. deprecated:: 0.4.0
        STTFactory is deprecated and will be made private in v1.0.0.
        Use :class:`ModelFactory.create_stt` instead.
    """

    _provider_classes = {
        "openai": OpenAISTTProvider,
    }

    @classmethod
    def create_stt(
        cls,
        provider: str,
        model_name: str | None = None,
        provider_config: Any | None = None,
        **kwargs
    ) -> Any:
        """Create a speech-to-text instance.
        
        .. deprecated:: 0.4.0
            Use :meth:`ModelFactory.create_stt` instead.
            Direct usage of STTFactory will be removed in v1.0.0.
        
        Args:
            provider: The STT provider to use
            model_name: Name of the model to instantiate (if applicable)
            provider_config: Provider-specific configuration (uses default if None)
            **kwargs: Additional arguments to pass to the provider
        
        Returns:
            Configured STT instance ready for use
            
        Raises:
            ConfigurationError: If the provider is unknown or unavailable
        """
        warnings.warn(
            "STTFactory is deprecated and will be made private in v1.0.0. "
            "Use ModelFactory.create_stt() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        if provider not in cls._provider_classes:
            raise ConfigurationError(f"Unknown STT provider: {provider}")

        # Check if STT provider module is available (uses different requirements than LLM)
        if not STT_PROVIDERS_AVAILABLE.get(provider, False):
            install_msg = {
                'openai': "uv add openai",
                'google': "uv add google-cloud-speech",  
                'azure': "uv add azure-cognitiveservices-speech"
            }.get(provider, f"uv add {provider}")
            
            raise ConfigurationError(
                f"STT provider '{provider}' is not available. "
                f"Install with: {install_msg}"
            )

        if provider_config is None:
            raise ConfigurationError(
                f"Provider configuration is required. "
                f"Please provide configuration for '{provider}' provider."
            )

        provider_class = cls._provider_classes[provider]
        provider_instance = provider_class(provider_config, model_name, **kwargs)

        return provider_instance


def get_available_providers() -> dict[str, dict[str, bool]]:
    """Get information about available providers.
    
    This function checks which providers have their required dependencies
    installed and returns availability information.
    
    Returns:
        Dictionary mapping provider types to availability status
    """
    return {
        'llm_providers': {
            provider: PROVIDERS_AVAILABLE.get(provider, False)
            for provider in PROVIDERS_AVAILABLE.keys()
            if provider in ["openai", "anthropic", "ollama", "bedrock"]
        },
        'embedding_providers': {
            provider: PROVIDERS_AVAILABLE.get(provider, False)
            for provider in PROVIDERS_AVAILABLE.keys()
            if provider in ["openai", "ollama", "bedrock"]
        },
        'stt_providers': {
            provider: STT_PROVIDERS_AVAILABLE.get(provider, False)
            for provider in STT_PROVIDERS_AVAILABLE.keys()
            if provider in ["openai"]
        }
    }
