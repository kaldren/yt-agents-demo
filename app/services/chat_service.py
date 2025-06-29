from services.kernel_manager import KernelManager
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.contents import ChatHistory

class ChatService:
    """Service for handling chat completions using Azure AI."""

    def __init__(self, km: KernelManager, system_prompt: str):
        """Initialize the ChatService with a KernelManager instance."""
        self._kernel_manager = km
        self._settings = AzureChatPromptExecutionSettings()
        self._settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        self._chat_history = ChatHistory()
        self._chat_history.add_message({
            "role": "system",
            "content": system_prompt
        })
    
    def add_message_to_history(self, role: str, content: str):
        """Add a message to the chat history."""
        message = {
            "role": role,
            "content": content
        }
        self._chat_history.add_message(message)


    async def get_chat_completion(self) -> str:
        """Get chat completion based on the provided history."""

        result = await self._kernel_manager.chat_completion.get_chat_message_content(
            chat_history=self._chat_history,
            kernel=self._kernel_manager._kernel,
            settings=self._settings
        )

        return result.content