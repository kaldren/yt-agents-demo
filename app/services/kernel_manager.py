import semantic_kernel as sk
import logging
import os
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from dotenv import load_dotenv

from plugins.azure_ai_search import AzureAISearch
load_dotenv()

logger = logging.getLogger(__name__)

class KernelManager:
    """A class to manage the kernel for the application."""

    def __init__(self):
        """Initialize the Kernelmanager and create the kernel."""
        self._kernel = None
        self._chat_completion = None
        self._embedding_service = None

    @property
    def chat_completion(self):
        return self._chat_completion

    @classmethod
    def create_kernel(cls) -> "KernelManager":
        """Create and return a Semantic Kernel instance."""

        self = cls()
        self._kernel = sk.Kernel()
        
        try:
            # Add Azure OpenAI service to the kernel
            self._chat_completion = AzureChatCompletion(
                deployment_name=os.getenv("AZURE_OPENAI_CHAT_MODEL_ID"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )
            self._kernel.add_service(self._chat_completion)

            self._embedding_service = AzureTextEmbedding(
                deployment_name=os.getenv("AZURE_OPENAI_EMBEDDING_MODEL_ID"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )
            self._kernel.add_service(self._embedding_service)

            self._kernel.add_plugin(AzureAISearch(), plugin_name="AzureAISearch")

            # Enable planning
            execution_settings = AzureChatPromptExecutionSettings()
            execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

            logger.info("Semantic Kernel configured successfully.")

        except Exception as e:
            logger.error(f"Failed to configure Semantic Kernel: {e}")
            raise
    
        return self