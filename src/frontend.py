import streamlit as st
import requests
import logging

logger = logging.getLogger(__name__) 

def get_agent_response(user_id, user_name, chat_history):
    """Send user message and chat history to backend and get response."""
    try:
        response = requests.post("http://localhost:8080/agent_call", json={"user_id": user_id, "user_name": user_name, "messages": chat_history})
        response_data = response.json().get('response')
        return response_data.get("user_id"), response_data.get("message")
    except Exception as e:
        return "", f"Error: {str(e)}"

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "waiting_for_response" not in st.session_state:
    st.session_state.waiting_for_response = False

if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

def handle_user_input():
    """Handles user input, updates chat history, clears input, and fetches response."""
    user_message = st.session_state.user_input.strip()
    
    if user_message:  
        # Append user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        # Clear input field
        st.session_state.user_input = ""
        
        # Indicate that we are waiting for a response
        st.session_state.waiting_for_response = True

        # Get agent response
        st.session_state.user_id, agent_message = get_agent_response(st.session_state.user_id, st.session_state.user_name, st.session_state.chat_history)
        
        st.session_state.chat_history.append({"role": "assistant", "content": agent_message})
        st.session_state.waiting_for_response = False

st.title("Greenlife support agent 🤖")

# User deets
st.text_input("User ID (Enter NA for first-time user):", key="user_id", value=st.session_state.user_id)
st.text_input("User Name:", key="user_name", value=st.session_state.user_name)

# Show existing chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**Agent:** {message['content']}")

# User input box with `on_change` callback
st.text_input("Type your message:", key="user_input", on_change=handle_user_input)

# Button to reset chat
if st.button("End Conversation"):
    st.session_state.chat_history = []
    del st.session_state.user_id
    del st.session_state.user_name
    st.session_state.waiting_for_response = False
    st.rerun()