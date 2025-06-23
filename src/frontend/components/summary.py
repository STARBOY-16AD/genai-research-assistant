"""
Summary component for document summaries
"""
import streamlit as st
import requests
from frontend.utils.ui_helpers import get_api_url, show_success, show_error

def render_summary_section():
    """Render the Document Summary interface"""
    st.markdown("<div style='animation: fade-in 0.5s ease-in-out;'>", unsafe_allow_html=True)
    st.header("📝 Document Summary")
    st.markdown("Generate a concise summary of your uploaded documents.")
    
    # Document selection
    documents = st.session_state.get("uploaded_documents", [])
    if not documents:
        st.warning("No documents uploaded yet.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    doc_options = {doc["filename"]: doc["document_id"] for doc in documents}
    selected_doc = st.selectbox("Select Document for Summary", list(doc_options.keys()))
    document_id = doc_options[selected_doc]
    
    # Generate summary button
    if st.button("Generate Summary", type="primary"):
        with st.spinner("Generating summary..."):
            try:
                response = requests.post(
                    f"{get_api_url()}/summarize",
                    json={"document_id": document_id},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.document_info['summary'] = data['summary']
                    show_success("Summary generated successfully!")
                    st.rerun()
                else:
                    error_data = response.json()
                    show_error(f"Failed to generate summary: {error_data.get('detail', 'Unknown error')}")
            except Exception as e:
                show_error(f"Error generating summary: {str(e)}")
    
    # Display summary
    if 'summary' in st.session_state.document_info and st.session_state.document_info.get('document_id') == document_id:
        st.markdown("### Summary")
        st.markdown(st.session_state.document_info['summary'])
    
    st.markdown("</div>", unsafe_allow_html=True)