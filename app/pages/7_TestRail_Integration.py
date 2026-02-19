import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from testrail_client import TestRailClient, find_similar_test_cases

st.set_page_config(layout="wide", page_title="TestRail Integration - AI QA Assistant")

st.title("🔗 TestRail Integration: Find Similar Existing Test Cases")

# Get TestRail client from session state
testrail_client = st.session_state.get('testrail_client')

# Use provided TestRail client or initialize a new one if not provided
if testrail_client is None:
    testrail_client = TestRailClient()

# Check if we have generated test cases from the Test Design tab
if 'generated_test_cases' not in st.session_state:
    st.warning("⚠️ No generated test cases found. Please go to the 'Test Design' page first and generate test cases.")
else:
    generated_test_cases = st.session_state['generated_test_cases']
    
    # Debug: Check what's in session state
    st.info(f"🔍 Debug: generated_test_cases type: {type(generated_test_cases)}, length: {len(generated_test_cases) if generated_test_cases else 0}")
    
    if not generated_test_cases:
        st.warning("⚠️ Generated test cases list is empty. Please go to the 'Test Design' page first and generate test cases.")
        
        # Show what other test case related keys are in session state
        test_case_keys = [key for key in st.session_state.keys() if 'test' in key.lower() or 'case' in key.lower()]
        if test_case_keys:
            st.info(f"🔍 Found these test-related keys in session state: {test_case_keys}")
            
            # Check if there are other test case keys that might have the data
            for key in test_case_keys:
                value = st.session_state[key]
                st.info(f"🔍 {key}: type={type(value)}, length={len(value) if hasattr(value, '__len__') else 'N/A'}")
            
            # Try to use raw output as fallback
            if 'generated_test_cases_output' in st.session_state:
                st.info("🔍 Attempting to use raw AI output as fallback...")
                raw_output = st.session_state['generated_test_cases_output']
                if raw_output:
                    # Create a simple test case from the raw output
                    fallback_test_case = {
                        'title': 'Generated Test Case (from raw output)',
                        'steps': [{'content': raw_output[:200] + '...', 'expected': ''}],
                        'preconditions': '',
                        'expected_results': ''
                    }
                    generated_test_cases = [fallback_test_case]
                    st.session_state['generated_test_cases'] = generated_test_cases
                    st.success("✅ Using fallback test case from raw AI output")
                else:
                    st.error("❌ Raw AI output is also empty")
        
        if not generated_test_cases:
            st.info("💡 You can navigate to the Test Design page using the sidebar menu.")
    else:
        st.subheader("Generated Test Cases from Previous Step:")
        st.info(f"Found {len(generated_test_cases)} generated test cases ready for similarity analysis.")
        
        # Show sample generated test cases for debugging
        with st.expander("📋 Sample Generated Test Cases (click to view)"):
            for i, gen_case in enumerate(generated_test_cases[:3]):  # Show first 3
                st.markdown(f"**Case {i+1}:** {gen_case.get('title', 'N/A')}")
                if gen_case.get('steps'):
                    st.markdown(f"Steps: {len(gen_case['steps'])}")
                    for j, step in enumerate(gen_case['steps'][:2]):  # Show first 2 steps
                        st.markdown(f"  {j+1}. {step.get('content', 'N/A')[:100]}...")
                st.markdown("---")
            if len(generated_test_cases) > 3:
                st.markdown(f"... and {len(generated_test_cases) - 3} more cases")
        
        # Configuration section
        st.subheader("⚙️ Search Configuration")
        
        # Note about hardcoded project ID
        st.info("ℹ️ **Note**: Searching in TestRail Project ID 3 (Company)")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Similarity threshold slider
            similarity_threshold = st.slider(
                "Similarity Threshold",
                min_value=0.1,
                max_value=1.0,
                value=0.5,
                step=0.05,
                help="Minimum similarity score to consider test cases as similar"
            )
            
            # Debug option for very low threshold
            use_debug_threshold = st.checkbox("Use very low threshold (0.1) for debugging", value=False)
            if use_debug_threshold:
                similarity_threshold = 0.1
                st.info("🔍 Using debug threshold of 0.1 to see more potential matches")
        
        with col2:
            # Maximum results
            max_results = st.number_input(
                "Max Results", 
                min_value=1, 
                max_value=50, 
                value=10,
                help="Maximum number of similar test cases to return"
            )
        
        with col3:
            # Search scope
            search_scope = st.selectbox(
                "Search Scope",
                ["All Test Cases", "Active Only", "Automated Only"],
                help="Scope of test cases to search in"
            )
        
        with col4:
            # Search button
            search_button = st.button("🔍 Search for Similar Test Cases", type="primary")
        
        # Search functionality
        if search_button:
            if testrail_client and testrail_client.client:
                st.subheader("🔍 Searching for Similar Test Cases...")
                
                try:
                    with st.spinner("Searching TestRail for similar test cases..."):
                        # First get existing test cases from TestRail
                        existing_test_cases = testrail_client.get_all_test_cases(project_id=3)
                        
                        if existing_test_cases:
                            # Get similar test cases
                            similar_cases = find_similar_test_cases(
                                generated_test_cases,
                                existing_test_cases,
                                similarity_threshold=similarity_threshold
                            )
                        else:
                            similar_cases = []
                            st.warning("⚠️ No existing test cases found in TestRail project.")
                        
                        if similar_cases:
                            st.success(f"✅ Found {len(similar_cases)} similar test cases!")
                            
                            # Display results
                            st.subheader("📋 Similar Test Cases Found")
                            
                            # Create a DataFrame for better display
                            results_data = []
                            for case in similar_cases:
                                results_data.append({
                                    'ID': case.get('id', 'N/A'),
                                    'Title': case.get('title', 'N/A'),
                                    'Similarity': f"{case.get('similarity', 0):.2f}",
                                    'Status': case.get('status', 'N/A'),
                                    'Type': case.get('type', 'N/A'),
                                    'Priority': case.get('priority', 'N/A')
                                })
                            
                            if results_data:
                                df = pd.DataFrame(results_data)
                                st.dataframe(df, use_container_width=True)
                            
                            # Store results in session state for potential use
                            st.session_state['similar_test_cases'] = similar_cases
                            
                        else:
                            st.warning("⚠️ No similar test cases found with the current threshold.")
                            st.info("💡 Try lowering the similarity threshold or check if there are test cases in the project.")
                            
                except Exception as e:
                    st.error(f"❌ Error searching TestRail: {str(e)}")
                    import traceback
                    st.error(f"Full traceback: {traceback.format_exc()}")
            else:
                st.error("❌ TestRail client not available. Please check TestRail configuration.")
                st.info("💡 Please check the main page for TestRail connection status.") 