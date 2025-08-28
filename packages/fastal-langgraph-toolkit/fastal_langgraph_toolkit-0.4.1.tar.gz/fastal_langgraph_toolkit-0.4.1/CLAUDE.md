# Fastal LangGraph Toolkit - Claude Code Context

## Project Overview

The **Fastal LangGraph Toolkit** is a production-ready Python package developed by the Fastal Group to provide common utilities and tools for building enterprise-grade LangGraph agents with multi-modal capabilities. Originally developed internally for client projects, this toolkit has been open-sourced to support the broader LangGraph community.

**PyPI Package**: `fastal-langgraph-toolkit`  
**Current Version**: v0.4.0 (Deprecation warnings added)  
**Previous Stable**: v0.3.1 (GPT-5 support, Beta status)  
**Development**: Uses `uv` (not pip) for dependency management  
**License**: MIT  
**Target**: Python 3.10+

## Core Architecture

### Main Modules

1. **ModelFactory** (`src/fastal/langgraph/toolkit/models/`)
   - Multi-provider LLM, embedding and speech factory
   - LLM Support: OpenAI (including GPT-5), Anthropic, Ollama, AWS Bedrock
   - Embedding Support: OpenAI, Ollama, AWS Bedrock
   - Speech Support: OpenAI Whisper (expanding to more providers)
   - Provider availability detection
   - Configuration abstraction
   - GPT-5 automatic parameter mapping and reasoning control

2. **Memory Management** (`src/fastal/langgraph/toolkit/memory/`)
   - `SummaryManager`: Intelligent conversation summarization
   - `SummaryConfig`: Configurable summarization behavior
   - `SummarizableState`: TypedDict base class for summary-enabled states

3. **Speech Processing** (`src/fastal/langgraph/toolkit/models/`)
   - `STTFactory`: Speech-to-text factory with provider abstraction
   - `TranscriptionResult`: Standardized result format across providers
   - `BaseSTTProvider`: Base class for all STT implementations
   - Error handling and async support

4. **Providers** (`src/fastal/langgraph/toolkit/models/providers/`)
   - LLM providers: `llm/anthropic.py`, `llm/bedrock.py`, `llm/ollama.py`, `llm/openai.py`
   - Embedding providers: `embeddings/bedrock.py`, `embeddings/ollama.py`, `embeddings/openai.py`
   - STT providers: `stt/openai.py` (more coming soon)

## Key Features

### 1. Multi-Provider Model Factory
- **Unified API**: Single interface for all LLM/embedding providers
- **GPT-5 Support**: Automatic parameter mapping and reasoning_effort control
- **Configuration Injection**: Clean separation of concerns
- **Provider Health Checks**: Automatic availability detection
- **Seamless Switching**: Change providers without code changes

```python
from fastal.langgraph.toolkit import ModelFactory
from types import SimpleNamespace

config = SimpleNamespace(api_key="your-key", temperature=0.7)
# Works with GPT-4 and GPT-5 models transparently
llm = ModelFactory.create_llm("openai", "gpt-5-mini", config)  # GPT-5 support
embeddings = ModelFactory.create_embeddings("openai", "text-embedding-3-small", config)
stt = ModelFactory.create_stt("openai", "whisper-1", config)
```

### 1.1 Enterprise Speech Processing
- **Multi-Format Support**: MP3, WAV, M4A, and other standard audio formats
- **Language Detection**: Automatic language identification with manual override support
- **Async Operations**: Full async/await support for non-blocking processing
- **Structured Results**: Standardized `TranscriptionResult` format with segments, timing, and metadata
- **Error Resilience**: Robust error handling with detailed logging and graceful fallbacks
- **Provider Abstraction**: Unified interface regardless of underlying STT provider

```python
from fastal.langgraph.toolkit import ModelFactory, TranscriptionResult

# Create STT instance
stt_config = SimpleNamespace(api_key="your-openai-key")
stt = ModelFactory.create_stt("openai", "whisper-1", stt_config)

# Transcribe audio with detailed results
with open("audio.mp3", "rb") as f:
    result: TranscriptionResult = stt.transcribe(
        f.read(),
        language="en",
        temperature=0.1,  # High accuracy
        response_format="verbose_json"
    )

print(f"Text: {result['text']}")
print(f"Language: {result['language']}")
print(f"Duration: {result['duration_seconds']}s")

# Process segments for detailed analysis
for segment in result.get('segments', []):
    print(f"{segment['start']:.2f}s: {segment['text']}")
```

