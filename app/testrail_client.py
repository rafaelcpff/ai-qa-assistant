import os
import streamlit as st
from typing import List, Dict, Optional, Tuple
import re
import requests
import json

# Try to import TestRailAPI, with fallback handling
try:
    from testrail_api import TestRailAPI
    TESTRAIL_API_AVAILABLE = True
except ImportError:
    TESTRAIL_API_AVAILABLE = False
    st.error("❌ testrail-api package not found. Install with: pip install testrail-api==1.8.0")
except AttributeError as e:
    if "__default_response_handler" in str(e):
        TESTRAIL_API_AVAILABLE = False
        st.error("❌ TestRail API library compatibility issue detected.")
        st.error("💡 Try: pip uninstall testrail-api && pip install testrail-api==1.8.0")
    else:
        TESTRAIL_API_AVAILABLE = False
        st.error(f"❌ TestRail API library error: {e}")

class TestRailClient:
    def __init__(self):
        self.client = None
        self._connect()
    
    @st.cache_data(ttl=3600, show_spinner="Connecting to TestRail...") # Cache connection for 1 hour
    def _cached_connect(_self, testrail_url: str, testrail_username: str, testrail_password: str):
        """
        Cached version of TestRail connection.
        This prevents repeated connection setup and authentication within 1 hour.
        Returns a tuple of (client, status, error_message) for external UI handling.
        """
        if not TESTRAIL_API_AVAILABLE:
            return None, "library_unavailable", "TestRail API library is not available due to compatibility issues. Please run: pip uninstall testrail-api && pip install testrail-api==1.8.0"
            
        try:
            # Use the TestRailAPI class from testrail-api package
            client = TestRailAPI(testrail_url, testrail_username, testrail_password)
            
            # Test connection by trying to get a case
            try:
                # Try to get a test case to verify connection
                client.cases.get_case(1)
            except Exception as test_error:
                # If case 1 doesn't exist, try to get projects instead
                try:
                    client.projects.get_projects()
                except Exception as project_error:
                    # If both fail, log the error but don't fail the connection
                    return client, "connection_warning", f"TestRail connection test failed, but connection may still work: {str(project_error)}"
            
            # If we get here, connection was successful
            return client, "success", "Successfully connected to TestRail"
            
        except AttributeError as attr_error:
            if "__default_response_handler" in str(attr_error):
                error_msg = "TestRail API library compatibility issue detected. This is a known issue with certain versions of the testrail-api package. Solution: Run 'pip uninstall testrail-api && pip install testrail-api==1.8.0' then restart the application."
                return None, "compatibility_error", error_msg
            else:
                error_msg = f"TestRail API library compatibility issue: {str(attr_error)}. Try updating the testrail-api package: pip install --upgrade testrail-api"
                return None, "library_error", error_msg
        except Exception as e:
            error_msg = f"Failed to connect to TestRail: {str(e)}"
            return None, "connection_error", error_msg
    
    def _connect(self):
        """Initialize TestRail API client connection using caching."""
        testrail_url = os.getenv("TESTRAIL_URL")
        testrail_username = os.getenv("TESTRAIL_USERNAME")
        testrail_password = os.getenv("TESTRAIL_PASSWORD")
        
        if not all([testrail_url, testrail_username, testrail_password]):
            st.warning("⚠️ TestRail credentials not found in environment variables. Please add TESTRAIL_URL, TESTRAIL_USERNAME, and TESTRAIL_PASSWORD to your .env file.")
            return
        
        # Use cached connection
        result = self._cached_connect(testrail_url, testrail_username, testrail_password)
        self.client, status, message = result
        
        # Handle different connection statuses with appropriate UI messages

        col1, col2, col3 = st.columns(3)

        with col1:
            if status == "success":
                st.success("Successfully connected to TestRail", icon="🎉")
            elif status == "connection_warning":
                st.warning(f"⚠️ {message}")
            elif status == "library_unavailable":
                st.error("❌ TestRail API library is not available due to compatibility issues.")
                st.error("💡 Please run: pip uninstall testrail-api && pip install testrail-api==1.8.0")
            elif status == "compatibility_error":
                st.error("❌ TestRail API library compatibility issue detected.")
                st.error("💡 This is a known issue with certain versions of the testrail-api package.")
                st.error("💡 **Solution:** Run these commands:")
                st.error("   pip uninstall testrail-api")
                st.error("   pip install testrail-api==1.8.0")
                st.error("   Then restart the application.")
            elif status == "library_error":
                st.error(f"❌ {message}")
            elif status == "connection_error":
                st.error(f"❌ {message}")


        
        # If connection failed, provide additional troubleshooting guidance
        if self.client is None:
            st.error("❌ TestRail connection failed. This may be due to:")
            st.error("1. Incorrect credentials in .env file")
            st.error("2. TestRail API library compatibility issues")
            st.error("3. Network connectivity problems")
            st.error("")
            st.error("💡 **Troubleshooting steps:**")
            st.error("• Check your TESTRAIL_URL, TESTRAIL_USERNAME, and TESTRAIL_PASSWORD in .env")
            st.error("• Try updating the testrail-api package: `pip install --upgrade testrail-api`")
            st.error("• Verify your TestRail instance is accessible from this environment")
    
    @st.cache_data(ttl=1800, show_spinner="Fetching test cases from TestRail...")  # Cache for 30 minutes
    def _cached_get_all_test_cases(_self, project_id: int = None) -> List[Dict]:
        """Cached version of test cases retrieval. Cache for 30 minutes."""
        if not _self.client:
            return []
        
        try:
            if project_id:
                all_cases = []
                offset = 0
                limit = 250  # TestRail default page size
                
                while True:
                    # Get cases with pagination parameters
                    response = _self.client.cases.get_cases(project_id, limit=limit, offset=offset)
                    cases = _self._parse_testrail_response(response)
                    
                    if not cases:
                        break
                    
                    all_cases.extend(cases)
                    
                    # If we got fewer cases than the limit, we've reached the end
                    if len(cases) < limit:
                        break
                    
                    offset += limit
                
                st.info(f"🔍 Retrieved {len(all_cases)} test cases from TestRail project {project_id} across all pages")
                return all_cases
            else:
                # Get all projects first, then get cases from each
                projects = _self.client.projects.get_projects()
                all_cases = []
                
                for project in projects:
                    project_cases = _self._cached_get_all_test_cases(project["id"])
                    all_cases.extend(project_cases)
                
                return all_cases
            
        except Exception as e:
            st.error(f"❌ Error retrieving test cases from TestRail: {str(e)}")
            return []

    def get_all_test_cases(self, project_id: int = None) -> List[Dict]:
        """Retrieve all test cases from TestRail with pagination support."""
        return self._cached_get_all_test_cases(project_id)
    
    def _parse_testrail_response(self, response) -> List[Dict]:
        """Parse TestRail API response to extract test cases."""
        if isinstance(response, dict):
            # Debug: Log the response structure
            st.info(f"🔍 Debug: Response is dict with keys: {list(response.keys())}")
            
            # Check if this is a paginated response with 'cases' field
            if 'cases' in response:
                cases = response['cases']
                if isinstance(cases, list):
                    st.info(f"🔍 Debug: Found {len(cases)} cases in paginated response")
                    return cases
                else:
                    st.warning(f"⚠️ Unexpected 'cases' field type: {type(cases)}")
                    return []
            else:
                # It might be a single test case or a different structure
                # Check if it has test case fields
                if 'id' in response and 'title' in response:
                    st.info("🔍 Debug: Found single test case in response")
                    return [response]
                else:
                    # If it's a dict but doesn't look like a test case, return as list
                    st.info(f"🔍 Debug: Response dict doesn't look like test case, returning as list")
                    return [response]
        elif isinstance(response, list):
            st.info(f"🔍 Debug: Response is list with {len(response)} items")
            return response
        else:
            st.warning(f"⚠️ Unexpected response type from TestRail: {type(response)}")
            return []
    
    def get_test_case(self, case_id: int) -> Optional[Dict]:
        """Retrieve a specific test case by ID."""
        if not self.client:
            return None
        
        try:
            case = self.client.cases.get_case(case_id)
            return case
        except Exception as e:
            st.error(f"❌ Error retrieving test case {case_id}: {str(e)}")
            return None
    
    def create_test_case(self, section_id: int, title: str, custom_steps_separated: List[Dict] = None, 
                        custom_expected: str = None, custom_preconds: str = None) -> Optional[Dict]:
        """Create a new test case in TestRail."""
        if not self.client:
            return None
        
        try:
            data = {
                'title': title,
                'type_id': 1,  # Functional test case
                'priority_id': 2,  # Medium priority
            }
            
            if custom_steps_separated:
                data['custom_steps_separated'] = custom_steps_separated
            
            if custom_expected:
                data['custom_expected'] = custom_expected
            
            if custom_preconds:
                data['custom_preconds'] = custom_preconds
            
            case = self.client.cases.add_case(section_id, **data)
            return case
        except Exception as e:
            st.error(f"❌ Error creating test case: {str(e)}")
            return None
    
    def update_test_case(self, case_id: int, title: str = None, custom_steps_separated: List[Dict] = None,
                        custom_expected: str = None, custom_preconds: str = None) -> Optional[Dict]:
        """Update an existing test case in TestRail."""
        if not self.client:
            return None
        
        try:
            data = {}
            
            if title:
                data['title'] = title
            
            if custom_steps_separated:
                data['custom_steps_separated'] = custom_steps_separated
            
            if custom_expected:
                data['custom_expected'] = custom_expected
            
            if custom_preconds:
                data['custom_preconds'] = custom_preconds
            
            if data:
                case = self.client.cases.update_case(case_id, **data)
                return case
            
            return None
        except Exception as e:
            st.error(f"❌ Error updating test case {case_id}: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600, show_spinner="Fetching sections from TestRail...")  # Cache for 1 hour
    def _cached_get_sections(_self, project_id: int) -> List[Dict]:
        """Cached version of sections retrieval. Cache for 1 hour."""
        if not _self.client:
            return []
        
        try:
            sections = _self.client.sections.get_sections(project_id)
            return sections
        except Exception as e:
            st.error(f"❌ Error retrieving sections: {str(e)}")
            return []

    def get_sections(self, project_id: int) -> List[Dict]:
        """Get all sections for a project."""
        return self._cached_get_sections(project_id)
    
    def create_section(self, project_id: int, name: str, parent_id: int = None) -> Optional[Dict]:
        """Create a new section in TestRail."""
        if not self.client:
            return None
        
        try:
            data = {'name': name}
            if parent_id:
                data['parent_id'] = parent_id
            
            section = self.client.sections.add_section(project_id, **data)
            return section
        except Exception as e:
            st.error(f"❌ Error creating section: {str(e)}")
            return None

def extract_test_case_info(text: str) -> List[Dict]:
    """Extract test case information from AI-generated text."""
    test_cases = []
    format_detected = "None"
    
    # First, try to extract from the new plain text TC-### format
    tc_pattern = r'TC-\d+\s*-\s*(.+?)(?=\n|$)'
    tc_matches = list(re.finditer(tc_pattern, text, re.IGNORECASE | re.DOTALL))
    
    if tc_matches:
        format_detected = "Plain text TC-### format"
        st.info(f"🔍 Detected {len(tc_matches)} test cases in plain text format")
        
        for match in tc_matches:
            title = match.group(1).strip()
            
            # Look for the content that follows this TC section
            start_pos = match.end()
            # Find the next section or end of text
            next_section = re.search(r'TC-\d+', text[start_pos:], re.IGNORECASE)
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = len(text)
            
            tc_content = text[start_pos:end_pos]
            
            # Extract information from the plain text format
            steps = []
            preconditions = ''
            expected_results = ''
            automation = 'No'  # Default value
            priority = 'Medium'  # Default value
            tags = ''  # Default value
            scenario_id = ''  # Default value
            
            # Extract Scenario ID
            scenario_match = re.search(r'Scenario ID:\s*([^\n]+)', tc_content, re.IGNORECASE)
            if scenario_match:
                scenario_id = scenario_match.group(1).strip()
            
            # Extract Priority
            priority_match = re.search(r'Priority:\s*([^\n]+)', tc_content, re.IGNORECASE)
            if priority_match:
                priority = priority_match.group(1).strip()
            
            # Extract Automation status
            automation_match = re.search(r'Automation:\s*([^\n]+)', tc_content, re.IGNORECASE)
            if automation_match:
                automation = automation_match.group(1).strip()
            
            # Extract Tags
            tags_match = re.search(r'Tags:\s*([^\n]+)', tc_content, re.IGNORECASE)
            if tags_match:
                tags = tags_match.group(1).strip()
            
            # Extract preconditions
            precond_match = re.search(r'Preconditions:\s*\n(.*?)(?=\n\w+:|$)', tc_content, re.IGNORECASE | re.DOTALL)
            if precond_match:
                preconditions = precond_match.group(1).strip()
            
            # Extract test steps with expected results
            steps_match = re.search(r'Test Steps:\s*\n(.*?)(?=\n\w+:|$)', tc_content, re.IGNORECASE | re.DOTALL)
            if steps_match:
                steps_text = steps_match.group(1)
                
                # Parse numbered steps with expected results in the format:
                # 1. [Action/Step]
                #    - Expected: [Expected result]
                step_pattern = r'(\d+)\.\s*(.+?)(?=\n\s*-\s*Expected:|\n\d+\.|\n\w+:|$)'
                expected_pattern = r'-\s*Expected:\s*(.+?)(?=\n\d+\.|\n\w+:|$)'
                
                step_matches = list(re.finditer(step_pattern, steps_text, re.DOTALL))
                expected_matches = list(re.finditer(expected_pattern, steps_text, re.DOTALL))
                
                for i, step_match in enumerate(step_matches):
                    step_content = step_match.group(2).strip()
                    expected = ''
                    
                    # Find corresponding expected result
                    if i < len(expected_matches):
                        expected = expected_matches[i].group(1).strip()
                    
                    steps.append({
                        'content': step_content,
                        'expected': expected
                    })
            
            # If no structured steps found, try alternative patterns
            if not steps:
                # Look for simple numbered steps (without expected results)
                simple_step_pattern = r'(\d+)\.\s*(.+?)(?=\n\d+\.|\n\w+:|$)'
                simple_matches = re.findall(simple_step_pattern, tc_content, re.DOTALL)
                for step_num, step_content in simple_matches:
                    steps.append({'content': step_content.strip(), 'expected': ''})
                
                # Also try to find any remaining numbered steps in the entire content
                if not steps:
                    remaining_step_pattern = r'(\d+)\.\s*(.+?)(?=\n\d+\.|\n\w+:|$)'
                    remaining_matches = re.findall(remaining_step_pattern, tc_content, re.DOTALL)
                    for step_num, step_content in remaining_matches:
                        steps.append({'content': step_content.strip(), 'expected': ''})
            
            # Create test case structure with all extracted fields
            test_case = {
                'title': title,
                'steps': steps if steps else [{'content': 'Test case steps not found', 'expected': ''}],
                'preconditions': preconditions,
                'expected_results': expected_results,
                'automation': automation,
                'priority': priority,
                'tags': tags,
                'scenario_id': scenario_id
            }
            
            test_cases.append(test_case)
    
    # If no plain text format found, try the markdown format
    if not test_cases:
        # Look for markdown format
        tc_pattern = r'###\s*TC-\d+\s*–\s*(.+?)(?=\n|$)'
        tc_matches = list(re.finditer(tc_pattern, text, re.IGNORECASE | re.DOTALL))
        
        if tc_matches:
            format_detected = "Markdown format"
            st.info(f"🔍 Detected {len(tc_matches)} test cases in markdown format")
            
            for match in tc_matches:
                title = match.group(1).strip()
                
                # Look for the content that follows this TC section
                start_pos = match.end()
                # Find the next section or end of text
                next_section = re.search(r'###\s*TC-\d+', text[start_pos:], re.IGNORECASE)
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = len(text)
                
                tc_content = text[start_pos:end_pos]
                
                # Extract information from markdown format
                steps = []
                preconditions = ''
                expected_results = ''
                automation = 'No'  # Default value
                priority = 'Medium'  # Default value
                tags = ''  # Default value
                scenario_id = ''  # Default value
                
                # Extract Scenario ID
                scenario_match = re.search(r'\*\*Scenario ID:\*\*\s*([^\n]+)', tc_content, re.IGNORECASE)
                if scenario_match:
                    scenario_id = scenario_match.group(1).strip()
                
                # Extract Priority
                priority_match = re.search(r'\*\*Priority:\*\*\s*([^\n]+)', tc_content, re.IGNORECASE)
                if priority_match:
                    priority = priority_match.group(1).strip()
                
                # Extract Automation status
                automation_match = re.search(r'\*\*Automation:\*\*\s*([^\n]+)', tc_content, re.IGNORECASE)
                if automation_match:
                    automation = automation_match.group(1).strip()
                
                # Extract Tags
                tags_match = re.search(r'\*\*Tags:\*\*\s*([^\n]+)', tc_content, re.IGNORECASE)
                if tags_match:
                    tags = tags_match.group(1).strip()
                
                # Extract preconditions from markdown table
                precond_match = re.search(r'Preconditions\s*\|\s*\n(.*?)(?=\n\w+\s*\|)', tc_content, re.IGNORECASE | re.DOTALL)
                if precond_match:
                    preconditions = precond_match.group(1).strip()
                
                # Extract test steps from markdown table
                steps_match = re.search(r'Test Steps\s*\|\s*\n(.*?)(?=\n\w+\s*\|)', tc_content, re.IGNORECASE | re.DOTALL)
                if steps_match:
                    steps_text = steps_match.group(1)
                    # Parse table rows
                    row_pattern = r'(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|'
                    row_matches = re.findall(row_pattern, steps_text, re.DOTALL)
                    
                    for row in row_matches:
                        step_num, action, expected, actual, status = row
                        steps.append({
                            'content': action.strip(),
                            'expected': expected.strip()
                        })
                
                # Create test case structure with all extracted fields
                test_case = {
                    'title': title,
                    'steps': steps if steps else [{'content': 'Test case steps not found', 'expected': ''}],
                    'preconditions': preconditions,
                    'expected_results': expected_results,
                    'automation': automation,
                    'priority': priority,
                    'tags': tags,
                    'scenario_id': scenario_id
                }
                
                test_cases.append(test_case)
    
    # If still no test cases found, try legacy format
    if not test_cases:
        format_detected = "Legacy format"
        st.info("🔍 Trying legacy format extraction")
        
        # Simple extraction for legacy format
        lines = text.split('\n')
        current_case = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('TC-') and '-' in line:
                if current_case:
                    test_cases.append(current_case)
                
                # Extract title
                title = line.split('-', 1)[1].strip()
                current_case = {
                    'title': title,
                    'steps': [],
                    'preconditions': '',
                    'expected_results': '',
                    'automation': 'No',
                    'priority': 'Medium',
                    'tags': '',
                    'scenario_id': ''
                }
            elif current_case and line.startswith(('1.', '2.', '3.', '4.', '5.')):
                step_content = line.split('.', 1)[1].strip()
                current_case['steps'].append({'content': step_content, 'expected': ''})
        
        if current_case:
            test_cases.append(current_case)
    
    st.info(f"🔍 Extracted {len(test_cases)} test cases using {format_detected}")
    
    # Debug: Show automation status for first few cases
    for i, case in enumerate(test_cases[:3]):
        st.info(f"🔍 Case {i+1}: Automation = '{case.get('automation', 'N/A')}', Priority = '{case.get('priority', 'N/A')}'")
    
    return test_cases

def find_similar_test_cases(generated_cases: List[Dict], existing_cases: List[Dict], 
                          similarity_threshold: float = 0.7, user_story_key: str = None,
                          cm_modules: str = None, cm_product_area: str = None) -> List[Tuple[Dict, Dict, float]]:
    """Find similar test cases between generated and existing ones with targeted search first."""
    similar_cases = []
    
    st.info(f"🔍 Starting enhanced similarity search: {len(generated_cases)} generated cases vs {len(existing_cases)} existing cases (threshold: {similarity_threshold})")
    
    # Step 1: Try to find test cases by user story reference first
    reference_matches = []
    if user_story_key:
        st.info(f"🔍 Step 1: Searching for test cases referencing user story {user_story_key}")
        reference_matches = find_test_cases_by_user_story_reference(existing_cases, user_story_key)
        if reference_matches:
            st.success(f"✅ Found {len(reference_matches)} test cases referencing {user_story_key}")
            # Add these with high similarity score
            for gen_case in generated_cases:
                for ref_case in reference_matches:
                    similar_cases.append((gen_case, ref_case, 0.9))  # High score for reference matches
        else:
            st.info(f"ℹ️ No test cases found referencing {user_story_key}")
    
    # Step 2: Try to find test cases by module/product area
    module_matches = []
    if cm_modules or cm_product_area:
        st.info(f"🔍 Step 2: Searching for test cases matching modules: {cm_modules}, product area: {cm_product_area}")
        module_matches = find_test_cases_by_module_area(existing_cases, cm_modules, cm_product_area)
        if module_matches:
            st.success(f"✅ Found {len(module_matches)} test cases matching module/product area criteria")
            # Add these with medium-high similarity score
            for gen_case in generated_cases:
                for module_case in module_matches:
                    # Check if this case is already added from reference search
                    already_added = any(existing_case == module_case for _, existing_case, _ in similar_cases)
                    if not already_added:
                        similar_cases.append((gen_case, module_case, 0.8))  # Medium-high score for module matches
        else:
            st.info(f"ℹ️ No test cases found matching module/product area criteria")
    
    # Step 3: General similarity search for remaining cases
    st.info(f"🔍 Step 3: Performing general similarity search on remaining cases")
    
    # Create a set of cases already matched to avoid duplicates
    already_matched_ids = set()
    for _, existing_case, _ in similar_cases:
        if isinstance(existing_case, dict) and 'id' in existing_case:
            already_matched_ids.add(existing_case['id'])
    
    # Filter out already matched cases
    remaining_cases = [case for case in existing_cases if not (isinstance(case, dict) and case.get('id') in already_matched_ids)]
    
    st.info(f"🔍 Performing similarity search on {len(remaining_cases)} remaining cases")
    
    # Debug: Show sample of existing case structure
    if remaining_cases and len(remaining_cases) > 0:
        sample_case = remaining_cases[0]
        if isinstance(sample_case, dict):
            st.info(f"🔍 Sample existing case keys: {list(sample_case.keys())}")
            if 'custom_steps_separated' in sample_case:
                custom_steps = sample_case['custom_steps_separated']
                st.info(f"🔍 custom_steps_separated type: {type(custom_steps)}, value: {custom_steps}")
    
    for i, gen_case in enumerate(generated_cases):
        gen_title = gen_case['title'].lower()
        gen_steps = ' '.join([step['content'] for step in gen_case['steps']]).lower()
        
        case_matches = 0
        best_similarity = 0.0
        
        for j, existing_case in enumerate(remaining_cases):
            try:
                # Handle both dictionary and string cases
                if isinstance(existing_case, dict):
                    existing_title = existing_case.get('title', '').lower()
                    existing_steps = ''
                    
                    # Extract steps from existing case with null checks
                    custom_steps = existing_case.get('custom_steps_separated')
                    if custom_steps and isinstance(custom_steps, list):
                        for step in custom_steps:
                            if isinstance(step, dict):
                                step_content = step.get('content', '')
                                if step_content:
                                    existing_steps += ' ' + step_content.lower()
                            elif isinstance(step, str):
                                existing_steps += ' ' + step.lower()
                    
                    # Also check for other step-related fields
                    if not existing_steps:
                        # Try alternative step fields
                        for field in ['steps', 'test_steps', 'actions']:
                            steps_data = existing_case.get(field)
                            if steps_data:
                                if isinstance(steps_data, list):
                                    for step in steps_data:
                                        if isinstance(step, dict):
                                            step_content = step.get('content', step.get('action', ''))
                                            if step_content:
                                                existing_steps += ' ' + step_content.lower()
                                        elif isinstance(step, str):
                                            existing_steps += ' ' + step.lower()
                                elif isinstance(steps_data, str):
                                    existing_steps += ' ' + steps_data.lower()
                                break
                else:
                    # If existing_case is a string, use it as title
                    existing_title = str(existing_case).lower()
                    existing_steps = ''
                
                # Calculate similarity scores
                title_similarity = _calculate_similarity(gen_title, existing_title)
                steps_similarity = _calculate_similarity(gen_steps, existing_steps)
                
                # Combined similarity score with balanced weighting
                combined_similarity = (title_similarity * 0.6) + (steps_similarity * 0.4)
                
                # Track best similarity for this case
                if combined_similarity > best_similarity:
                    best_similarity = combined_similarity
                
                # Less strict filtering: require minimum title similarity of 0.1 instead of 0.3
                if combined_similarity >= similarity_threshold and title_similarity >= 0.1:
                    similar_cases.append((gen_case, existing_case, combined_similarity))
                    case_matches += 1
                    
                # Debug: Show top 3 similarities for first generated case
                if i == 0 and j < 3:
                    st.info(f"🔍 Debug - Generated case 1 vs Existing case {j+1}:")
                    st.info(f"  Title similarity: {title_similarity:.3f}")
                    st.info(f"  Steps similarity: {steps_similarity:.3f}")
                    st.info(f"  Combined similarity: {combined_similarity:.3f}")
                    st.info(f"  Existing title: {existing_title[:100]}...")
                    st.info(f"  Existing steps: {existing_steps[:100]}...")
                    st.info("---")
                    
            except Exception as e:
                # Log error but continue processing other cases
                st.warning(f"⚠️ Error processing existing case {j}: {str(e)}")
                continue
        
        # Show summary for each generated case
        if case_matches == 0:
            st.warning(f"❌ Generated case {i+1}: No matches (best similarity: {best_similarity:.3f})")
        else:
            st.success(f"✅ Generated case {i+1}: Found {case_matches} matches (best similarity: {best_similarity:.3f})")
    
    # Sort by similarity score (highest first)
    similar_cases.sort(key=lambda x: x[2], reverse=True)
    
    st.info(f"🎯 Total matches found: {len(similar_cases)}")
    return similar_cases

def _calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings using word overlap."""
    if not text1 or not text2:
        return 0.0
    
    # Normalize text
    text1 = text1.lower().strip()
    text2 = text2.lower().strip()
    
    if not text1 or not text2:
        return 0.0
    
    # Split into words and remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'}
    
    words1 = set(word.strip('.,!?;:()[]{}"\'-') for word in text1.split() if word.strip('.,!?;:()[]{}"\'-').lower() not in stop_words and len(word.strip('.,!?;:()[]{}"\'-')) > 2)
    words2 = set(word.strip('.,!?;:()[]{}"\'-') for word in text2.split() if word.strip('.,!?;:()[]{}"\'-').lower() not in stop_words and len(word.strip('.,!?;:()[]{}"\'-')) > 2)
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    if union == 0:
        return 0.0
    
    jaccard_similarity = intersection / union
    
    # Also calculate word overlap percentage
    overlap_percentage = intersection / min(len(words1), len(words2)) if min(len(words1), len(words2)) > 0 else 0.0
    
    # Combine both metrics for better similarity score
    combined_similarity = (jaccard_similarity * 0.6) + (overlap_percentage * 0.4)
    
    return combined_similarity 

def find_test_cases_by_user_story_reference(existing_cases: List[Dict], user_story_key: str) -> List[Dict]:
    """Find test cases that reference a specific user story key in their reference field."""
    if not user_story_key or not existing_cases:
        return []
    
    matching_cases = []
    user_story_key_upper = user_story_key.upper()
    
    for case in existing_cases:
        if isinstance(case, dict):
            # Check refs field (TestRail reference field)
            refs = case.get('refs', '')
            if refs and user_story_key_upper in refs.upper():
                matching_cases.append(case)
                continue
            
            # Also check custom fields that might contain references
            for key, value in case.items():
                if key.startswith('custom_') and isinstance(value, str):
                    if user_story_key_upper in value.upper():
                        matching_cases.append(case)
                        break
    
    return matching_cases

def find_test_cases_by_module_area(existing_cases: List[Dict], cm_modules: str, cm_product_area: str) -> List[Dict]:
    """Find test cases that match the CM Modules and CM Product Area."""
    if not existing_cases:
        return []
    
    matching_cases = []
    
    # Normalize the search terms
    cm_modules_normalized = cm_modules.lower().strip() if cm_modules else ""
    cm_product_area_normalized = cm_product_area.lower().strip() if cm_product_area else ""
    
    for case in existing_cases:
        if isinstance(case, dict):
            case_title = case.get('title', '').lower()
            case_description = ''
            
            # Get case description from various possible fields
            for desc_field in ['description', 'custom_description', 'custom_goals', 'custom_mission']:
                desc_value = case.get(desc_field, '')
                if desc_value:
                    case_description += ' ' + desc_value.lower()
            
            # Check if modules match
            modules_match = False
            if cm_modules_normalized:
                # Split modules by common separators and check each
                module_terms = [term.strip() for term in cm_modules_normalized.replace(',', ';').replace('|', ';').split(';') if term.strip()]
                for module_term in module_terms:
                    if module_term in case_title or module_term in case_description:
                        modules_match = True
                        break
            
            # Check if product area matches
            area_match = False
            if cm_product_area_normalized:
                if cm_product_area_normalized in case_title or cm_product_area_normalized in case_description:
                    area_match = True
            
            # If either modules or product area matches, include the case
            if modules_match or area_match:
                matching_cases.append(case)
    
    return matching_cases 