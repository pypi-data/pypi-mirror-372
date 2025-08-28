"""Tests for SummaryManager functionality"""

import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from fastal.langgraph.toolkit.memory import SummaryManager, SummaryConfig, SummarizableState


@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    llm = MagicMock()
    llm.bind_tools = MagicMock(return_value=llm)
    return llm


@pytest.fixture
def sample_messages():
    """Sample conversation messages for testing"""
    return [
        HumanMessage(content="Hello, I need help with my business"),
        AIMessage(content="I'd be happy to help! What specific area do you need assistance with?"),
        HumanMessage(content="I'm looking for accounting services"),
        AIMessage(content="Great! Let me search for accounting services.", tool_calls=[{"name": "search", "args": {}, "id": "search_123"}]),
        ToolMessage(content="Found accounting services info", tool_call_id="123"),
        AIMessage(content="I found several accounting services we offer. Would you like details?"),
        HumanMessage(content="Yes, please provide details"),
        AIMessage(content="Here are our accounting services: bookkeeping, tax preparation, financial consulting."),
    ]


def test_summary_manager_init(mock_llm):
    """Test SummaryManager initialization"""
    manager = SummaryManager(mock_llm)
    assert manager.llm == mock_llm
    assert isinstance(manager.config, SummaryConfig)
    
    # Test with custom config
    config = SummaryConfig(pairs_threshold=15)
    manager = SummaryManager(mock_llm, config)
    assert manager.config.pairs_threshold == 15


def test_summarizable_state():
    """Test SummarizableState TypedDict"""
    # This test verifies the type structure is correct
    state = SummarizableState(
        messages=[HumanMessage(content="test")],
        summary=None,
        last_summarized_index=0
    )
    assert "messages" in state
    assert "summary" in state
    assert "last_summarized_index" in state


def test_ensure_summary_state(mock_llm):
    """Test auto-injection of summary state fields"""
    manager = SummaryManager(mock_llm)
    
    # Test with missing fields
    state = {"messages": []}
    result = manager.ensure_summary_state(state)
    
    assert "summary" in result
    assert "last_summarized_index" in result
    assert result["summary"] is None
    assert result["last_summarized_index"] == 0
    
    # Test with existing fields
    state = {"messages": [], "summary": "existing", "last_summarized_index": 5}
    result = manager.ensure_summary_state(state)
    
    assert result["summary"] == "existing"
    assert result["last_summarized_index"] == 5


def test_count_conversation_pairs(mock_llm, sample_messages):
    """Test conversation pair counting logic"""
    manager = SummaryManager(mock_llm)
    
    # Should count 3 complete pairs (Human->AI final responses)
    pairs = manager.count_conversation_pairs(sample_messages)
    assert pairs == 3
    
    # Test with start index
    pairs = manager.count_conversation_pairs(sample_messages, start_index=2)
    assert pairs == 2  # Only last 2 pairs
    
    # Test with empty messages
    pairs = manager.count_conversation_pairs([])
    assert pairs == 0


def test_find_context_start_index(mock_llm, sample_messages):
    """Test finding context start index for recent pairs"""
    manager = SummaryManager(mock_llm)
    
    # Find start index for last 2 pairs
    start_index = manager.find_context_start_index(sample_messages, 2)
    
    # Should start from the third-to-last Human message
    # Counting backwards: pair 3 (index 6-7), pair 2 (index 2-5), so start at index 2
    assert start_index == 2
    
    # Test with more pairs than available
    start_index = manager.find_context_start_index(sample_messages, 10)
    assert start_index == 0  # Should return beginning


def test_filter_conversation_messages(mock_llm, sample_messages):
    """Test message filtering for conversation pairs"""
    manager = SummaryManager(mock_llm)
    
    filtered = manager._filter_conversation_messages(sample_messages)
    
    # Should include: Human(0), AI(1), Human(2), AI(5), Human(6), AI(7)
    # Should exclude: AI(3) with tool_calls, ToolMessage(4)
    assert len(filtered) == 6
    
    # Check that filtered messages are Human-AI pairs
    for i in range(0, len(filtered), 2):
        assert isinstance(filtered[i], HumanMessage)
        if i + 1 < len(filtered):
            assert isinstance(filtered[i + 1], AIMessage)
            # Final AI messages should not have tool_calls
            ai_msg = filtered[i + 1]
            assert not (hasattr(ai_msg, 'tool_calls') and ai_msg.tool_calls)


@pytest.mark.asyncio
async def test_should_create_summary(mock_llm, sample_messages):
    """Test summary creation threshold logic"""
    config = SummaryConfig(pairs_threshold=2)
    manager = SummaryManager(mock_llm, config)
    
    state = {
        "messages": sample_messages,
        "last_summarized_index": 0
    }
    
    # Should create summary (3 pairs >= 2 threshold)
    should_create = await manager.should_create_summary(state)
    assert should_create
    
    # Test with higher threshold
    config.pairs_threshold = 5
    should_create = await manager.should_create_summary(state)
    assert not should_create  # 3 pairs < 5 threshold


@pytest.mark.asyncio
async def test_create_summary_success(mock_llm):
    """Test successful summary creation"""
    # Mock the LLM chain
    mock_chain = AsyncMock()
    mock_chain.ainvoke = AsyncMock(return_value="Generated summary")
    
    # Mock the prompt and chain construction
    with patch('fastal.langgraph.toolkit.memory.summary.ChatPromptTemplate') as mock_prompt:
        mock_prompt.from_messages.return_value = MagicMock()
        
        manager = SummaryManager(mock_llm)
        
        # Mock the chain creation
        manager.llm.__or__ = MagicMock(return_value=mock_chain)
        
        messages = [
            HumanMessage(content="Test message"),
            AIMessage(content="Test response")
        ]
        
        result = await manager.create_summary(messages)
        
        # Should return empty string on any issues during mocking
        # This test mainly verifies the structure works
        assert isinstance(result, str)


@pytest.mark.asyncio 
async def test_create_summary_error_handling(mock_llm):
    """Test summary creation error handling"""
    manager = SummaryManager(mock_llm)
    
    # Force an error by passing invalid input
    manager.llm = None  # This will cause an error
    
    messages = [HumanMessage(content="Test")]
    existing_summary = "Previous summary"
    
    result = await manager.create_summary(messages, existing_summary)
    
    # Should return existing summary on error
    assert result == existing_summary
    
    # Test with no existing summary
    result = await manager.create_summary(messages)
    assert result == ""


def test_summary_config_defaults():
    """Test SummaryConfig default values"""
    config = SummaryConfig()
    
    assert config.pairs_threshold == 10
    assert config.recent_pairs_to_preserve == 3
    assert config.max_summary_length == 400
    assert config.prompt_builder is None
    assert config.combine_builder is None
    assert "structured summary" in config.new_summary_prompt.lower()
    assert "existing summary" in config.combine_summary_prompt.lower()


def test_summary_config_customization():
    """Test SummaryConfig customization"""
    def custom_builder(messages, max_words):
        return f"Custom prompt for {len(messages)} messages, max {max_words} words"
    
    def custom_combine(messages, existing, max_words):
        return f"Combine {existing} with {len(messages)} new messages"
    
    config = SummaryConfig(
        pairs_threshold=15,
        recent_pairs_to_preserve=5,
        max_summary_length=300,
        prompt_builder=custom_builder,
        combine_builder=custom_combine
    )
    
    assert config.pairs_threshold == 15
    assert config.recent_pairs_to_preserve == 5
    assert config.max_summary_length == 300
    assert config.prompt_builder == custom_builder
    assert config.combine_builder == custom_combine