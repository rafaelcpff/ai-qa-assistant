import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def setup_llm():   
    # Google Gemini API configuration
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")  # Default to latest Gemini model (free tier)
    
    if not api_key:
        st.error("❌ GOOGLE_API_KEY not found in environment variables. Please add your Google API key to the .env file.")
        return None
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.5,  # Lower temperature for more focused responses
            max_output_tokens=4000,  # Increased for longer responses
            request_timeout=120,  # Increased timeout for longer responses
            convert_system_message_to_human=True,  # Handle system messages properly
        )
        return llm
    except Exception as e:
        st.error(f"❌ Could not connect to Google Gemini API. Please check your API key and internet connection. Error: {e}")
        return None

def get_jira_project_key_us():
    """Retrieves the Jira project key for user stories from .env."""
    return os.getenv("JIRA_PROJECT_KEY") # Assuming single key based on your last request

def get_jira_project_key_bug():
    """Retrieves the Jira project key for bug reports from .env."""
    # If you use separate keys, change to os.getenv("JIRA_PROJECT_KEY_BUGS")
    return os.getenv("JIRA_PROJECT_KEY") # Assuming single key based on your last request

def get_testrail_config():
    """Retrieves TestRail configuration from .env."""
    return {
        'url': os.getenv("TESTRAIL_URL"),
        'username': os.getenv("TESTRAIL_USERNAME"),
        'password': os.getenv("TESTRAIL_PASSWORD")
    }

def validate_testrail_config():
    """Validates that all required TestRail environment variables are set."""
    config = get_testrail_config()
    missing_vars = []
    
    if not config['url']:
        missing_vars.append("TESTRAIL_URL")
    if not config['username']:
        missing_vars.append("TESTRAIL_USERNAME")
    if not config['password']:
        missing_vars.append("TESTRAIL_PASSWORD")
    
    return missing_vars