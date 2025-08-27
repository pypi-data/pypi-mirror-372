"""Ollama embedding provider implementation.

This module provides the Ollama-specific implementation for text embeddings,
supporting locally-hosted embedding models through the Ollama service.
"""

from typing import Any

from ....exceptions import ConfigurationError
from ...base import BaseProvider

try:
    from langchain_ollama import OllamaEmbeddings
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class OllamaEmbeddingProvider(BaseProvider):
    """Ollama embedding provider implementation.
    
    Provides text embeddings using locally-hosted models through Ollama,
    enabling privacy-preserving embedding generation without external API calls.
    """

    def __init__(self, provider_config: Any, model_name: str, **kwargs):
        """Initialize the Ollama embedding provider.
        
        Args:
            provider_config: Ollama-specific configuration
            model_name: Name of the Ollama embedding model
            **kwargs: Additional parameters to pass to the model
        """
        super().__init__(provider_config)
        self.model_name = model_name
        self.kwargs = kwargs

    def _create_model(self) -> Any:
        """Create the Ollama embeddings instance.
        
        Returns:
            Configured OllamaEmbeddings instance
            
        Raises:
            ConfigurationError: If Ollama provider is not available
        """
        if not OLLAMA_AVAILABLE:
            raise ConfigurationError(
                "Ollama provider not available. Install: uv add langchain-ollama"
            )

        # Build model configuration
        model_config = {
            'model': self.model_name,
            'base_url': self.config.base_url,
            'timeout': self.config.timeout,
        }

        # Add any additional kwargs
        model_config.update(self.kwargs)

        return OllamaEmbeddings(**model_config)
    
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
            test_embeddings = OllamaEmbeddings(
                model=self.model_name,  # Use configured model
                base_url=self.config.base_url,
                timeout=5,  # Short timeout for health check
            )
            
            # Send minimal test embedding
            embedding = await test_embeddings.aembed_query("test")
            return bool(embedding and len(embedding) > 0)
            
        except Exception:
            return False
