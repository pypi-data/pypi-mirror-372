"""Model factory module for creating LLM and embedding instances."""

from .factory import LLMFactory, EmbeddingFactory, STTFactory, get_available_providers
from .types import TranscriptionResult, AudioResult, TranscriptionSegment, AudioFormat

# Unified factory interface
class ModelFactory:
    """Unified factory for creating AI models including LLM, embeddings, and speech models."""
    
    @classmethod
    def create_llm(cls, provider: str, model: str, config: dict, **kwargs):
        """Create an LLM instance."""
        return LLMFactory.create_llm(provider, model, config, **kwargs)
    
    @classmethod
    def create_embeddings(cls, provider: str, model: str, config: dict, **kwargs):
        """Create an embeddings instance."""
        return EmbeddingFactory.create_embeddings(provider, model, config, **kwargs)
    
    @classmethod
    def create_stt(cls, provider: str, model: str = None, config: dict = None, **kwargs):
        """Create a speech-to-text instance.
        
        Args:
            provider: The STT provider to use (e.g., 'openai')
            model: Optional model name (defaults to provider's default)
            config: Provider configuration with credentials
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Configured STT provider instance
        """
        return STTFactory.create_stt(provider, model, config, **kwargs)
    
    @classmethod
    def get_available_providers(cls):
        """Get information about available providers."""
        return get_available_providers()


__all__ = [
    "ModelFactory",
    "LLMFactory", 
    "EmbeddingFactory",
    "STTFactory",
    "get_available_providers",
    "TranscriptionResult",
    "AudioResult", 
    "TranscriptionSegment",
    "AudioFormat",
]