### 2. Intelligent Conversation Summarization
- **Ready-to-Use LangGraph Node**: `summary_node()` method provides instant integration
- **Conversation Pair Counting**: Smart Human+AI message pair detection
- **ReAct Tool Filtering**: Automatic exclusion of tool calls from summaries
- **Configurable Thresholds**: Customizable trigger points
- **Context Preservation**: Keep recent conversations for continuity
- **Custom Prompts**: Domain-specific summarization templates
- **State Auto-Injection**: Works with existing states
- **Built-in Error Handling**: Robust error management with optional logging

```python
from fastal.langgraph.toolkit import SummaryManager, SummarizableState
from langgraph.graph import StateGraph
import logging

class MyAgentState(SummarizableState):
    messages: Annotated[list, add_messages]
    thread_id: str
    # summary and last_summarized_index automatically provided

summary_manager = SummaryManager(llm)

# Optional: Configure logging for summary operations
logger = logging.getLogger(__name__)
summary_manager.set_logger(logger)

# Add ready-to-use summary node to your workflow
workflow = StateGraph(MyAgentState)
workflow.add_node("summary_check", summary_manager.summary_node)
workflow.set_entry_point("summary_check")
```

### 3. Memory Optimization
- **Token Efficiency**: 70-90% reduction in context size
- **Cost Control**: Significant reduction in API costs for long conversations
- **State Management**: Clean integration with LangGraph checkpointing

## Development Commands

### Build System
- **Package Manager**: `uv` (modern, fast Python package manager)
- **Build Backend**: `hatchling`
- **Test Framework**: Basic test suite in `tests/`

### Essential Commands
```bash
# Install dependencies
uv sync

# Run tests (with async support)
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/fastal/langgraph/toolkit

# Run only STT tests
uv run pytest tests/test_stt.py -v

# Build package
uv build

# Install in development mode
uv add --editable .

# Type checking (if configured)
uv run mypy src/

# Linting (if configured)
uv run ruff check src/
uv run ruff format src/

# Publish to PyPI (automated via GitHub Actions)
uv run twine upload dist/* --skip-existing
```

### Development Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **twine**: PyPI publishing

## Configuration Requirements

### Provider Configuration
The toolkit requires `SimpleNamespace` objects (not dictionaries) for type safety:

```python
from types import SimpleNamespace

# ✅ Correct
config = SimpleNamespace(
    api_key="sk-...",
    temperature=0.7,
    streaming=True
)

# ❌ Wrong - Don't use dictionaries
config = {"api_key": "sk-...", "temperature": 0.7}
```

### Environment Variables
Common environment variables:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

## Production Usage Patterns

### Enterprise Multi-Provider Setup
```python
import logging

class EnterpriseAgent:
    def __init__(self):
        # Primary: OpenAI, Fallback: Anthropic
        self.primary_llm = self._get_openai_llm()
        self.fallback_llm = self._get_anthropic_llm()
        self.stt = self._get_openai_stt()  # Speech processing
        self.summary_manager = SummaryManager(self.get_llm())
        
        # Configure logging for summary operations
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.summary_manager.set_logger(logger)
    
    def _get_openai_stt(self):
        """Configure OpenAI Whisper for enterprise use"""
        config = SimpleNamespace(
            api_key=os.getenv("OPENAI_API_KEY"),
            # Enterprise settings can be added here
        )
        return ModelFactory.create_stt("openai", "whisper-1", config)
```

