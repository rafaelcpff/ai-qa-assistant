import streamlit as st
import time
from jira_client import JiraClient
from testrail_client import TestRailClient
from config import setup_llm, get_jira_project_key_us, get_jira_project_key_bug, validate_testrail_config
from services.llm_chains import setup_llm_chains
import os # For os.getenv if needed globally or for checks

# --- Global Initialization (once per app run) ---
llm = setup_llm()
user_story_analysis_chain, test_case_generation_chain, test_automation_chain, bug_improvement_chain, user_story_review_chain, enhancement_story_review_chain = setup_llm_chains(llm)

jira_client = None
try:
    jira_client = JiraClient()
    # Check if Jira connection was successful
    if jira_client.jira is None:
        st.error("❌ Jira connection failed. Please check your .env file and credentials.")
except ValueError as e:
    st.error(f"❌ Jira configuration error: {e}. Please check your .env file.")
except Exception as e:
    st.error(f"❌ An unexpected error occurred during Jira client initialization: {e}")

# Initialize TestRail client
testrail_client = None
try:
    testrail_client = TestRailClient()
    # TestRail client handles its own UI messages in _connect method
except Exception as e:
    st.error(f"❌ TestRail configuration error: {e}. Please check your .env file.")

# Retrieve Jira project keys from config
jira_project_key_us = get_jira_project_key_us()
jira_project_key_bug = get_jira_project_key_bug()

# Check TestRail configuration
testrail_missing_vars = validate_testrail_config()

# Store objects in session state for pages to access
if 'jira_client' not in st.session_state:
    st.session_state['jira_client'] = jira_client
if 'testrail_client' not in st.session_state:
    st.session_state['testrail_client'] = testrail_client
if 'jira_project_key_us' not in st.session_state:
    st.session_state['jira_project_key_us'] = jira_project_key_us
if 'jira_project_key_bug' not in st.session_state:
    st.session_state['jira_project_key_bug'] = jira_project_key_bug

# Store LLM chains in session state
if 'user_story_analysis_chain' not in st.session_state:
    st.session_state['user_story_analysis_chain'] = user_story_analysis_chain
if 'test_case_generation_chain' not in st.session_state:
    st.session_state['test_case_generation_chain'] = test_case_generation_chain
if 'test_automation_chain' not in st.session_state:
    st.session_state['test_automation_chain'] = test_automation_chain
if 'bug_improvement_chain' not in st.session_state:
    st.session_state['bug_improvement_chain'] = bug_improvement_chain
if 'user_story_review_chain' not in st.session_state:
    st.session_state['user_story_review_chain'] = user_story_review_chain
if 'enhancement_story_review_chain' not in st.session_state:
    st.session_state['enhancement_story_review_chain'] = enhancement_story_review_chain

# --- Streamlit UI ---
st.set_page_config(
    layout="wide", 
    page_title="Home - AI QA Assistant",
    page_icon="🏠"
)
st.title("🏠 Home - AI QA Assistant")

st.markdown("""
Welcome to the AI QA Assistant! This is your central hub for managing user stories, monitoring system status, and navigating to different QA tools.

**Getting Started:**
1. Check the system status below to ensure all integrations are working
2. Fetch user stories from Jira using the button below
3. Navigate to other pages using the sidebar menu
""")

if llm is None:
    st.warning("AI features are disabled due to Google Gemini API connection issues. Please check your API key in the .env file.")
if jira_client is None:
    st.warning("Jira integration is disabled due to configuration issues. Please check your .env file.")
elif not jira_project_key_us: # Added a check for missing project key(s)
    st.warning("Jira Project Key for User Stories is not set in .env. Some Jira features may not work.")
elif not jira_project_key_bug:
    st.warning("Jira Project Key for Bug Reports is not set in .env. Some Jira features may not work.")

if testrail_client is None or testrail_missing_vars:
    st.warning("TestRail integration is disabled due to configuration issues. Please check TESTRAIL_SETUP.md for setup instructions.")
    if testrail_missing_vars:
        st.error(f"Missing TestRail environment variables: {', '.join(testrail_missing_vars)}")

# Global Jira Stories Fetch Section
if jira_client and jira_project_key_us:
    st.subheader("📋 Global Jira Stories Management")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # Show current status
        if 'existing_stories' in st.session_state and st.session_state['existing_stories']:
            st.success(f"✅ {len(st.session_state['existing_stories'])} user stories loaded and ready for use across all pages")
            
            # Show a few sample stories
            with st.expander("📄 Sample Stories (click to view all)"):
                for i, story in enumerate(st.session_state['existing_stories'][:5]):
                    st.markdown(f"**{story['key']}:** {story['title']}")
                if len(st.session_state['existing_stories']) > 5:
                    st.info(f"... and {len(st.session_state['existing_stories']) - 5} more stories")
        else:
            st.info("ℹ️ No user stories loaded yet. Click the button below to fetch stories from Jira.")

    with col2:
        if st.button("🔄 Fetch User Stories from Jira", key="global_fetch_stories", type="primary"):
            with st.spinner("Retrieving Jira user stories..."):
                existing_stories = jira_client.get_user_stories(
                    jql_query=f"project = {jira_project_key_us} AND type = 'Story' AND created >= -52w AND \"cm groups[checkboxes]\" IN (BE, FE) ORDER BY created DESC"
                )
                if existing_stories:
                    st.session_state['existing_stories'] = existing_stories
                    st.session_state['stories_fetched_at'] = time.time()
                    st.success(f"✅ Successfully fetched {len(existing_stories)} user stories from Jira!")
                    st.rerun()  # Refresh the page to show the new data
                else:
                    st.error("❌ No user stories found or an error occurred while fetching.")
        if st.button("🔄 Refresh Stories", key="refresh_stories", disabled=('existing_stories' not in st.session_state)):
            st.rerun()

elif jira_client and not jira_project_key_us:
    st.warning("⚠️ Jira Project Key for User Stories is not configured. Cannot fetch stories.")

st.markdown("---")  # Separator

# Navigation instructions
st.subheader("🧭 Navigation")
st.info("""
Use the sidebar menu to navigate between different pages:

🏠 **Home** - System overview, user stories management, and navigation hub
1. **User Story Review** - Quality assessment and improvement of user stories
2. **Test Analysis** - AI insights and quality risks for new user stories  
3. **Test Design** - Generate test cases and regression scenarios
4. **Test Automation** - Generate automation code for test cases
5. **Bug Improvement** - Enhance bug descriptions and labels
6. **Model Evaluation** - Basic model evaluation examples
7. **TestRail Integration** - Find similar existing test cases
8. **Cache Management** - Manage application caching
9. **Data Sanitization** - Preview and verify data sanitization before sending to AI APIs

Each page maintains its own state and can access shared data like user stories and AI chains.
""")

# Status overview
st.subheader("📊 System Status")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if llm is not None:
        st.success("✅ AI/LLM: Connected")
    else:
        st.error("❌ AI/LLM: Disconnected")

with col2:
    if jira_client is not None and jira_client.jira is not None:
        st.success("✅ Jira: Connected")
    else:
        st.error("❌ Jira: Disconnected")

with col3:
    if testrail_client is not None and testrail_client.client is not None:
        st.success("✅ TestRail: Connected")
    else:
        st.error("❌ TestRail: Disconnected")

with col4:
    if 'existing_stories' in st.session_state and st.session_state['existing_stories']:
        st.success(f"✅ Stories: {len(st.session_state['existing_stories'])} loaded")
    else:
        st.warning("⚠️ Stories: None loaded")