import streamlit as st
import sys
import os
from typing import List, Dict

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_chains import invoke_with_timeout

def format_test_cases_for_automation(automation_cases: List[Dict], framework_pref: str, additional_context: str) -> str:
    """Format test cases for automation input."""
    formatted_output = f"Framework: {framework_pref}\n"
    if additional_context:
        formatted_output += f"Additional Context: {additional_context}\n"
    formatted_output += "\nTest Cases:\n"
    
    for i, case in enumerate(automation_cases, 1):
        formatted_output += f"\n--- Test Case {i} ---\n"
        formatted_output += f"Title: {case.get('title', 'N/A')}\n"
        formatted_output += f"Priority: {case.get('priority', 'N/A')}\n"
        formatted_output += f"Tags: {case.get('tags', 'N/A')}\n"
        
        # Preconditions
        preconditions = case.get('preconditions', '')
        if preconditions:
            formatted_output += f"Preconditions: {preconditions}\n"
        
        # Steps
        steps = case.get('steps', [])
        if steps:
            formatted_output += "Steps:\n"
            for j, step in enumerate(steps, 1):
                if isinstance(step, dict):
                    formatted_output += f"  {j}. Action: {step.get('action', 'N/A')}\n"
                    if step.get('expected_result'):
                        formatted_output += f"     Expected: {step['expected_result']}\n"
                else:
                    formatted_output += f"  {j}. {step}\n"
        
        formatted_output += "\n"
    
    return formatted_output

st.set_page_config(layout="wide", page_title="Test Automation - AI QA Assistant")

st.title("🤖 Test Automation")
st.markdown("Generate automation prompts for test cases marked for automation.")

# Check if we have generated test cases
if 'generated_test_cases' not in st.session_state or not st.session_state['generated_test_cases']:
    st.warning("⚠️ No test cases found. Please generate test cases in the 'Test Design' page first.")
    st.info("💡 Go to the 'Test Design' page, enter a user story, and generate test cases before using this feature.")