### GPT-5 Model Configuration
```python
# GPT-5 support with automatic parameter mapping and restrictions handling
from fastal.langgraph.toolkit import ModelFactory
from types import SimpleNamespace

# Configuration can now contain ANY parameters - the provider handles them intelligently
config = SimpleNamespace(
    api_key="your-openai-key",
    temperature=0.7,  # Will be ignored for GPT-5 (only accepts 1 or omit)
    max_tokens=2000,  # Automatically mapped to max_completion_tokens for GPT-5
    # GPT-5 specific parameters can be in config or kwargs
    reasoning_effort="medium",
    verbosity="medium"
)

# Standard GPT-5 usage - backward compatible
llm = ModelFactory.create_llm("openai", "gpt-5-mini", config)

# Vision tasks with GPT-5 - optimized configuration
vision_llm = ModelFactory.create_llm(
    "openai", 
    "gpt-5-mini",
    config,
    max_completion_tokens=2000,  # Explicit parameter for clarity
    temperature=1,                # Use 1 for GPT-5 (or omit)
    reasoning_effort="minimal",   # Prevents reasoning tokens consuming output
    verbosity="low"              # Control output length
)

# Complex reasoning with GPT-5
reasoning_llm = ModelFactory.create_llm(
    "openai",
    "gpt-5",
    config,
    max_completion_tokens=4000,
    reasoning_effort="high",  # Maximum reasoning capability
    verbosity="high"         # Comprehensive outputs
)

# Important GPT-5 Restrictions:
# - temperature: Only accepts 1 or parameter omission (auto-handled with warning)
# - GPT-5 parameters (reasoning_effort, verbosity) go in model_kwargs.extra_body
# - Works seamlessly with vision/multimodal tasks
# - Config can contain any parameters - provider discriminates intelligently
```

### Multi-Modal Agent Architecture
```python
# Multi-modal agent with speech and text processing
class MultiModalEnterpriseAgent:
    def __init__(self):
        # Use GPT-5 for enhanced capabilities
        self.llm = ModelFactory.create_llm("openai", "gpt-5-mini", config)
        self.stt = ModelFactory.create_stt("openai", "whisper-1", config)
        self.summary_manager = SummaryManager(self.llm)
        
        # Configure logging
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.summary_manager.set_logger(logger)
    
    async def process_audio_input(self, audio_data: bytes, thread_id: str):
        """Process audio input with enterprise-grade error handling"""
        try:
            # Transcribe with high accuracy settings
            transcription = await self.stt.atranscribe(
                audio_data,
                temperature=0.0,  # Maximum accuracy for enterprise
                language="en",    # Can be made configurable
                response_format="verbose_json"
            )
            
            # Log for compliance/auditing
            logger.info(f"Audio processed for thread {thread_id}: {len(audio_data)} bytes")
            
            return transcription
            
        except Exception as e:
            logger.error(f"Audio processing failed for {thread_id}: {e}")
            # Return structured error response
            return {
                "text": "[Audio processing unavailable]",
                "error": str(e),
                "language": None,
                "duration_seconds": None,
                "segments": None,
                "warnings": ["Audio processing failed - please try again"]
            }
```

### Memory-Optimized Long Conversations
```python
# Aggressive summarization for cost efficiency
config = SummaryConfig(
    pairs_threshold=5,    # Frequent summarization
    recent_pairs_to_preserve=2,  # Minimal recent context
    max_summary_length=600
)
```

### Domain-Specific Summarization with Ready-to-Use Node
```python
# Customer service example with ready-to-use summary node
config = SummaryConfig(
    pairs_threshold=8,
    new_summary_prompt="""
    Create structured customer service summary:
    - Customer Information
    - Issue Summary  
    - Actions Taken
    - Current Status
    """
)

summary_manager = SummaryManager(llm, config)
summary_manager.set_logger(logger)  # Optional logging

# Use in LangGraph workflow
workflow.add_node("summary_check", summary_manager.summary_node)
```

## Testing and Quality

### Test Structure
- `tests/test_factory.py`: Model factory tests
- `tests/test_summary.py`: Summarization tests
- Basic unit test coverage for core functionality

### Performance Considerations
- **Token Efficiency**: ~84% reduction for 50-message conversations
- **Response Time**: 2-5s overhead for summary creation, 50-80% faster processing
- **Memory Usage**: 70-90% reduction in state size

## PyPI Publishing

### Package Configuration
- **Name**: `fastal-langgraph-toolkit`
- **Version**: `0.1.0` (Development status: Alpha)
- **Homepage**: `https://github.com/FastalGroup/fastal-langgraph-toolkit`
- **Dependencies**: LangChain Core, LangGraph, Pydantic

