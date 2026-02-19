import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_chains import invoke_with_timeout

st.set_page_config(layout="wide", page_title="Bug Improvement - AI QA Assistant")

st.title("🐛 Bug Improvement: Enhance Bug Descriptions & Labels")

def update_bug_fields():
    """Callback function to update form fields when bug selection changes"""
    if st.session_state.bug_selection != "-- Enter manually --":
        selected_bug_key = st.session_state.bug_selection.split(":")[0]
        selected_bug = next(bug for bug in st.session_state['existing_bugs'] if bug['key'] == selected_bug_key)
        
        st.session_state['current_bug_title'] = selected_bug['title']
        st.session_state['current_bug_description'] = selected_bug['description']
        st.session_state['current_bug_labels'] = ", ".join(selected_bug['labels'])
    else:
        st.session_state['current_bug_title'] = ""
        st.session_state['current_bug_description'] = ""
        st.session_state['current_bug_labels'] = ""

# Initialize session state variables if they don't exist
if 'current_bug_title' not in st.session_state:
    st.session_state['current_bug_title'] = ""
if 'current_bug_description' not in st.session_state:
    st.session_state['current_bug_description'] = ""
if 'current_bug_labels' not in st.session_state:
    st.session_state['current_bug_labels'] = ""
if 'existing_bugs' not in st.session_state:
    st.session_state['existing_bugs'] = None

# Get Jira client and project key from session state
jira_client = st.session_state.get('jira_client')
jira_project_key_bug = st.session_state.get('jira_project_key_bug')

if jira_client:
    st.subheader("Retrieve Existing Bug Reports from Jira (Optional)")
    # jira_project_key_bug is now passed as an argument
    retrieve_bugs = st.button(f"Retrieve Bugs from {jira_project_key_bug or 'Jira (Project Key Missing)'}", key="retrieve_bugs_improvement")

    if retrieve_bugs and jira_project_key_bug:
        with st.spinner("Retrieving Jira bug tickets..."):
            existing_bugs = jira_client.get_bug_tickets(jql_query=f"project = {jira_project_key_bug} AND type = 'Bug' AND created >= -52w AND \"cm groups[checkboxes]\" IN (BE, FE) ORDER BY created DESC")
            if existing_bugs:
                st.session_state['existing_bugs'] = existing_bugs
                st.success(f"Retrieved {len(existing_bugs)} bug tickets from Jira.")
                st.rerun()

    # Show bug selection if bugs are available
    if st.session_state['existing_bugs']:
        st.subheader("Recently Retrieved Bug Reports")
        
        # Create the selectbox for bug selection with callback
        selected_bug_option = st.selectbox(
            "Select a bug to improve (or enter manually below):",
            ["-- Enter manually --"] + [f"{bug['key']}: {bug['title']}" for bug in st.session_state['existing_bugs']],
            key="bug_selection",
            on_change=update_bug_fields
        )
        
        # Show selected bug info if a bug is selected
        if selected_bug_option != "-- Enter manually --":
            selected_bug_key = selected_bug_option.split(":")[0]
            st.info(f"Selected: {selected_bug_key} - {st.session_state['current_bug_title']}")

    # Display form fields with current session state values
    st.subheader("Bug Information")
    bug_title = st.text_input(
        "Bug Title", 
        value=st.session_state['current_bug_title'], 
        placeholder="Payment processing fails intermittently",
        key="bug_title_input"
    )
    
    bug_description = st.text_area(
        "Bug Description", 
        value=st.session_state['current_bug_description'], 
        placeholder="User attempts to make a payment. Sometimes it works, sometimes it fails with no clear error message. Observed on Chrome.",
        key="bug_description_input"
    )
    
    bug_labels = st.text_input(
        "Current Labels (comma-separated)", 
        value=st.session_state['current_bug_labels'], 
        placeholder="bug, p2, payment",
        key="bug_labels_input"
    )

    if st.button("Get AI Suggestions for Bug Improvement", key="get_bug_suggestions", type="primary"):
        # Get the bug improvement chain from session state
        bug_improvement_chain = st.session_state.get('bug_improvement_chain')
        if bug_improvement_chain:
            if bug_title and bug_description:
                with st.spinner("Generating bug improvement suggestions..."):
                    bug_improvement_output = invoke_with_timeout(
                        bug_improvement_chain,
                        {
                            "bug_title": bug_title,
                            "bug_description": bug_description,
                            "bug_labels": bug_labels
                        },
                        timeout_seconds=120
                    )
                    st.subheader("AI Suggestions for Bug Report Improvement")
                    st.markdown(bug_improvement_output)
            else:
                st.warning("Please provide a title and description for the bug.")
        else:
            st.error("❌ Bug Improvement chain not available. Please check the main page for initialization status.")
else:
    st.info("Jira integration is not configured or failed to initialize. Cannot retrieve existing bug reports or provide suggestions.")
    st.info("💡 Please check the main page for Jira connection status.") 