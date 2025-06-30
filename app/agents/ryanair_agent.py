import uuid
from typing import Optional, Dict, List, Any
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from services.kernel_manager import KernelManager

class RyanairAgent:
    """
    Agent responsible for handling Ryanair flight-related queries.
    This agent encapsulates the Q&A logic and maintains its own state.
    """
    
    # Class-level session counter for singleton pattern
    _session_counter = 0
    # Class-level chat history database for persistence across instances
    _chat_history_db = {}
    
    def __init__(self, kernel_manager: KernelManager, session_id: Optional[str] = None):
        """
        Initialize the Ryanair Agent.
        
        Args:
            kernel_manager: KernelManager instance for AI services
            session_id: Optional session ID for conversation continuity
        """
        self._kernel_manager = kernel_manager
        self._session_id = self._generate_session_id(session_id)
        self._chat_history = ChatHistory()
        self._settings = self._create_execution_settings()
        
        # Initialize system prompt
        self._initialize_system_prompt()
        
        # Initialize session in class-level database if it doesn't exist
        if self._session_id not in RyanairAgent._chat_history_db:
            RyanairAgent._chat_history_db[self._session_id] = []
    
    def _generate_session_id(self, session_id: Optional[str]) -> str:
        """Generate a unique session ID if not provided."""
        if session_id:
            return session_id
        else:
            RyanairAgent._session_counter += 1
            return f"session_{RyanairAgent._session_counter}"
    
    def _create_execution_settings(self) -> AzureChatPromptExecutionSettings:
        """Create execution settings for the agent."""
        settings = AzureChatPromptExecutionSettings()
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        return settings
    
    def _initialize_system_prompt(self):
        """Initialize the system prompt for the agent."""
        system_prompt = """You are a helpful assistant that specializes in answering questions about Ryanair flights, policies, and procedures. 

Your capabilities include:
- Answering questions about Ryanair flight policies
- Providing information about baggage allowances
- Explaining check-in procedures
- Sharing information about Ryanair's services and fees
- Using Azure AI Search to find relevant documentation when needed

Always be helpful, accurate, and provide clear, concise answers. If you need to search for specific information, use the available search functions."""
        
        self._chat_history.add_message({
            "role": "system",
            "content": system_prompt
        })
    
    @property
    def session_id(self) -> str:
        """Get the current session ID."""
        return self._session_id
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the agent's conversation history.
        
        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        message = {
            "role": role,
            "content": content
        }
        
        # Add to class-level database
        RyanairAgent._chat_history_db[self._session_id].append(message)
        
        # Add to semantic kernel chat history
        self._chat_history.add_message(message)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history for the current session.
        
        Returns:
            List of message dictionaries
        """
        return RyanairAgent._chat_history_db[self._session_id]
    
    def get_conversation_history_by_session(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get conversation history for a specific session.
        
        Args:
            session_id: Session ID to retrieve history for
            
        Returns:
            List of message dictionaries
        """
        return RyanairAgent._chat_history_db.get(session_id, [])
    
    async def process_query(self, user_query: str) -> str:
        """
        Process a user query and return a response.
        
        Args:
            user_query: The user's question or request
            
        Returns:
            The agent's response
        """
        # Add user message to history
        self.add_message("user", user_query)
        
        try:
            # Get response from AI
            result = await self._kernel_manager.chat_completion.get_chat_message_content(
                chat_history=self._chat_history,
                kernel=self._kernel_manager._kernel,
                settings=self._settings
            )
            
            response = result.content
            
            # Add assistant response to history
            self.add_message("assistant", response)
            
            return response
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error while processing your query: {str(e)}"
            self.add_message("assistant", error_response)
            return error_response
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the agent.
        
        Returns:
            Dictionary containing agent information
        """
        return {
            "agent_type": "RyanairFlightAssistant",
            "session_id": self._session_id,
            "conversation_length": len(self.get_conversation_history()),
            "capabilities": [
                "Flight policy queries",
                "Baggage information",
                "Check-in procedures",
                "Service and fee information",
                "Document search"
            ]
        }
    
    def reset_conversation(self) -> None:
        """Reset the conversation history for the current session."""
        RyanairAgent._chat_history_db[self._session_id] = []
        self._chat_history = ChatHistory()
        self._initialize_system_prompt()
    
    @classmethod
    def get_all_sessions(cls) -> List[str]:
        """
        Get all active session IDs.
        
        Returns:
            List of session IDs
        """
        return list(cls._chat_history_db.keys())
    
    @classmethod
    def cleanup_session(cls, session_id: str) -> bool:
        """
        Clean up a specific session.
        
        Args:
            session_id: Session ID to clean up
            
        Returns:
            True if session was found and cleaned up, False otherwise
        """
        if session_id in cls._chat_history_db:
            del cls._chat_history_db[session_id]
            return True
        return False
