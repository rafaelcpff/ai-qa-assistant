import streamlit as st
import sys
import os
from difflib import SequenceMatcher

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_chains import invoke_with_timeout

st.set_page_config(layout="wide", page_title="Model Evaluation - AI QA Assistant")

st.title("🤖 Model Evaluation (Basic Example)")
st.write("This section provides a basic example of how you *could* evaluate the model's accuracy. For a robust evaluation, you would typically use a dedicated dataset of prompts and expected responses.")

st.info("For a comprehensive evaluation, consider using LangChain's evaluation modules (e.g., `langchain.evaluation`) with pre-defined datasets and metrics (like ROUGE, BLEU, or custom LLM-as-a-judge metrics). This PoC demonstrates a conceptual approach.")

test_prompt = st.text_area("Enter a prompt for evaluation:", "Given these two user stories: 'As a user, I can log in.' and 'As a user, I can reset my password.', how would 'As a user, I can update my profile' affect existing features and what are the quality risks?")
expected_response = st.text_area("Enter the expected (gold standard) response:")

if st.button("Evaluate Response", key="evaluate_response", type="primary"):
    # Get the user story analysis chain from session state
    user_story_analysis_chain = st.session_state.get('user_story_analysis_chain')
    if user_story_analysis_chain:
        with st.spinner("Generating AI response for evaluation..."):
            ai_response = invoke_with_timeout(
                user_story_analysis_chain,
                {
                    "context_user_stories": "Key: US-001\nTitle: As a user, I can log in.\nDescription: Users can log into the platform using their email and password.\n\nKey: US-002\nTitle: As a user, I can reset my password.\nDescription: Users can reset forgotten passwords via email verification.",
                    "new_story_title": "As a user, I can update my profile",
                    "new_story_description": "Users can change their personal information such as name, email, and profile picture."
                },
                timeout_seconds=120
            )
            st.subheader("AI's Response:")
            st.markdown(ai_response)

            similarity_score = SequenceMatcher(None, expected_response.lower(), ai_response.lower()).ratio()

            st.subheader("Evaluation Result:")
            st.write(f"**Expected Response:**\n{expected_response}")
            st.write(f"**AI's Response:**\n{ai_response}")
            st.metric("Similarity Score (Ratio)", f"{similarity_score:.2f}")

            if similarity_score > 0.7:
                st.success("The AI's response is highly similar to the expected response.")
            elif similarity_score > 0.4:
                st.warning("The AI's response has some similarity, but could be improved.")
            else:
                st.error("The AI's response is significantly different from the expected response.")
    else:
        st.error("❌ User Story Analysis chain not available. Please check the main page for initialization status.") 