### Optional Dependencies
```toml
[project.optional-dependencies]
openai = ["langchain-openai>=0.1", "openai>=1.0.0"]
anthropic = ["langchain-anthropic>=0.1"]
ollama = ["langchain-ollama>=0.1"]
bedrock = ["langchain-aws>=0.1", "boto3>=1.26"]
stt = ["openai>=1.0.0"]  # Speech-to-text support
all = [all providers including speech]
```

## Release Management

### Versioning Strategy
- **v0.1.0**: Initial release (had TYPE_CHECKING import issues)
- **v0.1.1**: Bug fixes for import compatibility
- **v0.2.0**: Current stable - Speech-to-Text support with OpenAI Whisper integration

### GitHub Actions Workflow
- **Automated PyPI Publishing**: Triggered on GitHub releases
- **CI/CD Pipeline**: Syntax checking and testing
- **Secret Management**: PYPI_API_TOKEN configured for auto-publishing

### Release Process
1. Update version in `pyproject.toml` and `__init__.py`
2. Commit changes and create Git tag: `git tag v0.x.x`
3. Push tag: `git push origin v0.x.x`
4. Create GitHub release with `gh release create`
5. GitHub Actions automatically publishes to PyPI

## Release History

### v0.4.0 - Deprecation Warnings for Direct Factory Usage
**Important Changes:**
- Added deprecation warnings to `LLMFactory`, `EmbeddingFactory`, and `STTFactory`
- These classes will be made private in v1.0.0
- Users should migrate to using `ModelFactory` for all model creation
- Added TODO.md with v1.0.0 migration plan
- Full backward compatibility maintained

**Migration Required:**
```python
# OLD (deprecated in v0.4.0)
from fastal.langgraph.toolkit.models import LLMFactory, EmbeddingFactory, STTFactory

# NEW (use this instead)
from fastal.langgraph.toolkit import ModelFactory
```

### v0.3.0 - GPT-5 Model Support with Enhanced Configuration
**New Features:**
- Full support for OpenAI GPT-5 models (gpt-5, gpt-5-mini, gpt-5-nano)
- Automatic parameter mapping: `max_tokens` → `max_completion_tokens` for GPT-5
- Automatic temperature handling: GPT-5 only accepts temperature=1 (auto-managed with warnings)
- Support for `reasoning_effort` parameter (minimal, low, medium, high)
- Support for `verbosity` parameter (low, medium, high)
- Temperature now optional for all models (better API compliance)
- Complete backward compatibility with GPT-4 and earlier models
- Enhanced vision/multimodal task support with optimized configurations
- Comprehensive test suite with 15 GPT-5-specific tests

**Technical Improvements:**
- Intelligent configuration handling: Provider can now accept ANY parameters in config
- Automatic discrimination of GPT-5 specific parameters to `model_kwargs.extra_body`
- Flexible parameter sourcing: Parameters can come from config OR kwargs
- Improved config dictionary handling using `vars()` for any config object

### v0.2.0 - Speech-to-Text Integration
**New Features:**
- Complete Speech-to-Text support with OpenAI Whisper
- Multi-modal agent capabilities (text + speech)
- Async speech processing with `atranscribe()`
- Standardized `TranscriptionResult` format
- Enterprise-grade error handling for audio processing
- Comprehensive test suite with conditional OpenAI dependency

### v0.1.1 - Critical Bug Fixes
**TYPE_CHECKING Import Resolution**
**Problem**: v0.1.0 had import errors when optional dependencies weren't installed
```python
# v0.1.0 - PROBLEMATIC
def _create_model(self) -> OpenAIEmbeddings:  # Evaluated at import!

# v0.1.1 - FIXED
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from langchain_openai import OpenAIEmbeddings

def _create_model(self) -> "OpenAIEmbeddings":  # String annotation
```

**Solution**: Use TYPE_CHECKING for conditional imports and string type annotations

## Best Practices for Claude Code

