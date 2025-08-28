"""Common exceptions for Fastal LangGraph Toolkit."""


class ToolkitError(Exception):
    """Base exception for all toolkit errors."""
    pass


class ConfigurationError(ToolkitError):
    """Raised when there's a configuration error."""
    pass


class ProviderError(ToolkitError):
    """Raised when there's an error with a provider."""
    pass


class StateError(ToolkitError):
    """Raised when there's an error with state management."""
    pass