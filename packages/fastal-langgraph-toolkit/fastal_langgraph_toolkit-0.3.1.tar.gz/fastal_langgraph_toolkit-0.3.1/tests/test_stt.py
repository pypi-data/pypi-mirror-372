"""Tests for speech-to-text functionality."""

import pytest
from types import SimpleNamespace
from unittest.mock import Mock, patch, MagicMock

from fastal.langgraph.toolkit.models import ModelFactory, TranscriptionResult
from fastal.langgraph.toolkit.models.factory import STTFactory

# Only import if available to avoid test failures
try:
    from fastal.langgraph.toolkit.models.providers.stt.openai import OpenAISTTProvider
    OPENAI_STT_AVAILABLE = True
except ImportError:
    OPENAI_STT_AVAILABLE = False
    OpenAISTTProvider = None


class TestSTTFactory:
    """Test STT factory functionality."""

    def test_create_stt_with_invalid_provider(self):
        """Test creating STT with invalid provider raises error."""
        config = SimpleNamespace(api_key="test-key")
        
        with pytest.raises(Exception) as exc_info:
            STTFactory.create_stt("invalid_provider", "model", config)
        
        assert "Unknown STT provider" in str(exc_info.value)

    def test_create_stt_without_config(self):
        """Test creating STT without config raises error."""
        # Mock OpenAI as available to test config validation
        with patch('fastal.langgraph.toolkit.models.factory.STT_PROVIDERS_AVAILABLE', {'openai': True}):
            with pytest.raises(Exception) as exc_info:
                STTFactory.create_stt("openai", "whisper-1", None)
            
            assert "configuration is required" in str(exc_info.value)

    def test_create_stt_with_openai(self):
        """Test creating OpenAI STT provider."""
        if not OPENAI_STT_AVAILABLE:
            pytest.skip("OpenAI STT provider not available")
            
        config = SimpleNamespace(api_key="test-key")
        
        # Mock the OpenAI import and provider availability
        with patch('fastal.langgraph.toolkit.models.factory.STT_PROVIDERS_AVAILABLE', {'openai': True}):
            with patch.object(OpenAISTTProvider, '_create_model', return_value=Mock()):
                provider = STTFactory.create_stt("openai", "whisper-1", config)
                
                assert isinstance(provider, OpenAISTTProvider)
                assert provider.model_name == "whisper-1"
                assert provider.config.api_key == "test-key"


@pytest.mark.skipif(not OPENAI_STT_AVAILABLE, reason="OpenAI STT provider not available")
class TestOpenAISTTProvider:
    """Test OpenAI STT provider functionality."""

    def test_provider_initialization(self):
        """Test provider initializes correctly."""
        config = SimpleNamespace(api_key="test-key")
        provider = OpenAISTTProvider(config, "whisper-1")
        
        assert provider.model_name == "whisper-1"
        assert provider.config.api_key == "test-key"

    @patch('fastal.langgraph.toolkit.models.providers.stt.openai.OPENAI_AVAILABLE', True)
    def test_transcribe_with_mocked_client(self):
        """Test transcribe method with fully mocked OpenAI client."""
        config = SimpleNamespace(api_key="test-key")
        provider = OpenAISTTProvider(config, "whisper-1")
        
        # Mock the _create_model method to return a mock client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Test transcription"
        mock_response.language = "en"
        mock_response.duration = 5.0
        mock_response.segments = []
        
        mock_client.audio.transcriptions.create.return_value = mock_response
        
        with patch.object(provider, '_create_model', return_value=mock_client):
            with patch.object(provider, '_client', mock_client):
                audio_data = b"fake audio data"
                result = provider.transcribe(audio_data)
                
                assert result["text"] == "Test transcription"
                assert result["language"] == "en" 
                assert result["duration_seconds"] == 5.0

    def test_is_available_method(self):
        """Test is_available method."""
        config = SimpleNamespace(api_key="test-key")
        provider = OpenAISTTProvider(config, "whisper-1")
        
        # This should return the actual OPENAI_AVAILABLE status
        # In test environment without openai installed, it should be False
        availability = provider.is_available()
        assert isinstance(availability, bool)


class TestModelFactorySTT:
    """Test ModelFactory STT integration."""

    @patch('fastal.langgraph.toolkit.models.factory.PROVIDERS_AVAILABLE', {'openai': True})
    def test_create_stt_via_model_factory(self):
        """Test creating STT via unified ModelFactory."""
        if not OPENAI_STT_AVAILABLE:
            pytest.skip("OpenAI STT provider not available")
            
        config = SimpleNamespace(api_key="test-key")
        
        # Mock provider availability and OpenAI client
        with patch('fastal.langgraph.toolkit.models.factory.STT_PROVIDERS_AVAILABLE', {'openai': True}):
            with patch.object(OpenAISTTProvider, '_create_model', return_value=Mock()):
                provider = ModelFactory.create_stt("openai", "whisper-1", config)
                assert isinstance(provider, OpenAISTTProvider)

    def test_get_available_providers_includes_stt(self):
        """Test that available providers includes STT information."""  
        providers = ModelFactory.get_available_providers()
        
        assert 'stt_providers' in providers
        assert 'openai' in providers['stt_providers']
        # Value depends on whether OpenAI is actually installed
        assert isinstance(providers['stt_providers']['openai'], bool)
    
    def test_create_stt_without_openai_installed(self):
        """Test STT creation behavior when OpenAI is not installed."""
        config = SimpleNamespace(api_key="test-key")
        
        # Mock OpenAI as not available for STT
        with patch('fastal.langgraph.toolkit.models.factory.STT_PROVIDERS_AVAILABLE', {'openai': False}):
            with pytest.raises(Exception) as exc_info:
                ModelFactory.create_stt("openai", "whisper-1", config)
            
            assert "not available" in str(exc_info.value).lower()


class TestSTTRobustness:
    """Test STT functionality robustness and edge cases."""
    
    def test_stt_import_safety(self):
        """Test that STT imports don't break without OpenAI."""
        # This test ensures the module can be imported safely
        from fastal.langgraph.toolkit.models.providers.stt import openai as stt_openai
        
        # Should not raise ImportError even without OpenAI installed
        assert hasattr(stt_openai, 'OpenAISTTProvider')
        assert hasattr(stt_openai, 'OPENAI_AVAILABLE')
    
    def test_factory_availability_check(self):
        """Test factory availability checking works correctly."""
        from fastal.langgraph.toolkit.models.factory import PROVIDERS_AVAILABLE
        
        # Should have openai key (even if False)
        assert 'openai' in PROVIDERS_AVAILABLE
        assert isinstance(PROVIDERS_AVAILABLE['openai'], bool)