"""
Streamlit Frontend for GenAI Research Assistant - Fixed Version
"""
import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="GenAI Research Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import after set_page_config
import requests
from pathlib import Path
import uuid
from typing import Dict, List, Optional

# Safe CSS loading with error handling
def load_custom_css():
    """Load custom CSS with error handling"""
    try:
        css_path = Path("src/frontend/static/custom.css")
        if css_path.exists():
            with open(css_path, 'r', encoding='utf-8') as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            # Fallback: basic styling if CSS file doesn't exist
            st.markdown("""
            <style>
                .main-header { 
                    text-align: center; 
                    padding: 1rem 0; 
                    border-bottom: 2px solid #e0e0e0;
                    margin-bottom: 2rem;
                }
                .upload-section {
                    padding: 2rem;
                    border: 2px dashed #ccc;
                    border-radius: 10px;
                    text-align: center;
                    margin: 2rem 0;
                }
            </style>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load custom CSS: {e}")

# Load CSS
load_custom_css()

# Safe imports with error handling
def safe_import_components():
    """Import components with error handling"""
    try:
        from src.frontend.components.upload import render_upload_section
        from src.frontend.components.summary import render_summary_section
        from src.frontend.components.ask_anything import render_ask_anything_section
        from src.frontend.components.challenge_mode import render_challenge_section
        from src.frontend.utils.ui_helpers import init_session_state, get_api_url, toggle_theme
        return True, {
            'render_upload_section': render_upload_section,
            'render_summary_section': render_summary_section,
            'render_ask_anything_section': render_ask_anything_section,
            'render_challenge_section': render_challenge_section,
            'init_session_state': init_session_state,
            'get_api_url': get_api_url,
            'toggle_theme': toggle_theme
        }
    except ImportError as e:
        st.error(f"Could not import components: {e}")
        return False, {}

# Fallback components if imports fail
def fallback_upload_section():
    """Fallback upload section"""
    st.header("📁 Upload Document")
    st.info("Component loading failed. Basic upload functionality:")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'txt', 'docx'],
        help="Upload a PDF, TXT, or DOCX file"
    )
    if uploaded_file:
        st.success("File uploaded successfully!")
        st.session_state.document_uploaded = True
        st.session_state.document_info = {
            'filename': uploaded_file.name,
            'chunk_count': 'Unknown'
        }

def fallback_summary_section():
    """Fallback summary section"""
    st.header("📄 Document Summary")
    st.info("Summary functionality is not available due to component loading issues.")

def fallback_ask_anything_section():
    """Fallback ask anything section"""
    st.header("❓ Ask Anything")
    st.info("Q&A functionality is not available due to component loading issues.")

def fallback_challenge_section():
    """Fallback challenge section"""
    st.header("🎯 Challenge Mode")
    st.info("Challenge mode is not available due to component loading issues.")

def init_session_state_fallback():
    """Fallback session state initialization"""
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

def main():
    """Main application function"""
    
    # Try to import components
    import_success, components = safe_import_components()
    
    if import_success:
        # Use imported components
        init_session_state = components['init_session_state']
        render_upload_section = components['render_upload_section']
        render_summary_section = components['render_summary_section']
        render_ask_anything_section = components['render_ask_anything_section']
        render_challenge_section = components['render_challenge_section']
        toggle_theme = components['toggle_theme']
    else:
        # Use fallback components
        init_session_state = init_session_state_fallback
        render_upload_section = fallback_upload_section
        render_summary_section = fallback_summary_section
        render_ask_anything_section = fallback_ask_anything_section
        render_challenge_section = fallback_challenge_section
        toggle_theme = lambda: None  # No-op function
    
    # Initialize session state
    init_session_state()
    
    # App header
    st.title("🧠 GenAI Research Assistant")
    st.markdown("*AI-powered document analysis and reasoning assistant*")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        
        # Mode selection
        if st.session_state.get('document_uploaded', False):
            mode = st.selectbox(
                "Choose Mode",
                ["Document Summary", "Ask Anything", "Challenge Me"],
                key="mode_selection"
            )
        else:
            st.info("Upload a document to begin")
            mode = "Upload Document"
        
        # Document info
        if st.session_state.get('document_uploaded', False):
            st.header("Document Info")
            doc_info = st.session_state.get('document_info', {})
            st.write(f"**Filename:** {doc_info.get('filename', 'Unknown')}")
            st.write(f"**Chunks:** {doc_info.get('chunk_count', 'Unknown')}")
            
            # Theme toggle
            if st.button("Toggle Theme", type="secondary"):
                toggle_theme()
                st.rerun()
            
            # Reset button
            if st.button("Upload New Document", type="secondary"):
                reset_session()
    
    # Main content area
    if not st.session_state.get('document_uploaded', False):
        render_upload_section()
    else:
        if mode == "Document Summary":
            render_summary_section()
        elif mode == "Ask Anything":
            render_ask_anything_section()
        elif mode == "Challenge Me":
            render_challenge_section()

def reset_session():
    """Reset session state for new document"""
    keys_to_keep = ['api_url', 'theme']
    keys_to_reset = [key for key in st.session_state.keys() if key not in keys_to_keep]
    
    for key in keys_to_reset:
        del st.session_state[key]
    
    init_session_state_fallback()
    st.rerun()

if __name__ == "__main__":
    main()