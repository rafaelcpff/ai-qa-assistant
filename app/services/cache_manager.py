import streamlit as st
import hashlib
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import time

class CacheManager:
    """
    Centralized cache manager for the AI QA Assistant application.
    Provides caching for expensive operations like API calls and LLM responses.
    """
    
    @staticmethod
    def _generate_cache_key(data: Any, prefix: str = "") -> str:
        """Generate a unique cache key based on input data."""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        # Create a hash of the data
        hash_obj = hashlib.md5(data_str.encode())
        cache_key = f"{prefix}_{hash_obj.hexdigest()}"
        return cache_key
    
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def cache_jira_connection(base_url: str, email: str, api_token: str):
        """
        Cache Jira connection with a 1-hour TTL.
        This prevents repeated connection setup and authentication.
        """
        # This is a placeholder - the actual implementation is in the Jira client
        return None
    
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def cache_jira_stories(jql_query: str, project_key: str, max_results: Optional[int] = None) -> List[Dict]:
        """
        Cache Jira user stories with a 1-hour TTL.
        This prevents repeated API calls for the same query.
        """
        # This is a placeholder - the actual implementation will be in the Jira client
        # The cache key is based on the JQL query and parameters
        return []
    
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def cache_jira_bugs(jql_query: str, project_key: str, max_results: Optional[int] = None) -> List[Dict]:
        """
        Cache Jira bug tickets with a 1-hour TTL.
        This prevents repeated API calls for the same query.
        """
        # This is a placeholder - the actual implementation will be in the Jira client
        return []
    
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def cache_testrail_connection(testrail_url: str, testrail_username: str, testrail_password: str):
        """
        Cache TestRail connection with a 1-hour TTL.
        This prevents repeated connection setup and authentication.
        """
        # This is a placeholder - the actual implementation is in the TestRail client
        return None
    
    @staticmethod
    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def cache_testrail_cases(project_id: int, limit: int = 250, offset: int = 0) -> List[Dict]:
        """
        Cache TestRail test cases with a 30-minute TTL.
        Test cases change less frequently than Jira issues.
        """
        # This is a placeholder - the actual implementation will be in the TestRail client
        return []
    
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def cache_testrail_sections(project_id: int) -> List[Dict]:
        """
        Cache TestRail sections with a 1-hour TTL.
        Sections change very infrequently.
        """
        # This is a placeholder - the actual implementation will be in the TestRail client
        return []
    
    @staticmethod
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def cache_llm_response(prompt_hash: str, model_name: str, temperature: float) -> str:
        """
        Cache LLM responses with a 5-minute TTL.
        This prevents repeated API calls for identical prompts.
        """
        # This is a placeholder - the actual implementation will be in the LLM chains
        return ""
    
    @staticmethod
    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def cache_sanitized_data(original_text: str, sanitization_rules: Dict) -> str:
        """
        Cache sanitized data with a 30-minute TTL.
        Sanitization results are deterministic for the same input and rules.
        """
        # This is a placeholder - the actual implementation will be in the data sanitizer
        return ""
    
    @staticmethod
    @st.cache_data(ttl=600)  # Cache for 10 minutes
    def cache_similarity_analysis(generated_cases: List[Dict], existing_cases: List[Dict], 
                                threshold: float, user_story_key: str = None) -> List[Dict]:
        """
        Cache similarity analysis results with a 10-minute TTL.
        This prevents recalculating similarity for the same test cases.
        """
        # This is a placeholder - the actual implementation will be in the TestRail client
        return []
    
    @staticmethod
    def clear_all_caches():
        """Clear all cached data. Useful for debugging or when data becomes stale."""
        st.cache_data.clear()
        st.success("✅ All caches cleared successfully!")
    
    @staticmethod
    def get_cache_info() -> Dict[str, Any]:
        """Get information about cache usage and performance."""
        # Note: Streamlit doesn't provide direct cache statistics
        # This is a placeholder for future implementation
        return {
            "cache_enabled": True,
            "cache_ttl_default": "1 hour for API calls, 5 minutes for LLM responses",
            "note": "Cache statistics not directly available in Streamlit"
        }
    
    @staticmethod
    def create_cached_function(func: Callable, ttl: int = 3600, **kwargs):
        """
        Create a cached version of any function with specified TTL.
        
        Args:
            func: The function to cache
            ttl: Time to live in seconds
            **kwargs: Additional arguments to pass to st.cache_data
        
        Returns:
            Cached version of the function
        """
        @st.cache_data(ttl=ttl, **kwargs)
        def cached_func(*args, **func_kwargs):
            return func(*args, **func_kwargs)
        
        return cached_func 