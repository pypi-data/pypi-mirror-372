"""Base provider classes for fastal-langgraph-toolkit."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseProvider(ABC):
    """Base provider class."""
    
    def __init__(self, config: Any, model_name: Optional[str] = None, **kwargs):
        """Initialize provider with configuration."""
        self.config = config
        self.model_name = model_name
        self.kwargs = kwargs
    
    @abstractmethod
    def initialize(self) -> Any:
        """Initialize and return the provider instance."""
        pass