1. **Use uv for all package operations** - This project uses uv, not pip
2. **Always use latest version** - Install with `pip install fastal-langgraph-toolkit` (gets v0.4.0)
3. **Use ModelFactory, not individual factories** - Direct use of LLMFactory/EmbeddingFactory/STTFactory is deprecated
4. **Understand the provider system** - Check available providers before use
5. **Focus on the three main modules** - ModelFactory, SummaryManager, and Speech Processing
6. **Test with SimpleNamespace configs** - Required for proper operation across all providers
7. **Consider memory optimization** - The summarization system is the key differentiator
8. **Use ready-to-use summary_node()** - Prefer `summary_manager.summary_node` over custom implementations
9. **Configure logging** - Use `set_logger()` for automatic summary operation logging
10. **Handle audio gracefully** - Always implement error handling for STT operations
11. **Use async for speech** - Prefer `atranscribe()` for non-blocking audio processing
12. **Follow the existing patterns** - Enterprise-grade, production-ready code style

## Common Issues & Solutions

1. **"SimpleNamespace required" Error**: Use `types.SimpleNamespace` not dict
2. **Import errors without optional deps**: Upgrade to v0.2.0 (has TYPE_CHECKING fixes)
3. **Provider not available**: Check optional dependencies are installed
4. **Summary not created**: Verify conversation pair threshold is reached
5. **Memory usage**: Adjust `pairs_threshold` and `recent_pairs_to_preserve`
6. **Summary node errors**: Use built-in `summary_manager.summary_node` with error handling
7. **Missing summary logs**: Configure logger with `summary_manager.set_logger(logger)`
8. **STT transcription fails**: Check audio format (MP3/WAV/M4A), file size limits, and API key
9. **Audio file too large**: OpenAI Whisper has 25MB limit - consider audio preprocessing
10. **STT provider not available**: Install with `uv add fastal-langgraph-toolkit[stt]` or `uv add openai`
11. **Async STT not working**: Ensure using `await stt.atranscribe()` not `stt.transcribe()`
12. **Empty transcription results**: Check audio quality, volume levels, and language settings

## STT Testing Patterns

### Testing Without OpenAI Installed
The STT tests are designed to work without OpenAI installed, using conditional imports and skipping:

```python
# In tests/test_stt.py
try:
    from fastal.langgraph.toolkit.models.providers.stt.openai import OpenAISTTProvider
    OPENAI_STT_AVAILABLE = True
except ImportError:
    OPENAI_STT_AVAILABLE = False
    OpenAISTTProvider = None

@pytest.mark.skipif(not OPENAI_STT_AVAILABLE, reason="OpenAI STT provider not available")
class TestOpenAISTTProvider:
    # Tests run only when OpenAI is available
```

### Mock-Based STT Testing
```python
# Test transcription without real API calls
def test_transcribe_with_mocked_client(self):
    provider = OpenAISTTProvider(config, "whisper-1")
    
    mock_client = Mock()
    mock_response = Mock()
    mock_response.text = "Test transcription"
    mock_response.language = "en"
    mock_client.audio.transcriptions.create.return_value = mock_response
    
    with patch.object(provider, '_create_model', return_value=mock_client):
        result = provider.transcribe(audio_data)
        assert result["text"] == "Test transcription"
```

### Running STT Tests
```bash
# All tests (including STT)
uv run pytest tests/ -v

# STT tests only  
uv run pytest tests/test_stt.py -v

# STT tests with OpenAI available (if installed)
uv add openai && uv run pytest tests/test_stt.py -v
```

## Testing Strategy

### Environment Isolation
- **Development**: Full environment with all optional dependencies
- **CI**: Clean environment testing for import compatibility
- **Production Testing**: Multi-environment validation before release

### Test Coverage
- Unit tests for core functionality (LLM, embeddings, STT)
- Integration tests for provider compatibility
- Async test support with pytest-asyncio (including STT async operations)
- Import testing without optional dependencies (TYPE_CHECKING pattern)
- STT-specific test patterns:
  - Conditional test skipping when OpenAI not available
  - Mock-based transcription testing
  - Audio format and error handling validation
  - Provider availability and fallback testing

This toolkit represents battle-tested patterns from real enterprise implementations, extracted into a reusable package for the LangGraph community.