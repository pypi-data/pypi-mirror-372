"""Example usage of the Speech-to-Text functionality."""

import asyncio
from types import SimpleNamespace
from fastal.langgraph.toolkit import ModelFactory


def example_basic_usage():
    """Basic synchronous usage example."""
    # Configure provider
    config = SimpleNamespace(
        api_key="your-openai-api-key"  # Replace with actual key
    )
    
    # Create STT instance
    stt = ModelFactory.create_stt(
        provider="openai",
        model="whisper-1",  # Optional, defaults to whisper-1
        config=config
    )
    
    # Read audio file
    with open("audio.mp3", "rb") as f:
        audio_data = f.read()
    
    # Transcribe
    result = stt.transcribe(
        audio_data,
        language="en",  # Optional language hint
        temperature=0.2  # Lower = more deterministic
    )
    
    # Access results
    print(f"Text: {result['text']}")
    print(f"Language: {result['language']}")
    print(f"Duration: {result['duration_seconds']}s")
    
    # If segments are available
    if result.get('segments'):
        for i, segment in enumerate(result['segments']):
            print(f"Segment {i}: {segment['start']:.2f}s - {segment['end']:.2f}s")
            print(f"  Text: {segment['text']}")


async def example_async_usage():
    """Async usage example."""
    # Configure provider
    config = SimpleNamespace(api_key="your-openai-api-key")
    
    # Create STT instance
    stt = ModelFactory.create_stt("openai", config=config)
    
    # Read audio file
    with open("audio.mp3", "rb") as f:
        audio_data = f.read()
    
    # Async transcribe
    result = await stt.atranscribe(audio_data)
    
    print(f"Transcribed text: {result['text']}")


def example_with_multiple_files():
    """Example processing multiple files."""
    config = SimpleNamespace(api_key="your-openai-api-key")
    stt = ModelFactory.create_stt("openai", config=config)
    
    audio_files = ["file1.mp3", "file2.wav", "file3.m4a"]
    
    for file_path in audio_files:
        try:
            with open(file_path, "rb") as f:
                audio_data = f.read()
            
            result = stt.transcribe(
                audio_data,
                response_format="text"  # Simple text output
            )
            
            print(f"{file_path}: {result['text']}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")


def example_with_fallback_providers():
    """Example with provider fallback pattern."""
    providers = [
        ("openai", "whisper-1", SimpleNamespace(api_key="key1")),
        # Future: ("google", "chirp", SimpleNamespace(credentials="path")),
        # Future: ("azure", "speech", SimpleNamespace(key="key", region="region"))
    ]
    
    audio_data = b"..."  # Your audio data
    
    for provider, model, config in providers:
        try:
            stt = ModelFactory.create_stt(provider, model, config)
            result = stt.transcribe(audio_data)
            print(f"Successfully transcribed with {provider}")
            break
        except Exception as e:
            print(f"Failed with {provider}: {e}")
            continue


if __name__ == "__main__":
    # Check available providers
    providers = ModelFactory.get_available_providers()
    print("Available STT providers:", providers.get('stt_providers', {}))
    
    # Run examples (uncomment as needed)
    # example_basic_usage()
    # asyncio.run(example_async_usage())
    # example_with_multiple_files()
    # example_with_fallback_providers()