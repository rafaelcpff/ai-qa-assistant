import streamlit as st
import sys
import os
import time

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.cache_manager import CacheManager

st.set_page_config(layout="wide", page_title="Cache Management - AI QA Assistant")

st.title("⚡ Cache Management")
st.markdown("Manage application caching to improve performance and control data freshness.")

# Cache information section
st.subheader("📊 Cache Information")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Connection Cache",
        value="1 hour TTL",
        help="Jira and TestRail connections are cached for 1 hour"
    )

with col2:
    st.metric(
        label="Jira Data Cache",
        value="1 hour TTL",
        help="User stories and bug tickets are cached for 1 hour"
    )

with col3:
    st.metric(
        label="TestRail Data Cache", 
        value="30 min TTL",
        help="Test cases are cached for 30 minutes, sections for 1 hour"
    )

with col4:
    st.metric(
        label="LLM Response Cache",
        value="5 min TTL", 
        help="AI-generated responses are cached for 5 minutes"
    )

# Cache details
st.subheader("🔍 Cache Details")

cache_info = {
    "Connection Management": {
        "Jira Connection": "1 hour TTL - Prevents repeated authentication and connection setup",
        "TestRail Connection": "1 hour TTL - Prevents repeated authentication and connection setup",
        "Purpose": "Reduce connection overhead and improve startup performance"
    },
    "Jira Integration": {
        "User Stories": "1 hour TTL - Prevents repeated API calls for story queries",
        "Bug Tickets": "1 hour TTL - Prevents repeated API calls for bug queries",
        "Purpose": "Reduce Jira API load and improve response times"
    },
    "TestRail Integration": {
        "Test Cases": "30 minutes TTL - Test cases change less frequently",
        "Sections": "1 hour TTL - Sections change very infrequently", 
        "Purpose": "Reduce TestRail API load and improve performance"
    },
    "AI/LLM Operations": {
        "LLM Responses": "5 minutes TTL - Prevents repeated API calls for identical prompts",
        "Purpose": "Reduce Google Gemini API costs and improve response times"
    },
    "Data Processing": {
        "Text Sanitization": "30 minutes TTL - Sanitization is deterministic",
        "Similarity Analysis": "10 minutes TTL - Prevents recalculating similarity",
        "Purpose": "Improve performance for repeated operations"
    }
}

for category, details in cache_info.items():
    with st.expander(f"📋 {category}"):
        for item, description in details.items():
            st.write(f"**{item}:** {description}")

# Cache control section
st.subheader("🎛️ Cache Control")

col1, col2 = st.columns(2)

with col1:
    st.write("**Cache Actions:**")
    
    if st.button("🗑️ Clear All Caches", type="secondary"):
        CacheManager.clear_all_caches()
        st.rerun()
    
    if st.button("🔄 Refresh Cache Info", type="secondary"):
        st.rerun()

with col2:
    st.write("**Cache Status:**")
    
    # Show current cache status
    cache_status = CacheManager.get_cache_info()
    
    if cache_status["cache_enabled"]:
        st.success("✅ Caching is enabled")
    else:
        st.warning("⚠️ Caching is disabled")
    
    # Show cache statistics
    if cache_status["cache_enabled"]:
        st.info(f"📈 Cache hits: {cache_status.get('hits', 0)}")
        st.info(f"📉 Cache misses: {cache_status.get('misses', 0)}")
        
        hit_rate = cache_status.get('hit_rate', 0)
        if hit_rate > 0.7:
            st.success(f"🎯 Hit rate: {hit_rate:.1%} (Excellent)")
        elif hit_rate > 0.5:
            st.info(f"🎯 Hit rate: {hit_rate:.1%} (Good)")
        else:
            st.warning(f"🎯 Hit rate: {hit_rate:.1%} (Low)")

# Cache configuration
st.subheader("⚙️ Cache Configuration")

st.info("💡 Cache settings are configured in the application. For detailed configuration options, see the CACHING_GUIDE.md file.")

# Show cache directory info
cache_dir = CacheManager.get_cache_directory()
if cache_dir:
    st.write(f"**Cache Directory:** `{cache_dir}`")
    
    # Show cache size if available
    try:
        import os
        cache_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                        for dirpath, dirnames, filenames in os.walk(cache_dir)
                        for filename in filenames)
        
        if cache_size > 0:
            # Convert to MB
            cache_size_mb = cache_size / (1024 * 1024)
            st.write(f"**Cache Size:** {cache_size_mb:.2f} MB")
        else:
            st.write("**Cache Size:** Empty")
    except Exception as e:
        st.write(f"**Cache Size:** Unable to calculate ({str(e)})")
else:
    st.warning("⚠️ Cache directory not configured") 