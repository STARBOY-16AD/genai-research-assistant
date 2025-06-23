"""
Upload component for document processing
"""
import streamlit as st
import requests
import pdfplumber
from frontend.utils.ui_helpers import get_api_url, show_success, show_error
import time

def render_upload_section():
    """Render the document upload interface"""
    st.markdown("<div style='animation: fade-in 0.5s ease-in-out;'>", unsafe_allow_html=True)
    st.header("📄 Upload Document")
    st.markdown("Upload a PDF, TXT, or DOCX file to begin analysis.")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'txt', 'docx'],
        accept_multiple_files=False
    )
    
    if uploaded_file:
        # Document preview
        try:
            if uploaded_file.type == "application/pdf":
                st.write("PDF Preview (first page):")
                with pdfplumber.open(uploaded_file) as pdf:
                    st.text(pdf.pages[0].extract_text()[:500] + "..." if pdf.pages[0].extract_text() else "No text found.")
            elif uploaded_file.type == "text/plain":
                st.write("Text Preview:")
                content = uploaded_file.read().decode("utf-8")
                st.text(content[:500] + "..." if len(content) > 500 else content)
                uploaded_file.seek(0)  # Reset file pointer
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                st.write("DOCX Preview:")
                import docx
                doc = docx.Document(uploaded_file)
                content = " ".join(para.text for para in doc.paragraphs if para.text)
                st.text(content[:500] + "..." if len(content) > 500 else content)
                uploaded_file.seek(0)  # Reset file pointer
        except Exception as e:
            show_error(f"Error generating preview: {str(e)}")
        
        # Upload button
        if st.button("Process Document", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(100):
                time.sleep(0.02)  # Simulate processing
                progress_bar.progress(i + 1)
                status_text.text(f"Processing: {i + 1}%")
            
            try:
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = requests.post(
                    f"{get_api_url()}/upload",
                    files=files,
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.document_uploaded = True
                    st.session_state.document_id = data['document_id']
                    st.session_state.document_info = {
                        'filename': data['filename'],
                        'chunk_count': data['chunk_count']
                    }
                    st.session_state.uploaded_documents.append({
                        'document_id': data['document_id'],
                        'filename': data['filename']
                    })
                    show_success("Document uploaded successfully!")
                    st.rerun()
                else:
                    error_data = response.json()
                    show_error(f"Upload failed: {error_data.get('detail', 'Unknown error')}")
            except Exception as e:
                show_error(f"Error uploading document: {str(e)}")
            finally:
                progress_bar.empty()
                status_text.empty()
    
    st.markdown("</div>", unsafe_allow_html=True)