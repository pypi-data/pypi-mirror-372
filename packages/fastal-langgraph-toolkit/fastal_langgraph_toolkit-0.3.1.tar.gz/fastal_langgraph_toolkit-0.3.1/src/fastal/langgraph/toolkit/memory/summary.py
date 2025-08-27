"""Conversation summarization for LangGraph agents.

This module provides intelligent conversation summarization with:
- Conversation pair counting (Human + AI responses)
- Message filtering for ReAct loops
- Configurable thresholds and prompts
- State auto-injection for compatibility
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Callable

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


class SummarizableState(TypedDict):
    """Base state class for agents with conversation summarization.
    
    This is an optional base class that provides the required fields
    for conversation summarization. Agents can use this as a base
    or ensure their state has these fields.
    
    Attributes:
        messages: List of conversation messages with LangGraph annotation
        summary: Current conversation summary (None if no summary created yet)
        last_summarized_index: Index of first message NOT included in last summary
    """
    messages: Annotated[list, add_messages]
    summary: str | None
    last_summarized_index: int


@dataclass
class SummaryConfig:
    """Configuration for conversation summarization.
    
    Provides flexible configuration through template strings (simple)
    or builder functions (advanced) for maximum customization.
    
    Attributes:
        pairs_threshold: Number of conversation pairs to trigger summary creation
        recent_pairs_to_preserve: Number of recent pairs to keep in context
        max_summary_length: Maximum words for summary (0 = no limit)
        new_summary_prompt: Template for creating new summaries
        combine_summary_prompt: Template for combining existing + new summaries
        prompt_builder: Custom function for building summary prompts (advanced)
        combine_builder: Custom function for building combine prompts (advanced)
    """
    # Threshold configuration
    pairs_threshold: int = 10
    recent_pairs_to_preserve: int = 3
    max_summary_length: int = 400
    
    # Template strings for simple configuration
    new_summary_prompt: str = """Analyze the entire conversation and create a structured summary.

Create a summary that follows this structure:

1. USER INFORMATION (if provided):
   - Name: [if provided]
   - Contact details: [if provided]
   - Role/Position: [if provided]

2. CONVERSATION CONTEXT:
   - Main topic/subject
   - User's primary needs or questions
   - Key discussion points

3. REQUESTS AND ACTIONS:
   - Specific requests made by the user
   - Actions taken or discussed
   - Next steps or follow-ups

4. IMPORTANT DETAILS:
   - Relevant facts or information shared
   - Deadlines or time-sensitive items
   - Other significant points

IMPORTANT:
- Extract ONLY information explicitly provided in the conversation
- Use "not provided" when information is missing
- Focus on facts, not assumptions
- Maximum {max_words} words"""

    combine_summary_prompt: str = """Combine the existing summary with the new conversation into a complete, updated summary.

Create a summary that follows the same structure, maintaining ALL information from the previous summary and adding new information from the recent conversation.

EXISTING SUMMARY:
{existing_summary}

