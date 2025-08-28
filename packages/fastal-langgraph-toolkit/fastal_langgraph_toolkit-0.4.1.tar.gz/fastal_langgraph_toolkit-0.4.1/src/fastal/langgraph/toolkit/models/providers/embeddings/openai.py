"""OpenAI embedding provider implementation.

This module provides the OpenAI-specific implementation for text embeddings,
supporting all OpenAI embedding models including text-embedding-ada-002 and newer.
"""

from typing import TYPE_CHECKING, Any

from ....exceptions import ConfigurationError
from ...base import BaseProvider

if TYPE_CHECKING:
    from langchain_openai import OpenAIEmbeddings

try:
    from langchain_openai import OpenAIEmbeddings
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIEmbeddingProvider(BaseProvider):
    """OpenAI embedding provider implementation.
    
    Provides high-quality text embeddings using OpenAI's embedding models,
    suitable for semantic search and similarity comparisons.
    """

    def __init__(self, provider_config: Any, model_name: str, **kwargs):
        """Initialize the OpenAI embedding provider.
        
        Args:
            provider_config: OpenAI-specific configuration
            model_name: Name of the embedding model (e.g., 'text-embedding-ada-002')
            **kwargs: Additional parameters to pass to the model
        """
        super().__init__(provider_config)
        self.model_name = model_name
        self.kwargs = kwargs

    def _create_model(self) -> "OpenAIEmbeddings":
        """Create the OpenAI embeddings instance.
        
        Returns:
            Configured OpenAIEmbeddings instance
            
        Raises:
            ConfigurationError: If OpenAI provider is not available
        """
        if not OPENAI_AVAILABLE:
            raise ConfigurationError(
                "OpenAI provider not available. Install: uv add langchain-openai"
            )

        # Build model configuration
        model_config = {
            'model': self.model_name,
            'api_key': self.config.api_key,
            'base_url': self.config.base_url,
            'organization': self.config.organization,
            'timeout': self.config.timeout,
        }

        # Add any additional kwargs
        model_config.update(self.kwargs)

        return OpenAIEmbeddings(**model_config)
    
    def is_available(self) -> bool:
        """Check if OpenAI provider is available (module installed + API key).
        
        Returns:
            True if OpenAI is available and has API key
        """
        return OPENAI_AVAILABLE and bool(self.config.api_key)
    
    async def is_available_async(self) -> bool:
        """Test real OpenAI embeddings API connectivity using configured model.
        
        Tests the actual configured model to detect when models are deprecated.
        
        Returns:
            True if OpenAI embeddings API is reachable with configured model
        """
        if not self.is_available():
            return False
            
        try:
            # Test with the actual configured model
            test_embeddings = OpenAIEmbeddings(
                model=self.model_name,  # Use configured model
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                organization=self.config.organization,
                timeout=5,  # Short timeout for health check
            )
            
            # Send minimal test embedding
            embedding = await test_embeddings.aembed_query("test")
            return bool(embedding and len(embedding) > 0)
            
        except Exception:
            return False
