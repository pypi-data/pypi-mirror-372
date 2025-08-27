"""Configuration utilities for model providers.

This module provides utilities for handling provider configurations
in a flexible way that doesn't depend on a specific configuration system.
"""

import os
from typing import Any, Dict, Optional


def get_default_config(provider: str) -> Dict[str, Any]:
    """Get default configuration for a provider from environment variables.
    
    This provides a fallback mechanism for common environment variables
    when no explicit configuration is provided.
    
    Args:
        provider: The provider name (openai, anthropic, ollama, bedrock)
        
    Returns:
        Dictionary with provider configuration from environment
    """
    configs = {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": os.getenv("OPENAI_BASE_URL"),
            "organization": os.getenv("OPENAI_ORGANIZATION"),
        },
        "anthropic": {
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "base_url": os.getenv("ANTHROPIC_BASE_URL"),
        },
        "ollama": {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        },
        "bedrock": {
            "region_name": os.getenv("AWS_REGION"),
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "aws_session_token": os.getenv("AWS_SESSION_TOKEN"),
            "profile_name": os.getenv("AWS_PROFILE"),
        }
    }
    
    return configs.get(provider, {})


def create_provider_config(**kwargs) -> Any:
    """Create a provider configuration object.
    
    This is a convenience function for creating configuration objects
    that can be passed to the model factories.
    
    Args:
        **kwargs: Provider-specific configuration parameters
        
    Returns:
        Configuration object (currently a SimpleNamespace)
    """
    from types import SimpleNamespace
    return SimpleNamespace(**kwargs)