IMPORTANT:
- Keep ALL information from the existing summary
- Add only NEW information from the recent conversation
- Avoid repetition
- Maximum {max_words} words"""
    
    # Builder functions for advanced customization
    prompt_builder: Callable[[list, int], str] | None = None
    combine_builder: Callable[[list, str, int], str] | None = None


class SummaryManager:
    """Manages conversation summaries for LangGraph agents.
    
    This class provides intelligent conversation summarization with:
    - Conversation pair counting (Human message + AI response)
    - Automatic filtering of ReAct tool messages
    - Configurable thresholds and prompts
    - State auto-injection for compatibility with existing agents
    
    The summary system uses conversation pairs as the unit of measurement
    for determining when to create summaries, providing predictable behavior
    regardless of ReAct loop complexity.
    """
    
    def __init__(self, llm: "BaseChatModel", config: SummaryConfig | None = None):
        """Initialize the summary manager.
        
        Args:
            llm: Language model to use for summary generation
            config: Summary configuration (uses defaults if None)
        """
        self.llm = llm
        self.config = config or SummaryConfig()
    
    def ensure_summary_state(self, state: dict) -> dict:
        """Ensure state has required summary fields (auto-injection).
        
        This method automatically adds missing summary fields to the state,
        enabling use with existing agents that don't have summary fields.
        
        Args:
            state: Agent state dictionary
            
        Returns:
            State with summary fields ensured
        """
        if 'summary' not in state:
            state['summary'] = None
        if 'last_summarized_index' not in state:
            state['last_summarized_index'] = 0
        return state
    
    def count_conversation_pairs(self, messages: list, start_index: int = 0) -> int:
        """Count complete conversation pairs (Human→AI final response) from start_index.
        
        A conversation pair is complete when:
        - There's a Human message followed by an AI message without tool_calls
        - OR a Human message followed by AI with tools, tool responses, and final AI message
        
        This method automatically handles ReAct loops by focusing on final AI responses.
        
        Args:
            messages: List of messages to analyze
            start_index: Index to start counting from
            
        Returns:
            Number of complete conversation pairs
        """
        pairs = 0
        i = start_index
        
        while i < len(messages):
            # Look for Human message
            if isinstance(messages[i], HumanMessage):
                # Find the corresponding final AI response
                j = i + 1
                while j < len(messages):
                    if isinstance(messages[j], AIMessage) and not (hasattr(messages[j], 'tool_calls') and messages[j].tool_calls):
                        # Found final AI response
                        pairs += 1
                        i = j + 1
                        break
                    j += 1
                else:
                    # No final AI response found, stop counting
                    break
            else:
                i += 1
                
        return pairs
    
    def find_context_start_index(self, messages: list, num_pairs: int) -> int:
        """Find the index to start context from, based on recent conversation pairs.
        
        This method works backwards from the end of the message list to find
        the starting point that preserves the specified number of conversation pairs.
        
        Args:
            messages: Full list of messages
            num_pairs: Number of user-assistant conversation pairs to preserve
            
        Returns:
            Index to start from (0 if not enough pairs)
        """
        if not messages:
            return 0
        
        # Count conversation pairs from the end
        pairs_found = 0
        i = len(messages) - 1
        context_start_index = 0
        
        while i >= 0 and pairs_found < num_pairs:
            msg = messages[i]
            
            # Look for AI messages without tool calls (final responses)
            if isinstance(msg, AIMessage) and not (hasattr(msg, 'tool_calls') and msg.tool_calls):
                # Look for the corresponding user message
                j = i - 1
                while j >= 0:
                    if isinstance(messages[j], HumanMessage):
                        pairs_found += 1
                        context_start_index = j  # Remember start of this pair
                        i = j - 1  # Continue before this pair
                        break
                    j -= 1
                else:
                    # No user message found, stop
                    break
            else:
                i -= 1
        
        # Return the index where context should start
        return context_start_index
    
    def _filter_conversation_messages(self, messages: list) -> list:
        """Filter messages to include only conversation pairs for summarization.
        
        Automatically excludes ToolMessages and AIMessages with tool_calls
        to focus summaries on actual user-assistant conversations.
        
        Args:
            messages: Raw messages to filter
            
        Returns:
            Filtered messages containing only conversation pairs
        """
        filtered_messages = []
        i = 0
        
        while i < len(messages):
            msg = messages[i]
            
            if isinstance(msg, HumanMessage):
                filtered_messages.append(msg)
                
                # Find the corresponding final AI response (without tool_calls)
                j = i + 1
                while j < len(messages):
                    if isinstance(messages[j], AIMessage):
                        # Check if it's a final response (no tool calls)
                        if not (hasattr(messages[j], 'tool_calls') and messages[j].tool_calls):
                            filtered_messages.append(messages[j])
                            break
                    j += 1
            
            i += 1
        
        return filtered_messages
    
    def _build_summary_prompt(self, filtered_messages: list, existing_summary: str | None = None) -> ChatPromptTemplate:
        """Build prompt for summary creation using configuration.
        
        Uses custom builder functions if provided, otherwise uses template strings.
        Messages are converted to text and included in the system prompt to avoid
        polluting the LangGraph conversation state.
        
        Args:
            filtered_messages: Messages to summarize
            existing_summary: Previous summary if combining
            
        Returns:
            ChatPromptTemplate for summary generation
        """
        max_words = self.config.max_summary_length or 400
        
        # Convert messages to text format for inclusion in prompt
        conversation_text = "\n".join([
            f"{msg.__class__.__name__}: {msg.content}" 
            for msg in filtered_messages
        ])
        
        if existing_summary and self.config.combine_builder:
            # Use custom combine builder
            prompt_text = self.config.combine_builder(filtered_messages, existing_summary, max_words)
            full_prompt = f"{prompt_text}\n\nCONVERSATION TO ANALYZE:\n{conversation_text}"
            return ChatPromptTemplate.from_messages([
                ("system", full_prompt),
                ("human", "Create the structured summary:")
            ])
        
        elif not existing_summary and self.config.prompt_builder:
            # Use custom new summary builder  
            prompt_text = self.config.prompt_builder(filtered_messages, max_words)
            full_prompt = f"{prompt_text}\n\nCONVERSATION TO ANALYZE:\n{conversation_text}"
            return ChatPromptTemplate.from_messages([
                ("system", full_prompt),
                ("human", "Create the structured summary:")
            ])
        
        elif existing_summary:
            # Use template for combining
            prompt_text = self.config.combine_summary_prompt.format(
                existing_summary=existing_summary,
                max_words=max_words
            )
            full_prompt = f"{prompt_text}\n\nCONVERSATION TO ANALYZE:\n{conversation_text}"
            return ChatPromptTemplate.from_messages([
                ("system", full_prompt),
                ("human", "Create the structured summary:")
            ])
        
        else:
            # Use template for new summary
            prompt_text = self.config.new_summary_prompt.format(max_words=max_words)
            full_prompt = f"{prompt_text}\n\nCONVERSATION TO ANALYZE:\n{conversation_text}"
            return ChatPromptTemplate.from_messages([
                ("system", full_prompt),
                ("human", "Create the structured summary:")
            ])
    
    async def create_summary(
        self, 
        messages_to_summarize: list, 
        existing_summary: str | None = None
    ) -> str:
        """Create or update conversation summary.
        
        Automatically filters messages to include only conversation pairs
        (HumanMessage + final AIMessage responses), excluding ToolMessages
        and AIMessages with tool_calls for cleaner summaries.
        
        Args:
            messages_to_summarize: Raw messages to be summarized
            existing_summary: Previous summary to combine with new messages
            
        Returns:
            Structured summary text in the configured format
        """
        try:
            # Filter messages to include only conversation pairs
            filtered_messages = self._filter_conversation_messages(messages_to_summarize)
            
            if not filtered_messages:
                # No conversation messages to summarize
                return existing_summary or ""
            
            # Build prompt using configuration
            prompt = self._build_summary_prompt(filtered_messages, existing_summary)
            
            # Create summary
            chain = prompt | self.llm | StrOutputParser()
            
            if existing_summary:
                summary = await chain.ainvoke({"existing_summary": existing_summary})
            else:
                summary = await chain.ainvoke({})
            
            return summary.strip()
            
        except Exception as e:
            # Return existing summary on error, or empty string
            return existing_summary or ""
    
    async def should_create_summary(self, state: dict) -> bool:
        """Check if a new summary should be created based on configuration.
        
        Args:
            state: Agent state (will be auto-injected with summary fields if missing)
            
        Returns:
            True if summary should be created
        """
        # Ensure state has summary fields
        state = self.ensure_summary_state(state)
        
        messages = state.get("messages", [])
        last_summarized_index = state.get("last_summarized_index", 0)
        
        # Count conversation pairs since last summary
        pairs_since_summary = self.count_conversation_pairs(messages, last_summarized_index)
        
        return pairs_since_summary >= self.config.pairs_threshold
    
    async def process_summary(self, state: dict) -> dict:
        """Process summary creation if needed and return updated state.
        
        This is a convenience method that handles the complete summary workflow:
        - Check if summary is needed
        - Create summary if threshold reached
        - Update state with new summary and index
        - Auto-inject summary fields if missing
        
        Args:
            state: Agent state (will be auto-injected with summary fields if missing)
            
        Returns:
            Updated state with summary information
        """
        # Ensure state has summary fields
        state = self.ensure_summary_state(state)
        
        if not await self.should_create_summary(state):
            return {}
        
        messages = state["messages"]
        last_summarized_index = state.get("last_summarized_index", 0)
        current_summary = state.get("summary")
        
        # Find context start index to preserve recent conversation pairs
        context_start_index = self.find_context_start_index(
            messages,
            self.config.recent_pairs_to_preserve
        )
        
        # Create summary only for messages between last_summarized_index and context_start_index
        messages_to_summarize = messages[last_summarized_index:context_start_index]
        
        if not messages_to_summarize:
            return {}
        
        # Create new summary
        new_summary = await self.create_summary(messages_to_summarize, current_summary)
        
        # Return only updated summary fields (efficient for LangGraph nodes)
        return {
            "summary": new_summary,
            "last_summarized_index": context_start_index
        }
    
    async def summary_node(self, state: dict) -> dict:
        """Ready-to-use LangGraph node for conversation summarization.
        
        This is a complete LangGraph node that can be directly added to workflows.
        It handles the entire summary workflow and provides optional logging.
        
        Args:
            state: LangGraph state (will be auto-injected with summary fields if missing)
            
        Returns:
            Empty dict if no summary needed, or dict with summary fields if created
            
        Example:
            # In your LangGraph workflow
            workflow.add_node("summary_check", summary_manager.summary_node)
        """
        try:
            result = await self.process_summary(state)
            
            # Optional logging if logger provided via set_logger method
            if result and hasattr(self, '_logger') and self._logger:
                thread_id = state.get("thread_id", "unknown")
                messages = state.get("messages", [])
                last_summarized_index = state.get("last_summarized_index", 0)
                
                # Count pairs for logging
                pairs = self.count_conversation_pairs(messages, last_summarized_index)
                self._logger.info(
                    f"🎯 SUMMARY CREATED: Thread {thread_id} - {pairs} conversation pairs "
                    f"since last summary at index {last_summarized_index}"
                )
            
            return result
            
        except Exception as e:
            # Log error if logger available
            if hasattr(self, '_logger') and self._logger:
                self._logger.error(f"Error in summary node: {e}", exc_info=True)
            return {}
    
    def set_logger(self, logger):
        """Set logger for summary_node logging (optional).
        
        Args:
            logger: Logger instance for summary_node operations
        """
        self._logger = logger