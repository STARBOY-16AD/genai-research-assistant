"""
Challenge Mode component
"""
import streamlit as st
import requests
from frontend.utils.ui_helpers import get_api_url, show_success, show_error

def render_challenge_section():
    """Render the Challenge Mode interface"""
    st.markdown("<div style='animation: fade-in 0.5s ease-in-out;'>", unsafe_allow_html=True)
    st.header("🎯 Challenge Me")
    st.markdown("Test your understanding with AI-generated questions based on the document.")
    
    # Initialize challenge state
    if 'challenge_session_id' not in st.session_state:
        st.session_state.challenge_session_id = None
    if 'challenge_questions' not in st.session_state:
        st.session_state.challenge_questions = []
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'challenge_responses' not in st.session_state:
        st.session_state.challenge_responses = {}
    
    # Check if document is uploaded
    if not st.session_state.document_uploaded:
        st.warning("No document uploaded yet.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Generate questions button
    if not st.session_state.challenge_questions:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            num_questions = st.selectbox("Number of Questions:", [3, 4, 5], index=2)
            if st.button("Generate Questions", type="primary", use_container_width=True):
                with st.spinner("Generating questions..."):
                    generate_challenge_questions(num_questions)
                    if st.session_state.challenge_questions:
                        st.rerun()
    
    # Display questions and handle responses
    if st.session_state.challenge_questions:
        questions = st.session_state.challenge_questions
        
        # Progress bar
        progress = len(st.session_state.challenge_responses) / len(questions)
        st.progress(progress, text=f"Progress: {len(st.session_state.challenge_responses)}/{len(questions)}")
        
        # Question navigation
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if st.button("←", disabled=st.session_state.current_question_index == 0):
                st.session_state.current_question_index = max(0, st.session_state.current_question_index - 1)
                st.rerun()
        
        with col3:
            if st.button("→", disabled=st.session_state.current_question_index >= len(questions) - 1):
                st.session_state.current_question_index = min(len(questions) - 1, st.session_state.current_question_index + 1)
                st.rerun()
        
        # Current question
        current_q = questions[st.session_state.current_question_index]
        question_id = current_q['question_id']
        
        st.markdown(f"### Question {st.session_state.current_question_index + 1}")
        st.markdown(f"**{current_q['question']}**")
        
        # Show reasoning hint
        with st.expander("💡 Why this question?"):
            st.markdown(current_q['reasoning'])
        
        # Answer input
        if question_id not in st.session_state.challenge_responses:
            with st.form(f"answer_form_{question_id}"):
                user_answer = st.text_area(
                    "Your Answer:",
                    placeholder="Provide your detailed answer based on the document...",
                    height=150,
                    key=f"answer_{question_id}"
                )
                submitted = st.form_submit_button("Submit Answer", type="primary")
            
            if submitted and user_answer.strip():
                with st.spinner("Evaluating your answer..."):
                    evaluation = evaluate_answer(question_id, user_answer)
                    if evaluation:
                        st.session_state.challenge_responses[question_id] = evaluation
                        show_success("Answer evaluated successfully!")
                        st.rerun()
        
        else:
            # Show evaluation results
            evaluation = st.session_state.challenge_responses[question_id]
            
            # Score display
            score = evaluation['score']
            score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("Score", f"{score}/100", delta=None)
                st.write(f"{score_color}")
            
            with col2:
                st.markdown("**Expected Answer:**")
                st.info(evaluation['expected_answer'])
            
            # Detailed feedback
            st.markdown("**Feedback:**")
            st.markdown(evaluation['feedback'])
            
            # Reference chunks
            if evaluation.get('reference_chunks'):
                with st.expander("📖 Supporting References"):
                    for chunk in evaluation['reference_chunks']:
                        st.text(chunk['text'][:400] + "..." if len(chunk['text']) > 400 else chunk['text'])
                        st.divider()
        
        # Overall progress summary
        if len(st.session_state.challenge_responses) == len(questions):
            st.markdown("### 🎉 Challenge Complete!")
            
            scores = [resp['score'] for resp in st.session_state.challenge_responses.values()]
            avg_score = sum(scores) / len(scores)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Score", f"{avg_score:.1f}/100")
            with col2:
                st.metric("Best Score", f"{max(scores)}/100")
            with col3:
                st.metric("Questions Answered", f"{len(scores)}/{len(questions)}")
            
            # Reset button
            if st.button("Start New Challenge", type="secondary"):
                reset_challenge()
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def generate_challenge_questions(num_questions: int):
    """Generate challenge questions via API"""
    try:
        payload = {
            "document_id": st.session_state.document_id,
            "num_questions": num_questions
        }
        
        response = requests.post(
            f"{get_api_url()}/challenge",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.challenge_session_id = data['session_id']
            st.session_state.challenge_questions = data['questions']
            show_success(f"Generated {len(data['questions'])} challenge questions!")
        else:
            error_data = response.json()
            show_error(f"Failed to generate questions: {error_data.get('detail', 'Unknown error')}")
    except Exception as e:
        show_error(f"Error generating questions: {str(e)}")

def evaluate_answer(question_id: str, user_answer: str):
    """Evaluate user answer via API"""
    try:
        payload = {
            "session_id": st.session_state.challenge_session_id,
            "question_id": question_id,
            "user_answer": user_answer
        }
        
        response = requests.post(
            f"{get_api_url()}/evaluate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            show_error(f"Evaluation failed: {error_data.get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        show_error(f"Error evaluating answer: {str(e)}")
        return None

def reset_challenge():
    """Reset challenge state"""
    st.session_state.challenge_session_id = None
    st.session_state.challenge_questions = []
    st.session_state.current_question_index = 0
    st.session_state.challenge_responses = {}