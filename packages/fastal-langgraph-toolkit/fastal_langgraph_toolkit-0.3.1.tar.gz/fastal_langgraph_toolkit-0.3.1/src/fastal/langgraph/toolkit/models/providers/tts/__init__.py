"""Text-to-Speech providers module.

This module contains implementations for various TTS (Text-to-Speech) providers.

Note: TTS functionality is planned for implementation in future releases.
The architecture and provider structure are prepared but not yet implemented.

Planned providers:
- OpenAI TTS (v0.5.0)
- Google Cloud Text-to-Speech (v0.5.0) 
- ElevenLabs (v0.5.0)
- Azure Cognitive Services TTS (v0.5.0)

Current status: Structure prepared, implementation pending.
"""

from typing import Dict, Any

# Placeholder for future TTS provider availability
TTS_PROVIDERS_AVAILABLE: Dict[str, bool] = {
    "openai": False,      # Planned for v0.5.0
    "google": False,      # Planned for v0.5.0
    "elevenlabs": False,  # Planned for v0.5.0
    "azure": False,       # Planned for v0.5.0
}

__all__ = [
    "TTS_PROVIDERS_AVAILABLE",
]

# TODO: Implement in v0.5.0
# - TTSFactory class
# - Base TTS provider classes
# - TTS result types (AudioResult, VoiceOptions, etc.)
# - Integration with unified ModelFactory