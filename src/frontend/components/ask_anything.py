"""
Ask Anything component for querying documents
"""
import streamlit as st
import requests
import json
from frontend.utils.ui_helpers import get_api_url, show_success, show_error
def render_ask_anything_section():
    """Render the Ask Anything interface"""
    st.markdown("<div style='animation: fade-in 0.5s ease-in-out;'>", unsafe_allow_html=True)
    st.header("❓ Ask Anything")
    st.markdown("Ask questions about your uploaded documents.")
    
    # Document selection
    documents = st.session_state.get("uploaded_documents", [])
    if not documents:
        st.warning("No documents uploaded yet.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    doc_options = {doc["filename"]: doc["document_id"] for doc in documents}
    selected_docs = st.multiselect(
        "Select Documents to Query",
        list(doc_options.keys()),
        default=list(doc_options.keys())[:1]
    )
    document_ids = [doc_options[doc] for doc in selected_docs]
    
    if not document_ids:
        st.warning("Please select at least one document.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Question input
    with st.form("question_form"):
        question = st.text_input("Your Question:", placeholder="e.g., What is the main topic of the document?")
        submitted = st.form_submit_button("Ask", type="primary")
    
    if submitted and question.strip():
        with st.spinner("Processing your question..."):
            try:
                payload = {
                    "question": question,
                    "document_ids": document_ids,
                    "session_id": st.session_state.qa_session_id
                }
                response = requests.post(
                    f"{get_api_url()}/ask",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.qa_session_id = data['session_id']
                    st.session_state.conversation_history.append({
                        "question": question,
                        "answer": data['answer'],
                        "source_chunks": data['source_chunks']
                    })
                    show_success("Question answered successfully!")
                    st.rerun()
                else:
                    error_data = response.json()
                    show_error(f"Failed to process question: {error_data.get('detail', 'Unknown error')}")
            except Exception as e:
                show_error(f"Error processing question: {str(e)}")
    
    # Searchable conversation history
    if st.session_state.conversation_history:
        st.markdown("### Conversation History")
        search_query = st.text_input("Search History:", placeholder="Search questions or answers...")
        
        filtered_history = [
            entry for entry in st.session_state.conversation_history
            if search_query.lower() in entry['question'].lower() or search_query.lower() in entry['answer'].lower()
        ]
        
        for i, entry in enumerate(filtered_history):
            with st.expander(f"Q: {entry['question'][:50]}{'...' if len(entry['question']) > 50 else ''}"):
                st.markdown(f"**Question:** {entry['question']}")
                st.markdown(f"**Answer:** {entry['answer']}")
                if entry['source_chunks']:
                    st.markdown("**Sources:**")
                    for chunk in entry['source_chunks']:
                        st.text(chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text'])
                        st.divider()
        
        # History controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear History", type="secondary"):
                st.session_state.conversation_history = []
                st.session_state.qa_session_id = None
                show_success("Conversation history cleared!")
                st.rerun()
        with col2:
            if st.download_button(
                label="Download History",
                data=json.dumps(st.session_state.conversation_history, indent=2),
                file_name="conversation_history.json",
                mime="application/json"
            ):
                show_success("History downloaded!")
    
    st.markdown("</div>", unsafe_allow_html=True)