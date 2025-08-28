"""OpenAI Speech-to-Text provider implementation using Whisper.

This module provides the OpenAI-specific implementation for speech-to-text,
supporting the Whisper model for audio transcription.
"""

import io
import logging
from typing import TYPE_CHECKING, Any, Optional

from ....exceptions import ConfigurationError
from ...base import BaseSTTProvider
from ...types import TranscriptionResult, TranscriptionSegment

if TYPE_CHECKING:
    from openai import OpenAI, AsyncOpenAI

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI, AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAISTTProvider(BaseSTTProvider):
    """OpenAI Whisper speech-to-text provider implementation.
    
    Supports audio transcription using OpenAI's Whisper model with
    various audio formats and language detection capabilities.
    """

    def __init__(self, provider_config: Any, model_name: str | None = None, **kwargs):
        """Initialize the OpenAI STT provider.
        
        Args:
            provider_config: OpenAI-specific configuration with api_key
            model_name: Model name (default: 'whisper-1')
            **kwargs: Additional parameters to pass to the transcription
        """
        super().__init__(provider_config, model_name or "whisper-1", **kwargs)
        self._client = None
        self._async_client = None

    def _create_model(self) -> "OpenAI":
        """Create the OpenAI client instance.
        
        Returns:
            Configured OpenAI client
            
        Raises:
            ConfigurationError: If OpenAI is not available
        """
        if not OPENAI_AVAILABLE:
            raise ConfigurationError(
                "OpenAI provider is not available. Install with: uv add openai"
            )

        # Validate configuration
        if not hasattr(self.config, 'api_key'):
            raise ConfigurationError(
                "OpenAI provider requires 'api_key' in configuration"
            )

        # Create client
        self._client = OpenAI(api_key=self.config.api_key)
        
        # Also prepare async client for async operations
        self._async_client = AsyncOpenAI(api_key=self.config.api_key)
        
        return self._client

    def transcribe(
        self, 
        audio_data: bytes,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "verbose_json",
        temperature: float = 0,
        **kwargs
    ) -> TranscriptionResult:
        """Transcribe audio to text using OpenAI Whisper.
        
        Args:
            audio_data: Audio file data in bytes
            language: ISO-639-1 language code (optional)
            prompt: Optional text to guide the model's style
            response_format: Format of the response (default: verbose_json)
            temperature: Sampling temperature (0-1)
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            TranscriptionResult with text and metadata
        """
        # Ensure model is initialized
        if self._client is None:
            self._create_model()

        # Create file-like object from bytes
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.mp3"  # OpenAI requires a filename

        # Build transcription parameters
        params = {
            "model": self.model_name,
            "file": audio_file,
            "response_format": response_format,
            "temperature": temperature,
        }
        
        if language:
            params["language"] = language
        if prompt:
            params["prompt"] = prompt
            
        # Add any additional kwargs
        params.update(kwargs)

        try:
            # Call OpenAI API
            response = self._client.audio.transcriptions.create(**params)
            
            # Parse response based on format
            if response_format == "verbose_json":
                # Extract segments if available
                segments = []
                if hasattr(response, 'segments') and response.segments:
                    segments = [
                        TranscriptionSegment(
                            text=seg.text,
                            start=seg.start,
                            end=seg.end,
                            confidence=None  # OpenAI doesn't provide confidence
                        )
                        for seg in response.segments
                    ]
                
                return TranscriptionResult(
                    text=response.text,
                    language=getattr(response, 'language', None),
                    confidence=None,  # OpenAI doesn't provide overall confidence
                    duration_seconds=getattr(response, 'duration', None),
                    segments=segments if segments else None,
                    warnings=None
                )
            else:
                # For simple formats, just return the text
                return TranscriptionResult(
                    text=str(response),
                    language=language,
                    confidence=None,
                    duration_seconds=None,
                    segments=None,
                    warnings=None
                )
                
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise ConfigurationError(f"OpenAI transcription failed: {str(e)}")

    async def atranscribe(
        self, 
        audio_data: bytes,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "verbose_json",
        temperature: float = 0,
        **kwargs
    ) -> TranscriptionResult:
        """Async transcribe audio to text using OpenAI Whisper.
        
        Args:
            audio_data: Audio file data in bytes
            language: ISO-639-1 language code (optional)
            prompt: Optional text to guide the model's style
            response_format: Format of the response (default: verbose_json)
            temperature: Sampling temperature (0-1)
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            TranscriptionResult with text and metadata
        """
        # Ensure async client is initialized
        if self._async_client is None:
            self._create_model()

        # Create file-like object from bytes
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.mp3"  # OpenAI requires a filename

        # Build transcription parameters
        params = {
            "model": self.model_name,
            "file": audio_file,
            "response_format": response_format,
            "temperature": temperature,
        }
        
        if language:
            params["language"] = language
        if prompt:
            params["prompt"] = prompt
            
        # Add any additional kwargs
        params.update(kwargs)

        try:
            # Call OpenAI API
            response = await self._async_client.audio.transcriptions.create(**params)
            
            # Parse response based on format
            if response_format == "verbose_json":
                # Extract segments if available
                segments = []
                if hasattr(response, 'segments') and response.segments:
                    segments = [
                        TranscriptionSegment(
                            text=seg.text,
                            start=seg.start,
                            end=seg.end,
                            confidence=None  # OpenAI doesn't provide confidence
                        )
                        for seg in response.segments
                    ]
                
                return TranscriptionResult(
                    text=response.text,
                    language=getattr(response, 'language', None),
                    confidence=None,  # OpenAI doesn't provide overall confidence
                    duration_seconds=getattr(response, 'duration', None),
                    segments=segments if segments else None,
                    warnings=None
                )
            else:
                # For simple formats, just return the text
                return TranscriptionResult(
                    text=str(response),
                    language=language,
                    confidence=None,
                    duration_seconds=None,
                    segments=None,
                    warnings=None
                )
                
        except Exception as e:
            logger.error(f"Async transcription failed: {e}")
            raise ConfigurationError(f"OpenAI async transcription failed: {str(e)}")

    def is_available(self) -> bool:
        """Check if OpenAI STT is available.
        
        Returns:
            True if OpenAI module is installed
        """
        return OPENAI_AVAILABLE