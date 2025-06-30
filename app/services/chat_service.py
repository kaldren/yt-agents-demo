import uuid
from typing import Optional
from services.kernel_manager import KernelManager
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.contents import ChatHistory

class ChatService:
    """Service for handling chat completions using Azure AI."""
    
    # Class-level session counter for singleton pattern
    _session_counter = 0
    # Class-level chat history database for persistence across instances
    _chat_history_db = {}

    def __init__(self, km: KernelManager, system_prompt: str, session_id: Optional[str] = None):
        """Initialize the ChatService with a KernelManager instance."""
        self._kernel_manager = km
        self._settings = AzureChatPromptExecutionSettings()
        self._settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        
        # Generate unique session_id if not provided
        if session_id:
            self._session_id = session_id
        else:
            ChatService._session_counter += 1
            self._session_id = f"session_{ChatService._session_counter}"
        
        self._chat_history = ChatHistory()
        self._chat_history.add_message({
            "role": "system",
            "content": system_prompt
        })
        
        # Initialize session in class-level database if it doesn't exist
        if self._session_id not in ChatService._chat_history_db:
            ChatService._chat_history_db[self._session_id] = list()
    
    def add_message_to_history(self, role: str, content: str):
        """Add a message to the chat history."""

        message = {
            "role": role,
            "content": content
        }

        ChatService._chat_history_db[self._session_id].append(message)
        
        self._chat_history.add_message(message)

    def get_chat_history(self) -> list[dict]:
        """Get the chat history."""
        return ChatService._chat_history_db[self._session_id]
    
    def get_chat_history_by_session_id(self, session_id: str) -> list[dict]:
        """Get the chat history by session id."""
        return ChatService._chat_history_db.get(session_id, [])

    async def get_chat_completion(self) -> str:
        """Get chat completion based on the provided history."""

        result = await self._kernel_manager.chat_completion.get_chat_message_content(
            chat_history=self._chat_history,
            kernel=self._kernel_manager._kernel,
            settings=self._settings
        )

        return result.content