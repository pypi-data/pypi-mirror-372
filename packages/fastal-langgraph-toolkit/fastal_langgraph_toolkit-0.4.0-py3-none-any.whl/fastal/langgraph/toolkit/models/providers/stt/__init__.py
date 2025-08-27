"""Speech-to-text provider implementations.

This module contains implementations for various STT (Speech-to-Text) providers.

Current status:
- ✅ OpenAI (Whisper) - Fully implemented
- 🚧 Google Cloud Speech - Planned for v0.4.0
- 🚧 Azure Cognitive Services - Planned for v0.4.0

Additional providers may be added based on community feedback and demand.
"""

from .openai import OpenAISTTProvider

# Import placeholder providers (will raise NotImplementedError)
from .google import GoogleSTTProvider
from .azure import AzureSTTProvider

__all__ = [
    "OpenAISTTProvider",      # Available now
    "GoogleSTTProvider",      # Planned v0.4.0  
    "AzureSTTProvider",       # Planned v0.4.0
]