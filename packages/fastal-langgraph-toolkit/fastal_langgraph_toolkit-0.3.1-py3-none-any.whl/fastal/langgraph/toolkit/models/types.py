"""Common type definitions for speech models.

This module defines standardized data types for speech-to-text and
text-to-speech operations across all providers.
"""

from dataclasses import dataclass
from typing import List, TypedDict, Optional


class TranscriptionSegment(TypedDict):
    """Individual segment of a transcription."""
    text: str
    start: float
    end: float
    confidence: Optional[float]


class TranscriptionResult(TypedDict):
    """Standard result format for speech-to-text operations."""
    text: str
    language: Optional[str]
    confidence: Optional[float]
    duration_seconds: Optional[float]
    segments: Optional[List[TranscriptionSegment]]
    warnings: Optional[List[str]]


@dataclass
class AudioResult:
    """Standard result format for text-to-speech operations."""
    audio_data: bytes
    mime_type: str
    duration_seconds: float
    sample_rate: int
    voice: Optional[str] = None
    
    def to_file(self, path: str) -> None:
        """Save audio data to file.
        
        Args:
            path: File path to save audio data
        """
        with open(path, 'wb') as f:
            f.write(self.audio_data)


class AudioFormat(TypedDict):
    """Audio format specification."""
    mime_type: str
    encoding: str
    sample_rate: int
    channels: int