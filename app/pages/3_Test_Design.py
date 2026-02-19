import streamlit as st
import time
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_chains import invoke_with_timeout
from testrail_client import extract_test_case_info

st.set_page_config(layout="wide", page_title="Test Design - AI QA Assistant")

st.title("📝 Test Design: Generate Test Cases & Regression Scenarios")

if 'last_new_story_title' in st.session_state and 'last_new_story_description' in st.session_state and 'last_quality_risks' in st.session_state:
    st.subheader("New User Story from Previous Step:")
    st.markdown(f"**Title:** {st.session_state['last_new_story_title']}")
    st.markdown(f"**Description:** {st.session_state['last_new_story_description']}")
    st.subheader("Identified Quality Risks from Previous Step:")
    st.markdown(st.session_state['last_quality_risks'])

    if st.button("Generate Suggested Test Cases & Regression Scenarios", type="primary"):
        # Get the test case generation chain from session state
        test_case_generation_chain = st.session_state.get('test_case_generation_chain')
        if test_case_generation_chain:
            # Create a simple progress indicator
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            try:
                # Use original data directly (sanitization handled in background)
                title = st.session_state['last_new_story_title']
                description = st.session_state['last_new_story_description']
                risks = st.session_state['last_quality_risks']
                
                with st.spinner("AI is generating test cases... (timeout: 120s)"):
                    # Show initial status
                    status_placeholder.info("🔄 Starting AI processing...")
                    
                    # Invoke the chain with timeout
                    test_cases_output = invoke_with_timeout(
                        test_case_generation_chain,
                        {
                            "new_story_title": title,
                            "new_story_description": description,
                            "quality_risks": risks
                        },
                        timeout_seconds=120
                    )
                    
                    # Clear status indicators
                    progress_placeholder.empty()
                    status_placeholder.empty()
                    
                    # Store the generated test cases in session state
                    st.session_state['generated_test_cases_output'] = test_cases_output
                    
                    # Extract test case information
                    generated_test_cases = extract_test_case_info(test_cases_output)
                    st.session_state['generated_test_cases_parsed'] = generated_test_cases
                    
                    # Show results
                    st.subheader("✅ AI-Generated Test Cases & Regression Scenarios")
                    st.markdown(test_cases_output)
                    
                    # Store for later use in TestRail tab
                    st.session_state['generated_test_cases'] = generated_test_cases
                    
                    st.success("🎉 Test cases generated successfully! You can now use the 'TestRail Integration' page to find similar existing test cases.")
                    
            except Exception as e:
                progress_placeholder.empty()
                status_placeholder.empty()
                st.error(f"❌ An error occurred: {str(e)}")
                st.error(f"Error type: {type(e).__name__}")
                import traceback
                st.error(f"Full traceback: {traceback.format_exc()}")
        else:
            st.error("❌ Test Case Generation chain not available. Please check the main page for initialization status.")
else:
    st.info("Please go to the 'Test Analysis' page first, provide a new user story, and get insights to enable test case generation.")
    st.info("💡 You can navigate to the Test Analysis page using the sidebar menu.") 