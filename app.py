# app.py
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='chat_logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Configure page layout to wide
st.set_page_config(
    page_title="Gemini AI Chat Interface",
    layout="wide",  # Sets the view to wide
    initial_sidebar_state="expanded"  # Sidebar remains expanded by default
)

# Model configurations
MODELS = {
    "Gemini 1.5 Pro": {
        "model_name": "gemini-1.5-pro",
        "description": "Most capable model for complex tasks",
        "max_temperature": 1.0,
        "default_temperature": 0.7
    },
    "Gemini 1.5 Flash": {
        "model_name": "gemini-1.5-flash",
        "description": "Optimized for speed and efficiency",
        "max_temperature": 1.0,
        "default_temperature": 0.7
    },
    "Gemini 1.5 Flash 8B": {
        "model_name": "gemini-1.5-flash-8b",
        "description": "Lighter and faster variant",
        "max_temperature": 1.0,
        "default_temperature": 0.7
    },
    "LearnLM 1.5 Pro (Experimental)": {
        "model_name": "learnlm-1.5-pro-experimental",
        "description": "Experimental model with enhanced learning capabilities",
        "max_temperature": 1.0,
        "default_temperature": 0.7
    }
}

def save_conversation(question, response, model_name):
    """Save conversation to JSON file"""
    conversation = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'model': model_name,
        'question': question,
        'response': response
    }
    
    try:
        # Load existing conversations
        if os.path.exists('conversations.json'):
            with open('conversations.json', 'r') as f:
                conversations = json.load(f)
        else:
            conversations = []
        
        # Append new conversation
        conversations.append(conversation)
        
        # Save updated conversations
        with open('conversations.json', 'w') as f:
            json.dump(conversations, f, indent=2)
            
        # Also log to logging file
        logging.info(f"Model: {model_name}")
        logging.info(f"Q: {question}")
        logging.info(f"R: {response}")
        
    except Exception as e:
        logging.error(f"Error saving conversation: {str(e)}")

def get_gemini_response(question, model_name, temperature):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            question,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature
            )
        )
        return response.text
    except Exception as e:
        error_msg = f"An error occurred with {model_name}: {str(e)}"
        logging.error(error_msg)
        return error_msg

# Sidebar UI
with st.sidebar:
    st.title("🤖 Gemini AI Chat Interface")
    
    # Model selection
    st.subheader("Model Settings")
    selected_model = st.selectbox(
        "Choose a model",
        options=list(MODELS.keys()),
        index=0
    )
    
    # Model information
    st.info(MODELS[selected_model]["description"])
    
    # Temperature settings
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=MODELS[selected_model]["max_temperature"],
        value=MODELS[selected_model]["default_temperature"],
        step=0.1
    )
    
    # Model behavior explanation
    st.markdown("""
    #### Temperature Guide:
    - **0.0-0.3**: Focused, deterministic responses
    - **0.3-0.7**: Balanced creativity and coherence
    - **0.7-1.0**: More creative, diverse responses
    """)
    
    # Add conversation statistics
    if os.path.exists('conversations.json'):
        with open('conversations.json', 'r') as f:
            conversations = json.load(f)
            conversation_count = len(conversations)
            
            # Count conversations per model
            model_counts = {}
            for conv in conversations:
                model_name = conv.get('model', 'Unknown')
                model_counts[model_name] = model_counts.get(model_name, 0) + 1
        
        st.subheader("Statistics")
        st.write(f"Total conversations: {conversation_count}")
        
        # Show model usage breakdown
        st.write("Model Usage:")
        for model, count in model_counts.items():
            st.write(f"- {model}: {count}")

# Main chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "model" in message:
            st.caption(f"Model: {message['model']}")

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Get and display assistant response
    with st.chat_message("assistant"):
        model_name = MODELS[selected_model]["model_name"]
        response = get_gemini_response(prompt, model_name, temperature)
        st.markdown(response)
        st.caption(f"Model: {selected_model}")
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "model": selected_model
    })
    
    # Save the conversation
    save_conversation(prompt, response, selected_model)