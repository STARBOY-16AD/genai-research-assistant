import streamlit as st
from pathlib import Path

def init_session_state():
    """Initialize Streamlit session state with default values"""
    defaults = {
        'api_url': 'http://localhost:8000/api/v1',
        'document_uploaded': False,
        'document_id': None,
        'document_info': {},
        'conversation_history': [],
        'qa_session_id': None,
        'challenge_session_id': None,
        'challenge_questions': [],
        'current_question_index': 0,
        'challenge_responses': {},
        'theme': 'light',
        'uploaded_documents': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_api_url() -> str:
    """Get the API URL from session state"""
    return st.session_state.get('api_url', 'http://localhost:8000/api/v1')

def show_success(message: str):
    """Display a success message with consistent styling"""
    st.success(message, icon="✅")

def show_error(message: str):
    """Display an error message with consistent styling"""
    st.error(message, icon="❌")

def toggle_theme():
    """Toggle between light and dark theme"""
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
        st.markdown(
            """
            <style>
                body { background-color: #1a1a1a; color: #ffffff; }
                .stApp { background-color: #1a1a1a; color: #ffffff; }
                .stTextInput, .stTextArea, .stSelectbox { background-color: #2c2c2c; color: #ffffff; }
                .stButton > button { background-color: #4CAF50; color: #ffffff; }
                .css-1d391kg { background-color: #2c2c2c; }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.session_state.theme = 'light'
        st.markdown(
            """
            <style>
                body { background-color: #ffffff; color: #000000; }
                .stApp { background-color: #ffffff; color: #000000; }
                .stTextInput, .stTextArea, .stSelectbox { background-color: #ffffff; color: #000000; }
                .stButton > button { background-color: #4CAF50; color: #ffffff; }
                .css-1d391kg { background-color: #f0f2f6; }
            </style>
            """,
            unsafe_allow_html=True
        )