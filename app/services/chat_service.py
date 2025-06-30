from typing import Optional
from services.kernel_manager import KernelManager
from agents.ryanair_agent import RyanairAgent

class ChatService:
    """Service for handling chat completions using the Ryanair Agent."""

    def __init__(self, km: KernelManager, session_id: Optional[str] = None):
        """Initialize the ChatService with a KernelManager instance."""
        self._kernel_manager = km
        self._agent = RyanairAgent(km, session_id)
    
    def add_message_to_history(self, role: str, content: str):
        """Add a message to the chat history."""
        self._agent.add_message(role, content)

    def get_chat_history(self) -> list[dict]:
        """Get the chat history."""
        return self._agent.get_conversation_history()
    
    def get_chat_history_by_session_id(self, session_id: str) -> list[dict]:
        """Get the chat history by session id."""
        return self._agent.get_conversation_history_by_session(session_id)

    async def get_chat_completion(self) -> str:
        """Get chat completion based on the provided history."""
        # This method is kept for backward compatibility
        # In the new agent-based approach, you should use process_query directly
        raise NotImplementedError("Use process_query() method instead for agent-based interactions")

    async def process_query(self, user_query: str) -> str:
        """Process a user query using the Ryanair Agent."""
        return await self._agent.process_query(user_query)
    
    @property
    def session_id(self) -> str:
        """Get the current session ID."""
        return self._agent.session_id
    
    def get_agent_info(self) -> dict:
        """Get information about the underlying agent."""
        return self._agent.get_agent_info()
    
    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self._agent.reset_conversation()