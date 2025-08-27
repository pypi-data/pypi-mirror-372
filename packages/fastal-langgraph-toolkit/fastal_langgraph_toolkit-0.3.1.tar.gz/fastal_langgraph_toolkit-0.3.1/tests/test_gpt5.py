"""Tests for GPT-5 model support in OpenAI provider."""

import pytest
from types import SimpleNamespace
from unittest.mock import Mock, patch, MagicMock

from fastal.langgraph.toolkit.exceptions import ConfigurationError

# Conditional import to handle when langchain-openai is not installed
try:
    from fastal.langgraph.toolkit.models.providers.llm.openai import OpenAILLMProvider
    OPENAI_PROVIDER_AVAILABLE = True
except ImportError:
    OPENAI_PROVIDER_AVAILABLE = False
    OpenAILLMProvider = None


@pytest.mark.skipif(not OPENAI_PROVIDER_AVAILABLE, reason="OpenAI provider not available")
class TestGPT5Support:
    """Test GPT-5 specific functionality."""
    
    def test_gpt5_model_detection(self):
        """Test that GPT-5 models are correctly detected."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=0.7,
            max_tokens=1000,
            timeout=None
        )
        
        # Test GPT-5 models
        gpt5_models = ['gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-turbo']
        for model in gpt5_models:
            provider = OpenAILLMProvider(config, model)
            is_gpt5 = any(model.startswith(prefix) for prefix in provider.GPT5_MODELS)
            assert is_gpt5, f"{model} should be detected as GPT-5"
        
        # Test non-GPT-5 models
        non_gpt5_models = ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'davinci-002']
        for model in non_gpt5_models:
            provider = OpenAILLMProvider(config, model)
            is_gpt5 = any(model.startswith(prefix) for prefix in provider.GPT5_MODELS)
            assert not is_gpt5, f"{model} should not be detected as GPT-5"
    
    def test_gpt5_max_completion_tokens_mapping(self):
        """Test that max_tokens is mapped to max_completion_tokens for GPT-5."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=0.7,
            max_tokens=1000,
            timeout=None
        )
        
        # Mock _create_model to capture the arguments to ChatOpenAI
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Test GPT-5 with max_tokens (should map to max_completion_tokens)
                provider = OpenAILLMProvider(config, 'gpt-5-mini', max_tokens=2000)
                model = provider._create_model()
                
                # Check that max_completion_tokens was used
                assert 'max_completion_tokens' in captured_args
                assert captured_args['max_completion_tokens'] == 2000
                assert 'max_tokens' not in captured_args
    
    def test_gpt5_explicit_max_completion_tokens(self):
        """Test that explicit max_completion_tokens is respected for GPT-5."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=0.7,
            max_tokens=1000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Test GPT-5 with explicit max_completion_tokens
                provider = OpenAILLMProvider(config, 'gpt-5', max_completion_tokens=3000)
                model = provider._create_model()
                
                # Check that max_completion_tokens was used
                assert 'max_completion_tokens' in captured_args
                assert captured_args['max_completion_tokens'] == 3000
    
    def test_gpt4_keeps_max_tokens(self):
        """Test that GPT-4 models still use max_tokens parameter."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=0.7,
            max_tokens=1000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Test GPT-4 with max_tokens
                provider = OpenAILLMProvider(config, 'gpt-4-turbo', max_tokens=1500)
                model = provider._create_model()
                
                # Check that max_tokens was used (not max_completion_tokens)
                assert 'max_tokens' in captured_args
                assert captured_args['max_tokens'] == 1500
                assert 'max_completion_tokens' not in captured_args
    
    def test_gpt5_reasoning_effort(self):
        """Test that reasoning_effort is properly passed to GPT-5 models."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=0.7,
            max_tokens=1000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Test GPT-5 with reasoning_effort
                provider = OpenAILLMProvider(
                    config, 
                    'gpt-5-mini',
                    max_completion_tokens=2000,
                    reasoning_effort="minimal"
                )
                model = provider._create_model()
                
                # Check that model_kwargs contains extra_body with reasoning_effort
                assert 'model_kwargs' in captured_args
                assert 'extra_body' in captured_args['model_kwargs']
                assert captured_args['model_kwargs']['extra_body']['reasoning_effort'] == 'minimal'
    
    def test_gpt5_reasoning_effort_not_applied_to_gpt4(self):
        """Test that reasoning_effort is not applied to GPT-4 models."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=0.7,
            max_tokens=1000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Test GPT-4 with reasoning_effort (should be ignored)
                provider = OpenAILLMProvider(
                    config, 
                    'gpt-4',
                    max_tokens=2000,
                    reasoning_effort="high"
                )
                model = provider._create_model()
                
                # Check that model_kwargs is not added for GPT-4
                assert 'model_kwargs' not in captured_args
    
    def test_gpt5_backward_compatibility(self):
        """Test that existing code using max_tokens works with GPT-5."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=0.7,
            max_tokens=1000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Existing code pattern - using max_tokens with GPT-5
                provider = OpenAILLMProvider(config, 'gpt-5-mini', max_tokens=1500)
                model = provider._create_model()
                
                # Should automatically convert to max_completion_tokens
                assert 'max_completion_tokens' in captured_args
                assert captured_args['max_completion_tokens'] == 1500
                assert 'max_tokens' not in captured_args
    
    def test_gpt5_extra_body_preservation(self):
        """Test that existing extra_body is preserved when adding reasoning_effort."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=0.7,
            max_tokens=1000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Test GPT-5 with both extra_body and reasoning_effort
                provider = OpenAILLMProvider(
                    config, 
                    'gpt-5',
                    max_completion_tokens=2000,
                    reasoning_effort="medium",
                    extra_body={"custom_param": "value"}
                )
                model = provider._create_model()
                
                # Check that both parameters are in model_kwargs.extra_body
                assert 'model_kwargs' in captured_args
                assert 'extra_body' in captured_args['model_kwargs']
                assert captured_args['model_kwargs']['extra_body']['reasoning_effort'] == 'medium'
                assert captured_args['model_kwargs']['extra_body']['custom_param'] == 'value'


    def test_gpt5_temperature_restriction(self):
        """Test that GPT-5 models handle temperature restrictions correctly."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=0.7,  # This should be ignored for GPT-5
            max_tokens=1000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                with patch('warnings.warn') as mock_warn:
                    # Test GPT-5 with non-1 temperature (should be omitted)
                    provider = OpenAILLMProvider(config, 'gpt-5-mini', temperature=0.5)
                    model = provider._create_model()
                    
                    # Check that temperature was omitted
                    assert 'temperature' not in captured_args
                    # Check that a warning was issued
                    mock_warn.assert_called_once()
                    assert "GPT-5 models only support temperature=1" in str(mock_warn.call_args[0][0])
    
    def test_gpt5_temperature_equals_one(self):
        """Test that temperature=1 is preserved for GPT-5 models."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=1,  # This should be preserved
            max_tokens=1000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Test GPT-5 with temperature=1 (should be preserved)
                provider = OpenAILLMProvider(config, 'gpt-5', temperature=1)
                model = provider._create_model()
                
                # Check that temperature=1 was preserved
                assert 'temperature' in captured_args
                assert captured_args['temperature'] == 1
    
    def test_gpt4_temperature_preserved(self):
        """Test that temperature is preserved for non-GPT-5 models."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=0.3,
            max_tokens=1000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Test GPT-4 with custom temperature (should be preserved)
                provider = OpenAILLMProvider(config, 'gpt-4', temperature=0.3)
                model = provider._create_model()
                
                # Check that temperature was preserved
                assert 'temperature' in captured_args
                assert captured_args['temperature'] == 0.3
    
    def test_gpt5_verbosity_parameter(self):
        """Test that verbosity parameter is properly passed to GPT-5 models."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            max_tokens=1000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Test GPT-5 with verbosity parameter
                provider = OpenAILLMProvider(
                    config, 
                    'gpt-5-mini',
                    max_completion_tokens=2000,
                    verbosity="high"  # New GPT-5 parameter
                )
                model = provider._create_model()
                
                # Check that model_kwargs contains extra_body with verbosity
                assert 'model_kwargs' in captured_args
                assert 'extra_body' in captured_args['model_kwargs']
                assert captured_args['model_kwargs']['extra_body']['verbosity'] == 'high'
    
    def test_gpt5_multiple_extra_params(self):
        """Test that multiple GPT-5 parameters work together."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            max_tokens=1000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Test GPT-5 with both reasoning_effort and verbosity
                provider = OpenAILLMProvider(
                    config, 
                    'gpt-5',
                    max_completion_tokens=3000,
                    reasoning_effort="high",
                    verbosity="low"
                )
                model = provider._create_model()
                
                # Check that model_kwargs contains extra_body with both parameters
                assert 'model_kwargs' in captured_args
                assert 'extra_body' in captured_args['model_kwargs']
                assert captured_args['model_kwargs']['extra_body']['reasoning_effort'] == 'high'
                assert captured_args['model_kwargs']['extra_body']['verbosity'] == 'low'


@pytest.mark.skipif(not OPENAI_PROVIDER_AVAILABLE, reason="OpenAI provider not available")
class TestGPT5Integration:
    """Integration tests for GPT-5 models (requires mocked API)."""
    
    def test_gpt5_vision_configuration(self):
        """Test GPT-5 configuration for vision tasks."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=0.0,
            max_tokens=2000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Vision task configuration with minimal reasoning
                provider = OpenAILLMProvider(
                    config,
                    'gpt-5-mini',
                    max_completion_tokens=2000,
                    temperature=0.0,
                    reasoning_effort="minimal"  # Prevent reasoning tokens consuming output
                )
                model = provider._create_model()
                
                # Verify configuration
                assert captured_args['max_completion_tokens'] == 2000
                # Temperature 0.0 should be omitted for GPT-5 (not equal to 1)
                assert 'temperature' not in captured_args
                assert 'model_kwargs' in captured_args
                assert 'extra_body' in captured_args['model_kwargs']
                assert captured_args['model_kwargs']['extra_body']['reasoning_effort'] == 'minimal'
    
    def test_gpt5_complex_reasoning_configuration(self):
        """Test GPT-5 configuration for complex reasoning tasks."""
        config = SimpleNamespace(
            api_key="test-key",
            base_url=None,
            organization=None,
            temperature=0.7,
            max_tokens=4000,
            timeout=None
        )
        
        mock_chat_openai = MagicMock()
        captured_args = {}
        
        def capture_args(**kwargs):
            captured_args.update(kwargs)
            return mock_chat_openai
        
        with patch('fastal.langgraph.toolkit.models.providers.llm.openai.OPENAI_AVAILABLE', True):
            with patch('fastal.langgraph.toolkit.models.providers.llm.openai.ChatOpenAI', side_effect=capture_args, create=True):
                # Complex reasoning configuration
                provider = OpenAILLMProvider(
                    config,
                    'gpt-5',
                    max_completion_tokens=4000,
                    temperature=0.3,
                    reasoning_effort="high"  # Maximum reasoning capability
                )
                model = provider._create_model()
                
                # Verify configuration
                assert captured_args['max_completion_tokens'] == 4000
                # Temperature 0.3 should be omitted for GPT-5 (not equal to 1)
                assert 'temperature' not in captured_args
                assert 'model_kwargs' in captured_args
                assert 'extra_body' in captured_args['model_kwargs']
                assert captured_args['model_kwargs']['extra_body']['reasoning_effort'] == 'high'