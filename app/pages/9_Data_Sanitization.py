import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_sanitizer import DataSanitizer

st.set_page_config(layout="wide", page_title="Data Sanitization - AI QA Assistant")

st.title("🔒 Data Sanitization Preview & Verification")
st.info("Use this page to test and verify data sanitization before sending to AI APIs.")

sanitizer = DataSanitizer()

# Sidebar for configuration
with st.sidebar:
    st.subheader("🔧 Sanitization Settings")
    st.write("**Current Patterns:**")
    for category, patterns in sanitizer.sensitive_patterns.items():
        with st.expander(f"{category.title()} ({len(patterns)} patterns)"):
            for pattern in patterns:
                st.code(pattern, language="regex")

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Input Text")
    st.write("Enter text containing sensitive data to test sanitization:")
    
    # Sample text options
    sample_texts = {
        "None": "",
        "Company Data": "Fix bug in company payment system for company client ABC Corp",
        "Project Codes": "ST-123: Implement new feature for PROJ-456 and INC-101 backend system",
        "Email & URLs": "Contact john.doe@test.com. Check your company URL for updates",
        "API Tokens": "Use token {token} for authentication",
        "User Story": "ST-456: Add payment processing feature for company client. User rafael.fernandes@company.com reported issues with BE/FE integration.",
        "Bug Report": "ST-789: Payment fails for company client. Check https://company.atlassian.net. Labels: bug, p1, payment",
        "System Names": "PM and PP teams need to coordinate with BE/FE on API changes. Backend system integration required."
    }
    
    selected_sample = st.selectbox("Choose sample text:", list(sample_texts.keys()))
    
    if selected_sample != "None":
        input_text = st.text_area("Text to sanitize:", value=sample_texts[selected_sample], height=200, key="input_text_preview")
    else:
        input_text = st.text_area("Text to sanitize:", height=200, key="input_text_preview")

with col2:
    st.subheader("🔒 Sanitized Output")
    
    if input_text.strip():
        # Perform sanitization
        sanitized_text = sanitizer.sanitize_text(input_text)
        
        # Display sanitized text
        st.text_area("Sanitized text:", value=sanitized_text, height=200, key="sanitized_output_preview")
        
        # Show sanitization summary
        summary = sanitizer.get_sanitization_summary(input_text, sanitized_text)
        
        st.subheader("📊 Sanitization Summary")
        
        # Metrics
        col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
        with col_metrics1:
            st.metric("Original Length", f"{summary['original_length']} chars")
        with col_metrics2:
            st.metric("Sanitized Length", f"{summary['sanitized_length']} chars")
        with col_metrics3:
            st.metric("Reduction", f"{summary['sanitization_percentage']}%")
        
        # Replacements made
        if summary['replacements_made']:
            st.write("**Replacements by category:**")
            for category, count in summary['replacements_made'].items():
                st.write(f"• {category.replace('_', ' ').title()}: {count} replacements")
        else:
            st.success("✅ No sensitive data detected!")
        
        # Visual comparison
        st.subheader("🔍 Side-by-Side Comparison")
        
        # Create a visual diff-like display
        original_lines = input_text.split('\n')
        sanitized_lines = sanitized_text.split('\n')
        
        comparison_html = """
        <style>
        .comparison-container { display: flex; gap: 10px; }
        .original, .sanitized { flex: 1; padding: 10px; border-radius: 5px; }
        .original { background-color: #ffe6e6; border: 1px solid #ffcccc; }
        .sanitized { background-color: #e6ffe6; border: 1px solid #ccffcc; }
        .highlight { background-color: #ffffcc; padding: 2px; border-radius: 3px; }
        </style>
        <div class="comparison-container">
        <div class="original">
        <h4>🔴 Original Text</h4>
        """
        
        for line in original_lines:
            if line.strip():
                # Highlight sensitive terms
                highlighted_line = line
                for category, patterns in sanitizer.sensitive_patterns.items():
                    for pattern in patterns:
                        import re
                        highlighted_line = re.sub(pattern, r'<span class="highlight">\g<0></span>', highlighted_line, flags=re.IGNORECASE)
                comparison_html += f"<p>{highlighted_line}</p>"
            else:
                comparison_html += "<p><br></p>"
        
        comparison_html += """
        </div>
        <div class="sanitized">
        <h4>🟢 Sanitized Text</h4>
        """
        
        for line in sanitized_lines:
            if line.strip():
                comparison_html += f"<p>{line}</p>"
            else:
                comparison_html += "<p><br></p>"
        
        comparison_html += """
        </div>
        </div>
        """
        
        st.markdown(comparison_html, unsafe_allow_html=True)
        
        # Download options
        st.subheader("💾 Export Options")
        
        col_download1, col_download2 = st.columns(2)
        
        with col_download1:
            if st.button("📥 Download Original Text"):
                st.download_button(
                    label="Click to download",
                    data=input_text,
                    file_name="original_text.txt",
                    mime="text/plain"
                )
        
        with col_download2:
            if st.button("📥 Download Sanitized Text"):
                st.download_button(
                    label="Click to download",
                    data=sanitized_text,
                    file_name="sanitized_text.txt",
                    mime="text/plain"
                )
    else:
        st.info("Enter some text in the left column to see sanitization results.") 