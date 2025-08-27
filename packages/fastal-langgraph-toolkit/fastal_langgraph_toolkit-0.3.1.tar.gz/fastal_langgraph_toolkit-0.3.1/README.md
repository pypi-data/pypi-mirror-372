# Fastal LangGraph Toolkit

[![CI/CD](https://github.com/FastalGroup/fastal-langgraph-toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/FastalGroup/fastal-langgraph-toolkit/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/fastal-langgraph-toolkit)](https://pypi.org/project/fastal-langgraph-toolkit/)

**Production-ready toolkit for building enterprise LangGraph agents with multi-provider support, intelligent conversation management, and speech processing capabilities.**

## 🏢 About

The Fastal LangGraph Toolkit was originally developed internally by the **Fastal Group** to support enterprise-grade agentic application implementations across multiple client projects. After proving its effectiveness in production environments, we've open-sourced this toolkit to contribute to the broader LangGraph community.

### Why This Toolkit?

Building production LangGraph agents involves solving common challenges in advanced research and development projects:
- **Multi-provider Management**: Support for multiple LLM/embedding/speech providers with seamless switching
- **Context Management**: Intelligent conversation summarization for long-running sessions
- **Memory Optimization**: Token-efficient context handling for cost control
- **Speech Processing**: Enterprise-grade speech-to-text transcription capabilities
- **Type Safety**: Proper state management with TypedDict integration
- **Configuration Injection**: Clean separation between business logic and framework concerns

This toolkit provides battle-tested solutions for these challenges, extracted from real enterprise implementations.

## ✨ Features

### 🔄 Multi-Provider Model Factory (Chat LLM, Embeddings & Speech)
The current version of the model factory supports the following providers, more providers will be added in future versions.

- **LLM Support**: OpenAI, Anthropic, Ollama, AWS Bedrock
- **Embeddings Support**: OpenAI, Ollama, AWS Bedrock  
- **Speech-to-Text Support**: OpenAI Whisper (more providers coming soon)

Main features:
- **Configuration Injection**: Clean provider abstraction
- **Provider Health Checks**: Availability validation
- **Seamless Switching**: Change providers without code changes

### 🎤 Enterprise Speech Processing

Production-ready speech-to-text processing with enterprise-grade reliability and performance.

Features:
- **Multi-Format Support**: MP3, WAV, M4A, and other common audio formats
- **Language Detection**: Automatic language identification and custom language hints
- **Async Processing**: Full async/await support for non-blocking operations  
- **Segment Information**: Detailed timestamp and confidence data when available
- **Error Handling**: Robust error management with detailed logging
- **Type Safety**: Standardized `TranscriptionResult` format across providers
- **Lazy Loading**: Efficient resource management with provider lazy loading

### 🧠 Intelligent Conversation Summarization

The LangChain/LangGraph framework provides good support for managing both short-term and long-term memory in agents through the LangMem module. However, we found that automated summarization based solely on token counting is not a sufficient approach for most real and complex agents. The solution included in this kit offers an alternative and more sophisticated method, based on the structure of the conversation and a focus on the object and content of the discussions.

Features:
- **Ready-to-Use LangGraph Node**: `summary_node()` method provides instant integration
- **Conversation Pair Counting**: Smart Human+AI message pair detection
- **ReAct Tool Filtering**: Automatic exclusion of tool calls from summaries
- **Configurable Thresholds**: Customizable trigger points for summarization
- **Context Preservation**: Keep recent conversations for continuity
- **Custom Prompts**: Domain-specific summarization templates
- **State Auto-Injection**: Seamless integration with existing states
- **Token Optimization**: Reduce context length for cost efficiency
- **Built-in Error Handling**: Robust error management with optional logging

### 💾 Memory Management
- **`SummarizableState`**: Type-safe base class for summary-enabled states
- **Automatic State Management**: No manual field initialization required
- **LangGraph Integration**: Native compatibility with LangGraph checkpointing
- **Clean Architecture**: Separation of concerns between summary and business logic

## 📦 Installation

### From PyPI (Recommended)
```bash
# Using uv (recommended)
uv add fastal-langgraph-toolkit

# Using pip
pip install fastal-langgraph-toolkit
```

### Optional Dependencies for Speech Processing
```bash
# Install with STT support
uv add "fastal-langgraph-toolkit[stt]"

# Or install manually
uv add fastal-langgraph-toolkit openai
```

### Development Installation
```bash
# Clone the repository
git clone https://github.com/fastal/langgraph-toolkit.git
cd fastal-langgraph-toolkit

# Install in editable mode with uv
uv add --editable .

# Or with pip
pip install -e .
```

### Requirements
- **Python**: 3.10+ 
- **LangChain**: Core components for LLM integration
- **LangGraph**: State management and agent workflows
- **Pydantic**: Type validation and settings management

## 🚀 Quick Start

### Multi-Provider Model Factory

```python
from fastal.langgraph.toolkit import ModelFactory
from types import SimpleNamespace

# Configuration using SimpleNamespace (required)
config = SimpleNamespace(
    api_key="your-api-key",
    temperature=0.7,
    streaming=True  # Enable streaming for real-time responses
)

# Create LLM with different providers
openai_llm = ModelFactory.create_llm("openai", "gpt-4o", config)
claude_llm = ModelFactory.create_llm("anthropic", "claude-3-sonnet-20240229", config)
local_llm = ModelFactory.create_llm("ollama", "llama2", config)

# Create embeddings
embeddings = ModelFactory.create_embeddings("openai", "text-embedding-3-small", config)

# Check what's available in your environment
providers = ModelFactory.get_available_providers()
print(f"Available LLM providers: {providers['llm_providers']}")
print(f"Available embedding providers: {providers['embedding_providers']}")
print(f"Available STT providers: {providers['stt_providers']}")
```

### Speech-to-Text Processing

```python
from fastal.langgraph.toolkit import ModelFactory, TranscriptionResult
import asyncio

# Configure STT provider (OpenAI Whisper)
stt_config = SimpleNamespace(
    api_key="your-openai-api-key"
)

# Create STT instance
stt = ModelFactory.create_stt("openai", "whisper-1", stt_config)

# Synchronous transcription
with open("audio.mp3", "rb") as audio_file:
    audio_data = audio_file.read()

result = stt.transcribe(
    audio_data,
    language="en",        # Optional: Language hint
    temperature=0.2,      # Optional: Lower = more deterministic
    response_format="verbose_json"  # Get detailed segment information
)

print(f"Transcribed text: {result['text']}")
print(f"Detected language: {result['language']}")
print(f"Duration: {result['duration_seconds']} seconds")

# Process segments if available
if result.get('segments'):
    for segment in result['segments']:
        print(f"{segment['start']:.2f}s - {segment['end']:.2f}s: {segment['text']}")

# Async transcription
async def async_transcribe():
    result = await stt.atranscribe(audio_data, language="en")
    return result['text']

# Run async example
text = asyncio.run(async_transcribe())
print(f"Async result: {text}")
```

### Intelligent Conversation Summarization

#### Basic Setup
```python
from fastal.langgraph.toolkit import SummaryManager, SummaryConfig, SummarizableState
from langchain_core.messages import HumanMessage, AIMessage
from typing import Annotated
from langgraph.graph.message import add_messages

# 1. Define your state using SummarizableState (recommended)
class MyAgentState(SummarizableState):
    """Your agent state with automatic summary support"""
    messages: Annotated[list, add_messages]
    thread_id: str
    # summary and last_summarized_index are automatically provided

# 2. Create summary manager with default settings
llm = ModelFactory.create_llm("openai", "gpt-4o", config)
summary_manager = SummaryManager(llm)

# 3. Use ready-to-use summary node in your LangGraph workflow
from langgraph.graph import StateGraph
import logging

# Optional: Configure logging for summary operations
logger = logging.getLogger(__name__)
summary_manager.set_logger(logger)

# Add to your workflow
workflow = StateGraph(MyAgentState)
workflow.add_node("summary_check", summary_manager.summary_node)  # Ready-to-use!
workflow.set_entry_point("summary_check")
```

#### Advanced Configuration
```python
# Custom configuration for domain-specific needs
custom_config = SummaryConfig(
    pairs_threshold=20,  # Trigger summary after 20 conversation pairs
    recent_pairs_to_preserve=5,  # Keep last 5 pairs in full context
    max_summary_length=500,  # Max words in summary
    
    # Custom prompts for your domain
    new_summary_prompt="""
    Analyze this customer support conversation and create a concise summary focusing on:
    - Customer's main issue or request
    - Actions taken by the agent
    - Current status of the resolution
    - Any pending items or next steps
    
    Conversation to summarize:
    {messages_text}
    """,
    
    combine_summary_prompt="""
    Update the existing summary with new information from the recent conversation.
    
    Previous summary:
    {existing_summary}
    
    New conversation:
    {messages_text}
    
    Provide an updated comprehensive summary:
    """
)

summary_manager = SummaryManager(llm, custom_config)
```

#### Complete LangGraph Integration Example

**Simple Approach (Recommended):**
```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import logging

logger = logging.getLogger(__name__)

class CustomerSupportAgent:
    def __init__(self):
        self.llm = ModelFactory.create_llm("openai", "gpt-4o", config)
        self.summary_manager = SummaryManager(self.llm, custom_config)
        # Optional: Configure logging for summary operations
        self.summary_manager.set_logger(logger)
        self.graph = self._create_graph()
    
    async def _agent_node(self, state: MyAgentState) -> dict:
        """Main agent logic with optimized context"""
        messages = state["messages"]
        last_idx = state.get("last_summarized_index", 0)
        summary = state.get("summary")
        
        # Use only recent messages + summary for context efficiency
        recent_messages = messages[last_idx:]
        
        if summary:
            system_msg = f"Previous conversation summary: {summary}\n\nContinue the conversation:"
            context = [SystemMessage(content=system_msg)] + recent_messages
        else:
            context = recent_messages
        
        response = await self.llm.ainvoke(context)
        return {"messages": [response]}
    
    def _create_graph(self):
        workflow = StateGraph(MyAgentState)
        
        # Use ready-to-use summary node from toolkit
        workflow.add_node("summary_check", self.summary_manager.summary_node)
        workflow.add_node("agent", self._agent_node)
        
        workflow.set_entry_point("summary_check")
        workflow.add_edge("summary_check", "agent")
        workflow.add_edge("agent", "__end__")
        
        return workflow
    
    async def process_message(self, message: str, thread_id: str):
        """Process user message with automatic summarization"""
        async with AsyncPostgresSaver.from_conn_string(db_url) as checkpointer:
            app = self.graph.compile(checkpointer=checkpointer)
            
            config = {"configurable": {"thread_id": thread_id}}
            input_state = {"messages": [HumanMessage(content=message)]}
            
            result = await app.ainvoke(input_state, config=config)
            return result["messages"][-1].content
```

**Advanced Approach (Custom Implementation):**
```python
# If you need custom logic in your summary node
class AdvancedCustomerSupportAgent:
    def __init__(self):
        self.llm = ModelFactory.create_llm("openai", "gpt-4o", config)
        self.summary_manager = SummaryManager(self.llm, custom_config)
        self.graph = self._create_graph()
    
    async def _custom_summary_node(self, state: MyAgentState) -> dict:
        """Custom summary node with additional business logic"""
        thread_id = state.get("thread_id", "")
        
        # Custom business logic before summarization
        if self._should_skip_summary(state):
            return {}
        
        # Use summary manager for the actual summarization
        if await self.summary_manager.should_create_summary(state):
            result = await self.summary_manager.process_summary(state)
            
            # Custom logging or analytics
            if result:
                logger.info(f"Summary created for customer thread {thread_id}")
                self._track_summary_analytics(state, result)
            
            return result
        
        return {}
    
    def _should_skip_summary(self, state):
        """Custom business logic to skip summarization"""
        # Example: Skip for priority customers or short sessions
        return False
    
    def _track_summary_analytics(self, state, result):
        """Custom analytics tracking"""
        pass
```

## 📋 API Reference

### ModelFactory

Main factory class for creating LLM and embedding instances across multiple providers.

#### `ModelFactory.create_llm(provider: str, model: str, config: SimpleNamespace) -> BaseChatModel`

Creates an LLM instance for the specified provider.

**Parameters:**
- `provider`: Provider name (`"openai"`, `"anthropic"`, `"ollama"`, `"bedrock"`)
- `model`: Model name (e.g., `"gpt-4o"`, `"claude-3-sonnet-20240229"`)
- `config`: Configuration object with provider-specific settings

**Returns:** LangChain `BaseChatModel` instance

**Example:**
```python
from types import SimpleNamespace
from fastal.langgraph.toolkit import ModelFactory

config = SimpleNamespace(api_key="sk-...", temperature=0.7, streaming=True)
llm = ModelFactory.create_llm("openai", "gpt-4o", config)
```

#### `ModelFactory.create_embeddings(provider: str, model: str, config: SimpleNamespace) -> Embeddings`

Creates an embeddings instance for the specified provider.

**Parameters:**
- `provider`: Provider name (`"openai"`, `"ollama"`, `"bedrock"`)
- `model`: Model name (e.g., `"text-embedding-3-small"`)
- `config`: Configuration object with provider-specific settings

**Returns:** LangChain `Embeddings` instance

#### `ModelFactory.create_stt(provider: str, model: str | None, config: SimpleNamespace) -> BaseSTTProvider`

Creates a speech-to-text instance for the specified provider.

**Parameters:**
- `provider`: Provider name (`"openai"` - more providers coming soon)
- `model`: Optional model name (defaults to provider's default, e.g., `"whisper-1"`)
- `config`: Configuration object with provider-specific settings

**Returns:** STT provider instance with transcription capabilities

**Example:**
```python
from types import SimpleNamespace
from fastal.langgraph.toolkit import ModelFactory

config = SimpleNamespace(api_key="sk-...")
stt = ModelFactory.create_stt("openai", "whisper-1", config)

# Transcribe audio
with open("audio.mp3", "rb") as f:
    result = stt.transcribe(f.read(), language="en")
    print(result['text'])
```

#### `ModelFactory.get_available_providers() -> dict`

Returns available providers in the current environment.

**Returns:** Dictionary with `"llm_providers"`, `"embedding_providers"`, and `"stt_providers"` keys containing available provider lists

### SummaryManager

Manages intelligent conversation summarization with configurable thresholds and custom prompts.

#### `SummaryManager(llm: BaseChatModel, config: SummaryConfig | None = None)`

Initialize summary manager with LLM and optional configuration.

**Parameters:**
- `llm`: LangChain LLM instance for generating summaries
- `config`: Optional `SummaryConfig` instance (uses defaults if None)

#### `async should_create_summary(state: dict) -> bool`

Determines if summarization is needed based on conversation pairs threshold.

**Parameters:**
- `state`: Current agent state containing messages and summary info

**Returns:** `True` if summary should be created, `False` otherwise

#### `async process_summary(state: dict) -> dict`

Creates or updates conversation summary and returns state updates.

**Parameters:**
- `state`: Current agent state

**Returns:** Dictionary with `summary` and `last_summarized_index` fields

#### `count_conversation_pairs(messages: list, start_index: int = 0) -> int`

Counts Human+AI conversation pairs, excluding tool calls.

**Parameters:**
- `messages`: List of LangChain messages
- `start_index`: Starting index for counting (default: 0)

**Returns:** Number of complete conversation pairs

#### `async summary_node(state: dict) -> dict`

**Ready-to-use LangGraph node for conversation summarization.**

This method provides a complete LangGraph node that can be directly added to workflows. It handles the entire summary workflow internally and provides optional logging.

**Parameters:**
- `state`: LangGraph state (will be auto-injected with summary fields if missing)

**Returns:** Empty dict if no summary needed, or dict with summary fields if created

**Example:**
```python
# In your LangGraph workflow
summary_manager = SummaryManager(llm, config)
summary_manager.set_logger(logger)  # Optional logging

workflow.add_node("summary_check", summary_manager.summary_node)
workflow.set_entry_point("summary_check")
```

#### `set_logger(logger)`

Set logger for summary_node logging (optional).

**Parameters:**
- `logger`: Logger instance for summary_node operations

**Note:** When a logger is configured, `summary_node()` will automatically log when summaries are created.

### SummaryConfig

Configuration class for customizing summarization behavior.

#### `SummaryConfig(**kwargs)`

**Parameters:**
- `pairs_threshold: int = 10` - Trigger summary after N conversation pairs
- `recent_pairs_to_preserve: int = 3` - Keep N recent pairs in context
- `max_summary_length: int = 200` - Maximum words in summary
- `new_summary_prompt: str` - Template for creating new summaries
- `combine_summary_prompt: str` - Template for updating existing summaries

**Default Prompts:**
```python
# Default new summary prompt
new_summary_prompt = """
Analyze the conversation and create a concise summary highlighting:
- Main topics discussed
- Key decisions or conclusions
- Important context for future interactions

Conversation:
{messages_text}

Summary:
"""

# Default combine summary prompt  
combine_summary_prompt = """
Existing Summary: {existing_summary}

New Conversation: {messages_text}

Create an updated summary that combines the essential information:
"""
```

### SummarizableState

Base TypedDict class for states that support automatic summarization.

#### Inheritance Usage
```python
from fastal.langgraph.toolkit import SummarizableState
from typing import Annotated
from langgraph.graph.message import add_messages

class MyAgentState(SummarizableState):
    """Your custom state with summary support"""
    messages: Annotated[list, add_messages]
    thread_id: str
    # summary: str | None - automatically provided
    # last_summarized_index: int - automatically provided
```

**Provided Fields:**
- `summary: str | None` - Current conversation summary
- `last_summarized_index: int` - Index of first message NOT in last summary

### Speech-to-Text Providers

Base class and methods for speech-to-text operations across different providers.

#### `BaseSTTProvider.transcribe(audio_data: bytes, **kwargs) -> TranscriptionResult`

Transcribe audio to text synchronously.

**Parameters:**
- `audio_data`: Audio file data in bytes format
- `**kwargs`: Provider-specific parameters (language, temperature, etc.)

**Returns:** `TranscriptionResult` dictionary with transcription data

#### `BaseSTTProvider.atranscribe(audio_data: bytes, **kwargs) -> TranscriptionResult`

Transcribe audio to text asynchronously.

**Parameters:**
- `audio_data`: Audio file data in bytes format  
- `**kwargs`: Provider-specific parameters (language, temperature, etc.)

**Returns:** `TranscriptionResult` dictionary with transcription data

### TranscriptionResult

Standardized result format for speech-to-text operations.

#### Fields:
- `text: str` - The transcribed text
- `language: str | None` - Detected or specified language code
- `confidence: float | None` - Overall confidence score (if available)
- `duration_seconds: float | None` - Audio duration in seconds
- `segments: List[TranscriptionSegment] | None` - Detailed segment information
- `warnings: List[str] | None` - Any warnings or notes

#### TranscriptionSegment Fields:
- `text: str` - Segment text
- `start: float` - Start time in seconds
- `end: float` - End time in seconds  
- `confidence: float | None` - Segment confidence score

**Example:**
```python
result = stt.transcribe(audio_data, response_format="verbose_json")

print(f"Text: {result['text']}")
print(f"Language: {result['language']}")
print(f"Duration: {result['duration_seconds']}s")

# Process segments
for segment in result.get('segments', []):
    print(f"{segment['start']:.1f}s: {segment['text']}")
```

## ⚙️ Configuration

### SimpleNamespace Requirement

The toolkit requires configuration objects (not dictionaries) for type safety and dot notation access:

```python
from types import SimpleNamespace

# ✅ Correct - SimpleNamespace
config = SimpleNamespace(
    api_key="sk-...",
    base_url="https://api.openai.com/v1",  # Optional
    temperature=0.7,                        # Optional
    streaming=True                          # Optional
)

# ❌ Incorrect - Dictionary
config = {"api_key": "sk-...", "temperature": 0.7}
```

### Provider-Specific Configuration

#### OpenAI
```python
# For LLM and Embeddings
openai_config = SimpleNamespace(
    api_key="sk-...",              # Required (or set OPENAI_API_KEY)
    base_url="https://api.openai.com/v1",  # Optional
    organization="org-...",         # Optional
    temperature=0.7,               # Optional
    streaming=True,                # Optional
    max_tokens=1000                # Optional
)

# For Speech-to-Text (Whisper)
openai_stt_config = SimpleNamespace(
    api_key="sk-...",              # Required (or set OPENAI_API_KEY)
    # Most Whisper parameters are set per-request, not in config
)
```

#### Anthropic
```python
anthropic_config = SimpleNamespace(
    api_key="sk-ant-...",          # Required (or set ANTHROPIC_API_KEY)
    temperature=0.7,               # Optional
    streaming=True,                # Optional
    max_tokens=1000                # Optional
)
```

#### Ollama (Local)
```python
ollama_config = SimpleNamespace(
    base_url="http://localhost:11434",  # Optional (default)
    temperature=0.7,                    # Optional
    streaming=True                      # Optional
)
```

#### AWS Bedrock
```python
bedrock_config = SimpleNamespace(
    region="us-east-1",            # Optional (uses AWS config)
    aws_access_key_id="...",       # Optional (uses AWS config)
    aws_secret_access_key="...",   # Optional (uses AWS config)
    temperature=0.7,               # Optional
    streaming=True                 # Optional
)
```

### Environment Variables Helper

```python
from fastal.langgraph.toolkit.models.config import get_default_config

# Automatically uses environment variables
openai_config = get_default_config("openai")     # Uses OPENAI_API_KEY
anthropic_config = get_default_config("anthropic") # Uses ANTHROPIC_API_KEY
```

## 🎯 Advanced Examples

### Enterprise Multi-Provider Setup

```python
from fastal.langgraph.toolkit import ModelFactory
from types import SimpleNamespace
import os

class EnterpriseAgentConfig:
    """Enterprise configuration with fallback providers"""
    
    def __init__(self):
        self.primary_llm = self._setup_primary_llm()
        self.fallback_llm = self._setup_fallback_llm()
        self.embeddings = self._setup_embeddings()
    
    def _setup_primary_llm(self):
        """Primary: OpenAI GPT-4"""
        if os.getenv("OPENAI_API_KEY"):
            config = SimpleNamespace(
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.1,
                streaming=True,
                max_tokens=2000
            )
            return ModelFactory.create_llm("openai", "gpt-4o", config)
        return None
    
    def _setup_fallback_llm(self):
        """Fallback: Anthropic Claude"""
        if os.getenv("ANTHROPIC_API_KEY"):
            config = SimpleNamespace(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=0.1,
                streaming=True,
                max_tokens=2000
            )
            return ModelFactory.create_llm("anthropic", "claude-3-sonnet-20240229", config)
        return None
    
    def _setup_embeddings(self):
        """Embeddings with local fallback"""
        # Try OpenAI first
        if os.getenv("OPENAI_API_KEY"):
            config = SimpleNamespace(api_key=os.getenv("OPENAI_API_KEY"))
            return ModelFactory.create_embeddings("openai", "text-embedding-3-small", config)
        
        # Fallback to local Ollama
        config = SimpleNamespace(base_url="http://localhost:11434")
        return ModelFactory.create_embeddings("ollama", "nomic-embed-text", config)
    
    def get_llm(self):
        """Get available LLM with fallback logic"""
        return self.primary_llm or self.fallback_llm
```

### Domain-Specific Summarization

```python
from fastal.langgraph.toolkit import SummaryManager, SummaryConfig

class CustomerServiceSummaryManager:
    """Specialized summary manager for customer service conversations"""
    
    def __init__(self, llm):
        # Customer service specific configuration
        self.config = SummaryConfig(
            pairs_threshold=8,  # Shorter conversations in support
            recent_pairs_to_preserve=3,
            max_summary_length=400,
            
            new_summary_prompt="""
            Analyze this customer service conversation and create a structured summary:

            **Customer Information:**
            - Name/Contact: [Extract if mentioned]
            - Account/Order: [Extract if mentioned]

            **Issue Summary:**
            - Problem: [Main issue described]
            - Category: [Technical/Billing/General/etc.]
            - Urgency: [High/Medium/Low based on language]

            **Actions Taken:**
            - Solutions attempted: [List what agent tried]
            - Information provided: [Key info given to customer]

            **Current Status:**
            - Resolution status: [Resolved/Pending/Escalated]
            - Next steps: [What needs to happen next]

            **Conversation:**
            {messages_text}

            **Structured Summary:**
            """,
            
            combine_summary_prompt="""
            Update the customer service summary with new conversation information:

            **Previous Summary:**
            {existing_summary}

            **New Conversation:**
            {messages_text}

            **Updated Summary:**
            Merge the information, updating status and adding new actions/developments:
            """
        )
        
        self.summary_manager = SummaryManager(llm, self.config)
    
    async def process_summary(self, state):
        """Process with customer service specific logic"""
        return await self.summary_manager.process_summary(state)
```

### Multi-Modal Agent with Speech Processing

```python
from fastal.langgraph.toolkit import ModelFactory, SummaryManager, SummarizableState
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph
import asyncio

class MultiModalAgentState(SummarizableState):
    """State supporting both text and speech inputs"""
    messages: Annotated[list, add_messages]
    thread_id: str
    audio_transcriptions: list = []
    processing_metadata: dict = {}

class MultiModalAgent:
    """Agent that handles both text and speech inputs"""
    
    def __init__(self):
        # Configure providers
        config = SimpleNamespace(api_key=os.getenv("OPENAI_API_KEY"))
        
        self.llm = ModelFactory.create_llm("openai", "gpt-4o", config)
        self.stt = ModelFactory.create_stt("openai", "whisper-1", config)
        self.summary_manager = SummaryManager(self.llm)
        
        self.graph = self._create_graph()
    
    async def _audio_processing_node(self, state: MultiModalAgentState):
        """Node to process incoming audio files"""
        messages = state["messages"]
        latest_message = messages[-1] if messages else None
        
        # Check if latest message contains audio data
        audio_data = getattr(latest_message, 'audio_data', None)
        if not audio_data:
            return {}
        
        try:
            # Transcribe audio with enhanced settings
            transcription = await self.stt.atranscribe(
                audio_data,
                language="auto",  # Auto-detect language
                temperature=0.1,  # High accuracy
                response_format="verbose_json"  # Get segments
            )
            
            # Store transcription with metadata
            transcription_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "text": transcription["text"],
                "language": transcription["language"],
                "duration": transcription["duration_seconds"],
                "segments": transcription.get("segments", []),
                "message_id": len(messages) - 1
            }
            
            # Add transcribed text as new message
            from langchain_core.messages import HumanMessage
            text_message = HumanMessage(
                content=f"[Audio transcription]: {transcription['text']}"
            )
            
            return {
                "messages": [text_message],
                "audio_transcriptions": state.get("audio_transcriptions", []) + [transcription_record],
                "processing_metadata": {
                    **state.get("processing_metadata", {}),
                    "last_audio_processed": transcription_record["timestamp"]
                }
            }
            
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            # Add error message instead of failing
            error_message = HumanMessage(content="[Audio processing error - please try again]")
            return {"messages": [error_message]}

    async def _intelligent_agent_node(self, state: MultiModalAgentState):
        """Main agent node with audio context awareness"""
        messages = state["messages"]
        audio_transcriptions = state.get("audio_transcriptions", [])
        
        # Build context with audio awareness
        context_prefix = ""
        if audio_transcriptions:
            recent_audio = audio_transcriptions[-3:]  # Last 3 audio inputs
            audio_summary = "\n".join([
                f"- Audio {i+1}: {trans['text'][:100]}..." 
                for i, trans in enumerate(recent_audio)
            ])
            context_prefix = f"Recent audio inputs:\n{audio_summary}\n\n"
        
        # Use summarized context if available
        summary = state.get("summary", "")
        if summary:
            context_prefix += f"Conversation summary: {summary}\n\n"
        
        # Prepare messages with context
        if context_prefix:
            from langchain_core.messages import SystemMessage
            context_msg = SystemMessage(content=context_prefix + "Continue the conversation:")
            recent_messages = messages[-5:]  # Only recent messages
            llm_input = [context_msg] + recent_messages
        else:
            llm_input = messages
        
        response = await self.llm.ainvoke(llm_input)
        return {"messages": [response]}
    
    def _create_graph(self):
        """Create the multi-modal processing graph"""
        workflow = StateGraph(MultiModalAgentState)
        
        # Add nodes
        workflow.add_node("audio_processing", self._audio_processing_node)
        workflow.add_node("summary_check", self.summary_manager.summary_node)
        workflow.add_node("agent", self._intelligent_agent_node)
        
        # Define flow
        workflow.set_entry_point("audio_processing")
        workflow.add_edge("audio_processing", "summary_check")
        workflow.add_edge("summary_check", "agent")
        workflow.add_edge("agent", "__end__")
        
        return workflow.compile()
    
    async def process_audio_message(self, audio_data: bytes, thread_id: str):
        """Process audio input with full pipeline"""
        # Create audio message (custom message type)
        class AudioMessage:
            def __init__(self, audio_data):
                self.audio_data = audio_data
                self.content = "[Audio message]"
        
        config = {"configurable": {"thread_id": thread_id}}
        input_state = {
            "messages": [AudioMessage(audio_data)],
            "thread_id": thread_id
        }
        
        result = await self.graph.ainvoke(input_state, config=config)
        return result
    
    async def process_text_message(self, text: str, thread_id: str):
        """Process text input (standard flow)"""
        from langchain_core.messages import HumanMessage
        
        config = {"configurable": {"thread_id": thread_id}}
        input_state = {
            "messages": [HumanMessage(content=text)],
            "thread_id": thread_id
        }
        
        result = await self.graph.ainvoke(input_state, config=config)
        return result
    
    def get_audio_history(self, thread_id: str, limit: int = 10):
        """Get audio transcription history for a thread"""
        # This would typically query your checkpointer
        # For now, return from current state
        return {"transcriptions": "Audio history would be retrieved from checkpointer"}

# Usage example
async def multi_modal_example():
    agent = MultiModalAgent()
    
    # Process audio file
    with open("user_question.mp3", "rb") as f:
        audio_data = f.read()
    
    result = await agent.process_audio_message(audio_data, "user123")
    print("Audio processing result:", result["messages"][-1].content)
    
    # Follow up with text
    text_result = await agent.process_text_message(
        "Can you clarify that last point?", "user123"
    )
    print("Text follow-up:", text_result["messages"][-1].content)

# Run the example
# asyncio.run(multi_modal_example())
```

### Real-time Audio Processing Pipeline

```python
import aiofiles
from pathlib import Path

class RealTimeAudioProcessor:
    """Process audio files from a directory in real-time"""
    
    def __init__(self, watch_directory: str):
        self.watch_directory = Path(watch_directory)
        self.stt = ModelFactory.create_stt("openai", config=SimpleNamespace(
            api_key=os.getenv("OPENAI_API_KEY")
        ))
        self.processed_files = set()
    
    async def process_audio_file(self, file_path: Path):
        """Process a single audio file"""
        async with aiofiles.open(file_path, 'rb') as f:
            audio_data = await f.read()
        
        # Transcribe with optimized settings
        result = await self.stt.atranscribe(
            audio_data,
            language="en",
            temperature=0.0,  # Maximum accuracy
            response_format="verbose_json"
        )
        
        # Save results
        output_file = file_path.with_suffix('.json')
        output_data = {
            "source_file": str(file_path),
            "transcription": result,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        async with aiofiles.open(output_file, 'w') as f:
            await f.write(json.dumps(output_data, indent=2))
        
        return result
    
    async def watch_and_process(self):
        """Watch directory and process new audio files"""
        while True:
            try:
                # Find new audio files
                audio_files = list(self.watch_directory.glob("*.mp3")) + \
                             list(self.watch_directory.glob("*.wav")) + \
                             list(self.watch_directory.glob("*.m4a"))
                
                new_files = [f for f in audio_files if f not in self.processed_files]
                
                if new_files:
                    print(f"Found {len(new_files)} new audio files")
                    
                    # Process files concurrently
                    tasks = [self.process_audio_file(file) for file in new_files]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for file, result in zip(new_files, results):
                        if isinstance(result, Exception):
                            print(f"Error processing {file}: {result}")
                        else:
                            print(f"✓ Processed {file.name}: {result['text'][:100]}...")
                            self.processed_files.add(file)
                
                # Wait before next check
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                print("Stopping audio processor...")
                break
            except Exception as e:
                print(f"Error in watch loop: {e}")
                await asyncio.sleep(10)

# Usage
processor = RealTimeAudioProcessor("./audio_input")
# asyncio.run(processor.watch_and_process())
```

### Memory-Optimized Long Conversations

```python
from fastal.langgraph.toolkit import SummarizableState, SummaryManager
from typing import Annotated
from langgraph.graph.message import add_messages

class OptimizedConversationState(SummarizableState):
    """State optimized for very long conversations"""
    messages: Annotated[list, add_messages]
    thread_id: str
    user_context: dict = {}  # Additional user context
    conversation_metadata: dict = {}  # Metadata for analytics

class LongConversationAgent:
    """Agent optimized for handling very long conversations"""
    
    def __init__(self, llm):
        # Aggressive summarization for memory efficiency
        config = SummaryConfig(
            pairs_threshold=5,    # Frequent summarization
            recent_pairs_to_preserve=2,  # Minimal recent context
            max_summary_length=600,  # Comprehensive summaries
        )
        
        self.summary_manager = SummaryManager(llm, config)
        self.llm = llm
    
    async def process_with_optimization(self, state: OptimizedConversationState):
        """Process message with aggressive memory optimization"""
        
        # Always check for summarization opportunities
        if await self.summary_manager.should_create_summary(state):
            # Create summary to optimize memory
            summary_update = await self.summary_manager.process_summary(state)
            state.update(summary_update)
        
        # Use only recent context + summary for LLM call
        messages = state["messages"]
        last_idx = state.get("last_summarized_index", 0)
        summary = state.get("summary")
        
        # Ultra-minimal context for cost efficiency
        recent_messages = messages[last_idx:]
        
        if summary:
            context = f"Context: {summary}\n\nContinue conversation:"
            context_msg = SystemMessage(content=context)
            llm_input = [context_msg] + recent_messages[-2:]  # Only last exchange
        else:
            llm_input = recent_messages[-4:]  # Minimal fallback
        
        response = await self.llm.ainvoke(llm_input)
        return {"messages": [response]}
```

### Token Usage Analytics

```python
import tiktoken
from collections import defaultdict

class TokenOptimizedSummaryManager:
    """Summary manager with token usage tracking and optimization"""
    
    def __init__(self, llm, config=None):
        self.summary_manager = SummaryManager(llm, config)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
        self.token_stats = defaultdict(int)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    async def process_with_analytics(self, state):
        """Process summary with token usage analytics"""
        messages = state["messages"]
        
        # Count tokens before summarization
        total_tokens_before = sum(
            self.count_tokens(str(msg.content)) for msg in messages
        )
        
        # Process summary
        result = await self.summary_manager.process_summary(state)
        
        if result:  # Summary was created
            summary = result.get("summary", "")
            last_idx = result.get("last_summarized_index", 0)
            
            # Count tokens after summarization
            remaining_messages = messages[last_idx:]
            remaining_tokens = sum(
                self.count_tokens(str(msg.content)) for msg in remaining_messages
            )
            summary_tokens = self.count_tokens(summary)
            total_tokens_after = remaining_tokens + summary_tokens
            
            # Track savings
            tokens_saved = total_tokens_before - total_tokens_after
            self.token_stats["tokens_saved"] += tokens_saved
            self.token_stats["summaries_created"] += 1
            
            print(f"💰 Token optimization: {tokens_saved} tokens saved "
                  f"({total_tokens_before} → {total_tokens_after})")
        
        return result
    
    def get_analytics(self):
        """Get token usage analytics"""
        return dict(self.token_stats)
```

## 🔧 Best Practices

### 1. State Design
```python
# ✅ Use SummarizableState for automatic summary support
class MyAgentState(SummarizableState):
    messages: Annotated[list, add_messages]
    thread_id: str

# ❌ Don't manually define summary fields
class BadAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    thread_id: str
    summary: str | None  # Manual definition not needed
    last_summarized_index: int  # Manual definition not needed
```

### 2. Graph Architecture
```python
# ✅ Use ready-to-use summary node (Recommended)
summary_manager = SummaryManager(llm, config)
summary_manager.set_logger(logger)  # Optional logging

workflow.add_node("summary_check", summary_manager.summary_node)
workflow.set_entry_point("summary_check")  # Always check summary first
workflow.add_edge("summary_check", "agent")  # Then process
workflow.add_edge("tools", "agent")  # Tools return to agent, not summary

# ✅ Alternative: Custom summary node (if you need custom logic)
async def custom_summary_node(state):
    if await summary_manager.should_create_summary(state):
        return await summary_manager.process_summary(state)
    return {}

workflow.add_node("summary_check", custom_summary_node)

# ❌ Don't create summaries mid-conversation
# This would create summaries during tool execution
workflow.add_edge("tools", "summary_check")  # Wrong!
```

### 3. Configuration Management
```python
# ✅ Environment-based configuration
class ProductionConfig:
    def __init__(self):
        self.llm_config = SimpleNamespace(
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1,  # Conservative for production
            streaming=True
        )
        
        self.summary_config = SummaryConfig(
            pairs_threshold=12,  # Longer thresholds for production
            recent_pairs_to_preserve=4,
            max_summary_length=300
        )

# ❌ Don't hardcode credentials
bad_config = SimpleNamespace(api_key="sk-hardcoded-key")  # Never do this!
```

### 4. Error Handling
```python
# ✅ Use built-in error handling (Recommended)
# The summary_node() method already includes robust error handling
summary_manager = SummaryManager(llm, config)
summary_manager.set_logger(logger)  # Automatic error logging

workflow.add_node("summary_check", summary_manager.summary_node)

# ✅ Custom error handling (if needed)
async def robust_summary_node(state):
    """Custom summary node with additional error handling"""
    try:
        if await summary_manager.should_create_summary(state):
            return await summary_manager.process_summary(state)
        return {}
    except Exception as e:
        logger.error(f"Summary creation failed: {e}")
        # Continue without summary rather than failing
        return {}
```

### 5. Performance Monitoring
```python
import time
from functools import wraps

# ✅ Built-in monitoring (Recommended)
# The summary_node() automatically logs performance when logger is configured
summary_manager = SummaryManager(llm, config)
summary_manager.set_logger(logger)  # Automatic performance logging

workflow.add_node("summary_check", summary_manager.summary_node)

# ✅ Custom performance monitoring (if needed)
def monitor_performance(func):
    """Decorator to monitor summary performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start_time
        
        if result:  # Summary was created
            logger.info(f"Summary created in {duration:.2f}s")
        
        return result
    return wrapper

# Usage with custom node
@monitor_performance
async def monitored_summary_node(state):
    return await summary_manager.process_summary(state)
```

## 📊 Performance Considerations

### Token Efficiency
- **Without summarization**: ~50,000 tokens for 50-message conversation
- **With summarization**: ~8,000 tokens (84% reduction)
- **Cost savings**: Proportional to token reduction

### Response Time
- **Summary creation**: 2-5 seconds additional latency
- **Context processing**: 50-80% faster with summarized context
- **Overall impact**: Net positive for conversations >15 messages

### Memory Usage
- **State size**: Reduced by 70-90% with active summarization
- **Checkpointer storage**: Significantly smaller state objects
- **Database impact**: Reduced checkpoint table growth

## 🛠️ Troubleshooting

### Common Issues

#### 1. "SimpleNamespace required" Error
```python
# ❌ Cause: Using dictionary instead of SimpleNamespace
config = {"api_key": "sk-..."}

# ✅ Solution: Use SimpleNamespace
from types import SimpleNamespace
config = SimpleNamespace(api_key="sk-...")
```

#### 2. Summary Not Created
```python
# Check if threshold is reached
pairs = summary_manager.count_conversation_pairs(state["messages"])
print(f"Current pairs: {pairs}, Threshold: {config.pairs_threshold}")

# Check message types
for i, msg in enumerate(state["messages"]):
    print(f"{i}: {type(msg).__name__} - {hasattr(msg, 'tool_calls')}")
```

#### 3. Provider Not Available
```python
# Check available providers
providers = ModelFactory.get_available_providers()
print(f"Available: {providers}")

# Verify environment variables
import os
print(f"OpenAI key set: {bool(os.getenv('OPENAI_API_KEY'))}")
```

### Debug Mode
```python
# Enable debug logging for detailed output
import logging
logging.getLogger("fastal.langgraph.toolkit").setLevel(logging.DEBUG)
```

## 🗺️ Roadmap

The Fastal LangGraph Toolkit follows a structured development roadmap with clear versioning and feature additions. Current development status and planned features:

### Current Status (v0.3.0b1)
- ✅ **Multi-Provider LLM Support**: OpenAI, Anthropic, Ollama, AWS Bedrock
- ✅ **Multi-Provider Embeddings**: OpenAI, Ollama, AWS Bedrock  
- ✅ **Intelligent Conversation Summarization**: Production-ready with ready-to-use LangGraph node
- ✅ **OpenAI Speech-to-Text**: Whisper integration with full async support
- ✅ **Type Safety**: Full TypedDict integration and TYPE_CHECKING imports
- ✅ **Enterprise Testing**: Comprehensive test suite with CI/CD

### Planned Features

#### v0.4.0 - Extended STT Providers (Q1 2025)
- 🚧 **Google Cloud Speech-to-Text**: Full integration with streaming support
- 🚧 **Azure Cognitive Services STT**: Real-time transcription capabilities
- 🚧 **Advanced STT Features**: Speaker diarization, custom vocabularies, language detection
- 🚧 **STT Performance Optimizations**: Batch processing and caching

#### v0.5.0 - Text-to-Speech Support (Q2 2025)
- 🚧 **OpenAI TTS**: High-quality voice synthesis with multiple voices
- 🚧 **Google Cloud TTS**: WaveNet and Neural2 voice support
- 🚧 **ElevenLabs Integration**: Premium voice models and voice cloning
- 🚧 **Azure TTS**: Neural voices with emotion control
- 🚧 **TTSFactory**: Unified factory pattern for all TTS providers

#### v0.6.0 - Advanced Features (Q3 2025)
- 🚧 **Real-Time Streaming**: Live audio processing capabilities
- 🚧 **Audio Processing Pipeline**: Noise reduction, format conversion
- 🚧 **Multi-Language Support**: Enhanced language detection and switching
- 🚧 **Voice Activity Detection**: Smart audio segmentation

#### v1.0.0 - Production Release (Q4 2025)
- 🚧 **Enterprise Authentication**: OAuth, SAML, and enterprise SSO
- 🚧 **Advanced Monitoring**: Metrics, tracing, and observability
- 🚧 **Performance Optimizations**: Caching, connection pooling
- 🚧 **Documentation**: Complete enterprise deployment guides

### Provider Expansion Plans

**Speech-to-Text Providers (v0.4.0):**
- Google Cloud Speech-to-Text
- Azure Cognitive Services Speech
- AWS Transcribe (planned)
- AssemblyAI (community request)

**Text-to-Speech Providers (v0.5.0):**
- OpenAI TTS
- Google Cloud Text-to-Speech  
- ElevenLabs
- Azure Cognitive Services TTS
- AWS Polly (planned)

### Community Contributions

We welcome community contributions and feedback to help shape the roadmap:

- **Feature Requests**: Create issues for new provider requests or feature suggestions
- **Provider Implementations**: Community-contributed providers are welcome
- **Documentation**: Help improve examples and guides
- **Testing**: Real-world usage feedback from enterprise deployments

**Priority is given to providers with proven enterprise demand and active community support.**

### Version Strategy

- **Major versions** (1.x): Breaking changes, major architectural improvements
- **Minor versions** (0.x): New features, provider additions
- **Patch versions** (0.x.y): Bug fixes, security updates
- **Beta releases** (0.x.0b1): Pre-release testing with new features

**Current stable release**: v0.2.0 (STT functionality in beta)

## License

MIT License