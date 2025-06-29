from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from plugins.azure_ai_search import AzureAISearch
from dotenv import load_dotenv
import os
load_dotenv()

async def main():
    kernel = Kernel()

    # Add Service to the kernel
    chat_completion = AzureChatCompletion(
        deployment_name=os.getenv("AZURE_OPENAI_CHAT_MODEL_ID"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

    kernel.add_service(chat_completion)
    kernel.add_plugin(AzureAISearch(), plugin_name="AzureAISearch")

    # Enable planning
    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()


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

    result = await chat_completion.get_chat_message_content(
        chat_history=history,
        kernel=kernel,
        settings=execution_settings
    )

    print(f"Chat Completion Result: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())