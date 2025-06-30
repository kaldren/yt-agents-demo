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
    chat_service = ChatService(kernel, session_id=request.session_id)

    result = await chat_service.process_query(request.message)

    return {
        "chat_completion": result,
        "session_id": chat_service.session_id
    }
    
@app.get("/chat/history")
async def get_chat_history(session_id: str):
    kernel = KernelManager.create_kernel()
    chat_service = ChatService(kernel, session_id=session_id)

    return {
        "chat_history": chat_service.get_chat_history_by_session_id(session_id)
    }

@app.get("/chat")
async def root():
    kernel = KernelManager.create_kernel()
    chat_service = ChatService(kernel)

    result = await chat_service.process_query("Can I bring my AK47 on a Ryanair flight?")

    print(f"Chat Completion Result: {result}")

    result = await chat_service.process_query("Show me the whole conversation so far (including this one).")
    print(f"Chat History Result: {result}")

    return {
        "chat_completion": result,
        "session_id": chat_service.session_id
    }

@app.get("/agent/info")
async def get_agent_info(session_id: str):
    """Get information about the agent for a specific session."""
    kernel = KernelManager.create_kernel()
    chat_service = ChatService(kernel, session_id=session_id)
    
    return {
        "agent_info": chat_service.get_agent_info(),
        "session_id": session_id
    }

@app.post("/agent/reset")
async def reset_agent_conversation(session_id: str):
    """Reset the conversation for a specific session."""
    kernel = KernelManager.create_kernel()
    chat_service = ChatService(kernel, session_id=session_id)
    chat_service.reset_conversation()
    
    return {
        "message": "Conversation reset successfully",
        "session_id": session_id
    }

@app.get("/agent/sessions")
async def get_all_sessions():
    """Get all active session IDs."""
    from agents.ryanair_agent import RyanairAgent
    
    return {
        "active_sessions": RyanairAgent.get_all_sessions()
    }