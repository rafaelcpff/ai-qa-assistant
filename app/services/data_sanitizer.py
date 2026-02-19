import re
import hashlib
from typing import Dict, List, Any
import streamlit as st

class DataSanitizer:
    """
    Sanitizes sensitive data before sending to external APIs.
    Replaces company names, client names, project names, and other sensitive information
    with generic placeholders.
    """
    
    def __init__(self):
        # Common patterns to detect and replace
        self.sensitive_patterns = {
            # Company names and variations
            'company_names': [
                r'\company\b', r'\bcomp\s*any\b', r'\bcompany\b',
                r'\bCM\b', r'\bCompany\b', r'\bCompany\b'
            ],
            # Project codes and names
            'project_codes': [
                r'\bCM-\d+\b', r'\bPROJ-\d+\b', r'\bTASK-\d+\b', r'\bINC-\d+\b',
                r'\bproject\s*=\s*CM\b', r'\bproject\s*=\s*[A-Z]{2,}\b'
            ],
            # Email addresses
            'emails': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            # URLs and domains
            'urls': [
                r'https?://[^\s<>"]+|www\.[^\s<>"]+',
                r'\bcompany\.atlassian\.net\b',
                r'\bcompany\.com\b'
            ],
            # API tokens and keys
            'tokens': [
                r'\bATATT[A-Za-z0-9_-]{100,}\b',  # Jira API tokens
                r'\bAIza[A-Za-z0-9_-]{35}\b',  # Google API keys
                r'\bsk-[A-Za-z0-9]{48}\b',  # OpenAI API keys (legacy)
                r'\b[A-Za-z0-9]{32,}\b'  # Generic long tokens
            ],
            # Client names (common patterns)
            'client_names': [
                r'\bclient\s*:\s*[A-Za-z\s&]+',
                r'\bcustomer\s*:\s*[A-Za-z\s&]+',
                r'\buser\s*:\s*[A-Za-z\s&]+'
            ],
            # Internal system names
            'system_names': [
                r'\bBE\b', r'\bFE\b', r'\bBackend\b', r'\bFrontend\b',
                r'\bAPI\b', r'\bDatabase\b', r'\bSystem\b', r'\bPM\b', r'\bPP\b'
            ]
        }
        
        # Replacement mappings
        self.replacements = {
            'company_names': '[COMPANY_NAME]',
            'project_codes': '[PROJECT_CODE]',
            'emails': '[EMAIL]',
            'urls': '[URL]',
            'tokens': '[API_TOKEN]',
            'client_names': '[CLIENT_NAME]',
            'system_names': '[SYSTEM_NAME]'
        }
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = {}
        for category, patterns in self.sensitive_patterns.items():
            self.compiled_patterns[category] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def _cached_sanitize_text(_self, text: str) -> str:
        """
        Cached version of text sanitization.
        This prevents repeated processing of the same text within 30 minutes.
        """
        if not text:
            return ""
        
        # Convert to string if it's not already
        if not isinstance(text, str):
            text = str(text)
            
        sanitized_text = text
        
        # Apply email pattern first (before company name replacement)
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', re.IGNORECASE)
        sanitized_text = email_pattern.sub('[EMAIL]', sanitized_text)
        
        # Apply all other sanitization patterns
        for category, patterns in _self.compiled_patterns.items():
            replacement = _self.replacements[category]
            for pattern in patterns:
                sanitized_text = pattern.sub(replacement, sanitized_text)
        
        # Additional custom replacements
        sanitized_text = _self._custom_replacements(sanitized_text)
        
        return sanitized_text

    def sanitize_text(self, text: str) -> str:
        """
        Sanitizes a text string by replacing sensitive information.
        Uses caching to improve performance for repeated text.
        
        Args:
            text: The text to sanitize
            
        Returns:
            Sanitized text with sensitive information replaced
        """
        return self._cached_sanitize_text(text)
    
    def _custom_replacements(self, text: str) -> str:
        """
        Applies custom replacement rules.
        """
        # Replace specific hardcoded values
        custom_replacements = {
            'rafael.fernandes@company.com': '[USER_EMAIL]',
            'https://company.atlassian.net': '[JIRA_URL]',
            '': '[JIRA_TOKEN]',
            'company': '[COMPANY_NAME]',
            'company': '[COMPANY_NAME]',
            'ST-': '[PROJECT_CODE]-',
            'INC-': '[PROJECT_CODE]-',
            'TT': '[SYSTEM_NAME]',
            'TS': '[SYSTEM_NAME]',
        }
        
        for original, replacement in custom_replacements.items():
            text = text.replace(original, replacement)
        
        return text
    
    def sanitize_user_story(self, story: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitizes a user story dictionary.
        
        Args:
            story: User story dictionary with key, title, description
            
        Returns:
            Sanitized user story dictionary
        """
        return {
            "key": self.sanitize_text(story.get("key", "")),
            "title": self.sanitize_text(story.get("title", "")),
            "description": self.sanitize_text(story.get("description", ""))
        }
    
    def sanitize_bug_ticket(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitizes a bug ticket dictionary.
        
        Args:
            ticket: Bug ticket dictionary with key, title, description, labels
            
        Returns:
            Sanitized bug ticket dictionary
        """
        return {
            "key": self.sanitize_text(ticket.get("key", "")),
            "title": self.sanitize_text(ticket.get("title", "")),
            "description": self.sanitize_text(ticket.get("description", "")),
            "labels": [self.sanitize_text(label) for label in ticket.get("labels", [])]
        }
    
    def sanitize_stories_list(self, stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sanitizes a list of user stories.
        
        Args:
            stories: List of user story dictionaries
            
        Returns:
            List of sanitized user story dictionaries
        """
        return [self.sanitize_user_story(story) for story in stories]
    
    def sanitize_bugs_list(self, bugs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sanitizes a list of bug tickets.
        
        Args:
            bugs: List of bug ticket dictionaries
            
        Returns:
            List of sanitized bug ticket dictionaries
        """
        return [self.sanitize_bug_ticket(bug) for bug in bugs]
    
    def get_sanitization_summary(self, original_text: str, sanitized_text: str) -> Dict[str, Any]:
        """
        Provides a summary of what was sanitized.
        
        Args:
            original_text: Original text
            sanitized_text: Sanitized text
            
        Returns:
            Dictionary with sanitization summary
        """
        original_length = len(original_text)
        sanitized_length = len(sanitized_text)
        
        # Count replacements by category
        replacements_count = {}
        for category, patterns in self.compiled_patterns.items():
            count = 0
            for pattern in patterns:
                count += len(pattern.findall(original_text))
            if count > 0:
                replacements_count[category] = count
        
        return {
            "original_length": original_length,
            "sanitized_length": sanitized_length,
            "replacements_made": replacements_count,
            "sanitization_percentage": round((1 - sanitized_length / original_length) * 100, 2) if original_length > 0 else 0
        } 