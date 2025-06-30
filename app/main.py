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

from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.get("/health")
async def health_check():
    """Health check endpoint for container monitoring."""
    return {"status": "healthy", "service": "ryanair-flight-assistant"}

@app.post("/chat")
async def chat(request: ChatRequest):
    kernel = KernelManager.create_kernel()
    chat_service = ChatService(kernel, system_prompt="You are a helpful assistant that only answers questions about Ryanair flights.", session_id=request.session_id)

    chat_service.add_message_to_history(
        role="user",
        content=request.message
    )

    result = await chat_service.get_chat_completion()

    chat_service.add_message_to_history(
        role="assistant",
        content=result
    )

    return {
        "chat_completion": result,
    }
    
@app.get("/chat/history")
async def get_chat_history(session_id: str):
    kernel = KernelManager.create_kernel()
    chat_service = ChatService(kernel, system_prompt="You are a helpful assistant that only answers questions about Ryanair flights.", session_id=session_id)

    return {
        "chat_history": chat_service.get_chat_history_by_session_id(session_id)
    }

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