import semantic_kernel as sk
import logging
import os
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class Kernelmanager:
    """A class to manage the kernel for the application."""

    def create_kernel() -> sk.Kernel:
        """Create and return a Semantic Kernel instance."""
        kernel = sk.Kernel()
        
        try:
            # Add Azure OpenAI service to the kernel
            chat_completion = AzureChatCompletion(
                deployment_name=os.getenv("AZURE_OPENAI_CHAT_MODEL_ID"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )
            kernel.add_service(chat_completion)

            embedding_service = AzureTextEmbedding(
                deployment_name=os.getenv("AZURE_OPENAI_EMBEDDING_MODEL_ID"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )
            kernel.add_service(embedding_service)

            logger.info("Semantic Kernel configured successfully.")

        except Exception as e:
            logger.error(f"Failed to configure Semantic Kernel: {e}")
            raise
    
        return kernel