else:
    # Check if LLM chain is available
    test_automation_chain = st.session_state.get('test_automation_chain')
    if test_automation_chain is None:
        st.warning("⚠️ AI features are not available. Please check your Google Gemini API configuration.")
    else:
        generated_test_cases = st.session_state['generated_test_cases']
        
        # Filter test cases marked for automation
        automation_cases = []
        for case in generated_test_cases:
            automation_status = case.get('automation', '').lower()
            if automation_status in ['yes', 'true', 'y', '1']:
                automation_cases.append(case)
        
        st.info(f"📊 Found {len(automation_cases)} test cases marked for automation out of {len(generated_test_cases)} total cases.")
        
        if not automation_cases:
            st.warning("⚠️ No test cases are marked for automation.")
            st.info("💡 In the 'Test Design' page, ensure some test cases have 'Automation: Yes' before using this feature.")
            
            # Show sample of generated cases for reference
            with st.expander("📋 View Generated Test Cases"):
                for i, case in enumerate(generated_test_cases[:5]):
                    st.markdown(f"**Case {i+1}:** {case.get('title', 'N/A')}")
                    st.markdown(f"**Automation:** {case.get('automation', 'N/A')}")
                    st.markdown("---")
        else:
            # Display automation cases
            st.subheader("🚀 Test Cases Ready for Automation")
            
            # Create a summary of automation cases
            automation_summary = []
            for i, case in enumerate(automation_cases):
                case_info = {
                    'id': f"TC-{i+1:03d}",
                    'title': case.get('title', 'N/A'),
                    'priority': case.get('priority', 'N/A'),
                    'tags': case.get('tags', 'N/A'),
                    'steps_count': len(case.get('steps', [])),
                    'scenario_id': case.get('scenario_id', 'N/A')
                }
                automation_summary.append(case_info)
            
            # Display summary table
            if automation_summary:
                st.markdown("### Automation Cases Summary")
                summary_data = []
                for case in automation_summary:
                    summary_data.append({
                        'ID': case['id'],
                        'Title': case['title'][:80] + '...' if len(case['title']) > 80 else case['title'],
                        'Priority': case['priority'],
                        'Tags': case['tags'],
                        'Steps': case['steps_count'],
                        'Scenario ID': case['scenario_id']
                    })
                
                st.dataframe(summary_data, use_container_width=True)
            
            # Show detailed automation cases
            with st.expander("📋 View Detailed Automation Cases"):
                for i, case in enumerate(automation_cases):
                    st.markdown(f"### {case.get('title', 'N/A')}")
                    st.markdown(f"**ID:** {case.get('id', f'TC-{i+1:03d}')}")
                    st.markdown(f"**Priority:** {case.get('priority', 'N/A')}")
                    st.markdown(f"**Tags:** {case.get('tags', 'N/A')}")
                    st.markdown(f"**Scenario ID:** {case.get('scenario_id', 'N/A')}")
                    
                    # Show preconditions
                    preconditions = case.get('preconditions', '')
                    if preconditions:
                        st.markdown("**Preconditions:**")
                        # Handle preconditions as string (split by newlines if multiple)
                        if isinstance(preconditions, str):
                            # Split by newlines and filter out empty lines
                            precond_lines = [line.strip() for line in preconditions.split('\n') if line.strip()]
                            for precond in precond_lines:
                                st.markdown(f"- {precond}")
                        elif isinstance(preconditions, list):
                            # Handle as list (backward compatibility)
                            for precond in preconditions:
                                st.markdown(f"- {precond}")
                    
                    # Show steps
                    steps = case.get('steps', [])
                    if steps:
                        st.markdown("**Steps:**")
                        for j, step in enumerate(steps, 1):
                            if isinstance(step, dict):
                                st.markdown(f"{j}. **{step.get('action', 'N/A')}**")
                                if step.get('expected_result'):
                                    st.markdown(f"   *Expected:* {step['expected_result']}")
                            else:
                                st.markdown(f"{j}. {step}")
                    
                    st.markdown("---")
            
            # Automation configuration
            st.subheader("⚙️ Automation Configuration")
            
            col1, col2 = st.columns(2)
            with col1:
                framework_pref = st.selectbox(
                    "Preferred Automation Framework",
                    ["Selenium + JDI Light + TestNG + Gradle", "OpenAPI + OkHttp + JUnit + Gradle", "k6 + TypeScript", "Playwright + TypeScript"],
                    help="Select your preferred automation framework for code generation"
                )
            
            with col2:
                additional_context = st.text_area(
                    "Additional Context (Optional)",
                    placeholder="Any specific requirements, patterns, or context for automation...",
                    help="Optional: Add specific automation requirements or patterns"
                )
            
            # Generate automation code
            if st.button("🤖 Generate Prompt for Cursor IDE", type="primary"):
                if test_automation_chain:
                    try:
                        # Format test cases for automation
                        formatted_cases = format_test_cases_for_automation(automation_cases, framework_pref, additional_context)
                        
                        with st.spinner("Generating automation code... (timeout: 120s)"):
                            automation_output = invoke_with_timeout(
                                test_automation_chain,
                                {
                                    "test_cases": formatted_cases,
                                    "testing_framework": framework_pref,
                                    "additional_context": additional_context
                                },
                                timeout_seconds=120
                            )
                            
                            st.subheader("🤖 Generated Automation Code")
                            st.markdown(automation_output)
                            
                            # Store in session state for potential export
                            st.session_state['generated_automation_code'] = automation_output
                            st.session_state['automation_framework'] = framework_pref
                            
                            st.success("🎉 Automation code generated successfully!")
                            
                    except Exception as e:
                        st.error(f"❌ An error occurred: {str(e)}")
                        import traceback
                        st.error(f"Full traceback: {traceback.format_exc()}")
                else:
                    st.error("❌ Test Automation chain not available. Please check the main page for initialization status.") 