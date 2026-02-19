import streamlit as st
import time
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_chains import invoke_with_timeout

st.set_page_config(layout="wide", page_title="Test Analysis - AI QA Assistant")

st.title("📈 Test Analysis: New User Story Insights & Quality Risks")

# Check if stories are available in global session state
if 'existing_stories' in st.session_state and st.session_state['existing_stories']:
    existing_stories = st.session_state['existing_stories']
    
    # Show status info
    if 'stories_fetched_at' in st.session_state:
        fetch_time = time.strftime('%H:%M:%S', time.localtime(st.session_state['stories_fetched_at']))
        st.info(f"📊 Using {len(existing_stories)} user stories fetched at {fetch_time}")
    
    st.subheader("Select User Story for Analysis")
    
    # Create a dropdown for selecting user stories
    story_options = [f"{story['key']}: {story['title']}" for story in existing_stories]
    selected_story_display = st.selectbox(
        "Choose a user story to analyze",
        options=story_options,
        index=None,
        placeholder="Select a user story from the list..."
    )
    
    # Find the selected story object
    selected_story = None
    if selected_story_display:
        selected_key = selected_story_display.split(": ")[0]
        selected_story = next((story for story in existing_stories if story['key'] == selected_key), None)
        
        # Display selected story details
        if selected_story:
            st.subheader("Selected User Story Details")
            
            # Display story information in a nice format
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**Key:** {selected_story['key']}")
                st.markdown(f"**Title:** {selected_story['title']}")
            
            with col2:
                with st.expander("📄 Description", expanded=True):
                    st.write(selected_story.get('description', 'No description available'))
            
            # Extract comments and linked tickets from the story data
            new_story_comments = selected_story.get('comments', '')
            new_story_linked_tickets = selected_story.get('linked_tickets', '')

            col1, col2 = st.columns([2, 1])
            with col1:
                # Allow manual override of comments and linked tickets
                new_story_comments = st.text_area(
                    "Additional Comments (Optional Override)", 
                    value=new_story_comments,
                    placeholder="Any additional comments, notes, or context about this user story...",
                    help="Optional: Add or modify comments that might be relevant for analysis"
                )

            with col2:
                new_story_linked_tickets = st.text_input(
                    "Linked Tickets (Optional Override)", 
                    value=new_story_linked_tickets,
                    placeholder="PROJ-123, PROJ-456, PROJ-789",
                    help="Optional: Enter or modify Jira ticket keys separated by commas"
                )

        if st.button("Get AI Insights & Risks (Test Analysis)", key="get_ai_insights", type="primary"):
            # Get the user story analysis chain from session state
            user_story_analysis_chain = st.session_state.get('user_story_analysis_chain')
            if user_story_analysis_chain:
                if selected_story:
                    # Use original data directly (sanitization handled in background)
                    title = selected_story['title']
                    description = selected_story.get('description', '')
                    comments = new_story_comments if new_story_comments else ""
                    linked_tickets = new_story_linked_tickets if new_story_linked_tickets else ""
                    
                    # Create context string from stories
                    context_str = "\n\n".join([f"Key: {s['key']}\nTitle: {s['title']}\nDescription: {s['description']}" for s in st.session_state['existing_stories']])
                    
                    with st.spinner("Generating insights... (timeout: 120s)"):
                        analysis_output = invoke_with_timeout(
                            user_story_analysis_chain,
                            {
                                "context_user_stories": context_str,
                                "new_story_title": title,
                                "new_story_description": description,
                                "new_story_comments": comments,
                                "new_story_linked_tickets_comma_separated": linked_tickets
                            },
                            timeout_seconds=120
                        )
                        st.subheader("AI Analysis")
                        st.markdown(analysis_output)
                        st.session_state['last_quality_risks'] = analysis_output.split("Quality Risks:")[-1].split("Suggested Areas for Focus")[0].strip()
                        st.session_state['last_new_story_title'] = selected_story['title']
                        st.session_state['last_new_story_description'] = selected_story.get('description', '')
                        st.session_state['last_new_story_comments'] = new_story_comments
                        st.session_state['last_new_story_linked_tickets'] = new_story_linked_tickets
            else:
                st.error("❌ User Story Analysis chain not available. Please check the main page for initialization status.")
else:
    st.warning("⚠️ No user stories available. Please go to the main page and fetch user stories from Jira first.")
    st.info("💡 You can navigate back to the main page using the sidebar menu.") 