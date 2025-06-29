from services.kernel_manager import KernelManager
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai import FunctionChoiceBehavior

class ChatService:
    """Service for handling chat completions using Azure AI."""
    def __init__(self, km: KernelManager):
        """Initialize the ChatService with a KernelManager instance."""
        self._kernel_manager = km
        self._settings = AzureChatPromptExecutionSettings()
        self._settings.function_choice_behavior = FunctionChoiceBehavior.Auto()


    async def get_chat_completion(self, history: list) -> str:
        """Get chat completion based on the provided history."""

        return await self._kernel_manager.chat_completion.get_chat_message_content(
            chat_history=history,
            kernel=self._kernel_manager._kernel,
            settings=self._settings
        )