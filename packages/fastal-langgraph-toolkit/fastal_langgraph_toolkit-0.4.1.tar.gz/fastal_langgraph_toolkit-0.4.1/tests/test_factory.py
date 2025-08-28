"""Basic tests for ModelFactory"""

import pytest
from types import SimpleNamespace

from fastal.langgraph.toolkit import ModelFactory
from fastal.langgraph.toolkit.exceptions import ConfigurationError


def test_model_factory_import():
    """Test that ModelFactory can be imported"""
    assert ModelFactory is not None


def test_get_available_providers():
    """Test that get_available_providers returns expected structure"""
    providers = ModelFactory.get_available_providers()
    
    assert isinstance(providers, dict)
    assert "llm_providers" in providers
    assert "embedding_providers" in providers
    assert isinstance(providers["llm_providers"], dict)
    assert isinstance(providers["embedding_providers"], dict)


def test_create_llm_invalid_provider():
    """Test that invalid provider raises ConfigurationError"""
    config = SimpleNamespace(api_key="test")
    
    with pytest.raises(ConfigurationError):
        ModelFactory.create_llm("invalid_provider", "model", config)


def test_create_embeddings_invalid_provider():
    """Test that invalid provider raises ConfigurationError"""
    config = SimpleNamespace(api_key="test")
    
    with pytest.raises(ConfigurationError):
        ModelFactory.create_embeddings("invalid_provider", "model", config)


def test_create_llm_missing_config():
    """Test that missing config raises ConfigurationError"""
    with pytest.raises(ConfigurationError):
        ModelFactory.create_llm("openai", "gpt-4", None)


def test_create_embeddings_missing_config():
    """Test that missing config raises ConfigurationError"""
    with pytest.raises(ConfigurationError):
        ModelFactory.create_embeddings("openai", "text-embedding-3-small", None)