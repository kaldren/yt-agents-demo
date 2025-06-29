from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from services.chat_service import ChatService
from services.kernel_manager import KernelManager
from plugins.azure_ai_search import AzureAISearch
from dotenv import load_dotenv
import os
load_dotenv()

async def main():
    kernel = KernelManager.create_kernel()
    chat_service = ChatService(kernel)

    history = ChatHistory()
    # create dictionary with role and content

    # Add dictionary to chat history for system and user messages
    dict = {
        "role": "system",
        "content": "Only answer questions about Ryanair flights. If you don't know the answer, say exactly 'I don't know'. DO NOT USE YOUR GENERAL KNOWLEDGE FOR ANY REASON!"
    }
    history.add_message(dict)

    dict = {
        "role": "user",
        "content": "Can I bring my AK47 on a Ryanair flight?"
    }

    history.add_message(dict)

    result = await chat_service.get_chat_completion(history)

    print(f"Chat Completion Result: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())