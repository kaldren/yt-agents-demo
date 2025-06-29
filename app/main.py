from fastapi import FastAPI
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

app = FastAPI()

@app.get("/chat")
async def root():
    kernel = KernelManager.create_kernel()
    chat_service = ChatService(kernel, system_prompt="You are a helpful assistant that only answers questions about Ryanair flights.")

    chat_service.add_message_to_history(
        role="user",
        content="Can I bring my AK47 on a Ryanair flight?"
    )

    result = await chat_service.get_chat_completion()

    print(f"Chat Completion Result: {result}")

    chat_service.add_message_to_history(
        role="assistant",
        content=result
    )

    chat_service.add_message_to_history(
        role="user",
        content="Show me the whole conversation so far (including this one)."
    )

    result = await chat_service.get_chat_completion()
    print(f"Chat History Result: {result}")

    return {
        "chat_completion": result,
    }