import streamlit as st
import requests
import json
from typing import Optional

# Configuration
FASTAPI_BASE_URL = "http://localhost:8000"

def main():
    st.title("Ryanair Flight Assistant")
    st.write("Ask questions about Ryanair flights and policies")
    
    # Session management
    if "session_id" not in st.session_state:
        st.session_state.session_id = "123"  # Default session
    
    # Sidebar for session management
    with st.sidebar:
        st.header("Session Management")
        new_session_id = st.text_input("Session ID", value=st.session_state.session_id)
        if st.button("Change Session"):
            st.session_state.session_id = new_session_id
            st.rerun()
        
        if st.button("View Chat History"):
            view_chat_history()
    
    # Main chat interface
    st.header("Chat")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about Ryanair flights..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response from FastAPI
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_chat_completion(prompt, st.session_state.session_id)
                if response:
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.error("Failed to get response from server")

def get_chat_completion(message: str, session_id: str) -> Optional[str]:
    """Send message to FastAPI backend and get response."""
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/chat",
            json={"message": message, "session_id": session_id},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["chat_completion"]
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None

def view_chat_history():
    """Display chat history for current session."""
    try:
        response = requests.get(
            f"{FASTAPI_BASE_URL}/chat/history",
            params={"session_id": st.session_state.session_id}
        )
        if response.status_code == 200:
            history = response.json()["chat_history"]
            if history:
                st.subheader(f"Chat History for Session {st.session_state.session_id}")
                for i, message in enumerate(history):
                    st.write(f"**{message['role'].title()}:** {message['content']}")
            else:
                st.info("No chat history found for this session.")
        else:
            st.error(f"Error fetching history: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")

if __name__ == "__main__":
    main() 