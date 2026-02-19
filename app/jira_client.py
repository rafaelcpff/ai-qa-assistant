from jira import JIRA
import os
import requests
import streamlit as st
from dotenv import load_dotenv
from services.data_sanitizer import DataSanitizer
from services.adf_parser import ADFParser

load_dotenv()

class JiraClient:

    story_jql_query = "project = CM AND type = Story AND created >= -52w AND \"cm groups[checkboxes]\" IN (BE, FE) ORDER BY created DESC"
    bug_jql_query = "project = CM AND type = Bug AND created >= -52w AND \"cm groups[checkboxes]\" IN (BE, FE) ORDER BY created DESC"

    def __init__(self):
        self.base_url = os.getenv("JIRA_BASE_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")

        if not all([self.base_url, self.email, self.api_token]):
            raise ValueError("Jira credentials [JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN] must be set in .env")

        # Use cached connection
        result = self._cached_connect()
        self.jira, status, message = result
        
        # Handle connection status (UI messages will be handled in main.py)
        if status == "connection_error":
            raise ValueError(message)
        
        self.sanitizer = DataSanitizer()

    @st.cache_data(ttl=3600, show_spinner="Connecting to Jira...")  # Cache connection for 1 hour
    def _cached_connect(_self):
        """
        Cached version of Jira connection.
        This prevents repeated connection setup and authentication within 1 hour.
        Returns a tuple of (client, status, error_message) for external UI handling.
        """
        try:
            jira = JIRA(basic_auth=(_self.email, _self.api_token), options={"server": _self.base_url})
            
            # Test connection by trying to get a project
            try:
                jira.projects()
            except Exception as test_error:
                # If projects call fails, connection might still be valid
                return jira, "connection_warning", f"Jira connection test failed, but connection may still work: {str(test_error)}"
            
            return jira, "success", "Successfully connected to Jira"
            
        except Exception as e:
            error_msg = f"Failed to connect to Jira: {str(e)}"
            return None, "connection_error", error_msg

    def _get_all_issues(self, jql_query, max_results=None):
        """
        Helper method to retrieve all issues matching a JQL query using direct REST API calls.
        This bypasses the Jira Python library's limitations and retrieves ALL matching issues.
        """
        all_issues = []
        start_at = 0
        batch_size = 100  # Jira's recommended batch size
        
        print(f"Starting to fetch issues with JQL: {jql_query}")
        
        while True:
            try:
                # Use direct REST API call for unlimited pagination
                url = f"{self.base_url}/rest/api/3/search"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
                auth = (self.email, self.api_token)
                
                payload = {
                    "jql": jql_query,
                    "startAt": start_at,
                    "maxResults": batch_size,
                    "fields": ["summary", "description", "labels"]
                }
                
                response = requests.post(url, json=payload, headers=headers, auth=auth)
                response.raise_for_status()
                
                data = response.json()
                issues = data.get('issues', [])
                
                # If no more issues, break
                if not issues:
                    break
                
                # Convert to Jira Issue objects for consistency
                jira_issues = []
                for issue_data in issues:
                    # Create a simple object that mimics the Jira Issue structure
                    class MockIssue:
                        def __init__(self, data):
                            self.key = data['key']
                            self.fields = type('MockFields', (), {
                                'summary': data['fields'].get('summary', ''),
                                'description': data['fields'].get('description', ''),
                                'labels': data['fields'].get('labels', [])
                            })()
                    
                    jira_issues.append(MockIssue(issue_data))
                
                all_issues.extend(jira_issues)
                
                print(f"Fetched batch of {len(issues)} issues (total so far: {len(all_issues)})")
                
                # If we got fewer issues than requested, we've reached the end
                if len(issues) < batch_size:
                    print(f"Reached end of results. Total issues fetched: {len(all_issues)}")
                    break
                
                start_at += batch_size
                
                # Safety check to prevent infinite loops
                if max_results and len(all_issues) >= max_results:
                    all_issues = all_issues[:max_results]
                    break
                    
            except Exception as e:
                print(f"Error retrieving issues batch starting at {start_at}: {e}")
                break
        
        return all_issues

    @st.cache_data(ttl=3600, show_spinner="Fetching user stories from Jira...")  # Cache for 1 hour
    def _cached_get_user_stories(_self, jql_query, max_results=None):
        """
        Cached version of user stories retrieval.
        This prevents repeated API calls for the same query within 1 hour.
        """
        try:
            issues = _self._get_all_issues(jql_query, max_results)
            user_stories = []
            for issue in issues:
                # Parse ADF description to plain text
                description = issue.fields.description if issue.fields.description else "No description available."
                if description and description != "No description available.":
                    description = ADFParser.parse_adf_to_text(description)
                
                user_stories.append({
                    "key": issue.key,
                    "title": issue.fields.summary,
                    "description": description
                })
            
            print(f"Retrieved {len(user_stories)} user stories from Jira")
            
            # Sanitize the stories before returning
            sanitized_stories = _self.sanitizer.sanitize_stories_list(user_stories)
            return sanitized_stories
        except Exception as e:
            print(f"Error retrieving Jira issues: {e}")
            return []

    def get_user_stories(self, jql_query=story_jql_query, max_results=None):
        """
        Retrieves ALL user stories from Jira based on a JQL query using pagination.
        Returns a sanitized list of dictionaries with key, title, and description.
        Uses caching to improve performance.
        """
        return self._cached_get_user_stories(jql_query, max_results)

    @st.cache_data(ttl=3600, show_spinner="Fetching bug tickets from Jira...")  # Cache for 1 hour
    def _cached_get_bug_tickets(_self, jql_query, max_results=None):
        """
        Cached version of bug tickets retrieval.
        This prevents repeated API calls for the same query within 1 hour.
        """
        try:
            issues = _self._get_all_issues(jql_query, max_results)
            bug_tickets = []
            for issue in issues:
                # Parse ADF description to plain text
                description = issue.fields.description if issue.fields.description else "No description available."
                if description and description != "No description available.":
                    description = ADFParser.parse_adf_to_text(description)
                
                bug_tickets.append({
                    "key": issue.key,
                    "title": issue.fields.summary,
                    "description": description,
                    "labels": issue.fields.labels if issue.fields.labels else []
                })
            
            print(f"Retrieved {len(bug_tickets)} bug tickets from Jira")
            
            # Sanitize the bug tickets before returning
            sanitized_bugs = _self.sanitizer.sanitize_bugs_list(bug_tickets)
            return sanitized_bugs
        except Exception as e:
            print(f"Error retrieving Jira bug issues: {e}")
            return []

    def get_bug_tickets(self, jql_query=bug_jql_query, max_results=None):
        """
        Retrieves ALL bug tickets from Jira based on a JQL query using pagination.
        Returns a sanitized list of dictionaries with key, title, description, and labels.
        Uses caching to improve performance.
        """
        return self._cached_get_bug_tickets(jql_query, max_results)

    if __name__ == "__main__":
        try:
            jira_client = JiraClient()
            print("Retrieving user stories...")
            stories = jira_client.get_user_stories(jql_query=JiraClient.story_jql_query)
            for story in stories:
                print(f"Key: {story['key']}, Title: {story['title']}")

            print("\nRetrieving bug tickets...")
            bug_tickets = jira_client.get_bug_tickets(jql_query=JiraClient.bug_jql_query)
            for ticket in bug_tickets:
                print(f"Key: {ticket['key']}, Title: {ticket['title']}")
        except ValueError as e:
            print(f"Configuration error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")