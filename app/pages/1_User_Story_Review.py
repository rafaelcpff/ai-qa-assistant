import streamlit as st
import time
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_chains import invoke_with_timeout

st.set_page_config(layout="wide", page_title="User Story Review - AI QA Assistant")

st.title("📋 Story Review: Quality Assessment & Improvement")

st.markdown("""
This page allows you to review both regular user stories and enhancement tickets containing multiple improvements.
- **Story**: Use for individual user stories with clear acceptance criteria
- **Enhancement**: Use for multi-item improvement tickets with various UX/UI enhancements and functional tweaks
""")

# Check if stories are available in global session state
if 'existing_stories' in st.session_state and st.session_state['existing_stories']:
    existing_stories = st.session_state['existing_stories']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # Show status info
        if 'stories_fetched_at' in st.session_state:
            fetch_time = time.strftime('%H:%M:%S', time.localtime(st.session_state['stories_fetched_at']))
            st.info(f"📊 Using {len(existing_stories)} user stories fetched at {fetch_time}")
    
    st.subheader("Select User Story for Review")
    
    # Create a dropdown for selecting user stories
    story_options = [f"{story['key']}: {story['title']}" for story in existing_stories]
    selected_story_display = st.selectbox(
        "Choose a user story to review",
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
            
            # Add radio button for story type selection
            story_type = st.radio(
                "Select Story Type:",
                options=["Story", "Enhancement"],
                index=0,
                help="Choose 'Story' for regular user stories or 'Enhancement' for multi-item improvement tickets"
            )
            
            if st.button("Review User Story Quality", key="review_story_quality", type="primary"):
                # Get the appropriate chain based on story type
                if story_type == "Story":
                    review_chain = st.session_state.get('user_story_review_chain')
                    chain_name = "User Story Review"
                else:  # Enhancement
                    review_chain = st.session_state.get('enhancement_story_review_chain')
                    chain_name = "Enhancement Story Review"
                
                if review_chain:
                    if selected_story:
                        # Use original data directly (sanitization handled in background)
                        title = selected_story['title']
                        description = selected_story.get('description', '')
                        
                        with st.spinner(f"Reviewing {story_type.lower()} quality... (timeout: 120s)"):
                            review_output = invoke_with_timeout(
                                review_chain,
                                {
                                    "user_story_title": title,
                                    "user_story_description": description
                                },
                                timeout_seconds=120
                            )
                            
                            # Parse and display the review results
                            st.subheader(f"📊 {chain_name} Results")
                            
                            # Extract initial rating
                            if "Initial Rating:" in review_output:
                                initial_rating_section = review_output.split("Initial Rating:")[1].split("###")[0].strip()
                                # Extract the rating number
                                rating_match = initial_rating_section.strip()
                                if rating_match:
                                    # Create a beautiful rating display
                                    col1, col2, col3 = st.columns([1, 2, 1])
                                    with col2:
                                        st.markdown("### 📊 Initial Quality Rating")
                                        # Extract numeric rating
                                        import re
                                        rating_number = re.search(r'(\d+)/10', rating_match)
                                        if rating_number:
                                            rating = int(rating_number.group(1))
                                            # Create emoji-based rating display
                                            emoji_rating = "⭐" * rating + "☆" * (10 - rating)
                                            st.markdown(f"## {emoji_rating}")
                                            st.markdown(f"### **{rating}/10**")
                                            
                                            # Add color-coded rating description
                                            if rating <= 3:
                                                st.error("🔴 Poor Quality - Needs significant improvement")
                                            elif rating <= 5:
                                                st.warning("🟡 Fair Quality - Room for improvement")
                                            elif rating <= 7:
                                                st.info("🟢 Good Quality - Minor improvements needed")
                                            elif rating <= 9:
                                                st.success("🟢 Very Good Quality - Well written")
                                            else:
                                                st.success("🟢 Excellent Quality - Outstanding!")
                            
                            # Display the full review
                            with st.expander("📋 Complete Review Analysis", expanded=True):
                                st.markdown(review_output)
                else:
                    st.error(f"❌ {chain_name} chain not available. Please check the main page for initialization status.")
else:
    st.warning("⚠️ No user stories available. Please go to the main page and fetch user stories from Jira first.")
    st.info("💡 You can navigate back to the main page using the sidebar menu.") 